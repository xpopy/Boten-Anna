import discord
from discord.ext import commands
import sys

sys.path.append('./cogs')
import utils

class Custom(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	#This is an example command, change the "wave" to whatever you want your command to be, or add a completely new function
	@commands.command()
	async def wave(self, ctx, *, user: discord.Member):
		#Command code goes here
		await utils.tenorAPI(ctx, "anime wave", f"**{ctx.author.mention} waves to {user.mention}**")


def setup(bot):
	bot.add_cog(Custom(bot))
