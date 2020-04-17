import asyncio
import os
import sys

from concurrent import futures as concurFuture
from functools import partial
from glob import glob as globglob
from subprocess import PIPE as subprocPIPE
from subprocess import STDOUT as subprocSTDOUT
from subprocess import Popen as subprocPopen

import discord
from youtube_dl import YoutubeDL as youtubeDownloader
from youtube_dl import utils as youtubeUtils

sys.path.append('./cogs')
import utils



ffmpeg_options = {
	'options': '-vn'
}
# Suppress noise about console usage from errors
youtubeUtils.bug_reports_message = lambda: ''
ytdl_format_options = {
	'dump-json': True,
	'limit-rate': "2M",
	'flat-playlist': True,
	'format': 'bestaudio/best',
	'outtmpl': "/music_cache/" + '%(extractor)s-%(id)s.%(ext)s',
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
		loop = loop or asyncio.get_event_loop()
		ytID = getYTid(url)
		existingFiles = globglob(f"./music_cache/youtube-{ytID}.*")
		if existingFiles:
			return cls(discord.FFmpegPCMAudio(existingFiles[0], **ffmpeg_options))

		mPlayer.update_np_downloading.set()
		if not mPlayer.current:
			mPlayer.update_np.set()
			mPlayer.stop_update_np.set()
			

		with concurFuture.ThreadPoolExecutor() as executor:
			to_run = partial(ytdl.extract_info, url, download=not stream)
			data = await loop.run_in_executor(executor, to_run)

		mPlayer.update_np_downloading.clear()
		if not data:
			return None
		
		mPlayer.update_np_normalizing.set()

		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]

		filename = data['url'] if stream else ytdl.prepare_filename(data)	
	
		if not mPlayer.current:
			mPlayer.update_np.set()
			mPlayer.stop_update_np.set()

		if not stream:
			with concurFuture.ThreadPoolExecutor() as executor:
				to_run = partial(normalizeAudio, filename)
				newfilename = await loop.run_in_executor(executor, to_run)
			filename = newfilename

		mPlayer.update_np_normalizing.clear()

		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options))



def setup(bot):
	#Don't actually want to add this as a cog to the bot as it's imported instead
	return True
