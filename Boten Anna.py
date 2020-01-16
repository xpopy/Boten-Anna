import discord
from discord.ext import commands
from discord.utils import get
from dataclasses import dataclass, field
import os
from subprocess import Popen as subprocPopen, PIPE as subprocPIPE, STDOUT as subprocSTDOUT
from requests import get as requestGet
from random import randrange, choice as randElement
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#pipenv shell
#pipenv install (package)
#pipenv lock

#TODO: split up into modules (cogs?)



#TODO: default playlist is empty string is weird
#TODO: maybe place player and downloader in a try catch loop so that it doesn't crash when an issue happens
#TODO: join is buggy if there's no song in playlist
#TODO: Check if ffmpeg is installed in initialization

#TODO: Write a short comment on what functions do
#TODO: rewrite help as a dictionary with categories, commands, short description and a long description
	#TODO: https://i.imgur.com/L2Z3IYo.png
	#TODO: Move it to initialize so it doesn't have to create it every time we want to check help
#TODO: re-enable playing playlists
	#TODO: best would probably be to webscrape the playlist to get all info
	#TODO: --playlist-random  may help
	#TODO: maybe make it like default playlist, a queue of urls
		#TODO: shuffle?
#TODO: is typing is bugged
#TODO: bot run exception catches all exceptions when it's only meant to capture the "wrong token" one
#TODO: check if youtube playlist has a "last edited" field so i can save the playlist and not update it all the time
	#TODO: maybe rework saving playlists so it saves names (name of playlist), time etc?
	#TODO: set this once done    prepareDefault = True   in   nextSong = getQueueList(mPlayer, procDefault = True, prepareDefault = False)[0]

#TODO: add undo: https://github.com/pckv/pcbot/blob/master/plugins/music.py
#TODO: play youtube radio
#TODO: play streams
#TODO: soundcloud (apparently youtubedl already supports it, look it up
#TODO: make use of types in args like func(ctx, arg1: int)

"""TODO: seek in a video?""" # can't, no api implemented for it

def datetime_from_utc_to_local(utc_datetime):
	now_timestamp = time.time()
	offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
	return utc_datetime + offset
def checkHighfive(first_poster, original_channel, prefix):
	def inner_check(message):
		if message.channel == original_channel and f"{prefix}highfive" in message.content:
			return True
		else:
			return False
	return inner_check
def snapVolumeToSteps(volume, increase=True):
	volume_steps = [0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.22, 0.3, 0.4, 0.55, 0.8, 1, 1.25, 1.5]
	closestToCurrent = min(volume_steps, key=lambda x:abs(x-volume)) 
	if increase:
		newVolumeIndex = volume_steps.index(closestToCurrent) + 1
	else:
		newVolumeIndex = volume_steps.index(closestToCurrent) - 1
	
	new_index = sorted((0, newVolumeIndex, len(volume_steps)-1 ))[1]
	return volume_steps[new_index]
