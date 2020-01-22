import importlib
import subprocess
import sys

from tendo import singleton

import cogs.bot as bot

#TODO: check if cogs folder exists
	# also check for bot.py and maybe utils.py

#TODO: test restart when using pipenv
	#TODO: might have to replace the command and run the run.bat instead

if __name__ == "__main__":

	exitCode = bot.run()

	if exitCode == "restart":
		print("Restarting Bot")
		print()
		subprocess.call([sys.executable, "run.py"])
