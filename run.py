import discord
from discord.ext import commands
from tendo import singleton
import cogs.bot as bot
import json
import sys
import os


#TODO: check if cogs folder exists
	# also check for bot.py and maybe utils.py

if __name__ == "__main__":
	me = singleton.SingleInstance()
	bot.run()

	print("we're back")