def tenorGIF(searchTerm):
	# set the apikey and limit
	apikey = settings['tenor_key']
	lmt = 20

	# get the top 8 GIFs for the search term
	r = requestGet(
		"https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (searchTerm, apikey, lmt))

	if r.status_code == 200:
		gif = json.loads(r.content)["results"][randrange(lmt)]
		if imgFormat := gif["media"][0].get("gif"):
			return imgFormat["url"]
		elif imgFormat := gif["media"][0].get("tinygif"):
			return imgFormat["url"]
		else:
			return None
	else:
		return None
def normalizeAudio(filename):
	pre, ext = os.path.splitext(filename)
	if ext == ".mp3":
		os.rename(filename, pre + ".m4a")

	newfilename = pre + ".mp3"
	target_il  = -16.0
	target_lra = +11.0
	target_tp  = -1.5

	cmd = ["ffmpeg",
		"-hide_banner", "-nostats",
		"-i", filename,
		"-af",
		f"loudnorm=I={target_il}:LRA={target_lra}:tp={target_tp}:print_format=json", 
		"-f", "null", "-"]

	p = subprocPopen(cmd, stdout=subprocPIPE, stderr=subprocSTDOUT, universal_newlines=False)

	input_i = None
	input_lra = None
	input_tp = None
	input_thresh = None
	target_offset = None

	while True:
		line = p.stdout.readline().decode("utf8", errors='replace').strip()
		if "input_i" in line:
			input_i = float(line.split("\"")[3])
		if "input_lra" in line:
			input_lra = float(line.split("\"")[3])
		if "input_tp" in line:
			input_tp = float(line.split("\"")[3])
		if "input_thresh" in line:
			input_thresh = float(line.split("\"")[3])
		if "target_offset" in line:
			target_offset = float(line.split("\"")[3])
			break

	loudnorm_string = 'loudnorm='
	loudnorm_string += 'print_format=summary:'
	loudnorm_string += 'linear=true:'
	loudnorm_string += f"I={target_il}:"
	loudnorm_string += f"LRA={target_lra}:"
	loudnorm_string += f"tp={target_tp}:"
	loudnorm_string += f"measured_I={input_i}:"
	loudnorm_string += f"measured_LRA={input_lra}:"
	loudnorm_string += f"measured_tp={input_tp}:"
	loudnorm_string += f"measured_thresh={input_thresh}:"
	loudnorm_string += f"offset={target_offset}"

	cmdNormalize = ["ffmpeg",
					"-y", "-hide_banner", "-nostats",
					"-i", filename,
					"-af", loudnorm_string,
					newfilename]
	proc = subprocPopen(cmdNormalize, stdout=subprocPIPE, stderr=subprocPIPE, universal_newlines=False)

	while True:
		line = proc.stdout.readline().decode("utf8", errors='replace').strip()
		if line == '' and proc.poll() is not None:
			break
		
	os.remove(filename) 
	return newfilename
def clampTitle(title):
	maxLength = 40
	if len(title) > maxLength:
		title = title[:maxLength] + "..."
	if title.rfind("[") > title.rfind("]"):
		title = title[:title.rfind("[")]
	return title
def remove_player(guild):
	del players[guild.id]
def get_player(guild):
	"""Retrieve the guild player, or generate one."""
	try:
		player = players[guild.id]
	except KeyError:
		player = MusicPlayer(bot, guild)
		players[guild.id] = player
	return player
def convert_seconds(seconds):
	"""converts seconds to a string with format "m:s" or "h:m:s" """
	minutes, seconds = divmod(seconds, 60)
	if minutes > 60:
		hours, minutes = divmod(minutes, 60)
		return '{:d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
	else:
		return '{}:{:02d}'.format(minutes, seconds)
def parseYTurl(url):
	playlist = False

	#Find the start position of the ID
	try: 
		start = url.index("?v=") + 3
	except:
		try:
			start = url.index("youtu.be/") + 9
		except:
			try:
				start = url.index("playlist?list=") + 14
				playlist = True
			except:
				raise Exception("Wrong URL format")
	#Find the end position of the ID
	try:
		end = url.index("&", start)
	except:
		end = len(url)

	ytID = url[start:end]
	if playlist:
		ytURL = "https://www.youtube.com/playlist?list=" + ytID
	else:
		ytURL = "https://www.youtube.com/watch?v=" + ytID
	return ytURL
def getYTid(url):
	#Find the start position of the ID
	try: 
		start = url.index("?v=") + 3
	except:
		try:
			start = url.index("youtu.be/") + 9
		except:
			try:
				start = url.index("playlist?list=") + 14
			except:
				raise Exception("Wrong URL format")
	#Find the end position of the ID
	try:
		end = url.index("&", start)
	except:
		end = len(url)

	ytID = url[start:end]
	return ytID
def isurl(url):
	#Find the start position of the ID
	return "https://" in url
def isPlaylist(url):
	if "watch?v=" in url:
		return False
	else:
		return "playlist?list=" in url
def get_song_data_async(url):
	""" gets url, title, amounts of songs or the thumbnail of either a playlist or a single song"""		
	if isurl(url):
		data = ytdl.extract_info(url, download=False)
		if 'entries' in data:
			data = data['entries'][0] 
		return (clampTitle(data['title']), data['webpage_url'], data["thumbnail"], data["duration"])
	else:
		#faster but only works for search
		query_string = urlParse.urlencode({"search_query" : url})
		text = requestGet("https://www.youtube.com/results?" + query_string).text
		soup = bs4Soup(text, features="html.parser")

		div = soup.select(".yt-lockup-dismissable")[0]
		if div.select(".yt-lockup-playlist-item"):
			#It's a playlist, we don't support playing it like this
			return (None, None, None, None)


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
def is_connected_player(mPlayer):
	voice_client = get(mPlayer.bot.voice_clients, guild=mPlayer._guild)
	return voice_client and voice_client.is_connected()
def RepresentsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False
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
def create_playlist_string(mPlayer, playlist, startIndex, itemsPerPage):
	description = ""
	if len(playlist) == 0:
		description += f'Default playlist is empty` \n'
		return description
	else:
		description +='**Default playlist:** \n\n'
	for song in playlist[ startIndex : startIndex + itemsPerPage ]:
		description += f'[{song}]({song}) \n'
	return description
def create_queue_string(mPlayer, queueList, startIndex, itemsPerPage):
	description = ""

	timeSum = 0
	for song in queueList:
		timeSum += song.duration

	if len(queueList) > 0:
		description += f'Current queue | {len(queueList)} songs | `{convert_seconds(timeSum)}` \n'
	else:
		description += f'Playing from default playlist \n'
	description += "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ \n" 

	i = startIndex
	for song in queueList[ startIndex : startIndex + itemsPerPage ]:
		i+=1
		description += (f'**#{i}** `{convert_seconds(song.duration)}`:'
			+ (" PlayNext " if song.playnext else "")
			+ f' [{song.title}]({song.url})'
			+ f' - {song.requester} '
			+ '\n')

	if i == len(queueList) and mPlayer.processedQueue.default:
		if len(queueList) > 0:
			description += "\n"
		description += "Default playlist: \n"
		for song in mPlayer.processedQueue.default:
			i+=1
			description += (f'**#{i}** `{convert_seconds(song.duration)}`:'
				+ f' [{song.title}]({song.url})'
				+ '\n')
	return description
def getQueueList(mPlayer, procDefault = False, prepareDefault = False):
	queueList = []
	queueList += mPlayer.processedQueue.playnow
	queueList += mPlayer.prepareQueue.playnow
	queueList += mPlayer.processedQueue.playnext
	queueList += mPlayer.prepareQueue.playnext
	queueList += mPlayer.processedQueue.play
	queueList += mPlayer.prepareQueue.play
	if procDefault:
		queueList += mPlayer.processedQueue.default
	if prepareDefault:
		queueList += mPlayer.prepareQueue.default
	return queueList
def getQueuedAmount(mPlayer, procDefault = True, prepareDefault = False):
	amount = 0

	if procDefault:
		amount += len(mPlayer.processedQueue)
	else:
		amount += len(mPlayer.processedQueue.getQueue())
	
	if prepareDefault:
		amount += len(mPlayer.prepareQueue)
	else: 
		amount += len(mPlayer.prepareQueue.getQueue())
	return amount
def getBoolSetting(guildID, setting):
	if not str(guildID) in serverSettings:
		return True
	if not setting in serverSettings[str(guildID)]:
		return True
	else:
		return serverSettings[str(guildID)][setting]
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
def get_settings_json(json_file, server):
	try:
		data = json.load(json_file)
		if not server in data:
			data[server] = {"volume": 0.5, "acceptedVoiceChannels": [], "acceptedTextChannels": []}
	except json.JSONDecodeError:
		data = {}
		data[server] = {"volume": 0.5, "acceptedVoiceChannels": [], "acceptedTextChannels": []}
	json_file.seek(0)
	return data
def update_settings_json_async(server, field_to_update, new_value, add_to_list=True, clear_list=False):
	global serverSettings
	with open(server_settings_location, 'r+') as jsonFile:
		data = get_settings_json(jsonFile, server)
		
		if field_to_update == 'acceptedTextChannels' or field_to_update == 'acceptedVoiceChannels':
			if clear_list:
				data[server][field_to_update] = []
			elif add_to_list:
				data[server][field_to_update].append(new_value)
			else:
				data[server][field_to_update].remove(new_value)
		else:
			data[server][field_to_update] = new_value

		json.dump(data, jsonFile)
		jsonFile.truncate()
		serverSettings = data
def update_playlist_json_async(server, url, add = False):
	global serverSettings
	with open(playlist_location, 'r+') as jsonFile:
		data = get_playlist_json(jsonFile, server)
		
		if len(url) == 0:
			data[server] = []
		elif add:
			data[server].append(url)
		else:
			data[server].remove(url)
		
		json.dump(data, jsonFile)
		jsonFile.truncate()
async def get_playlist_info(url, loop=None):
	loop = loop or asyncio.get_event_loop()
	return await loop.run_in_executor(None, lambda: get_playlist_info_async(url))
async def get_song_data(url, loop=None):
	loop = loop or asyncio.get_event_loop()
	return await loop.run_in_executor(None, lambda: get_song_data_async(url))
async def getDefaultPlaylist(guildID):
	data = {}
	server = str(guildID)
	with open(playlist_location, 'r', encoding='utf-8') as json_file:
		data = get_playlist_json(json_file, server)
	return data[server]
async def update_settings_json(server, field_to_update, new_value, add_to_list=True, clear_list=False, loop=None):
	loop = loop or asyncio.get_event_loop()
	await loop.run_in_executor(None, lambda: update_settings_json_async(server, field_to_update, new_value, add_to_list, clear_list))
async def update_playlist_json(server, url, add = False, loop=None):
	loop = loop or asyncio.get_event_loop()
	await loop.run_in_executor(None, lambda: update_playlist_json_async(server, url, add))
async def setVolume(guild, vc, newVolume):
	mPlayer = get_player(guild)
	mPlayer.volume = newVolume
	if vc != None and vc.source != None:
		vc.source.volume = newVolume
	await update_settings_json(str(guild.id), 'volume', float(newVolume))
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
async def add_song(ctx, url, stream=False, play_next=False, play_now=False):
	async with ctx.typing():
		try:
			url = parseYTurl(url)
		except:
			None
		
		if isPlaylist(url):
			#TODO
			if True:
				await ( await ctx.send(f"Playlists aren't implemented yet sorry! Please add a playlist to the default playlist instead")).delete(delay=15)
				await ctx.message.delete(delay=15)
				return
			else:
				if play_next or play_now:
					await ( await ctx.send(f"Can't play a playlist using playnow or playnext, sorry!")).delete(delay=15)
					await ctx.message.delete(delay=15)
					return
				
				title, url, songs = await get_playlist_info(url)
				mPlayer = get_player(ctx.guild)
				mPlayer.prepareQueue.play = mPlayer.prepareQueue.play + songs
				mPlayer.downloader.set()
				embed = discord.Embed(title=title, url=url, description=f"[{len(songs)} queued]")
				await ctx.send(embed=embed)

		else:
			title, url, thumbnail, duration = await get_song_data(url)

			songObj = Song(title=title, url=url, thumbnail=thumbnail, duration=duration, requester=ctx.author.mention)
			mPlayer = get_player(ctx.guild)

			if play_next:
				songObj.playnext = True
				mPlayer.prepareQueue.playnext.append(songObj)
				mPlayer.downloader.set()

				embed = discord.Embed(title=title, url=url, description=f"Queued **#1**, `[{convert_seconds(duration)}]`")
				embed.set_thumbnail(url=thumbnail)
				await ctx.send(embed=embed)

			elif play_now:
				songObj.playnext = True
				mPlayer.prepareQueue.playnow.append(songObj)
				mPlayer.downloader.set()
				
				val = getBoolSetting(str(ctx.guild.id), 'nowPlayingAuto')
				if val:
					await now_playing(ctx.guild, ctx.channel, preparing=True)
				else:
					embed = discord.Embed(title=title, url=url, description=f"`[{convert_seconds(duration)}]`")
					embed.set_thumbnail(url=thumbnail)
					await ctx.send(embed=embed)

			elif mPlayer.current != None:
				mPlayer.prepareQueue.play.append(songObj)
				mPlayer.downloader.set()

				embed = discord.Embed(title=title, url=url, description=f"Queued **#{getQueuedAmount(mPlayer, procDefault = False, prepareDefault = False)}**, `[{convert_seconds(duration)}]`")
				embed.set_thumbnail(url=thumbnail)
				await ctx.send(embed=embed)

			else:
				mPlayer.prepareQueue.play.append(songObj)
				mPlayer.downloader.set()
				
				val = getBoolSetting(str(ctx.guild.id), 'nowPlayingAuto')
				if val:
					await now_playing(ctx.guild, ctx.channel)
				else:
					embed = discord.Embed(title=title, url=url, description=f"`[{convert_seconds(duration)}]`")
					embed.set_thumbnail(url=thumbnail)
					await ctx.send(embed=embed)
async def now_playing(guild, channel=None, preparing=False, dontSticky = False, forceSticky = False):
	mPlayer = get_player(guild)
	currentPlayer = mPlayer.current
	msg = mPlayer.current_np_message


	if preparing:
		if getQueuedAmount(mPlayer, procDefault = True, prepareDefault = False) > 0:
			nextSong = getQueueList(mPlayer, procDefault = True, prepareDefault = True)[0]
			print(nextSong)
			embed = discord.Embed(title=nextSong.title, url=nextSong.url, description="Preparing song...")
		else:
			embed = discord.Embed(description="Preparing song...")

		if msg and not forceSticky:
			await msg.edit(embed=embed)
			await set_message_reactions(msg, [])
		else:
			message = await channel.send(content="Now playing:", embed=embed)
			mPlayer.current_np_message = message
			mPlayer.stop_update_np.set()
		return

	if currentPlayer == None:
		if guild.voice_client == None:
			embed = discord.Embed(title="Player stopped")
		elif getQueuedAmount(mPlayer, procDefault = True, prepareDefault = True) > 0:
			if getQueuedAmount(mPlayer, procDefault = True, prepareDefault = False) > 0:
				nextSong = getQueueList(mPlayer, procDefault = True, prepareDefault = False)[0]
				if mPlayer.update_np_downloading.is_set():
					embed = discord.Embed(title=nextSong.title, url=nextSong.url, description="Downloading song...")
				elif mPlayer.update_np_normalizing.is_set():
					embed = discord.Embed(title=nextSong.title, url=nextSong.url, description="Normalizing song volume...")
				else:
					embed = discord.Embed(title=nextSong.title, url=nextSong.url, description="Preparing song...")
			else:
				embed = discord.Embed(description="Preparing song...")
		else:
			embed = discord.Embed(description="There's no song playing")
		if msg:
			await msg.edit(embed=embed)
			await set_message_reactions(msg, [])
		else:
			message = await channel.send(content="Now playing:", embed=embed)
			mPlayer.current_np_message = message
			mPlayer.stop_update_np.set()
		return

	sticky = getBoolSetting(str(guild.id), 'nowPlayingSticky')
	if (not forceSticky) and ( (dontSticky) or (not sticky) or (msg and msg.channel.last_message_id == msg.id) ):
		em =  msg.embeds[0].description
		description = create_progressbar(mPlayer.timePaused,
										 mPlayer.timeStarted,
										 currentPlayer.duration,
										 guild.voice_client.is_paused())

		embed = discord.Embed(title=currentPlayer.title, url=currentPlayer.url, description=description)
		await msg.edit(embed=embed)
		controls = getBoolSetting(str(guild.id), 'nowPlayingControls')
		if not controls:
			await set_message_reactions(msg, [])
		elif em == "There's no song playing" or em == "Preparing song..." or em == "Downloading song..."  or em == "Normalizing song volume..." :
			await set_message_reactions(msg, ["⏯️", "⏭️", "🔉", "🔊"])
	else:
		if msg:
			channel = msg.channel
		
		content = "Now playing:"
		
		description = create_progressbar(mPlayer.timePaused,
										 mPlayer.timeStarted,
										 currentPlayer.duration,
										 guild.voice_client.is_paused())

		embed = discord.Embed(title=currentPlayer.title, url=currentPlayer.url, description=description)
		if msg:
			await msg.delete()
		message = await channel.send(content=content, embed=embed)
		mPlayer.current_np_message = message
		if not msg:
			mPlayer.stop_update_np.set()
		controls = getBoolSetting(str(guild.id), 'nowPlayingControls')
		if controls:
			await set_message_reactions(message, ["⏯️", "⏭️", "🔉", "🔊"])
		else:
			await set_message_reactions(message, [])
async def set_message_reactions(msg, new_reactions):
	await msg.clear_reactions()

	for reaction in new_reactions:
		await msg.add_reaction(reaction)
async def not_connected_message(ctx):
	if ctx.voice_client is None:
		return await ctx.send("I'm not connected to a voice channel.")
	if ctx.author.voice.channel != ctx.voice_client.channel:
		return await ctx.send(f"You have to be in **{ctx.voice_client.channel.name}** to do that")
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
async def bookList(channel, mPlayer, func, playList, itemsPerPage=5):
	''' Generates a list with pages that you can flip back and forth '''
	pageIndex = 1
	listIndex = 0
	queueLength = len(playList)
	pages = queueLength // itemsPerPage + (queueLength % itemsPerPage > 0)  #rounding up

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
			reaction, user = await bot.wait_for('reaction_add', timeout=60.0)
		except asyncio.TimeoutError:
			await message.clear_reactions()
			break
		else:
			if user == bot.user:
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
async def determine_prefix(bot, message):
	''' Returns the prefix for the server that the message was sent in '''
	guild = message.guild
	#Only allow custom prefixs in guild
	if guild:
		guildSettings = serverSettings.get(str(guild.id))
		if guildSettings:
			return guildSettings.get("prefix", settings['defaultPrefix'])
		else:
			return settings['defaultPrefix']
	else:
		return settings['defaultPrefix']
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
					'prepare_default_playlist']

	if not helpCommand:
		#no helpCommand which means show the whole help message
		prefix = await determine_prefix(bot, ctx.message)
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

		prefix = await determine_prefix(bot, ctx.message)
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
		elif helpCommand == "prepare_default_playlist":
			commandSyntax += "prepare_default_playlist"
			description += "Downloads all songs that are in the default playlist and prepares them so that next time you play it will be instant"
		commandSyntax += "`\n\n"
		embed = discord.Embed(description=commandSyntax + description)
		embed.set_author(name=bot.user.name + " Help Menu" , icon_url=bot.user.avatar_url)
		embed.set_footer(text="Syntax: (x | y): use either x or y, (x): x is optional")
		await ctx.send(embed=embed)	
