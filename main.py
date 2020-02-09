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

	if exitCode == "update":

		print("\nUpdating...\n")

		gitDir = "./bin/git/cmd/git.exe"

		if not os.path.isdir('.git'):
			raise EnvironmentError("Missing .git folder.")

		# Make sure that we can actually use Git on the command line
		try:
			with open('tmpFile', "w") as outfile:
				subprocess.check_call(f'{gitDir} --version', stdout=outfile)
			if os.path.exists("tmpFile"):
				os.remove("tmpFile")
		except subprocess.CalledProcessError:
			if os.path.exists("tmpFile"):
				os.remove("tmpFile")
			raise EnvironmentError("Couldn't use Git on the CLI. You will need to run 'git pull' yourself.")
			
		#Ignoring changes done to the custom.py file so we don't overwrite it
		subprocess.check_call(f'{gitDir} update-index --assume-unchanged cogs/custom.py')

		try:
			out = subprocess.check_output(f'{gitDir} pull')
			text = out.decode("utf-8")
			print(text)

			if not "Already up to date" in text:
				print("\nUpdate successful! Loading...\n")

		except subprocess.CalledProcessError:
			raise OSError("Could not update the bot. You have modified files that are tracked by Git (e.g the bot\'s source files).\n" +
							"You will need to run 'git pull' yourself or manually update the files.")

		subprocess.call([sys.executable, "main.py", exitCode, channelID ])


	if exitCode == "restart":
		print()
		print("Restarting Bot")
		print("Note: Don't worry if you get an error while the bot is restarting, it's fine")
		print()
		subprocess.call([sys.executable, "main.py", exitCode, channelID])
