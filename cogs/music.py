import discord
from discord.ext import commands
import asyncio
import sys

sys.path.append('./cogs')
import utils


async def is_accepted_voice_channel(ctx):
	if not str(ctx.guild.id) in serverSettings:
		return True
	if not serverSettings[str(ctx.guild.id)]['acceptedVoiceChannels']:
		return True
	else:
		if ctx.author.voice.channel.id in serverSettings[str(ctx.guild.id)]['acceptedVoiceChannels']:
			return True
		else:
			await ctx.send(f"I'm not allowed to join your voice channel")
			return False
async def is_accepted_text_channel(ctx):
	if not str(ctx.guild.id) in serverSettings:
		return True
	if not serverSettings[str(ctx.guild.id)]['acceptedTextChannels']:
		return True
	else:
		return ctx.channel.id in serverSettings[str(ctx.guild.id)]['acceptedTextChannels']
async def is_bot_connected(ctx):
	''' Checks if the bot is connected to a voice channel ''' 
	if ctx.voice_client is None:
		await ctx.send("I'm not connected to a voice channel.")
		return False
	else:
		return True
async def is_user_connected_to_bot_channel(ctx):
	''' Checks if a user is connecter to the same voice channel as the bot is '''
	if ctx.author.voice is not None:
		if ctx.author.voice.channel == ctx.voice_client.channel:
			return True
	await ctx.send(f"You have to be in `🔊 {ctx.voice_client.channel.name}` to do that")
	return False	
async def is_user_connected(ctx):
	''' Checks if the user is connected to a voice chanel '''
	if ctx.author.voice is not None:
		return True
	await ctx.send('You have to join a voice channel to do that')
	return False
async def is_dj(ctx):
	'''Checks if the user has the dj_role role'''
	server = str(ctx.guild.id)
	if ctx.author.guild_permissions.administrator:
		return True
	if 'dj_role' in serverSettings[server]:
		djRole = get(ctx.guild.roles, id=serverSettings[server]['dj_role'])
		if djRole in ctx.author.roles:
			return True
		else:
			await ctx.send("You don't have the required permissions to do that")
			return False
	await ctx.send("You don't have the required permissions to do that")
	return False	
async def join_voice_and_play(ctx):
	"""returns True if we can play a song afterwards"""
	if ctx.voice_client == None:
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


