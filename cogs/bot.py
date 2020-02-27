import os
import sys
import json
import time
import asyncio

import discord
from discord.ext import commands
from discord.ext import tasks
from requests import get as requestGet
from tendo import singleton

sys.path.append('./cogs')
import utils

#Folder and File locations
cogs_folder = 'cogs'

#Check for Discord API token
if utils.getConfig('token') == "PUT_DISCORD_TOKEN_HERE": # Don't actually put your token here, it's only a test to see if there exists a token
	print("\nWrong token, open the settings/config.json file and replace \"PUT_TOKEN_HERE\" with your bots token from the discord developer portal\n" +
			"It has to be surrounded by quotes, example: \"NjQdMzayODY5cTI3ODYtMzA2.XcVZPg.ZjG28fgYJkzEw3abOgs3r3DtJVQ\"\n")
	quit()

uptime = time.time()
hasSentUpdateNotification = False
returnCode = "exit"
restartReplyChannel = None
bot = commands.Bot(command_prefix=utils.determine_prefix)

#Make sure cogs folder exists
if not os.path.exists(f'./{cogs_folder}'):
	os.makedirs(f'./{cogs_folder}')

#Load all cogs
print("Loading modules")
for filename in os.listdir(f'./{cogs_folder}'):
	if filename == "utils.py" or filename == "bot.py":
		continue
	if filename.endswith('.py'):
		try:
			bot.load_extension(f'{cogs_folder}.{filename[:-3]}')
			print(f'"{filename}" loaded')
		except Exception as e:
			print(f'"{filename}" failed to load:')
			print(f"\t{e}")

async def exitWithCode(exitCode, ctx):
	global returnCode
	global restartReplyChannel

	if ctx.guild is None:
		restartReplyChannel = str(ctx.message.author.id)
	else:
		restartReplyChannel = str(ctx.channel.id)
	returnCode = exitCode
	player = bot.get_cog('Music')
	try:
		player.disconnect_all_players()
	except:
		pass
	return await bot.logout()


@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.errors.CheckFailure):
		return

	elif isinstance(error, commands.errors.BadArgument):
		await ctx.send(error)

	elif isinstance(error, commands.errors.MissingRequiredArgument):
		if ctx.command.parent is not None:
			await utils.helpFunction(ctx, helpCommand = ctx.command.parent.aliases + [ctx.command.parent.name] )
		else:
			await utils.helpFunction(ctx, helpCommand = ctx.command.aliases + [ctx.command.name] )

	elif isinstance(error, discord.errors.Forbidden):
		print("Missing permissions")
		await ctx.send("Something failed because I'm missing permissions, check documentation or contact the developer")

	elif isinstance(error, commands.errors.CommandNotFound):
		return

	else:
		raise(error)


#Disabled
'''
@bot.check
async def globally_block_dms(ctx):
	if ctx.guild is not None:
		return True
	else:
		if ctx.command == "update" or ctx.command == "help":
			return True
		else:
			return False
'''

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	if message.guild is None:
		if (message.content.startswith('update') or 
		   message.content.startswith('restart') or 
		   message.content.startswith('reload') or 
		   message.content.startswith('help')):
			await bot.process_commands(message)
		else:
			info = await bot.application_info()
			if message.author == info.owner:
				await message.channel.send("I only respond to `help`, `update` or `restart` without any prefixes")
			else:
				await message.channel.send("I only respond to `help` without any prefixes")
	else:
		await bot.process_commands(message)

		
@bot.check
async def log_to_console(ctx):
	if not ctx.invoked_subcommand:
		msg = ctx.message
		if ctx.guild is None:
			print(f'{msg.created_at}, DM, User: {msg.author}: {msg.content}')
		else:
			print(f'{msg.created_at}, Server: {msg.guild.name}, User: {msg.author}: {msg.content}')
	return True
	
@tasks.loop(seconds=86400.0)
async def check_for_update():
	global hasSentUpdateNotification
	if not hasSentUpdateNotification:
		try:
			json_data = requestGet("https://raw.githubusercontent.com/xpopy/Boten-Anna/master/app.json").json()
			onlineVersion = json_data['version']
			currentVersion = 0

			with open('app.json') as json_file:
				data = json.load(json_file)
				currentVersion = data['version']

			if utils.versiontuple(onlineVersion) > utils.versiontuple(currentVersion):
				#There's a new version, send a message to owner that the bot can be updated
				info = await bot.application_info()
				hasSentUpdateNotification = True

				updateString = (f"There's a new version available: {onlineVersion}, your version: {currentVersion}" +
							"\nPlease run \"(prefix)update\" in order to automatically update." +
							"\nDon't forget to check the console output to see if the update went well.\n")

				await info.owner.send(updateString)
				print(updateString)

		except Exception as e:
			print(e)


@bot.command()
@commands.is_owner()
async def update(ctx):
	await ctx.send("Updating, brb :D")
	await exitWithCode("update", ctx)


@bot.command()
@commands.is_owner()
async def load(ctx, extension):
	'''Loads the specified extension'''
	try:
		bot.load_extension(f'{cogs_folder}.{extension}')
		response = f'\'{extension}\' has been loaded'
		await ctx.send(response)
		print(response)
	except Exception as e:
		print(e)

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
	'''Unloads the specified extension'''
	try:
		bot.unload_extension(f'{cogs_folder}.{extension}')
		response = f'\'{extension}\' has been unloaded'
		await ctx.send(response)
		print(response)
	except commands.errors.ExtensionNotLoaded:
		response = f'\'{filename[:-3]}\' was not loaded, will ignore'
		await ctx.send(response)
		print(response)

