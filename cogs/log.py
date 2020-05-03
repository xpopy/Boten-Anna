from datetime import datetime
from colorama import Fore as color, Style as style, init

init()

green = color.GREEN
white = color.WHITE
red = color.RED
yellow = color.YELLOW
blue = color.BLUE


def currTime():
	return f"{style.DIM}{datetime.now().replace(microsecond=0)}{style.RESET_ALL}{style.NORMAL}"

def text(message = ""):
	print(message)

def command(message, user, server = None ):
	prefix = f"{green}[CMD]{white}"
	if server:
		full_message = f'{green}Server:{white} {server}, {green}User:{white} {user}: {message}'
	else:
		full_message = f'{green}DM{white}, {green}User:{white} {user}: {message}'
	print(f"{prefix} {currTime()}: {full_message}")

def info(message):
	prefix = f"{blue}{style.BRIGHT}[INFO]{white}{style.RESET_ALL}"
	print(f"{prefix} {currTime()}: {message}")

def warning(message):
	prefix = f"{yellow}[WARNING]{white}"
	print(f"{prefix} {currTime()}: {message}")

def error(message):
	prefix = f"{red}[ERROR]{white}"
	print(f"{prefix} {currTime()}: {message}")

def setup(bot):
	#Don't actually want to add this as a cog to the bot as it's imported instead
	return True
