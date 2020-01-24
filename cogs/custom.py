import discord
from discord.ext import commands


class Custom(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	#This is an example command, change the "exampleFunction" to whatever you want your command to be 
	@commands.command()
	async def exampleFunction(self,  ctx, *, user: discord.Member):
		#Command code goes here
		await ctx.send(f"Hello {user.mention}")


def setup(bot):
	bot.add_cog(Custom(bot))
