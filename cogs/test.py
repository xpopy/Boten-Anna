import discord
from discord.ext import commands
import sys

sys.path.append('./cogs')
import utils

class Test(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"'{self.__class__.__name__}' loaded")


	@commands.command()
	async def tesawdt(self, ctx):
		await ctx.send("42")



	

def setup(bot):
	bot.add_cog(Test(bot))