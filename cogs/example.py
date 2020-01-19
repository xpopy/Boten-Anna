import discord
from discord.ext import commands

class Example(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"'{self.__class__.__name__}' loaded")


	@commands.command()
	async def test2(self, ctx):
		await ctx.send("42")

	

def setup(bot):
	bot.add_cog(Example(bot))