@bot.command(aliases=["restart"])
@commands.is_owner()
async def reload(ctx, extension = None):
	'''Reloads the specified extension. \n
	If no extension is given then reload all extensions'''
	if extension:
		try:
			bot.reload_extension(f'{cogs_folder}.{extension}')
			response = f'\'{extension}\' has been reloaded'
			await ctx.send(response)
			print(response)
		except Exception as e:
			await ctx.send(e)
			print(e)
		return
	else:
		await exitWithCode("restart", ctx)

@bot.command(aliases=['setprofilepic'])
@commands.is_owner()
async def setprofilepicture_(ctx, url):
	img_data = requestGet(url).content
	with open('profilePic.jpg', 'wb') as handler:
		handler.write(img_data)
	with open('profilePic.jpg', 'rb') as fp:
		await bot.user.edit(avatar=fp.read())
	await ctx.send("New profile picture set, it may take a few seconds for it to update")

@bot.command(aliases=['prefix', 'annaprefix'])
@commands.has_permissions(administrator=True)
async def prefix_(ctx, *args):
	if len(args) == 0:
		return await ctx.send(f"Current prefix is \"{ await utils.determine_prefix(bot, ctx.message)}\"")

	newPrefix = " ".join(args)
	if newPrefix.isspace():
		return await ctx.send(f"The prefix can not be only spaces")

	server = str(ctx.guild.id)
	utils.updateServerSettings(server, 'prefix', newPrefix)
	await ctx.send(f"Changed prefix to \"{newPrefix}\"")

@bot.command()
async def github(ctx):
	await ctx.send("Here you can find the official github repository for this bot: https://github.com/xpopy/Boten-Anna")

@bot.command()
async def invite(ctx):
	await ctx.send(f"https://discordapp.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=3501120&scope=bot")

@bot.command()
async def stats(ctx):
	amountOfGuilds = len(bot.guilds)
	amountOfMembers = 0
	for guild in bot.guilds:
		amountOfMembers += guild.member_count
	file_amount, total_size = utils.folder_info("./music_cache")

	text = f"Uptime: {utils.formatUptime(time.time() - uptime)}\n"
	if amountOfGuilds == 1:
		text += f"Serving {amountOfGuilds} guild with {amountOfMembers} members\n"
	else:
		text += f"Serving {amountOfGuilds} guilds with {amountOfMembers} members\n"
	text += f"{utils.bytesToReadable(total_size)} storage used for {file_amount} cached songs"

	embed = discord.Embed(title="", description=text)
	await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def debug(ctx):
	from pprint import pprint
	musicCog = bot.get_cog('music')
	if musicCog is not None:
		mPlayer = musicCog.get_player(ctx.guild)
		print("\n\n")
		for element in dir(mPlayer):
			if "__" in element:
				continue
			print(f"{element}: \t \t{getattr(mPlayer, element)}\n")

#Discord.py generates its own help command, lets remove that to make our own
bot.remove_command('help')
@bot.command(aliases=['help', 'commands'])
async def help_(ctx, *args):
	argslen = len(args)
	if argslen == 0:
		await utils.helpFunction(ctx)
	elif argslen == 1:
		await utils.helpFunction(ctx, helpCommand=args[0])
	else:
		await ctx.send("Too many arguments")

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
	await ctx.send("Shutting down...")
	await exitWithCode("exit", ctx)

@bot.event
async def on_ready():
	print()
	
	print("Loading done\n")
	print("-------------------------------------\n")

	ver = ""
	with open('app.json') as json_file:
		data = json.load(json_file)
		ver = data['version']
	
	print('Client:')
	print(f"{bot.user.name}, {bot.user.id}, Version: {ver}")
	print()

	info = await bot.application_info()
	print('Owner:')
	print(f"{info.owner.name}, {info.owner.id}")
	print()
	if not bot.guilds:
		print("The bot haven't joined any servers, copy the link below and add the bot to your server to get started\n"
			 		+ f"https://discordapp.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=3501120&scope=bot")
	else:
		print('Guild list:')
		for guild in bot.guilds:
			print(f"{guild.name}, {guild.id}")
	print()
	
	if restartReplyChannel is not None:
		channel = bot.get_channel(int(restartReplyChannel))
		if channel is None:
			channel = bot.get_user(int(restartReplyChannel))
			
		if channel is not None:
			if returnCode == "restart":
				await channel.send("Succesfully restarted")
			elif returnCode == "update":
				await channel.send("Succesfully updated")

	check_for_update.start()

	


def run(action = "exit", channelID = None):
	try:
		global returnCode
		global restartReplyChannel

		me = singleton.SingleInstance() 

		returnCode = action
		restartReplyChannel = channelID

		bot.run(utils.getConfig('token'))

		del me
		return returnCode, restartReplyChannel
		
	except Exception as e:
		if isinstance(e, discord.errors.LoginFailure):
			print("\nWrong token, please make sure the token in the config file is the corrent one\n\n")
		else:
			print(e)
