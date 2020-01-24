import asyncio
import json
import os
import time
from subprocess import PIPE as subprocPIPE
from subprocess import STDOUT as subprocSTDOUT
from subprocess import Popen as subprocPopen
from urllib import parse as urlParse

import discord
from bs4 import BeautifulSoup as bs4Soup
from requests import get as requestGet

import ytdl

configCache = {}
serverSettingsCache = {}
playlistCache = {}
server_settings_location = "settings/serverSettings.json"
playlist_location = "settings/serverPlaylists.json"
defaultPrefix = "$"
defaultSettings = {"volume": 0.5,
				   "acceptedVoiceChannels": [],
				   "acceptedTextChannels": [],
				   'prefix': defaultPrefix,
				   'dj_role': None,
				   'nowPlayingAuto': True,
				   'nowPlayingSticky': True,
				   'nowPlayingControls': True}


def initializeJsonFile(fileLocation):
	print("Initializing the server settings file")
	os.makedirs(os.path.dirname(fileLocation), exist_ok=True)
	with open(fileLocation, 'w+') as f:
		data = {}
		json.dump(data, f)

async def determine_prefix(bot, message):
	''' Returns the prefix for the server that the message was sent in '''
	#Only allow custom prefixs in guild
	if message.guild:
		return getServerSetting(message.guild.id, "prefix")
	else:
		return getConfig("prefix")

def getConfig(key):
	''' Returns the bot config if it exists, otherwise generate it '''
	global configCache
	if configCache:
		return configCache[key]

	configFile = 'settings/config.json'
	if not os.path.exists(configFile):
		os.makedirs(os.path.dirname(configFile), exist_ok=True)
		with open(configFile, 'w+') as f:
			data = ('{ \n' +
						'\t"token": "PUT_DISCORD_TOKEN_HERE", \n' +
						'\t"tenor_key": "PUT_TENOR_TOKEN_HERE", \n' +
						f'\t"defaultPrefix": "{defaultPrefix}"\n' +
					'}')
			f.write(data)
			print()
			print("Generated config file, open it and insert the bot token")
			print()
			quit()
	else:
		with open(configFile) as json_file:
			data = json.load(json_file)
	return data[key]

def getServerSetting(server, field):
	''' Returns the server settings if it exists, otherwise generate it '''
	global serverSettingsCache
	if type(server) == int:
		server = str(server)

	if serverSettingsCache:
		if server in serverSettingsCache:
			if field not in serverSettingsCache[server]:
				updateServerSettings(server, field, defaultSettings[field])
			return serverSettingsCache[server][field]

	if not os.path.exists(server_settings_location):
		initializeJsonFile(server_settings_location)

	with open(server_settings_location, 'r+') as json_file:
		data = json.load(json_file)
		if server not in data:
			data[server] = defaultSettings
			json_file.seek(0)
			json.dump(data, json_file)
			json_file.truncate()
			serverSettingsCache = data
		else:
			serverSettingsCache = data

	if field not in serverSettingsCache[server]:
		updateServerSettings(server, field, defaultSettings[field])
	return serverSettingsCache[server][field]

def updateServerSettings(server, field, new_value):
	''' Updates the server settings if it exists, otherwise generate it '''
	global serverSettingsCache
	if type(server) == int:
		server = str(server)

	if not os.path.exists(server_settings_location):
		initializeJsonFile(server_settings_location)
		
	with open(server_settings_location, 'r+') as json_file:
		data = json.load(json_file)
		json_file.seek(0)

		if server not in data:
			data[server] = {}

		data[server][field] = new_value
		json.dump(data, json_file)
		json_file.truncate()
		serverSettingsCache = data

def getServerPlaylist(server):
	''' Returns the server playlist if it exists, otherwise generate it '''
	global playlistCache
	if type(server) == int:
		server = str(server)	

	if playlistCache:
		if server in playlistCache:
			return playlistCache[server]
		else:
			return []

	if not os.path.exists(playlist_location):
		initializeJsonFile(playlist_location)

	with open(playlist_location, 'r+') as json_file:
		data = json.load(json_file)
		if server not in data:
			data[server] = []
			json_file.seek(0)
			json.dump(data, json_file)
			json_file.truncate()
			playlistCache = data
		else:
			playlistCache = data
		
	return playlistCache[server]

