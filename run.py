from tendo import singleton
import subprocess
import sys
import importlib
import cogs.bot as bot


#TODO: check if cogs folder exists
	# also check for bot.py and maybe utils.py

#TODO: test restart when using pipenv

if __name__ == "__main__":
#	me = singleton.SingleInstance()

	exitCode = bot.run()

	if exitCode == "restart":
		print("Restarting Bot")
		print()
		subprocess.call([sys.executable, "run.py"])

