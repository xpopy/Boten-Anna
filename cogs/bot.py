import asyncio
import json
import os
import sys

import discord
from discord.ext import commands
from requests import get as requestGet
from tendo import singleton

sys.path.append('./cogs')
import utils

#Only allow one bot to be online at the same time
#me = singleton.SingleInstance() 


#Folder and File locations
cogs_folder = 'cogs'

#Check for Discord API token
if utils.getConfig('token') == "PUT_DISCORD_TOKEN_HERE": # Don't actually put your token here, it's only a test to see if there exists a token
	print("\nWrong token, open the settings/config.json file and replace \"PUT_TOKEN_HERE\" with your bots token from the discord developer portal\n" +
			"It has to be surrounded by quotes, example: \"NjQdMzayODY5cTI3ODYtMzA2.XcVZPg.ZjG28fgYJkzEw3abOgs3r3DtJVQ\"\n")
	quit()


returnCode = "exit"
bot = commands.Bot(command_prefix=utils.determine_prefix)

#Make sure cogs folder exists
if not os.path.exists(f'./{cogs_folder}'):
	os.makedirs(f'./{cogs_folder}')

#Load all cogs
print()
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
print()


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



@bot.check
async def globally_block_dms(ctx):
	return ctx.guild is not None

@bot.check
async def log_to_console(ctx):
	if not ctx.invoked_subcommand:
		print('{0.created_at}, Server: {0.guild.name}, User: {0.author}: {0.content}'.format(ctx.message))
		return True



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
		global returnCode
		returnCode = "restart"
		await ctx.send("Restarting, brb :D")
		return await ctx.bot.logout()

@bot.command(aliases=['setpp', 'setprofilepic', 'setprofilepicture'])
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
	await utils.updateServerSettings(server, 'prefix', newPrefix)
	await ctx.send(f"Changed prefix to \"{newPrefix}\"")

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
	return await ctx.bot.logout()

@bot.event
async def on_ready():
	print()
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print()


def run():
	try:
		bot.run(utils.getConfig('token'))
		return returnCode
		
	except Exception as e:
		if isinstance(e, discord.errors.LoginFailure):
			print("\nWrong token, please make sure the token in the config file is the corrent one\n\n")
		else:
			print(e)