def updateServerPlaylist(server, new_value):
	''' Updates the server playlist '''
	global playlistCache
	if type(server) == int:
		server = str(server)

	if not os.path.exists(playlist_location):
		initializeJsonFile(playlist_location)
		
	with open(playlist_location, 'r+') as json_file:
		data = json.load(json_file)
		json_file.seek(0)

		if server not in data:
			data[server] = {}

		data[server] = new_value
		json.dump(data, json_file)
		json_file.truncate()
		playlistCache = data


def representsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

async def set_message_reactions(msg, new_reactions):
	await msg.clear_reactions()
	for reaction in new_reactions:
		await msg.add_reaction(reaction)

def get_playlist_info_async(url):
	cmd = ["youtube-dl", "-J", "-i", "--flat-playlist", url]
	proc = subprocPopen(cmd, stdout=subprocPIPE, stderr=subprocPIPE)
	o, _ = proc.communicate()
	data_string = o.decode('ascii')

	data = json.loads(data_string)
	#print(data)
	playlist_name = data['title']
	playlist_url = data['webpage_url']
	data = data['entries']
	domain = "https://www.youtube.com/watch?v="
	urls = []
	#print(data[0])
	for video in data:
		url = domain + video["id"]
		urls.append(url)

	return (clampTitle(playlist_name), playlist_url, urls)

async def get_playlist_info(url, loop=None):
	loop = loop or asyncio.get_event_loop()
	return await loop.run_in_executor(None, lambda: get_playlist_info_async(url))

def isurl(url):
	#Find the start position of the ID
	return "https://" in url

def clampTitle(title):
	maxLength = 40
	if len(title) > maxLength:
		title = title[:maxLength] + "..."
	if title.rfind("[") > title.rfind("]"):
		title = title[:title.rfind("[")]
	return title

def get_song_data_async(url):
	""" gets url, title, amounts of songs or the thumbnail of either a playlist or a single song"""		
	if isurl(url):
		print("is url")
		data = ytdl.ytdl.extract_info(url, download=False)
		if 'entries' in data:
			data = data['entries'][0] 
		return (clampTitle(data['title']), data['webpage_url'], data["thumbnail"], data["duration"])
	else:
		#faster but only works for search
		query_string = urlParse.urlencode({"search_query" : url})
		text = requestGet("https://www.youtube.com/results?" + query_string).text
		
		soup = bs4Soup(text, features="html.parser")

		f= open("error.txt","w+")
		f.write(text)
		f.close() 


		divs = soup.select(".yt-lockup-dismissable")
		for element in divs:
			if element.select(".yt-lockup-playlist-item"):
				#It's a playlist, we don't support playing it like this
				continue
			else:
				div = element


		img0 = div.select(".yt-lockup-thumbnail img")[0]
		a0 = div.select(".yt-lockup-title a")[0]
		span0 = div.select(".yt-lockup-title span")[0]

		title = a0['title']
		href =  "https://www.youtube.com" + a0['href']
		thumb = img0['src'] if not img0.has_attr('data-thumb') else img0['data-thumb']

		durationSplit  = span0.text.split(": ")[1].split(":") 
		durationSplit.reverse()
		duration = 0
		i = 0
		for part in durationSplit:
			if i == 0:
				duration += int(part.replace('.', '')) 
			else:
				duration += int(part) * (i * 60)
			i += 1
		return (clampTitle(title), href, thumb, duration)

async def get_song_data(url, loop=None):
	loop = loop or asyncio.get_event_loop()
	return await loop.run_in_executor(None, lambda: get_song_data_async(url))

def convert_seconds(seconds):
	"""converts seconds to a string with format "m:s" or "h:m:s" """
	minutes, seconds = divmod(seconds, 60)
	if minutes > 60:
		hours, minutes = divmod(minutes, 60)
		return '{:d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
	else:
		return '{}:{:02d}'.format(minutes, seconds)

def isPlaylist(url):
	if "watch?v=" in url:
		return False
	else:
		return "playlist?list=" in url

def create_progressbar(timePaused, timeStarted, duration, is_paused):
	if is_paused:
		progress_time = round(timePaused)
		description = ":pause_button: "
	else:
		progress_time = round(time.time() - timeStarted)
		description = ":arrow_forward: "
	
	trackPercentage = progress_time/duration
	trackBarParts = 11
	trackPosition = round(trackBarParts * trackPercentage)

	for i in range(trackBarParts + 1):
		if i != trackPosition:
			description += "▬"
		else:
			description += ":radio_button:"

	songProgress = convert_seconds(progress_time)
	songDuration = convert_seconds(duration)
	description += f" `{songProgress}/{songDuration}`"
	return description