async def handleNPReactions(reaction, user, mPlayer):
	''' Handles the Now Playing message reactions '''
	vc = reaction.message.guild.voice_client
	await reaction.remove(user)

	if (not user.voice) or user.voice.channel != vc.channel:
		#Only users in the same voice channel can use reactions
		return

	if reaction.emoji == "⏭️":
		if vc and vc.source:	
			vc.source.volume = 0
			vc.stop()
			await reaction.message.edit(content=f"{user.mention} skipped a song")

	elif reaction.emoji == "⏯️":
		if vc.is_paused():
			vc.resume()
			mPlayer.timeStarted = time.time() - mPlayer.timePaused
			await reaction.message.edit(content=f"{user.mention} resumed the player")
		else:
			vc.pause()
			mPlayer.timePaused = time.time() - mPlayer.timeStarted
			await reaction.message.edit(content=f"{user.mention} paused the player")
		mPlayer.update_np.set()
	
	elif reaction.emoji == "🔉":
		newVolume = snapVolumeToSteps(mPlayer.volume, increase=False)
		await setVolume(reaction.message.guild, vc, newVolume)
		await reaction.message.edit(content=f"{user.mention} lowered the volume to `{round(newVolume*100)}`")
	
	elif reaction.emoji == "🔊":
		newVolume = snapVolumeToSteps(mPlayer.volume, increase=True)
		await setVolume(reaction.message.guild, vc, newVolume)
		await reaction.message.edit(content=f"{user.mention} increased the volume to `{round(newVolume*100)}`")


#########################################################################
#																		#
#	  ######  ##          ###     ######   ######  ########  ###### 	#
#	 ##    ## ##         ## ##   ##    ## ##    ## ##       ##    ##	#
#	 ##       ##        ##   ##  ##       ##       ##       ##      	#
#	 ##       ##       ##     ##  ######   ######  ######    ###### 	#
#	 ##       ##       #########       ##       ## ##             ##	#
#	 ##    ## ##       ##     ## ##    ## ##    ## ##       ##    ##	#
#	  ######  ######## ##     ##  ######   ######  ########  ###### 	#
#																		#
#########################################################################

class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *args):
		super().__init__(source)

	@classmethod
	async def regather_stream(cls, data, *, loop):
		"""Used for preparing a stream, instead of downloading.
		Since Youtube Streaming links expire."""
		loop = loop or asyncio.get_event_loop()

		to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
		data = await loop.run_in_executor(None, to_run)

		return cls(discord.FFmpegPCMAudio(data['url']))
		
	@classmethod
	async def from_url(cls, mPlayer, url, *, loop=None, stream=False):
		ytID = getYTid(url)
		existingFiles = globglob(f"{settings['musicFolder']}youtube-{ytID}.*")
		if existingFiles:
			return cls(discord.FFmpegPCMAudio(existingFiles[0], **ffmpeg_options))

		mPlayer.update_np_downloading.set()
		if not mPlayer.current:
			mPlayer.update_np.set()

		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		mPlayer.update_np_downloading.clear()
		if not data:
			return None

		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]

		filename = data['url'] if stream else ytdl.prepare_filename(data)	
	
		mPlayer.update_np_normalizing.set()
		if not mPlayer.current:
			mPlayer.update_np.set()

		if not stream:
			with concurFuture.ProcessPoolExecutor() as pool:
				to_run = partial(normalizeAudio, filename)
				newfilename = await loop.run_in_executor(pool, to_run)
			filename = newfilename

		mPlayer.update_np_normalizing.clear()

		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options))

