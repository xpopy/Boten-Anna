import importlib
import subprocess
import sys
import os
import cogs.log as log


if not os.path.exists('./cogs') or not os.path.exists('./cogs/bot.py') or not os.path.exists('./cogs/utils.py'):
	log.text()
	log.error("Missing important files, please reinstall and read the installation instructions")
	log.text()
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
		if action:
			exitCode, channelID = bot.run(action, channelID)
		else:
			exitCode, channelID = bot.run()
	except Exception as e:
		log.error(e)

	if exitCode == "restart":
		log.text()
		log.info("Restarting Bot")
		log.text("Note: Don't worry if you get an error while the bot is restarting, it's fine")
		log.text()
		exitCodeFile = open("exitCode.tmp","w+")
		exitCodeFile.write(exitCode + "\n")
		exitCodeFile.write(channelID)
		exitCodeFile.close()
