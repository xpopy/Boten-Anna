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

	try:
		exitCode = bot.run()
	except Exception as e:
		print(e)

	if exitCode == "restart":
		print("Restarting Bot")
		print("Note: Don't worry if you get an error while the bot is restarting, it's fine")
		print()
		subprocess.call([sys.executable, "main.py"])
