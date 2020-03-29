import importlib
import subprocess
import sys
import os


if not os.path.exists('./cogs') or not os.path.exists('./cogs/bot.py') or not os.path.exists('./cogs/utils.py'):
	print()
	print("Missing important files, please reinstall and read the installation instructions")
	print()
	exit()

import cogs.bot as bot

if __name__ == "__main__":
	
	#Add ffmpeg to PATH
	os.environ['PATH'] += ';' + os.path.abspath('bin/')
	sys.path.append(os.path.abspath('bin/'))

	action = None
	channelID = None

	if len(sys.argv) == 3:
		action = sys.argv[1]
		channelID = sys.argv[2]

	try:
		exitCode, channelID = bot.run(action, channelID)
	except Exception as e:
		print(e)

	if exitCode == "restart":
		print()
		print("Restarting Bot")
		print("Note: Don't worry if you get an error while the bot is restarting, it's fine")
		print()
		subprocess.call(["Run.bat", exitCode, channelID])
