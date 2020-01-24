import importlib
import subprocess
import sys

from tendo import singleton

import cogs.bot as bot

if __name__ == "__main__":

	try:
		exitCode = bot.run()
	except Exception as e:
		print(e)

	if exitCode == "restart":
		print("Restarting Bot")
		print()
		subprocess.call([sys.executable, "run.py"])