class Music(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"'{self.__class__.__name__}' loaded")


	@commands.command(aliases=['join', 'j'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	async def join_(self, ctx):
		defaultPlaylist = await utils.getDefaultPlaylist(ctx.guild.id)
		if len(defaultPlaylist) == 0:
			return await ctx.send("There's no song to be played, either use the play command with a song or add a song to the default playlist")

		if(await join_voice_and_play(ctx)):
			mPlayer = get_player(ctx.guild)
			mPlayer.downloader.set()
			
			await asyncio.sleep(1)
			val = getBoolSetting(str(ctx.guild.id), 'nowPlayingAuto')
			if val:
				await now_playing(ctx.guild, ctx.channel, preparing=True, forceSticky=True)

	@commands.command(aliases=['play', 'p'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	async def play_(self, ctx,  *args):
		if len(args) == 0:
			defaultPlaylist = await utils.getDefaultPlaylist(ctx.guild.id)
			if len(defaultPlaylist) == 0:
				return await ctx.send("There's no song to be played, either use the command again with a song or add a song to the default playlist")

		if(await join_voice_and_play(ctx)):
			if len(args) > 0:
				url = " ".join(args)
				await add_song(ctx, url, stream=False)
			else:
				mPlayer = get_player(ctx.guild)
				mPlayer.downloader.set()
				
				await asyncio.sleep(1)
				val = getBoolSetting(str(ctx.guild.id), 'nowPlayingAuto')
				if val:
					await now_playing(ctx.guild, ctx.channel, preparing=True, forceSticky=True)

	@commands.command(aliases=['playnext', 'pnext', 'pn'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	async def playnext_(self, ctx, *, url):
		if(await join_voice_and_play(ctx)):
			await add_song(ctx, url, play_next=True, stream=False)

	@commands.command(aliases=['playnow', 'pnow'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	@commands.check(is_dj)
	async def playnow_(self, ctx, *, url):
		if(await join_voice_and_play(ctx)):
			await add_song(ctx, url, play_now=True, stream=False)

	@commands.command(aliases=['stream', 'playstream'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	async def stream_(self, ctx, *, url):
		if(await join_voice_and_play(ctx)):
			await add_song(ctx, url, stream=True)


	@commands.group(aliases=['playlist', 'pl'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_dj)
	async def playlist_(self, ctx):
		if ctx.invoked_subcommand is None:
			mPlayer = get_player(ctx.guild)
			defaultPlaylist = await utils.getDefaultPlaylist(ctx.guild.id)
			await bookList(ctx.channel, mPlayer, create_playlist_string, defaultPlaylist, itemsPerPage=10)
	
	@playlist_.command(aliases=['clear'])
	async def clear_playlist(self, ctx):
		server = str(ctx.guild.id)
		mPlayer = get_player(ctx.guild)
		await update_playlist_json(server, [])
		mPlayer.prepareQueue.default = []
		await ctx.send(f"Default playlist cleared.")

	@playlist_.command(aliases=['add'])
	async def add_to_playlist(self, ctx, *args):
		server = str(ctx.guild.id)
		mPlayer = get_player(ctx.guild)
		searchOrUrl = " ".join(args)
		if isPlaylist(searchOrUrl): #It's a playlist
			title, url, songs = await get_playlist_info(searchOrUrl)

			data = await utils.getDefaultPlaylist(server)
			if url in data:
				return await ctx.send(f"That playlist is already added")

			await update_playlist_json(server, url, add = True)
			mPlayer.prepareQueue.default = mPlayer.prepareQueue.default + songs
			shuffle(mPlayer.prepareQueue.default)
			
			embed = discord.Embed(title="Playlist: " + title, url=url, description=f"Added playlist with {len(songs)} songs")
			await ctx.send(embed=embed)
		else: #It's either a bunch of words or an url
			try:
				title, url, thumbnail, _ = await get_song_data(searchOrUrl)
			except:
				await ctx.send(f"Wrong arguments, check `{await determine_prefix(bot, ctx.message)}help playlist`")
			
			data = await utils.getDefaultPlaylist(server)
			if url in data:
				return await ctx.send(f"That song already exists in the playlist")
		
			await update_playlist_json(server, url, add = True)
			mPlayer.prepareQueue.default.append(url)
			shuffle(mPlayer.prepareQueue.default)

			embed = discord.Embed(title=title, url=url, description=f"have been added to the playlist")
			embed.set_thumbnail(url=thumbnail)
			await ctx.send(embed=embed)

	@playlist_.command(aliases=['remove'])
	async def remove_from_playlist(self, ctx, *args):
		server = str(ctx.guild.id)
		mPlayer = get_player(ctx.guild)
		searchOrUrl = " ".join(args)
		if isPlaylist(searchOrUrl):
			title, url, songs = await get_playlist_info(searchOrUrl)

			data = await utils.getDefaultPlaylist(server)
			if not url in data:
				return await ctx.send(f"That youtube playlist doesn't exist in the playlist")

			await update_playlist_json(server, url, add = False)
			for song in songs:
				if song in mPlayer.prepareQueue.default:
					mPlayer.prepareQueue.default.remove(song)

			embed = discord.Embed(title="Playlist: " + title, url=url, description=f"Removed playlist with {len(songs)} songs")
			await ctx.send(embed=embed)
		else:
			try:
				title, url, thumbnail, _ = await get_song_data(searchOrUrl)
			except:
				await ctx.send(f"Wrong arguments, check `{await determine_prefix(bot, ctx.message)}help playlist`")

			data = await utils.getDefaultPlaylist(server)
			if not url in data:
				return await ctx.send(f"That song doesn't exist in the playlist")
				
			await update_playlist_json(server, url, add = False)
			mPlayer.prepareQueue.default.remove(url)

			embed = discord.Embed(title=title, url=url, description=f"have been removed from the playlist")
			embed.set_thumbnail(url=thumbnail)
			await ctx.send(embed=embed)


	@commands.command(aliases=['volume', 'vol', 'v'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def volume_(self, ctx, *args):
		mPlayer = get_player(ctx.guild)

		if len(args) == 1:
			if not RepresentsInt(args[0]):
				await ( await ctx.send(f"Wrong arguments, please follow the documentation or use {await determine_prefix(bot, ctx.message)}help.")).delete(delay=15)
				return await ctx.message.delete(delay=15)

			volume = int(args[0])
			if  volume > 150:
				await ctx.send("You can't set the volume over 150%")
			elif volume <= 0:
				await ctx.send("The volume has to be over 0%")
			else:
				oldVolume = mPlayer.volume
				newVolume = volume / 100
				await setVolume(ctx.guild, ctx.voice_client, newVolume)
				await ctx.send(f"Changed volume from `{int(oldVolume*100)}%` to `{volume}%`")
		else:
			await ctx.send(f"Volume: `{int(mPlayer.volume*100)}`%")

	@commands.command(aliases=['shuffle', 'random', 'randomize'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	@commands.check(is_dj)
	async def shuffle_(self, ctx):
		mPlayer = get_player(ctx.guild)
		mPlayer.processedQueue.default = []

		shuffle(mPlayer.prepareQueue.default)

		for song in mPlayer.processedQueue.getQueue():
			if not song.playnext:
				mPlayer.processedQueue.remove(song)
				mPlayer.processedQueue.play.append(song)
			
		shuffle(mPlayer.processedQueue.play)
		mPlayer.downloader.set()

		await ctx.message.add_reaction("👌")

	@commands.command(aliases=['pause'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def pause_(self, ctx):
		mPlayer = get_player(ctx.guild)
		if ctx.voice_client.is_paused():
			await ( await ctx.send("I'm already paused")).delete(delay=10)
			return await ctx.message.delete(delay=10)

		ctx.voice_client.pause()
		mPlayer.timePaused = time.time() - mPlayer.timeStarted
		mPlayer.update_np.set()
		await ctx.message.add_reaction("👌")

	@commands.command(aliases=['resume', 'continue'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def resume_(self, ctx):
		mPlayer = get_player(ctx.guild)
		if not ctx.voice_client.is_paused():
			await ( await ctx.send("I'm already playing")).delete(delay=10)
			return await ctx.message.delete(delay=10)

		ctx.voice_client.resume()
		mPlayer.timeStarted = time.time() - mPlayer.timePaused
		mPlayer.update_np.set()
		await ctx.message.add_reaction("👌")

	@commands.command(aliases=['skip', 's'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def skip_(self, ctx):
		vc = ctx.voice_client
		if not vc.is_playing() and not vc.is_paused():
			await ( await ctx.send("There's no song playing")).delete(delay=10)
			return await ctx.message.delete(delay=10)

		await ctx.message.add_reaction("👌")
		vc.source.volume = 0
		vc.stop()

	@commands.command(aliases=['remove', 'r'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def remove_(self, ctx, indexToRemove):
		mPlayer = get_player(ctx.guild)
		
		try: 
			indexToRemove = int(indexToRemove)
		except:
			return await ctx.send("The argument has to be an integer above 0.") 

		if indexToRemove < 1:
			return await ctx.send("The argument has to be an integer above 0.")

		queueList = getQueueList(mPlayer, procDefault = True)
		if indexToRemove > len(queueList):
			return await ctx.send("Index is larger than the amount of queued songs")
			
		elementToRemove = queueList[indexToRemove-1]
	
		if elementToRemove in mPlayer.processedQueue.playnow:
			mPlayer.processedQueue.playnow.remove(elementToRemove)
		elif elementToRemove in mPlayer.prepareQueue.playnow:
			mPlayer.prepareQueue.playnow.remove(elementToRemove)
		elif elementToRemove in mPlayer.processedQueue.playnext:
			mPlayer.processedQueue.playnext.remove(elementToRemove)
		elif elementToRemove in mPlayer.prepareQueue.playnext:
			mPlayer.prepareQueue.playnext.remove(elementToRemove)
		elif elementToRemove in mPlayer.processedQueue.play:
			mPlayer.processedQueue.play.remove(elementToRemove)
		elif elementToRemove in mPlayer.prepareQueue.play:
			mPlayer.prepareQueue.play.remove(elementToRemove)
		elif elementToRemove in mPlayer.processedQueue.default:
			mPlayer.processedQueue.default.remove(elementToRemove)

		mPlayer.downloader.set()

		return await ctx.send(f"Removed #{indexToRemove}: `{elementToRemove.title}` from the queue")
		
	@commands.command(aliases=['clear'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	@commands.check(is_dj)
	async def clear_(self, ctx):
		mPlayer = get_player(ctx.guild)

		mPlayer.prepareQueue.playnow = []
		mPlayer.prepareQueue.playnext = []
		mPlayer.prepareQueue.play = []
		mPlayer.processedQueue = SongQueue()

		await ctx.send("Cleared the queue")

	@commands.command(aliases=['queue', 'q'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	async def queue_(self, ctx, *args):
		mPlayer = get_player(ctx.guild)
		queueList = getQueueList(mPlayer, procDefault = False)

		if not queueList and not mPlayer.processedQueue.default:
			description = ""
			description += "**There's nothing in the queue** \n"
			if mPlayer.current:
				description += f"Currently playing: **[{mPlayer.current.title}]({mPlayer.current.url})**"
			embed = discord.Embed(title="", description=description)
			return await ctx.send(embed=embed)

		await bookList(ctx.channel, mPlayer, create_queue_string, queueList)


	@bot.group(aliases=['nowplaying', 'np', 'current'])
	@commands.check(is_accepted_text_channel)
	async def nowplaying_(self, ctx):
		if ctx.invoked_subcommand is None:
			if await is_bot_connected(ctx):
				await now_playing(ctx.guild, ctx.channel)

	@nowplaying_.command()
	@commands.check(is_dj)
	async def sticky(self, ctx):
		#toggle sticking now playing to the bottom
		server = str(ctx.guild.id)
		setting = 'nowPlayingSticky'
		current = getBoolSetting(server, setting)
		await update_settings_json(server, setting, (not current))
		return await ctx.send(f"Toggled Now Playing Sticky to `{not current}`")

	@nowplaying_.command()
	@commands.check(is_dj)
	async def controls(self, ctx):
		#toggle reaction controls
		server = str(ctx.guild.id)
		setting = 'nowPlayingControls'
		current = getBoolSetting(server, setting)
		await update_settings_json(server, setting, (not current))
		return await ctx.send(f"Toggled Now Playing Controls to `{not current}`")

	@nowplaying_.command()
	@commands.check(is_dj)
	async def auto(self, ctx):
		#toggle automatically send a nowplaying message when starting the player
		server = str(ctx.guild.id)
		setting = 'nowPlayingAuto'
		current = getBoolSetting(server, setting)
		await update_settings_json(server, setting, (not current))
		return await ctx.send(f"Toggled Now Playing automatically send to `{not current}`")


	@commands.command(aliases=['setdj'])
	@commands.has_permissions(manage_roles=True)
	async def setdj_(self, ctx, *args):
		if len(args) == 0:
			server = str(ctx.guild.id)
			if not server in serverSettings or 'dj_role' not in serverSettings[server]:
				return await ctx.send(f"No role have been assigned as DJ")

			role = get(ctx.guild.roles, id=serverSettings[server]['dj_role'])

			return await ctx.send(f"Current DJ role: '{role.name}'")
			
		if len(args) > 1:
			return await ctx.send(f"Too many arguments, enter only one role ID")
		
		try:
			role = get(ctx.guild.roles, id=int(args[0]))
		except ValueError:
			if args[0].lower() == "none":
				await update_settings_json(str(ctx.guild.id), 'dj_role', None)
				return await ctx.send(f"Cleared DJ role, now only admins can use the DJ functions")
			else:
				return await ctx.send(f"Wrong role type, please enter only the ID of a role (google how to get discord roles ID)")
		if not role:
			return await ctx.send(f"Can't find any roles with that ID, are you sure you copy pasted it right?")

		await update_settings_json(str(ctx.guild.id), 'dj_role', role.id)
		await ctx.send(f"Gave '{role.name}' the DJ permission")

	@commands.command(aliases=['leave', 'disconnect', 'stop'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	@commands.check(is_dj)
	async def leave_(self, ctx):
		mPlayer = get_player(ctx.guild)
		mPlayer.stop_player = True
		mPlayer._guild.voice_client.stop()


	@bot.group(aliases=['musictc'])
	@commands.check(is_dj)
	async def musictc_(self, ctx):
		server = str(ctx.guild.id)
		if not server in serverSettings:
			serverSettings[server] = {}
			serverSettings[server]['acceptedTextChannels'] = []
		if ctx.invoked_subcommand is None:
			accTC = serverSettings[server]['acceptedTextChannels']
			if len(accTC) == 0:
				return await ctx.send(f"I'm currently reading all text channels for commands, you can limit me to specific channels using {await determine_prefix(bot, ctx.message)}limittc add #channel_name")
			else:
				channelText = ""
				for index, channelID in enumerate(accTC):
					channelText += ctx.guild.get_channel(channelID).mention
					if index != len(accTC) - 1:
						channelText += ", "
				await ctx.send(f"These are the channels I'm currently watching: {channelText}")

	@musictc_.command(aliases=['clear'])
	async def clear_tc(self, ctx):
		server = str(ctx.guild.id)
		await update_settings_json(server, 'acceptedTextChannels', None, clear_list=True)
		await ctx.send(f"I'm now reading commands from all text channels")

	@musictc_.command(aliases=['add'])
	async def add_tc(self, ctx, channel: Current_or_id_channel(False)):
		server = str(ctx.guild.id)
		accTC = serverSettings[server]['acceptedTextChannels']
		if channel.id in accTC:
			await ctx.send(f"The channel {channel.mention} is already one of the allowed text channels")
		else:
			await update_settings_json(server, 'acceptedTextChannels', channel.id, add_to_list=True)
			await ctx.send(f"I've added {channel.mention} to the allowed text channels")

	@musictc_.command(aliases=['remove'])
	async def remove_tc(self, ctx, channel: Current_or_id_channel(False)):
		server = str(ctx.guild.id)
		if not server in serverSettings:
			serverSettings[server] = {}
			serverSettings[server]['acceptedTextChannels'] = []

		accTC = serverSettings[server]['acceptedTextChannels']

		if len(accTC) == 0:
			return await ctx.send(f"The allowed text channels list is currently empty, I'm listening to all text channels")
		if channel.id in accTC:
			await update_settings_json(server, 'acceptedTextChannels', channel.id, add_to_list=False)
			await ctx.send(f"I've removed {channel.mention} from the allowed text channels")
		else:
			await ctx.send(f"That channel is not an allowed text channel")


	@bot.group(aliases=['musicvc'])
	@commands.check(is_dj)
	async def musicvc_(self, ctx):
		server = str(ctx.guild.id)
		if not server in serverSettings:
			serverSettings[server] = {}
			serverSettings[server]['acceptedVoiceChannels'] = []

		if ctx.invoked_subcommand is None:
			accVC = serverSettings[server]['acceptedVoiceChannels']
			if len(accVC) == 0:
				return await ctx.send(f"I can currently join any voice channel, you can limit me to specific channels using {await determine_prefix(bot, ctx.message)}limitvc add channelID")
			else:
				channelText = ""
				print(accVC)
				for index, channelID in enumerate(accVC):
					channelText += ctx.guild.get_channel(channelID).mention
					if index != len(accVC) - 1:
						channelText += ", "
				await ctx.send(f"These are the channels I can currently join: {channelText}")

	@musicvc_.command(aliases=['clear'])
	async def clear_vc(self, ctx):
		server = str(ctx.guild.id)
		await update_settings_json(server, 'acceptedVoiceChannels', [], clear_list=True)
		await ctx.send(f"I can now join any voice channel")

	@musicvc_.command(aliases=['add'])
	async def add_vc(self, ctx, channel: Current_or_id_channel(True)):
		server = str(ctx.guild.id)
		accVC = serverSettings[server]['acceptedVoiceChannels']
		if channel.id in accVC:
			await ctx.send(f"The channel {channel.mention} is already one of the allowed voice channels")
		else:
			await update_settings_json(server, 'acceptedVoiceChannels', channel.id, add_to_list=True)
			await ctx.send(f"I've added {channel.mention} to the allowed voice channels")

	@musicvc_.command(aliases=['remove'])
	async def remove_vc(self, ctx, channel: Current_or_id_channel(True)):
		server = str(ctx.guild.id)
		accVC = serverSettings[server]['acceptedVoiceChannels']
		if len(accVC) == 0:
			return await ctx.send(f"The allowed voice channels list is currently empty, I can already join all voice channels")
		if channel.id in accVC:
			await update_settings_json(server, 'acceptedVoiceChannels', channel.id, add_to_list=False)
			await ctx.send(f"I've removed {channel.mention} from the allowed voice channels")
		else:
			await ctx.send(f"That channel is not an allowed voice channel")


	@commands.command(aliases=['download_default_playlist'])
	@commands.check(is_dj)
	async def download_default_playlist_(self, ctx):
		mPlayer = get_player(ctx.guild)

		server = str(mPlayer._guild.id)
		data = await utils.getDefaultPlaylist(server)
		if not data:
			return await ctx.send(content="There's no songs in the default playlist")

		print("downloading default playlist")
		playlistlist = []
		for link in data:
			if "playlist?list=" in link:
				_, _, links = await get_playlist_info(link)
				playlistlist = playlistlist + links
			else:
				playlistlist.append(link)

		await ctx.send(content=f"Downloading {len(playlistlist)} songs from default playlist, this might take a while...")
					
		print("downloading default")
		msg = await ctx.send(content=f"`0/{len(playlistlist)} songs downloaded`")
		for i, url in enumerate(playlistlist, 1):
			skip = False
			for song in mPlayer.processedQueue:
				if song.url == url:
					#Song is already in queue, no need to download it again so just duplicate the object
					skip = True
			if skip:
				continue

			print(f"{i}/{len(playlistlist)} downloading: " + url)
			await YTDLSource.from_url(mPlayer, url, loop=bot.loop, stream=False)
			if i%2:
				await msg.edit(content = f"`{i}/{len(playlistlist)} songs downloaded`")

		await msg.edit(content = f"`{len(playlistlist)}/{len(playlistlist)} songs downloaded`")
		await ctx.send("Finished downloading and preparing the default playlist")
		



	

def setup(bot):
	bot.add_cog(Music(bot))