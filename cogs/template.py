import discord
from discord.ext import commands


class Template(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	"""
	@commands.Cog.listener()
	async def on_ready(self):
		print(f"'{self.__class__.__name__}' loaded")
	"""


	@commands.command()
	async def func(self, ctx):
		await ctx.send("42")

	

def setup(bot):
	bot.add_cog(Template(bot))