class Current_or_id_channel(commands.Converter):
	''' Argument type converter, makes sure the argument is either "current", a channel ID or a channel mention '''
	__slots__ = ('is_voice')

	def __init__(self, is_voice):
		self.is_voice = is_voice

	async def convert(self, ctx, argument):
		if argument == "current":
			if self.is_voice:
				if ctx.author.voice is not None:
					channel = ctx.author.voice.channel
				else:
					raise commands.errors.BadArgument("You have to be in a voice channel to use that")
			else:
				channel = ctx.channel
		elif len(ctx.message.channel_mentions) > 0:
			channel = ctx.message.channel_mentions[0]
		else:
			try:
				channel = ctx.guild.get_channel(int(argument))
				if not channel:
					raise commands.errors.BadArgument("Can't find a channel with that ID")
			except:
				raise commands.errors.BadArgument("Bad argument, either use `current` for the current channel, tag a channel like `#general`"
						+ " or use its ID (Settings > Appearance > Enable Developer Mode, then rightclick the channel and copy its ID)")
		return channel

@dataclass
class Song:
	''' Class for storing info about a song '''
	title: str
	url: str
	thumbnail: str 
	duration: int
	requester: int
	playnext: bool = False #optional, only set for playnext
	source: YTDLSource = None # Optional, a player that will added later

@dataclass
class SongQueue:
	''' Class for storing queues '''
	playnow: list = field(default_factory=list)
	playnext: list = field(default_factory=list)
	play: list = field(default_factory=list)
	default: list = field(default_factory=list)

	def __iter__(self):
		return iter(self.playnow + self.playnext + self.play + self.default)
	def __len__(self):
		return len(self.playnow + self.playnext + self.play + self.default)
	def getQueue(self):
		return self.playnow + self.playnext + self.play
	def getDefault(self):
		return self.default
	def remove(self, element):
		if element in self.playnow:
			self.playnow.remove(element)
			return True
		if element in self.playnext:
			self.playnext.remove(element)
			return True
		if element in self.play:
			self.play.remove(element)
			return True
		return False


class MusicPlayer:
	"""A class assigned to each guild that's currently playing music"""
	__slots__ = ('bot', '_guild',
				'downloader', 'playNext', 'update_np', 'stop_update_np', 'update_np_downloading', 'update_np_normalizing',
				'prepareQueue', 'processedQueue',
				'current', 'current_np_message',
				'volume', 'timeStarted', 'timePaused', 'stop_player')

	def __init__(self, bot, guild):
		self.bot = bot
		self._guild = guild

		self.downloader = asyncio.Event()
		self.playNext = asyncio.Event()
		self.update_np = asyncio.Event()
		self.stop_update_np = asyncio.Event()
		self.update_np_downloading = asyncio.Event()
		self.update_np_normalizing = asyncio.Event()

		self.prepareQueue = SongQueue()
		self.processedQueue = SongQueue()

		self.current = None #class Song with player
		self.current_np_message = None #last NowPlaying message

		self.timeStarted = None
		self.timePaused = None
		self.stop_player = False

		server = str(guild.id)
		if not server in serverSettings:
			serverSettings[server] = {"volume": 0.5, "acceptedVoiceChannels": [], "acceptedTextChannels": []}
		self.volume = serverSettings[server]["volume"]

		self.update_np.clear()
		self.stop_update_np.clear()
		self.downloader.clear()
		self.playNext.clear()
		bot.loop.create_task(self.update_now_playing())
		bot.loop.create_task(self.player_loop())
		bot.loop.create_task(self.downloader_loop())
	def wakeUpPlayer(self):
		if (not self.current) and self._guild.voice_client:
			self.playNext.set()
	async def update_now_playing(self):
		"""update "Now Playing" loop"""
		await self.bot.wait_until_ready()
		while not self.bot.is_closed():

			await self.stop_update_np.wait()

			# Wait for the next song. If we timeout cancel the player and disconnect
			try:
				async with timeout(5):
					await self.update_np.wait()
					self.update_np.clear()

			except asyncio.TimeoutError:
				#TODO: go through message history, check last message and compare time since it was sent, if it was sent within 5s ago, then np update but skip sticky
				if self.current_np_message:
					message = (await self.current_np_message.channel.history(limit=1).flatten())[0]

					localTimezoneCreatedAt = datetime_from_utc_to_local(message.created_at)
					if (time.time() - localTimezoneCreatedAt.timestamp()) < 10:
						await self.stop_update_np.wait()
						await now_playing(self._guild, dontSticky = True)
					else:
						await self.stop_update_np.wait()
						await now_playing(self._guild)
			else:
				await self.stop_update_np.wait()
				await now_playing(self._guild)
			if self.current == None and getQueuedAmount(self, procDefault = True, prepareDefault = True) == 0:
				self.stop_update_np.clear()
	async def downloader_loop(self):
		await self.bot.wait_until_ready()
		await self.downloader.wait()
		self.downloader.clear()

		while not self.bot.is_closed():

			if not is_connected_player(self):
				if self.stop_player:
					await self.destroy(self._guild) 
				await self.downloader.wait()
				self.downloader.clear()

			#print("checking for something to download")
			if self.prepareQueue.playnow:
				print("downloading playnow")
				songObj = self.prepareQueue.playnow[0]
				await self.prepareYTSource(songObj)
				if self.prepareQueue.playnow and self.prepareQueue.playnow[0] == songObj:
					del self.prepareQueue.playnow[0]
				else:
					continue
				if not songObj.source or not is_connected_player(self):
					continue
				self.processedQueue.playnow.append(songObj)
				self.wakeUpPlayer()
				if self._guild.voice_client.source:
					self._guild.voice_client.source.volume = 0
				self._guild.voice_client.stop()

			elif self.prepareQueue.playnext:
				print("downloading playnext")
				songObj = self.prepareQueue.playnext[0]
				await self.prepareYTSource(songObj)
				if self.prepareQueue.playnext and self.prepareQueue.playnext[0] == songObj:
					del self.prepareQueue.playnext[0]
				else:
					continue
				if not songObj.source or not is_connected_player(self):
					continue
				self.processedQueue.playnext.append(songObj)
				self.wakeUpPlayer()

			elif len(self.processedQueue.getQueue()) < max_processed_songs:

				if self.prepareQueue.play:
					print("downloading song")
					songObj = self.prepareQueue.play[0]
					await self.prepareYTSource(songObj)
					if self.prepareQueue.play and self.prepareQueue.play[0] == songObj:
						del self.prepareQueue.play[0]
					else:
						continue
					if not songObj.source or not is_connected_player(self):
						continue
					self.processedQueue.play.append(songObj)
					self.wakeUpPlayer()

				elif len(self.processedQueue) < max_processed_songs:

					if self.prepareQueue.default:
						print("downloading default")
						url = self.prepareQueue.default[0]
						self.prepareQueue.default = self.prepareQueue.default[1:] + self.prepareQueue.default[:1]
						songObj = Song(title="temp", url=url,
										thumbnail="temp",
										duration=None,
										requester=None)
						await self.prepareYTSource(songObj)
						if not songObj.source:
							continue
						title, url, thumbnail, duration = await get_song_data(url)
						songObj.url = url
						songObj.title = title
						songObj.duration = duration
						songObj.thumbnail = thumbnail
						if not is_connected_player(self):
							continue
						self.processedQueue.default.append(songObj)
						self.wakeUpPlayer()

					else:
						server = str(self._guild.id)
						data = await getDefaultPlaylist(server)
						if data:
							print("preparing default")
							newList = []
							for link in data:
								if "playlist?list=" in link:
									_, _, links = await get_playlist_info(link)
									newList = newList + links
								else:
									newList.append(link)

							if not is_connected_player(self):
								continue
							self.prepareQueue.default = newList
							shuffle(self.prepareQueue.default)
							continue

						else:
							print("nothing to download, waiting")
							await self.downloader.wait()
							self.downloader.clear()
				else:
					print("filled list, waiting")
					await self.downloader.wait()
					self.downloader.clear()
			else:
				print("filled list, waiting")
				await self.downloader.wait()
				self.downloader.clear()

			await asyncio.sleep(2)
	async def player_loop(self):
		"""main player loop."""
		await self.bot.wait_until_ready()
		while not self.bot.is_closed():

			await self.playNext.wait()
			self.playNext.clear()
		
			# Wait for the next song. If we timeout cancel the player and disconnect
			try:
				async with timeout(time_wait_diconnect_emtpy_playlist):
					while(True):
						if self.processedQueue.playnow:
							songObj = self.processedQueue.playnow.pop(0)
							break
						elif self.prepareQueue.playnow:
							await self.playNext.wait()
							self.playNext.clear()

						elif self.processedQueue.playnext:
							songObj = self.processedQueue.playnext.pop(0)
							break
						elif self.prepareQueue.playnext:
							await self.playNext.wait()
							self.playNext.clear()

						elif self.processedQueue.play:
							songObj = self.processedQueue.play.pop(0)
							break
						elif self.prepareQueue.play:
							await self.playNext.wait()
							self.playNext.clear()

						elif self.processedQueue.default:
							songObj = self.processedQueue.default.pop(0)
							break
						else:
							#Nothing to play, wait for new song
							await self.playNext.wait()
							self.playNext.clear()

			except asyncio.TimeoutError:
				await self.destroy(self._guild)
				return

			songObj.source.volume = self.volume
			self.current = songObj
			self.timeStarted = time.time()
			self.timePaused = None
			
			self.update_np.set()
			if self.current_np_message:
				self.stop_update_np.set()

			self._guild.voice_client.play(songObj.source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.playNext.set))
			await self.playNext.wait()

			self.current = None

			#Song finished, make sure to clean it up
			#songObj.source.cleanup()
			
			if self.stop_player:
				await self.destroy(self._guild) 
				await self.playNext.wait()
				self.playNext.clear()
				#return
			else:
				self.downloader.set()
				await asyncio.sleep(time_to_wait_between_songs)
	async def prepareYTSource(self, songObj):
		for song in list(self.processedQueue) + ([self.current] if self.current else []):
			if song.url == songObj.url:
				#Song is already in queue, no need to download it again so just duplicate the object
				songObj.source = song.source
				return
		songObj.source = await YTDLSource.from_url(self, songObj.url, loop=bot.loop, stream=False)
	async def destroy(self, guild):
		"""Disconnect and cleanup the player."""
		self.current = None
		self.stop_player = False
		self.prepareQueue = SongQueue()
		self.processedQueue = SongQueue()

		if guild.voice_client:
			guild.voice_client.stop()
			await guild.voice_client.disconnect()

		self.stop_update_np.set()
		#remove_player(guild)