async def joinVoice(ctx):
	"""joins the requested voice channel, returns true if it did join and false if it can't join"""
	if not ctx.voice_client:
		# Bot is not in a channel
		await ctx.message.author.voice.channel.connect()
		return True

	elif ctx.author.voice.channel == ctx.voice_client.channel:
		# Bot is in same channel
		return True
	else:
		# Bot is in another channel
		await ctx.send('I\'m already playing in the voice channel `{}`, join me!'.format(ctx.voice_client.channel.name))
		return False

async def bookList(channel, mPlayer, func, playList, itemsPerPage=5):
	''' Generates a list with pages that you can flip back and forth '''
	pageIndex = 1
	listIndex = 0
	queueLength = len(playList)
	pages = queueLength // itemsPerPage + (queueLength % itemsPerPage > 0)  #rounding up
	if pages == 0:
		pages = 1

	leftEmoji = "⬅️"
	rightEmoji = "➡️"

	description = func(mPlayer, playList, listIndex, itemsPerPage)
	originalEmbed = discord.Embed(title="", description=description)
	originalEmbed.set_footer(text=f"Page {pageIndex}/{pages}")
	message = await channel.send(embed=originalEmbed)
	
	if not pages > 1:
		return

	await message.add_reaction(leftEmoji)
	await message.add_reaction(rightEmoji)
	while True:
		try:
			reaction, user = await mPlayer.bot.wait_for('reaction_add', timeout=60.0)
		except asyncio.TimeoutError:
			await message.clear_reactions()
			break
		else:
			if user == mPlayer.bot.user:
				continue
			await message.remove_reaction(reaction, user)
			if str(reaction.emoji) == leftEmoji and pageIndex > 1:
				pageIndex -= 1
				listIndex -= itemsPerPage
				description = func(mPlayer, playList, listIndex, itemsPerPage)
				embed = discord.Embed(title="", description=description)
				embed.set_footer(text=f"Page {pageIndex}/{pages}")
				await message.edit(embed=embed)
			elif str(reaction.emoji) == rightEmoji and pageIndex < pages:
				pageIndex += 1
				listIndex += itemsPerPage
				description = func(mPlayer, playList, listIndex, itemsPerPage)
				embed = discord.Embed(title="", description=description)
				embed.set_footer(text=f"Page {pageIndex}/{pages}")
				await message.edit(embed=embed)


