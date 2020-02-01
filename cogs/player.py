import asyncio
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from random import shuffle

import discord
from async_timeout import timeout
from discord.utils import get

sys.path.append('./cogs')
import utils
import ytdl



time_to_wait_between_songs = 0
max_processed_songs = 3
time_wait_diconnect_emtpy_playlist = 300



def is_connected_player(mPlayer):
	voice_client = get(mPlayer.bot.voice_clients, guild=mPlayer._guild)
	return voice_client and voice_client.is_connected()

def datetime_from_utc_to_local(utc_datetime):
	now_timestamp = time.time()
	offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
	return utc_datetime + offset



@dataclass
class Song:
	''' Class for storing info about a song '''
	title: str
	url: str
	thumbnail: str 
	duration: int
	requester: int
	playnext: bool = False #optional, only set for playnext
	source: ytdl.YTDLSource = None # Optional, a player that will added later

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

		self.volume = utils.getServerSetting(guild.id, "volume")

		self.update_np.clear()
		self.stop_update_np.clear()
		self.downloader.clear()
		self.playNext.clear()
		bot.loop.create_task(self.update_now_playing())
		bot.loop.create_task(self.player_loop())
		bot.loop.create_task(self.downloader_loop())

	async def add_song(self, ctx, url, stream=False, play_next=False, play_now=False):
		async with ctx.typing():
			try:
				url = parseYTurl(url)
			except:
				None
			
			if utils.isPlaylist(url):
				if True:
					await ( await ctx.send(f"Playlists aren't implemented yet sorry! Please add a playlist to the default playlist instead")).delete(delay=15)
					await ctx.message.delete(delay=15)
					return
				else:
					if play_next or play_now:
						await ( await ctx.send(f"Can't play a playlist using playnow or playnext, sorry!")).delete(delay=15)
						await ctx.message.delete(delay=15)
						return
					
					title, url, songs = await utils.get_playlist_info(url)
					self.prepareQueue.play = self.prepareQueue.play + songs
					self.downloader.set()
					embed = discord.Embed(title=title, url=url, description=f"[{len(songs)} queued]")
					await ctx.send(embed=embed)

			else:
				title, url, thumbnail, duration = await utils.get_song_data(url)

				songObj = Song(title=title, url=url, thumbnail=thumbnail, duration=duration, requester=ctx.author.mention)

				if play_next:
					songObj.playnext = True
					self.prepareQueue.playnext.append(songObj)
					self.downloader.set()

					embed = discord.Embed(title=title, url=url, description=f"Queued **#1**, `[{utils.convert_seconds(duration)}]`")
					embed.set_thumbnail(url=thumbnail)
					await ctx.send(embed=embed)

				elif play_now:
					songObj.playnext = True
					self.prepareQueue.playnow.append(songObj)
					self.downloader.set()
					
					val = utils.getServerSetting(self._guild.id, 'nowPlayingAuto')
					if val:
						await self.now_playing(ctx.channel, preparing=True)
					else:
						embed = discord.Embed(title=title, url=url, description=f"`[{utils.convert_seconds(duration)}]`")
						embed.set_thumbnail(url=thumbnail)
						await ctx.send(embed=embed)

				elif self.current != None:
					self.prepareQueue.play.append(songObj)
					self.downloader.set()

					embed = discord.Embed(title=title, url=url, description=f"Queued **#{self.getQueuedAmount(procDefault = False, prepareDefault = False)}**, `[{utils.convert_seconds(duration)}]`")
					embed.set_thumbnail(url=thumbnail)
					await ctx.send(embed=embed)

				else:
					self.prepareQueue.play.append(songObj)
					self.downloader.set()
					
					val = utils.getServerSetting(self._guild.id, 'nowPlayingAuto')
					if val:
						await self.now_playing(ctx.channel)
					else:
						embed = discord.Embed(title=title, url=url, description=f"`[{utils.convert_seconds(duration)}]`")
						embed.set_thumbnail(url=thumbnail)
						await ctx.send(embed=embed)
	async def now_playing(self, channel=None, preparing=False, dontSticky = False, forceSticky = False):
		currentPlayer = self.current
		msg = self.current_np_message

		if preparing:
			if self.getQueuedAmount(procDefault = True, prepareDefault = False) > 0:
				nextSong = self.getQueueList(procDefault = True, prepareDefault = True)[0]
				embed = discord.Embed(title=nextSong.title, url=nextSong.url, description="Preparing song...")
			else:
				embed = discord.Embed(description="Preparing song...")

			if msg and not forceSticky:
				await msg.edit(embed=embed)
				await utils.set_message_reactions(msg, [])
			else:
				message = await channel.send(content="Now playing:", embed=embed)
				self.current_np_message = message
				self.stop_update_np.set()
			return

		if currentPlayer == None:
			if self._guild.voice_client == None:
				embed = discord.Embed(title="Player stopped")
			elif self.getQueuedAmount(procDefault = True, prepareDefault = True) > 0:
				if self.getQueuedAmount(procDefault = True, prepareDefault = False) > 0:
					nextSong = self.getQueueList(procDefault = True, prepareDefault = False)[0]
					if self.update_np_downloading.is_set():
						embed = discord.Embed(title=nextSong.title, url=nextSong.url, description="Downloading song...")
					elif self.update_np_normalizing.is_set():
						embed = discord.Embed(title=nextSong.title, url=nextSong.url, description="Normalizing song volume...")
					else:
						embed = discord.Embed(title=nextSong.title, url=nextSong.url, description="Preparing song...")
				else:
					embed = discord.Embed(description="Preparing song...")
			else:
				embed = discord.Embed(description="There's no song playing")
			if msg:
				await msg.edit(embed=embed)
				await utils.set_message_reactions(msg, [])
			else:
				message = await channel.send(content="Now playing:", embed=embed)
				self.current_np_message = message
				self.stop_update_np.set()
			return

		sticky = utils.getServerSetting(self._guild.id, 'nowPlayingSticky')
		if (not forceSticky) and ( (dontSticky) or (not sticky) or (msg and msg.channel.last_message_id == msg.id) ):
			em =  msg.embeds[0].description
			description = utils.create_progressbar(self.timePaused,
											self.timeStarted,
											currentPlayer.duration,
											self._guild.voice_client.is_paused())

			embed = discord.Embed(title=currentPlayer.title, url=currentPlayer.url, description=description)
			await msg.edit(embed=embed)
			controls = utils.getServerSetting(self._guild.id, 'nowPlayingControls')
			if not controls:
				await utils.set_message_reactions(msg, [])
			elif em == "There's no song playing" or em == "Preparing song..." or em == "Downloading song..."  or em == "Normalizing song volume..." :
				await utils.set_message_reactions(msg, ["⏯️", "⏭️", "🔉", "🔊"])
		else:
			if msg:
				channel = msg.channel
			
			content = "Now playing:"
			
			description = utils.create_progressbar(self.timePaused,
											self.timeStarted,
											currentPlayer.duration,
											self._guild.voice_client.is_paused())

			embed = discord.Embed(title=currentPlayer.title, url=currentPlayer.url, description=description)
			if msg:
				await msg.delete()
			message = await channel.send(content=content, embed=embed)
			self.current_np_message = message
			if not msg:
				self.stop_update_np.set()
			controls = utils.getServerSetting(self._guild.id, 'nowPlayingControls')
			if controls:
				await utils.set_message_reactions(message, ["⏯️", "⏭️", "🔉", "🔊"])
			else:
				await utils.set_message_reactions(message, [])
	async def setVolume(self, newVolume):
		self.volume = newVolume
		vc = self._guild.voice_client
		if vc != None and vc.source != None:
			vc.source.volume = newVolume
		utils.updateServerSettings(self._guild.id, 'volume', float(newVolume))
	def getQueuedAmount(self, procDefault = True, prepareDefault = False):
		amount = 0

		if procDefault:
			amount += len(self.processedQueue)
		else:
			amount += len(self.processedQueue.getQueue())
		
		if prepareDefault:
			amount += len(self.prepareQueue)
		else: 
			amount += len(self.prepareQueue.getQueue())
		return amount
	def getQueueList(self, procDefault = False, prepareDefault = False):
		queueList = []
		queueList += self.processedQueue.playnow
		queueList += self.prepareQueue.playnow
		queueList += self.processedQueue.playnext
		queueList += self.prepareQueue.playnext
		queueList += self.processedQueue.play
		queueList += self.prepareQueue.play
		if procDefault:
			queueList += self.processedQueue.default
		if prepareDefault:
			queueList += self.prepareQueue.default
		return queueList
	def wakeUpPlayer(self):
		if (not self.current) and self._guild.voice_client:
			self.playNext.set()
	async def update_now_playing(self):
		"""update "Now Playing" loop"""
		await self.bot.wait_until_ready()
		while not self.bot.is_closed():
			try:
				await self.stop_update_np.wait()
				try:
					async with timeout(5):
						await self.update_np.wait()
						self.update_np.clear()

				except asyncio.exceptions.CancelledError:
					pass
				except asyncio.exceptions.TimeoutError:
					if self.current_np_message:
						message = (await self.current_np_message.channel.history(limit=1).flatten())[0]

						localTimezoneCreatedAt = datetime_from_utc_to_local(message.created_at)
						if (time.time() - localTimezoneCreatedAt.timestamp()) < 10:
							await self.stop_update_np.wait()
							await self.now_playing(dontSticky = True)
						else:
							await self.stop_update_np.wait()
							await self.now_playing()
				else:
					await self.stop_update_np.wait()
					await self.now_playing()
				if self.current == None and self.getQueuedAmount( procDefault = True, prepareDefault = True) == 0:
					self.stop_update_np.clear()
			except:
				pass
	async def downloader_loop(self):
		await self.bot.wait_until_ready()
		await self.downloader.wait()
		self.downloader.clear()

		while not self.bot.is_closed():
			try:
				if not is_connected_player(self):
					if self.stop_player:
						await self.destroy(self._guild) 
					await self.downloader.wait()
					self.downloader.clear()

				#print("checking for something to download")
				if self.prepareQueue.playnow:
					#print("downloading playnow")
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
					#print("downloading playnext")
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
						#print("downloading song")
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
							#print("downloading from default playlist")
							url = self.prepareQueue.default[0]
							self.prepareQueue.default = self.prepareQueue.default[1:] + self.prepareQueue.default[:1]
							songObj = Song(title="temp", url=url,
											thumbnail="temp",
											duration=None,
											requester=None)
							await self.prepareYTSource(songObj)
							if not songObj.source:
								continue
							title, url, thumbnail, duration = await utils.get_song_data(url)
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
							data = utils.getServerPlaylist(server)
							if data:
								#print("preparing default playlist")
								newList = []
								for link in data:
									if "playlist?list=" in link:
										_, _, links = await utils.get_playlist_info(link)
										newList = newList + links
									else:
										newList.append(link)

								if not is_connected_player(self):
									continue
								self.prepareQueue.default = newList
								shuffle(self.prepareQueue.default)
								continue

							else:
								#print("nothing to download, waiting")
								await self.downloader.wait()
								self.downloader.clear()
					else:
						#print("filled queue, waiting")
						await self.downloader.wait()
						self.downloader.clear()
				else:
					#print("filled queue, waiting")
					await self.downloader.wait()
					self.downloader.clear()

				await asyncio.sleep(2)
			except:
				pass
	async def player_loop(self):
		"""main player loop."""
		await self.bot.wait_until_ready()
		while not self.bot.is_closed():
			try:
				await self.playNext.wait()
				self.playNext.clear()


				# Wait for the next song. If we timeout cancel the player and disconnect
				try:
					async with timeout(time_wait_diconnect_emtpy_playlist):
						while(True):
							if self.stop_player:
								await self.destroy(self._guild) 
								await self.playNext.wait()
								self.playNext.clear()
							elif self.processedQueue.playnow:
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
			except:
				pass
	async def prepareYTSource(self, songObj):
		for song in list(self.processedQueue) + ([self.current] if self.current else []):
			if song.url == songObj.url:
				#Song is already in queue, no need to download it again so just duplicate the object
				songObj.source = song.source
				return
		try:
			songObj.source = await ytdl.YTDLSource.from_url(self, songObj.url, loop=self.bot.loop, stream=False)
		except:
			pass

	async def destroy(self, guild):
		"""Disconnect and cleanup the player."""
		if guild.voice_client:
			guild.voice_client.stop()
			await guild.voice_client.disconnect()
		self.current = None
		self.stop_player = False
		self.prepareQueue = SongQueue()
		self.processedQueue = SongQueue()
		self.stop_update_np.set()
		#remove_player(guild)


def setup(bot):
	#Don't actually want to add this as a cog to the bot as it's imported through music.py
	return True
