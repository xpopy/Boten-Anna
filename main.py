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

	try:
		exitCode = bot.run()
	except Exception as e:
		print(e)

	if exitCode == "update":

		if not os.path.isdir('.git'):
			raise EnvironmentError("Missing .git folder.")

		# Make sure that we can actually use Git on the command line
		try:
			subprocess.check_call('git --version', shell=True, stdout=subprocess.DEVNULL)
		except subprocess.CalledProcessError:
			raise EnvironmentError("Couldn't use Git on the CLI. You will need to run 'git pull' yourself.")

		print("Passed Git checks...")

		try:
			subprocess.check_call('git pull --assume-unchanged cogs/custom.py', shell=True)
		except subprocess.CalledProcessError:
			raise OSError("Could not update the bot. You have modified files that are tracked by Git (e.g the bot\'s source files).\n" +
							"You will need to run 'git pull' yourself or manually update the files.")

		print("Update successful, restarting...")
		subprocess.call([sys.executable, "main.py"])


	if exitCode == "restart":
		print()
		print("Restarting Bot")
		print("Note: Don't worry if you get an error while the bot is restarting, it's fine")
		print()
		subprocess.call([sys.executable, "main.py"])