if __name__ == "__main__":
	from youtube_dl import YoutubeDL as youtubeDownloader, utils as youtubeUtils
	from concurrent import futures as concurFuture
	from bs4 import BeautifulSoup as bs4Soup
	from urllib import parse as urlParse
	from async_timeout import timeout
	from glob import glob as globglob
	from re import search as reSearch
	from functools import partial
	from datetime import datetime
	from threading import Thread
	from tendo import singleton
	from random import shuffle
	import youtube_dl
	import asyncio
	import ffmpeg
	import json
	import time
	
	#Only allow one instance of this code
	me = singleton.SingleInstance()
	
#####################################################################################	
#																					#
#	 ####  ##    ##  #### ######## ####    ###    ##       #### ######## ########	#
#	  ##   ###   ##   ##     ##     ##    ## ##   ##        ##       ##  ##      	#
#	  ##   ####  ##   ##     ##     ##   ##   ##  ##        ##      ##   ##      	#
#	  ##   ## ## ##   ##     ##     ##  ##     ## ##        ##     ##    ######  	#
#	  ##   ##  ####   ##     ##     ##  ######### ##        ##    ##     ##      	#
#	  ##   ##   ###   ##     ##     ##  ##     ## ##        ##   ##      ##      	#	
#	 ####  ##    ##  ####    ##    #### ##     ## ######## #### ######## ########	#
#																					#
#####################################################################################

#Initialize:

	configFile = 'settings/config.json'
	playlist_location = "settings/serverPlaylists.json"
	server_settings_location = "settings/serverSettings.json"
	nekoApiUrl = "https://nekos.life/api/v2/"

	players = {} # a MusicPlayer for each server
	serverSettings = {} #{server: {volume: 0.5, acceptedVoiceChannels: [], acceptedTextChannels: []} ....}
	
	time_to_wait_between_songs = 0
	max_processed_songs = 3
	time_wait_diconnect_emtpy_playlist = 300
	timeout_download = 20
	youtube_download_rate = "2M" # 2mb/s

	#initialize config file
	if not os.path.exists(configFile):
		os.makedirs(os.path.dirname(configFile), exist_ok=True)
		with open(configFile, 'w+') as conFile:
			data = '{ \n\t"token": "PUT_TOKEN_HERE", \n\t"musicFolder": "music_cache/", \n\t"defaultPrefix": "$"\n}'
			conFile.write(data)
			print("Generated config file, open it and insert the bot token")
			quit()

	with open(configFile) as json_data_file:
		settings = json.load(json_data_file)

	#Initialize playlist and server_settings files
	try:
		f1 = open(playlist_location, 'x')
		f1.close()
	except:
		None
	try:
		f1 = open(server_settings_location, 'x')
		f1.close()
	except:
		with open(server_settings_location, 'r', encoding='utf-8') as json_file:
			try:
				data = json.load(json_file)
			except json.JSONDecodeError:
				print("SERVERSETTINGS JSON ERROR")
				data = {}
			serverSettings = data

	bot = commands.Bot(command_prefix=determine_prefix)

	#Check for Discord API token
	if settings['token'] == "PUT_TOKEN_HERE":
		print("\nWrong token, open the settings/config.json file and replace \"PUT_TOKEN_HERE\" with your bots token from the discord developer portal\n" +
			  "It has to be surrounded by quotes, example: \"NjQdMzayODY5cTI3ODYtMzA2.XcVZPg.ZjG28fgYJkzEw3abOgs3r3DtJVQ\"\n")
		quit()

	


	ffmpeg_options = {
		'options': '-vn'
	}
	# Suppress noise about console usage from errors
	youtubeUtils.bug_reports_message = lambda: ''
	ytdl_format_options = {
		'dump-json': True,
		'limit-rate': youtube_download_rate,
		'flat-playlist': True,
		'format': 'bestaudio/best',
		'outtmpl': settings['musicFolder'] + '%(extractor)s-%(id)s.%(ext)s',
		'restrictfilenames': True,
		'no-playlist': True,
		'nocheckcertificate': True,
		'ignoreerrors': True,
		'logtostderr': False,
		'quiet': True,
		'no_warnings': False,
		'youtube-skip-dash-manifest': True,
		'geo-bypass': True,
		'default_search': 'auto',
		'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
	}
	ytdl = youtubeDownloader(ytdl_format_options)


#################################################################
#																#
#	 ######## ##     ## ######## ##    ## ########  ###### 		#
#	 ##       ##     ## ##       ###   ##    ##    ##    ##		#
#	 ##       ##     ## ##       ####  ##    ##    ##      		#
#	 ######   ##     ## ######   ## ## ##    ##     ###### 		#
#	 ##        ##   ##  ##       ##  ####    ##          ##		#
#	 ##         ## ##   ##       ##   ###    ##    ##    ##		#
#	 ########    ###    ######## ##    ##    ##     ###### 		#
#																#
#################################################################

#Events:

	@bot.event
	async def on_ready():
		print('Logged in as')
		print(bot.user.name)
		print(bot.user.id)
		print('------')

	@bot.event
	async def on_reaction_add(reaction, user):	
		if user == bot.user or reaction.message.author != bot.user:
			return
			
		mPlayer = get_player(reaction.message.guild)
		if mPlayer.current_np_message and mPlayer.current_np_message.id == reaction.message.id:
			await handleNPReactions(reaction, user, mPlayer)

	@bot.event
	async def on_voice_state_update(member, before, after):
		mPlayer = get_player(member.guild)
		if is_connected_player(mPlayer):
			vc = get(bot.voice_clients, guild=member.guild)
			if len(vc.channel.members) == 1 and vc.channel.members[0] == bot.user:
				mPlayer.stop_player = True
				vc.stop()

	@bot.event
	async def on_command_error(ctx, error):
		if isinstance(error, commands.errors.CheckFailure):
			return

		elif isinstance(error, commands.errors.BadArgument):
			await ctx.send(error)

		elif isinstance(error, commands.errors.MissingRequiredArgument):
			if ctx.command.parent is not None:
				await helpFunction(ctx, helpCommand = ctx.command.parent.aliases + [ctx.command.parent.name] )
			else:
				await helpFunction(ctx, helpCommand = ctx.command.aliases + [ctx.command.name] )


		elif isinstance(error, discord.errors.Forbidden):
			print("Missing permissions")
			await ctx.send("Something failed because I'm missing permissions, check documentation or contact the developer")

		elif isinstance(error, commands.errors.CommandNotFound):
			return

		else:
			raise(error)

#################################################################
#																#
#	  ######  ##     ## ########  ######  ##    ##  ###### 		#
#	 ##    ## ##     ## ##       ##    ## ##   ##  ##    ##		#
#	 ##       ##     ## ##       ##       ##  ##   ##      		#
#	 ##       ######### ######   ##       #####     ###### 		#
#	 ##       ##     ## ##       ##       ##  ##         ##		#
#	 ##    ## ##     ## ##       ##    ## ##   ##  ##    ##		#
#     ######  ##     ## ########  ######  ##    ##  ###### 		#
#																#
#################################################################

#Checks:

	@bot.check
	async def globally_block_dms(ctx):
		return ctx.guild is not None

	@bot.check
	async def log_to_console(ctx):
		print('{0.created_at}, Server: {0.guild.name}, User: {0.author}: {0.content}'.format(ctx.message))
		return True




