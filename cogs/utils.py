import discord
import json
import os


config = {}
serverSettings = {}
server_settings_location = "settings/serverSettings.json"
playlist_location = "settings/serverPlaylists.json"
defaultPrefix = "$"

async def determine_prefix(bot, message):
	''' Returns the prefix for the server that the message was sent in '''
	global config
	#Only allow custom prefixs in guild
	if not config:
		config = getConfig()
	guild = message.guild
	if guild:
		guildSettings = getServerSetting(str(guild.id), "prefix")
		if guildSettings:
			return guildSettings.get("prefix", config['defaultPrefix'])
		else:
			return config['defaultPrefix']
	else:
		return config['defaultPrefix']

async def set_message_reactions(msg, new_reactions):
	await msg.clear_reactions()

	for reaction in new_reactions:
		await msg.add_reaction(reaction)

def getConfig():
	print("getting config")
	''' Returns the bot config if it exists, otherwise generate it '''
	global config
	if config:
		return config

	configFile = 'settings/config.json'
	if not os.path.exists(configFile):
		os.makedirs(os.path.dirname(configFile), exist_ok=True)
		with open(configFile, 'w+') as f:
			data = ('{ \n' +
						'\t"token": "PUT_DISCORD_TOKEN_HERE", \n' +
						'\t"tenor_key": "PUT_TENOR_TOKEN_HERE", \n' +
						f'\t"defaultPrefix": {defaultPrefix}\n' +
					'}')
			f.write(data)
			print("Generated config file, open it and insert the bot token")
			quit()
	else:
		with open(configFile) as json_file:
			data = json.load(json_file)
	return data

def initializeServerSettings():
	print("Initializing the server settings file")
	os.makedirs(os.path.dirname(server_settings_location), exist_ok=True)
	with open(server_settings_location, 'w+') as f:
		data = {}
		f.write(data)

def getServerSetting(server, field):
	''' Returns the server settings if it exists, otherwise generate it '''
	global serverSettings
	if type(server) == int:
		server = str(server)

	if serverSettings:
		if server in serverSettings:
			return serverSettings[server][field]

	if not os.path.exists(server_settings_location):
		initializeServerSettings()

	with open(server_settings_location, 'r+') as json_file:
		data = json.load(json_file)
		if server not in data:
			data[server] = {"volume": 0.5, "acceptedVoiceChannels": [], "acceptedTextChannels": [], 'prefix': defaultPrefix}
			json_file.seek(0)
			json.dump(data, json_file)
			json_file.truncate()
			serverSettings = data

	return serverSettings[server][field]

def updateServerSettings(server, field, new_value):
	''' Updates the server settings if it exists, otherwise generate it '''
	global serverSettings
	if type(server) == int:
		server = str(server)

	if not os.path.exists(server_settings_location):
		initializeServerSettings()
		
	with open(server_settings_location, 'r+') as json_file:
		data = json.load(json_file)
		json_file.seek(0)

		if server not in data:
			data[server] = {}

		data[server][field] = new_value
		json.dump(data, json_file)
		json_file.truncate()
		serverSettings = data

def getServerPlaylist(server: str):
	''' Returns the server playlist if it exists, otherwise generate it '''

	if not os.path.exists(playlist_location):
		print("Initializing playlist file")
		os.makedirs(os.path.dirname(playlist_location), exist_ok=True)
		with open(playlist_location, 'w+') as f:
			data = '{}'
			f.write(data)
	else:
		with open(playlist_location, 'r') as json_file:
			data = json.load(json_file)
	return data[server]

def get_playlist_json(json_file, server):
	try:
		data = json.load(json_file)
		if not server in data:
			data[server] = []
	except json.JSONDecodeError:
		data = {}
		data[server] = []
	json_file.seek(0)
	return data
async def getDefaultPlaylist(guildID):
	data = {}
	server = str(guildID)
	with open(playlist_location, 'r', encoding='utf-8') as json_file:
		data = get_playlist_json(json_file, server)
	return data[server]




async def helpFunction(ctx, helpCommand=None):
	''' Generates a help message, if a helpCommand is given then it generates a help message specific for that command '''
	funCommandList = ["8ball", "kiss", "hug", "poke",
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







