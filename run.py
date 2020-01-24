import importlib
import subprocess
import sys

from tendo import singleton

import cogs.bot as bot

#TODO: check if cogs folder exists
	# also check for bot.py and maybe utils.py

#TODO: test restart when using pipenv
	#TODO: might have to replace the command and run the run.bat instead

#TODO: !stop doesn't stop the player when preparing a song
#TODO: add a command to limit normalization to either on, only default playlist, or off.
	#TODO: Maybe default to off and only allow creator to allow it on any server they want
#TODO: when restarting and shutting down, make sure to stop all processes

if __name__ == "__main__":

	try:
		exitCode = bot.run()
	except Exception as e:
		print(e)

	if exitCode == "restart":
		print("Restarting Bot")
		print()
		subprocess.call([sys.executable, "run.py"])