#####################################
#									#
#	 ######## ##     ## ##    ##	#
#	 ##       ##     ## ###   ##	#
#	 ##       ##     ## ####  ##	#
#	 ######   ##     ## ## ## ##	#
#	 ##       ##     ## ##  ####	#
#	 ##       ##     ## ##   ###	#
#	 ##        #######  ##    ##	#
#									#
#####################################

#Fun commands:

	@bot.command(aliases=['8ball', '8'])
	async def question8ball(ctx, *, question: str):

		if question[-1] != "?":
			return await ctx.send(content="That doesn't look like a question, didn't you learn punctuation in school?")
		
		response = requestGet(nekoApiUrl + "8ball").json()['response']
		await ctx.send(content = "`" + response + "`")

	@bot.command()
	async def kiss(ctx, *, user: discord.Member):
		if user == ctx.author:
			return await ctx.send(content = f"You can't kiss yourself you dummy")

		url = requestGet(nekoApiUrl + "img/kiss").json()['url']

		text = f"**{ctx.author.mention} kisses {user.mention}**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of nekos.life")

		await ctx.send(embed=embed)

	@bot.command()
	async def hug(ctx, *, user: discord.Member):
		url = requestGet(nekoApiUrl + "img/hug").json()['url']

		if user == ctx.author:
			text = f"**{ctx.author.mention} hugs themself**"
		else:
			text = f"**{ctx.author.mention} hugs {user.mention}**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of nekos.life")

		await ctx.send(embed=embed)

	@bot.command()
	async def poke(ctx, *, user: discord.Member):

		url = requestGet(nekoApiUrl + "img/poke").json()['url']

		if user == ctx.author:
			text = f"**{ctx.author.mention} pokes themself**"
		else:
			text = f"**{ctx.author.mention} pokes {user.mention}**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of nekos.life")

		await ctx.send(embed=embed)

	@bot.command()
	async def feed(ctx, *, user: discord.Member):

		url = requestGet(nekoApiUrl + "img/feed").json()['url']

		if user == ctx.author:
			text = f"**{ctx.author.mention} feeds themself**"
		else:
			text = f"**{ctx.author.mention} feeds {user.mention}**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of nekos.life")

		await ctx.send(embed=embed)

	@bot.command()
	async def cuddle(ctx, *, user: discord.Member):

		url = requestGet(nekoApiUrl + "img/cuddle").json()['url']

		if user == ctx.author:
			text = f"**{ctx.author.mention} cuddles themself**"
		else:
			text = f"**{ctx.author.mention} cuddles {user.mention}**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of nekos.life")

		await ctx.send(embed=embed)

	@bot.command()
	async def slap(ctx, *, user: discord.Member):

		url = requestGet(nekoApiUrl + "img/slap").json()['url']

		if user == ctx.author:
			text = f"**{ctx.author.mention} slaps themself**"
		else:
			text = f"**{ctx.author.mention} slaps {user.mention}**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of nekos.life")

		await ctx.send(embed=embed)

	@bot.command()
	async def pat(ctx, *, user: discord.Member):

		url = requestGet(nekoApiUrl + "img/pat").json()['url']

		if user == ctx.author:
			text = f"**{ctx.author.mention} pats themself**"
		else:
			text = f"**{ctx.author.mention} pats {user.mention}**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of nekos.life")

		await ctx.send(embed=embed)

	@bot.command()
	async def tickle(ctx, *, user: discord.Member):

		url = requestGet(nekoApiUrl + "img/tickle").json()['url']

		if user == ctx.author:
			text = f"**{ctx.author.mention} tickles themself**"
		else:
			text = f"**{ctx.author.mention} tickles {user.mention}**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of nekos.life")

		await ctx.send(embed=embed)

	@bot.command()
	async def lick(ctx, *, user: discord.Member):

		url = tenorGIF("anime lick")

		if user == ctx.author:
			text = f"**{ctx.author.mention} licks themself**"
		else:
			text = f"**{ctx.author.mention} licks {user.mention}**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of tenor.com")

		await ctx.send(embed=embed)

	@bot.command()
	async def highfive(ctx, *, user: discord.Member = None):
		if user:
			#Highfive another user directly
			if user == ctx.author:
				text = f"**{ctx.author.mention} high fives themself**"
			else:
				text = f"**{ctx.author.mention} high fives {user.mention}**"
		else:
			#This command will be run twice, depending on the content we may want to let the first command do the work
			messages = await ctx.channel.history(limit=5).flatten()
			for i, message in enumerate(messages):
				if message.author == bot.user and message.embeds and  "high fives" in message.embeds[0].description:
					break
				elif message.author == bot.user and "was left hanging" in message.content:
					break
				elif message.author == bot.user and "prepares for a high five" in message.content:
					return
				elif message.content == f"{await determine_prefix(bot, ctx.message)}highfive":
					if i == 0:
						continue
					else:
						break

			msg = await ctx.send(content=f"{ctx.author.mention} prepares for a high five")

			try:
				message = await bot.wait_for('message', check=checkHighfive(ctx.author, msg.channel, await determine_prefix(bot, message)), timeout=5.0)

			except asyncio.TimeoutError:
				return await ctx.send(content=f"{ctx.author.mention} wanted to high five but was left hanging...")

			else:
				if message.content == f"{await determine_prefix(bot, ctx.message)}highfive {ctx.author.mention}":
					#Someone highfived back directly to the original poster, just let the other command do the work
					return
				if message.content == f"{await determine_prefix(bot, ctx.message)}highfive":
					if message.author == ctx.author:
						return await ctx.send(content=f"{ctx.author.mention} was left hanging so they tried to save it by high fiving themselfs... feelsbadman")
					else:
						text = f"**{message.author.mention} high fives {ctx.author.mention}**"
						
		#High five text is done, time to get the gif and post it
		url = tenorGIF("anime highfive")
		
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of tenor.com")
		await ctx.send(embed=embed)

	@bot.command(alias=["owo"])
	async def uwu(ctx, *, message = None):
		if message:
			urlString = urlParse.quote(message, safe='')
			text = requestGet(nekoApiUrl + "owoify" + "?text=" + urlString).json()['owo']
		else:
			#get previous message and uwuify that
			messages = await ctx.channel.history(limit=5).flatten()
			isAfterOP = False
			for message in messages:
				if isAfterOP:
					#This is the message we want
					urlString = urlParse.quote(message.content, safe='')
					text = requestGet(nekoApiUrl + "owoify" + "?text=" + urlString).json()['owo']
					break
				elif message.author == ctx.author:
					isAfterOP = True

		uwuFaces = ["^~^", "UwU", "OwO", "oWo", "OvO", "UvU", "*~*", ":3", "=3", "<(^V^<)"]

		await ctx.send(content=text + " " + randElement(uwuFaces))

	@bot.command()
	async def smug(ctx):

		url = requestGet(nekoApiUrl + "img/smug").json()['url']

		text = f"**{ctx.author.mention} is being smug**"
		embed = discord.Embed(description = text)
		embed.set_image(url=url)
		embed.set_footer(text="Made with the help of nekos.life")

		await ctx.send(embed=embed)

	@bot.command()
	async def fact(ctx):
		text = requestGet(nekoApiUrl + "fact").json()['fact']
		await ctx.send(content= "`" + text + "`")

	@bot.command()
	async def oof(ctx):
		messages = await ctx.channel.history(limit=5).flatten()
		isAfterOP = False
		for message in messages:
			if isAfterOP:
				#This is the message we want
				await ctx.message.delete()
				await set_message_reactions(message, ["🅾", "🇴", "🇫"])
				break
			elif message.author == ctx.author:
				isAfterOP = True
	
	@bot.command()
	async def rekt(ctx):
		rektMessages = ["REKT",
						"REKTangle",
						"SHREKT",
						"REKT-it Ralph",
						"Total REKTall",
						"The Lord of the REKT",
						"The Usual SusREKTs",
						"North by NorthREKT",
						"REKT to the Future",
						"Once Upon a Time in the REKT",
						"The Good, the Bad, and the REKT",
						"LawREKT of Arabia",
						"Tyrannosaurus REKT",
						"eREKTile dysfunction",
						"Witness ProtREKTion",
						"Doctor REKTopus",
						"Lord of the REKT",
						"Saving Private REKTan",
						"Close Encounters of the REKT kind",
						"The Thousand Year REKT",
						"You have the REKT to remain silent",
						"Better Dead Than REKT",
						"From REKTa With Love",
						"Really REKT",
						"Full mast eREKTion",
						"REKTum",
						"ResurREKT",
						"CorREKT",
						"IndiREKT",
						"Cash4REKT.com",
						"Grapes of REKT",
						"Ship REKT",
						"REKT marks the spot",
						"Caught REKT handed",
						"The REKT Side Story",
						"Singin' In The REKT",
						"Painting The Roses REKT",
						"REKT Van Winkle",
						"Parks and REKT",
						"Lord of the REKTs: The Reking of the King",
						"Star TREKT",
						"The REKT Prince of Bel-Air",
						"A Game of REKT",
						"REKTflix",
						"REKT it like it's hot",
						"REKTBox 360",
						"The REKT-men",
						"School Of REKT",
						"I am Fire, I am REKT",
						"REKT and Roll",
						"Professor REKT",
						"Catcher in the REKT",
						"REKT-22",
						"Harry Potter: The Half-REKT Prince",
						"Great REKTspectations",
						"Paper Scissors REKT",
						"REKTCraft",
						"Grand REKT Auto V",
						"Call of REKT: Modern Reking 2",
						"Legend Of Zelda: Ocarina of REKT",
						"Left 4 REKT",
						"Pokemon: Fire REKT",
						"The Shawshank REKTemption",
						"The REKTfather",
						"The REKT Knight",
						"Fiddler on the REKT",
						"The REKT Files",
						"The Good, the Bad, and The REKT",
						"ForREKT Gump",
						"The Silence of the REKTs",
						"The Green REKT",
						"GladiREKT",
						"SpiREKTed Away",
						"Terminator 2: REKTment Day",
						"The REKT Knight Rises",
						"The REKT King",
						"REKT-E",
						"Citizen REKT",
						"Requiem for a REKT",
						"REKT TO REKT ass to ass",
						"Star Wars: Episode VI - Return of the REKT",
						"BraveREKT",
						"BatREKT Begins",
						"2001: A REKT Odyssey",
						"The Wolf of REKT Street",
						"REKT's Labyrinth",
						"12 Years a REKT",
						"GraviREKT",
						"Finding REKT",
						"The AREKTers",
						"There Will Be REKT",
						"Christopher REKTellston",
						"Hachi: A REKT Tale",
						"The REKT Ultimatum",
						"ShREKT",
						"REKTal Exam",
						"REKTium for a Dream",
						"EREKTile Dysfunction",
						"www.rekkit.com",
						"www.TREKT.tv",
						"2Girls1REKT",
						"16 and REKT",
						"League of REKT",
						"DegREKT",
						"REKTPing",
						"jQREKT",
						"imsoREKT",
						"Silence of the REKT",
						"Wake me up when REKTember ends",
						"REKT-al cancer",
						"reQt",
						"REKTyourcat",
						"REKTunMi",
						"Santa REKTaus",
						"El REKTo",
						"Welcome to the Recktoning",
						"eREKTion",
						"Eat, sleep, REKT, repeat",
						"The REKTtiticaca",
						"topREKT",
						"REKTification",
						"topkREKT",
						"BanREKT",
						"DiREKTX",
						"SwiftREKT",
						"COR REKT",
						"REKT in pieces",
						"50 shades of REKT",
						"BaREKT Obama",
						"No Country For REKT Men",
						"The REKT Age",
						"Star Wars: Knights of the REKT Republic",
						"REKT my potato pc",
						"harry potter and the deathly REKT",
						"e=mREKT²",
						"REKT Kong",
						"R3KT",
						"REKT'Sai",
						"eREKT",
						"REKTacia",
						"Vaginasaurus REKT",
						"Uncaught TypeError: REKT is not a function",
						"Uncaught REKTError: REKT is not defined",
						"MUM GET THE CAMEREKT",
						"misdiREKT",
						"REKT and Morty",
						"It is a truth universally acknowledged, that a REKT man in possession of a REKT fortune, must be in want of a REKT",
						"sudo apt-get REKT",
						"libREKT.so",
						"https://en.wikipedia.org/wiki/List_of_REKT_centers_in_the_United_States",
						"President-EREKT of the United States",
						"We Will We Will REKT You"
						]

		shuffle(rektMessages)
		rektField = f"☑ {rektMessages[0]}"
		for rekt in rektMessages[1:8]:
			rektField += f"\n☑ {rekt}"

		embed = discord.Embed(title="Are you REKT?")

		embed.add_field(name="NOT REKT", value="⬜ Not Rekt", inline=True)
		embed.add_field(name="REKT", value=rektField, inline=True)

		msg = await ctx.send(embed=embed)
		await set_message_reactions(msg, ["☑", "🇷", "🇪", "🇰", "🇹"])

	@bot.command()
	async def dadjoke(ctx):
		r = requestGet("https://icanhazdadjoke.com/", headers = {'Accept': 'application/json'})
		joke = r.json()['joke']
		await ctx.send(content=f"`{joke}`")