async def helpFunction(ctx, helpCommand=None):
	''' Generates a help message, if a helpCommand is given then it generates a help message specific for that command '''
	funCommandList = ["8ball", "coinflip", "kiss", "hug", "poke",
					"feed", "cuddle", "slap", "pat", "tickle", 
					"smug", "lick", "highfive", "uwu", "fact", 
					"oof", "rekt", "dadjoke"]

	commandList = 	["join", "play", "playnext",  
						"volume",  "pause", "resume", "remove", "skip",
						"queue", "nowplaying", "leave"]

	djcommandList = ["playlist",
					"playnow",
					"shuffle",
					"clear",
					"setdj",
					"prefix",
					"musictc",
					"musicvc",
					'download_default_playlist']

	if not helpCommand:
		#no helpCommand which means show the whole help message
		prefix = await determine_prefix(ctx.bot, ctx.message)
		description = ""
		description += f"Current prefix is: `{prefix}`\n\n"
		description += f"__**Fun commands**__ \n"
		for command in funCommandList:
			description += command + "\n"
		description += f"\n__**Music commands**__ \n"
		for command in commandList:
			description += command + "\n"
		description += "\n__**DJ commands**__ \n"
		for command in djcommandList:
			description += command + "\n"
		description += f"\nUse `{prefix}help (command)` for more info on that command"
		embed = discord.Embed(title="Help", description=description)
		await ctx.send(embed=embed)	

	else:
		#helpCommand might be a list of aliases, check which one is the correct command and assign that
		if isinstance(helpCommand, list):
			for alias in helpCommand:
				if alias in funCommandList + commandList + djcommandList:
					helpCommand = alias
					break

		prefix = await determine_prefix(ctx.bot, ctx.message)
		commandSyntax = "`Syntax: " + prefix
		description = ""

		if helpCommand not in funCommandList + commandList + djcommandList:
			return await ctx.send(f"Either that command doesn't exist or you're using an alias, try the full command name found in {prefix}help")

		if helpCommand == "8ball":
			commandSyntax += "8ball question"
			description += "Asks the 8ball a question and it will reply with the truth"

		elif helpCommand == "coinflip":
			commandSyntax += "coinflip"
			description += "Flips a coin, duuh"

		elif helpCommand == "kiss":
			commandSyntax += "kiss @user"
			description += "Kisses the tagged user"

		elif helpCommand == "hug":
			commandSyntax += "hug @user"
			description += "Hugs the tagged user"

		elif helpCommand == "poke":
			commandSyntax += "poke @user"
			description += "Pokes the tagged user"

		elif helpCommand == "feed":
			commandSyntax += "feed @user"
			description += "Feeds the tagged user some food"

		elif helpCommand == "cuddle":
			commandSyntax += "cuddle @user"
			description += "Cuddles the tagged user"

		elif helpCommand == "slap":
			commandSyntax += "slap @user"
			description += "Slaps the tagged user"

		elif helpCommand == "pat":
			commandSyntax += "pat @user"
			description += "Pats the tagged user"

		elif helpCommand == "tickle":
			commandSyntax += "tickle @user"
			description += "Tickles the tagged user"

		elif helpCommand == "smug":
			commandSyntax += "smug"
			description += "Act smug"

		elif helpCommand == "lick":
			commandSyntax += "lick @user"
			description += "Creepily licks the other user"

		elif helpCommand == "highfive":
			commandSyntax += "highfive (@user)"
			description += "High fives the tagged user. If no user is included then it will wait for someone else to high five back"

		elif helpCommand == "uwu":
			commandSyntax += "(uwu | owo) (message)"
			description += "uwuifies the previous message, or if a message is provided in the command then it will uwuify that instead"

		elif helpCommand == "fact":
			commandSyntax += "fact"
			description += "Sends a random fact message"

		elif helpCommand == "oof":
			commandSyntax += "oof"
			description += "Reacts with 🅾🇴🇫 on the previous message"

		elif helpCommand == "rekt":
			commandSyntax += "rekt"
			description += "Sends a rekt message"

		elif helpCommand == "dadjoke":
			commandSyntax += "dadjoke"
			description += "Sends a random dadjoke"

		elif helpCommand == "join":
			commandSyntax += "(join | j)"
			description += "Joins the voice channel you are currently in, if it's allowed"
		
		elif helpCommand == "play":
			commandSyntax += "(play | p) song"
			description += "Joins your voice channel and plays a song \n"
			description += "Note, song can also be a youtube url for a video"
		
		elif helpCommand == "playnext":
			commandSyntax += "(playnext | pnext | pn) song"
			description += "Places the song first in the queue so that it plays after the currently playing song"
		
		elif helpCommand == "playnow":
			commandSyntax += "(playnow | pnow) song"
			description += "Skips the currently playing song to play the requested song"
		
		elif helpCommand == "playlist":
			commandSyntax += "(playlist | pl) (clear | add song | remove song)"
			description += "Adds or removes songs from the default playlist (which plays when there's nothing else queued)\n\n"
			description += "Note that a song cand be either a youtube url, a song name, or a link to a youtube playlist\n\n"
			description += f"**Example:** `{prefix}playlist clear` completely clears the default playlist\n"
			description += f"**Example:** `{prefix}playlist add darude sandstorm` adds \"Darude Sandstorm\" to the default playlist\n"
			description += f"**Example:** `{prefix}playlist remove darude sandstorm`, you guessed it, removes \"Darude Sandstorm\" from the default playlist"
		
		elif helpCommand == "volume":
			commandSyntax += "(volume | vol | v) (volume)"
			description += "Sets the volume for the bot. Run the command without an parameter and it will tell you the current volume"
		
		elif helpCommand == "shuffle":
			commandSyntax += "shuffle"
			description += "Shuffles/randomizes the play queue"
		
		elif helpCommand == "pause":
			commandSyntax += "pause"
			description += "Pauses the player"
		
		elif helpCommand == "resume":
			commandSyntax += "(resume | continue)"
			description += "Resumes the player"
		
		elif helpCommand == "skip":
			commandSyntax += "(skip | s)"
			description += "Skips the current song"
		
		elif helpCommand == "remove":
			commandSyntax += "(remove | r) index"
			description += f"Removes the song at the requested index. Indexes can be found using {prefix}queue"
		
		elif helpCommand == "clear":
			commandSyntax += "clear"
			description += "Clears everything in the play queue"
	
		elif helpCommand == "queue":
			commandSyntax += "(queue | q)"
			description += "Shows a list of the queued songs"
		
		elif helpCommand == "nowplaying":
			commandSyntax += "(nowplaying | np | current) (sticky | controls | auto)"
			description += "Shows the currently playing song and its progress\n\n"
			description += "Running the command with one of the parameters (sticky, controls or auto) will toggle that setting (this require the DJ permission)\n\n"
			description += f"**Example:** `{prefix}np sticky` toggles the sticky function so that the now playing post will update to stay at the bottom or not\n"
			description += f"**Example:** `{prefix}np controls` toggles the reaction controls on the now playing post \n"
			description += f"**Example:** `{prefix}np auto` toggles the now playing post autmatically appearing when you summon the bot"
		
		elif helpCommand == "setdj":
			commandSyntax += "setdj (roleID | none)"
			description += "Assign DJ permissions to a role\n\n" 
			description += "You can get the roleID by enabling Developer Mode in discord settings > appearance, then rightclick on a role and copy its ID\n"
			description += "If there's no role assigned only admins can use the DJ functions\n\n"
			description += f"**Example:** `{prefix}setdj` displays the current role that has DJ permissions\n"
			description += f"**Example:** `{prefix}setdj 653341521223090183` sets the role with ID \"653341521223090183\" as DJ\n"
			description += f"**Example:** `{prefix}setdj none\" removes the DJ permissions from whatever role it was set to before."

		elif helpCommand == "leave":
			commandSyntax += "leave"
			description += "Stops the player and leaves the voice channel"
		
		elif helpCommand == "prefix":
			commandSyntax += "(prefix | annaprefix) new_prefix"
			description += "Sets a new prefix\n\n"
			description += f"Use `{prefix}annaprefix` if another bot is using the same prefix as me\n"
			description += f"Encapsulate the new prefix with quote marks if you want the prefix to end with a space like this `\"! \"` \n"

		elif helpCommand == "musictc":
			commandSyntax += "musictc (clear | add (#channel | current) | remove (#channel | current))"
			description += "Limits the bot to only read music commands from specific textchannels\n\n"
			description += "If there's no channels added then the bot will listen to all channels\n"
			description += "Run without parameters to show the current channels\n\n"
			description += f"**Example:** `{prefix}musictc add current` adds the textchannel you wrote in to the channels the bot will read from\n"
			description += f"**Example:** `{prefix}musictc remove #channel` removes the channel you tagged\n"
			description += f"**Example:** `{prefix}musictc clear` will make the bot read from all channels again"
		
		elif helpCommand == "musicvc":
			commandSyntax += "musicvc (clear | add (ID | current) | remove (ID | current))"
			description += "Limits the bot to only join and play music in specific voice channels\n\n"
			description += "If there's no channels added then the bot can join all channels\n"
			description += "Run without parameters to show the current channels\n"
			description += "To get the ID of a voice channel, enable developer mode in discord settings and then rightclick on a voice channel and copy its ID\n\n"
			description += f"**Example:** `{prefix}musicvc add current` adds the voicechannel you're currently in \n"
			description += f"**Example:** `{prefix}musicvc remove 653341521223090183` removes the channel with the ID \"653341521223090183\"\n"
			description += f"**Example:** `{prefix}musicvc clear` will make the bot able to join all channels again"
		elif helpCommand == "download_default_playlist":
			commandSyntax += "download_default_playlist"
			description += "Downloads all songs that are in the default playlist and prepares them so that next time you play it will be instant"
		commandSyntax += "`\n\n"
		embed = discord.Embed(description=commandSyntax + description)
		embed.set_author(name=ctx.bot.user.name + " Help Menu" , icon_url=ctx.bot.user.avatar_url)
		embed.set_footer(text="Syntax: (x | y): use either x or y, (x): x is optional")
		await ctx.send(embed=embed)	