#####################################################
#													#
#	 ##     ## ##     ##  ######  ####  ###### 		#
#	 ###   ### ##     ## ##    ##  ##  ##    ##		#
#	 #### #### ##     ## ##        ##  ##      		#
#	 ## ### ## ##     ##  ######   ##  ##      		#
#	 ##     ## ##     ##       ##  ##  ##      		#
#	 ##     ## ##     ## ##    ##  ##  ##    ##		#
#	 ##     ##  #######   ######  ####  ###### 		#
#													#
#####################################################

#Music commands:

	@bot.command(aliases=['join', 'j'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	async def join_(ctx):
		mPlayer = get_player(ctx.guild)
		if ctx.voice_client == None:
			# Bot is not in a channel
			await ctx.message.author.voice.channel.connect()
			mPlayer.downloader.set()

			await asyncio.sleep(1)

			val = getBoolSetting(str(ctx.guild.id), 'nowPlayingAuto')
			if val:
				await now_playing(ctx.guild, ctx.channel, preparing=True, forceSticky=True)

		elif ctx.message.author.voice.channel == ctx.voice_client.channel:
			# Bot is in same channel
			await ctx.send('I\'m already in your channel dummy')
		else:
			# Bot is in another channel
			await ctx.voice_client.move_to(ctx.message.author.voice.channel)

	@bot.command(aliases=['play', 'p'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	async def play_(ctx,  *args):
		if len(args) == 0:
			defaultPlaylist = await getDefaultPlaylist(ctx.guild.id)
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

	@bot.command(aliases=['playnext', 'pnext', 'pn'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	async def playnext_(ctx, *, url):
		if(await join_voice_and_play(ctx)):
			await add_song(ctx, url, play_next=True, stream=False)

	@bot.command(aliases=['playnow', 'pnow'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	@commands.check(is_dj)
	async def playnow_(ctx, *, url):
		if(await join_voice_and_play(ctx)):
			await add_song(ctx, url, play_now=True, stream=False)

	@bot.command(aliases=['stream', 'playstream'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_user_connected)
	@commands.check(is_accepted_voice_channel)
	async def stream_(ctx, *, url):
		if(await join_voice_and_play(ctx)):
			await add_song(ctx, url, stream=True)


	@bot.group(aliases=['playlist', 'pl'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_dj)
	async def playlist_(ctx):
		if ctx.invoked_subcommand is None:
			mPlayer = get_player(ctx.guild)
			defaultPlaylist = await getDefaultPlaylist(ctx.guild.id)
			await bookList(ctx.channel, mPlayer, create_playlist_string, defaultPlaylist, itemsPerPage=10)
	
	@playlist_.command(aliases=['clear'])
	async def clear_playlist(ctx):
		server = str(ctx.guild.id)
		mPlayer = get_player(ctx.guild)
		await update_playlist_json(server, [])
		mPlayer.prepareQueue.default = []
		await ctx.send(f"Default playlist cleared.")

	@playlist_.command(aliases=['add'])
	async def add_to_playlist(ctx, *args):
		server = str(ctx.guild.id)
		mPlayer = get_player(ctx.guild)
		searchOrUrl = " ".join(args)
		if isPlaylist(searchOrUrl): #It's a playlist
			title, url, songs = await get_playlist_info(searchOrUrl)

			data = await getDefaultPlaylist(server)
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
			
			data = await getDefaultPlaylist(server)
			if url in data:
				return await ctx.send(f"That song already exists in the playlist")
		
			await update_playlist_json(server, url, add = True)
			mPlayer.prepareQueue.default.append(url)
			shuffle(mPlayer.prepareQueue.default)

			embed = discord.Embed(title=title, url=url, description=f"have been added to the playlist")
			embed.set_thumbnail(url=thumbnail)
			await ctx.send(embed=embed)

	@playlist_.command(aliases=['remove'])
	async def remove_from_playlist(ctx, *args):
		server = str(ctx.guild.id)
		mPlayer = get_player(ctx.guild)
		searchOrUrl = " ".join(args)
		if isPlaylist(searchOrUrl):
			title, url, songs = await get_playlist_info(searchOrUrl)

			data = await getDefaultPlaylist(server)
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

			data = await getDefaultPlaylist(server)
			if not url in data:
				return await ctx.send(f"That song doesn't exist in the playlist")
				
			await update_playlist_json(server, url, add = False)
			mPlayer.prepareQueue.default.remove(url)

			embed = discord.Embed(title=title, url=url, description=f"have been removed from the playlist")
			embed.set_thumbnail(url=thumbnail)
			await ctx.send(embed=embed)


	@bot.command(aliases=['volume', 'vol', 'v'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def volume_(ctx, *args):
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

	@bot.command(aliases=['shuffle', 'random', 'randomize'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	@commands.check(is_dj)
	async def shuffle_(ctx):
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

	@bot.command(aliases=['pause'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def pause_(ctx):
		mPlayer = get_player(ctx.guild)
		if ctx.voice_client.is_paused():
			await ( await ctx.send("I'm already paused")).delete(delay=10)
			return await ctx.message.delete(delay=10)

		ctx.voice_client.pause()
		mPlayer.timePaused = time.time() - mPlayer.timeStarted
		mPlayer.update_np.set()
		await ctx.message.add_reaction("👌")

	@bot.command(aliases=['resume', 'continue'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def resume_(ctx):
		mPlayer = get_player(ctx.guild)
		if not ctx.voice_client.is_paused():
			await ( await ctx.send("I'm already playing")).delete(delay=10)
			return await ctx.message.delete(delay=10)

		ctx.voice_client.resume()
		mPlayer.timeStarted = time.time() - mPlayer.timePaused
		mPlayer.update_np.set()
		await ctx.message.add_reaction("👌")

	@bot.command(aliases=['skip', 's'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def skip_(ctx):
		vc = ctx.voice_client
		if not vc.is_playing() and not vc.is_paused():
			await ( await ctx.send("There's no song playing")).delete(delay=10)
			return await ctx.message.delete(delay=10)

		await ctx.message.add_reaction("👌")
		vc.source.volume = 0
		vc.stop()

	@bot.command(aliases=['remove', 'r'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	async def remove_(ctx, indexToRemove):
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
		
	@bot.command(aliases=['clear'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	@commands.check(is_dj)
	async def clear_(ctx):
		mPlayer = get_player(ctx.guild)

		mPlayer.prepareQueue.playnow = []
		mPlayer.prepareQueue.playnext = []
		mPlayer.prepareQueue.play = []
		mPlayer.processedQueue = SongQueue()

		await ctx.send("Cleared the queue")

	@bot.command(aliases=['queue', 'q'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	async def queue_(ctx, *args):
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
	async def nowplaying_(ctx):
		if ctx.invoked_subcommand is None:
			if await is_bot_connected(ctx):
				await now_playing(ctx.guild, ctx.channel)

	@nowplaying_.command()
	@commands.check(is_dj)
	async def sticky(ctx):
		#toggle sticking now playing to the bottom
		server = str(ctx.guild.id)
		setting = 'nowPlayingSticky'
		current = getBoolSetting(server, setting)
		await update_settings_json(server, setting, (not current))
		return await ctx.send(f"Toggled Now Playing Sticky to `{not current}`")

	@nowplaying_.command()
	@commands.check(is_dj)
	async def controls(ctx):
		#toggle reaction controls
		server = str(ctx.guild.id)
		setting = 'nowPlayingControls'
		current = getBoolSetting(server, setting)
		await update_settings_json(server, setting, (not current))
		return await ctx.send(f"Toggled Now Playing Controls to `{not current}`")

	@nowplaying_.command()
	@commands.check(is_dj)
	async def auto(ctx):
		#toggle automatically send a nowplaying message when starting the player
		server = str(ctx.guild.id)
		setting = 'nowPlayingAuto'
		current = getBoolSetting(server, setting)
		await update_settings_json(server, setting, (not current))
		return await ctx.send(f"Toggled Now Playing automatically send to `{not current}`")


	@bot.command(aliases=['setdj'])
	@commands.has_permissions(manage_roles=True)
	async def setdj_(ctx, *args):
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

	@bot.command(aliases=['leave', 'disconnect', 'stop'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_bot_connected)
	@commands.check(is_user_connected_to_bot_channel)
	@commands.check(is_dj)
	async def leave_(ctx):
		mPlayer = get_player(ctx.guild)
		mPlayer.stop_player = True
		mPlayer._guild.voice_client.stop()


	@bot.group(aliases=['musictc'])
	@commands.check(is_dj)
	async def musictc_(ctx):
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
	async def clear_tc(ctx):
		server = str(ctx.guild.id)
		await update_settings_json(server, 'acceptedTextChannels', None, clear_list=True)
		await ctx.send(f"I'm now reading commands from all text channels")

	@musictc_.command(aliases=['add'])
	async def add_tc(ctx, channel: Current_or_id_channel(False)):
		server = str(ctx.guild.id)
		accTC = serverSettings[server]['acceptedTextChannels']
		if channel.id in accTC:
			await ctx.send(f"The channel {channel.mention} is already one of the allowed text channels")
		else:
			await update_settings_json(server, 'acceptedTextChannels', channel.id, add_to_list=True)
			await ctx.send(f"I've added {channel.mention} to the allowed text channels")

	@musictc_.command(aliases=['remove'])
	async def remove_tc(ctx, channel: Current_or_id_channel(False)):
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
	async def musicvc_(ctx):
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
	async def clear_vc(ctx):
		server = str(ctx.guild.id)
		await update_settings_json(server, 'acceptedVoiceChannels', [], clear_list=True)
		await ctx.send(f"I can now join any voice channel")

	@musicvc_.command(aliases=['add'])
	async def add_vc(ctx, channel: Current_or_id_channel(True)):
		server = str(ctx.guild.id)
		accVC = serverSettings[server]['acceptedVoiceChannels']
		if channel.id in accVC:
			await ctx.send(f"The channel {channel.mention} is already one of the allowed voice channels")
		else:
			await update_settings_json(server, 'acceptedVoiceChannels', channel.id, add_to_list=True)
			await ctx.send(f"I've added {channel.mention} to the allowed voice channels")

	@musicvc_.command(aliases=['remove'])
	async def remove_vc(ctx, channel: Current_or_id_channel(True)):
		server = str(ctx.guild.id)
		accVC = serverSettings[server]['acceptedVoiceChannels']
		if len(accVC) == 0:
			return await ctx.send(f"The allowed voice channels list is currently empty, I can already join all voice channels")
		if channel.id in accVC:
			await update_settings_json(server, 'acceptedVoiceChannels', channel.id, add_to_list=False)
			await ctx.send(f"I've removed {channel.mention} from the allowed voice channels")
		else:
			await ctx.send(f"That channel is not an allowed voice channel")


	@bot.command(aliases=['download_default_playlist'])
	@commands.check(is_dj)
	async def download_default_playlist_(ctx):
		mPlayer = get_player(ctx.guild)

		server = str(mPlayer._guild.id)
		data = await getDefaultPlaylist(server)
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
		


######################################
#									 #
#	 ########   #######  ########	 #
#	 ##     ## ##     ##    ##   	 #
#	 ##     ## ##     ##    ##   	 #
#	 ########  ##     ##    ##   	 #
#	 ##     ## ##     ##    ##   	 #
#	 ##     ## ##     ##    ##   	 #
#	 ########   #######     ##   	 #
#									 #
######################################

#Bot commands:

	@bot.command()
	@commands.is_owner()
	async def debug(ctx):
		from pprint import pprint
		mPlayer = get_player(ctx.guild)
		print("\n\n")
		for element in dir(mPlayer):
			if "__" in element:
				continue
			print(f"{element}: \t \t{getattr(mPlayer, element)}\n")
	
	@bot.command(aliases=['prefix', 'annaprefix'])
	@commands.check(is_accepted_text_channel)
	@commands.check(is_dj)
	async def prefix_(ctx, *args):
		if len(args) == 0:
			return await ctx.send(f"Current prefix is \"{ await determine_prefix(bot, ctx.message)}\"")

		newPrefix = " ".join(args)
		if newPrefix.isspace():
			return await ctx.send(f"The prefix can not be only spaces")

		server = str(ctx.guild.id)
		await update_settings_json(server, 'prefix', newPrefix)
		await ctx.send(f"Changed prefix to \"{newPrefix}\"")

	@bot.command(aliases=['setpp', 'setprofilepic', 'setprofilepicture'])
	@commands.is_owner()
	async def setprofilepicture_(ctx, url):
		img_data = requestGet(url).content
		with open('profilePic.jpg', 'wb') as handler:
			handler.write(img_data)

		with open('profilePic.jpg', 'rb') as fp:
			await bot.user.edit(avatar=fp.read())

		await ctx.send("New profile picture set, it may take a few seconds for it to update")

	#Discord.py generates its own help command, lets remove that to make our own
	bot.remove_command('help')
	@bot.command(aliases=['help', 'commands'])
	async def help_(ctx, *args):
		argslen = len(args)
		if argslen == 0:
			await helpFunction(ctx)
		elif argslen == 1:
			await helpFunction(ctx, helpCommand=args[0])
		else:
			await ctx.send("Too many arguments")

	@bot.command()
	@commands.is_owner()
	async def shutdown(ctx):
		return await ctx.bot.logout()


#Run

	try:
		bot.run(settings['token'])
	except:
		print("\nWrong token, please make sure the token in the config file is the corrent one\n\n")
