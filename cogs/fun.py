import discord
from discord.ext import commands
from requests import get as requestGet
from urllib import parse as urlParse
from bs4 import BeautifulSoup as bs4Soup
from random import randrange, shuffle, randint, choice as randElement
import wikipedia
import wikipediaapi
import asyncio
import json
import sys

sys.path.append('./cogs')
import utils



def MAL_scrape(term):
	""" Scrapes the MyAnimeList site for animes """
	# Search for term
	query_string = urlParse.urlencode({"q": term})
	text = requestGet("https://myanimelist.net/search/all?" + query_string).text
	soup = bs4Soup(text, features="html.parser")
	
	# Select the first result
	div = soup.select("article")[0]
	url = div.select(".information > a")[0]['href']

	# Go to anime page
	text = requestGet(url).text
	soup = bs4Soup(text, features="html.parser")
	sidebar = soup.select(".borderClass > .js-scrollfix-bottom")[0]

	if not soup.select(".title-english"):
		title = soup.select(".h1-title > span")[0].text
	else:
		title = soup.select(".title-english")[0].text

	score = soup.select(".score")[0].text.replace(" ", "").split("\n")[1]
	status = sidebar.select("span:contains('Status:')")[0].parent.text.split('\n  ')[1]
	aired = sidebar.select("span:contains('Aired:')")[0].parent.text.split('\n  ')[1]
	episodes = sidebar.select("span:contains('Episodes:')")[0].parent.text.split('\n  ')[1]
	genresList = sidebar.select("span:contains('Genres:')")[0].parent.select("a")
	genresList2 = []
	for g in genresList:
		genresList2 += [g.text]
	genres = (", ").join(genresList2)

	thumbnail = sidebar.select("img")[0]['data-src']

	
	description = ""

	if status == "Currently Airing":
		status = "Airing"
	elif status == "Finished Airing":
		status = "Finished"
	if score != "N/A":
		description += f"**Score:** {score} | "
	if episodes != "Unknown":
		description += f"**Episodes:** {episodes} \n "
	
	description += f"**Status:** {status} | **Aired:** {aired} \n"
	description += f"**Genres:** {genres}"

	return title, url, description, thumbnail

def checkHighfive(first_poster, original_channel, prefix):
	def inner_check(message):
		if message.channel == original_channel and f"{prefix}highfive" in message.content:
			return True
		else:
			return False
	return inner_check


class Fun(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=['mal'])
	async def anime(self, ctx, *, searchTerm):
		title, url, description, thumbnail = MAL_scrape(searchTerm)
		embed = discord.Embed(title=title, url=url, description = description)
		embed.set_thumbnail(url=thumbnail)
		await ctx.send(embed=embed)

	@commands.command(aliases=['wikipedia'])
	async def wiki(self, ctx, *, searchTerm):
		# Yes I use both "wikipedia" and "wikipedia-api" apis, deal with it
		wikiTerm = wikipedia.search(searchTerm)[0]
		wiki_search = wikipediaapi.Wikipedia('en')
		r = wiki_search.page(wikiTerm)
		embed = discord.Embed(title="Wikipedia: " + r.title.capitalize(), url=r.fullurl, description = r.summary[0:500] + "...")
		await ctx.send(embed=embed)

	@commands.command(aliases=['flip', 'coin'])
	async def coinflip(self, ctx):
		flip = randint(0, 1)
		if flip:
			await ctx.send(content = "`It's tails!`")
		else:
			await ctx.send(content = "`It's heads!`")

	@commands.command(aliases=['8ball', '8'])
	async def question8ball(self, ctx, *, question: str):
		if question[-1] != "?":
			return await ctx.send(content="That doesn't look like a question, didn't you learn punctuation in school?")
		
		await utils.nekosAPI(ctx, "8ball", None)

	@commands.command()
	async def kiss(self, ctx, *, user: discord.Member):
		if user == ctx.author:
			return await ctx.send(content = f"You can't kiss yourself you dummy")

		await utils.nekosAPI(ctx, "img/kiss", f"**{ctx.author.mention} kisses {user.mention}**")

	@commands.command()
	async def hug(self, ctx, *, user: discord.Member):
		if user == ctx.author:
			await utils.nekosAPI(ctx, "img/hug", f"**{ctx.author.mention} hugs themself**")
		else:
			await utils.nekosAPI(ctx, "img/hug", f"**{ctx.author.mention} hugs {user.mention}**")

	@commands.command()
	async def poke(self, ctx, *, user: discord.Member):
		if user == ctx.author:
			await utils.nekosAPI(ctx, "img/poke", f"**{ctx.author.mention} pokes themself**")
		else:
			await utils.nekosAPI(ctx, "img/poke", f"**{ctx.author.mention} pokes {user.mention}**")

	@commands.command()
	async def feed(self, ctx, *, user: discord.Member):
		if user == ctx.author:
			await utils.nekosAPI(ctx, "img/feed", f"**{ctx.author.mention} feeds themself**")
		else:
			await utils.nekosAPI(ctx, "img/feed", f"**{ctx.author.mention} feeds {user.mention}**")

	@commands.command()
	async def cuddle(self, ctx, *, user: discord.Member):
		if user == ctx.author:
			await utils.nekosAPI(ctx, "img/cuddle", f"**{ctx.author.mention} cuddles themself**")
		else:
			await utils.nekosAPI(ctx, "img/cuddle", f"**{ctx.author.mention} cuddles {user.mention}**")

	@commands.command()
	async def slap(self, ctx, *, user: discord.Member):
		if user == ctx.author:
			await utils.nekosAPI(ctx, "img/slap", f"**{ctx.author.mention} slaps themself**")
		else:
			await utils.nekosAPI(ctx, "img/slap", f"**{ctx.author.mention} slaps {user.mention}**")

	@commands.command()
	async def pat(self, ctx, *, user: discord.Member):
		if user == ctx.author:
			await utils.nekosAPI(ctx, "img/pat", f"**{ctx.author.mention} pats themself**")
		else:
			await utils.nekosAPI(ctx, "img/pat", f"**{ctx.author.mention} pats {user.mention}**")

	@commands.command()
	async def tickle(self, ctx, *, user: discord.Member):
		if user == ctx.author:
			await utils.nekosAPI(ctx, "img/pat", f"**{ctx.author.mention} tickles themself**")
		else:
			await utils.nekosAPI(ctx, "img/pat", f"**{ctx.author.mention} tickles {user.mention}**")

	@commands.command()
	async def lick(self, ctx, *, user: discord.Member):
		if user == ctx.author:
			await utils.tenorAPI(ctx, "anime lick", f"**{ctx.author.mention} licks themself**")
		else:
			await utils.tenorAPI(ctx, "anime lick", f"**{ctx.author.mention} licks {user.mention}**")

	@commands.command()
	async def highfive(self, ctx, *, user: discord.Member = None):
		if user:
			#Highfive another user directly
			if user == ctx.author:
				text = f"**{ctx.author.mention} high fives themself**"
			else:
				text = f"**{ctx.author.mention} high fives {user.mention}**"
		else:
			#This command will be run twice, depending on the content we may want to let the first command do the work
			messages = await ctx.channel.history(limit=5).flatten()
			for i, message in enumerate(messages):
				if message.author == self.bot.user and message.embeds and  "high fives" in message.embeds[0].description:
					break
				elif message.author == self.bot.user and "was left hanging" in message.content:
					break
				elif message.author == self.bot.user and "prepares for a high five" in message.content:
					return
				elif message.content == f"{await utils.determine_prefix(self.bot, ctx.message)}highfive":
					if i == 0:
						continue
					else:
						break

			msg = await ctx.send(content=f"{ctx.author.mention} prepares for a high five")

			try:
				message = await self.bot.wait_for('message', check=checkHighfive(ctx.author, msg.channel, await utils.determine_prefix(self.bot, message)), timeout=5.0)

			except asyncio.TimeoutError:
				return await ctx.send(content=f"{ctx.author.mention} wanted to high five but was left hanging...")

			else:
				if message.content == f"{await utils.determine_prefix(self.bot, ctx.message)}highfive {ctx.author.mention}":
					#Someone highfived back directly to the original poster, just let the other command do the work
					return
				if message.content == f"{await utils.determine_prefix(self.bot, ctx.message)}highfive":
					if message.author == ctx.author:
						return await ctx.send(content=f"{ctx.author.mention} was left hanging so they tried to save it by high fiving themselfs... feelsbadman")
					else:
						text = f"**{message.author.mention} high fives {ctx.author.mention}**"
						
		#High five text is done, time to get the gif and post it
		await utils.tenorAPI(ctx, "anime highfive", text)

	@commands.command()
	async def dab(self, ctx):
		await utils.tenorAPI(ctx, "anime dab", f"**{ctx.author.mention} dabs**")

	@commands.command()
	async def flex(self, ctx):
		await utils.tenorAPI(ctx, "anime flex", f"**{ctx.author.mention} flexes**")

	@commands.command()
	async def cry(self, ctx):
		await utils.tenorAPI(ctx, "anime cry", f"**{ctx.author.mention} cries**")

	@commands.command(aliases=["owo"])
	async def uwu(self, ctx, *, message = None):
		await utils.nekosAPI(ctx, "uwu", message)

	@commands.command()
	async def smug(self, ctx):
		await utils.nekosAPI(ctx, "img/smug", f"**{ctx.author.mention} is being smug**")

	@commands.command()
	async def fact(self, ctx):
		await utils.nekosAPI(ctx, "fact", None)

	@commands.command()
	async def oof(self, ctx):
		messages = await ctx.channel.history(limit=5).flatten()
		isAfterOP = False
		for message in messages:
			if isAfterOP:
				#This is the message we want
				await ctx.message.delete()
				await utils.set_message_reactions(message, ["🅾", "🇴", "🇫"])
				break
			elif message.author == ctx.author:
				isAfterOP = True

	@commands.command()
	async def rekt(self, ctx):
		rektMessages = ["REKT",
						"REKTangle",
						"SHREKT",
						"REKT-it Ralph",
						"Total REKTall",
						"The Lord of the REKT",
						"The Usual SusREKTs",
						"North by NorthREKT",
						"REKT to the Future",
						"Once Upon a Time in the REKT",
						"The Good, the Bad, and the REKT",
						"LawREKT of Arabia",
						"Tyrannosaurus REKT",
						"eREKTile dysfunction",
						"Witness ProtREKTion",
						"Doctor REKTopus",
						"Lord of the REKT",
						"Saving Private REKTan",
						"Close Encounters of the REKT kind",
						"The Thousand Year REKT",
						"You have the REKT to remain silent",
						"Better Dead Than REKT",
						"From REKTa With Love",
						"Really REKT",
						"Full mast eREKTion",
						"REKTum",
						"ResurREKT",
						"CorREKT",
						"IndiREKT",
						"Cash4REKT.com",
						"Grapes of REKT",
						"Ship REKT",
						"REKT marks the spot",
						"Caught REKT handed",
						"The REKT Side Story",
						"Singin' In The REKT",
						"Painting The Roses REKT",
						"REKT Van Winkle",
						"Parks and REKT",
						"Lord of the REKTs: The Reking of the King",
						"Star TREKT",
						"The REKT Prince of Bel-Air",
						"A Game of REKT",
						"REKTflix",
						"REKT it like it's hot",
						"REKTBox 360",
						"The REKT-men",
						"School Of REKT",
						"I am Fire, I am REKT",
						"REKT and Roll",
						"Professor REKT",
						"Catcher in the REKT",
						"REKT-22",
						"Harry Potter: The Half-REKT Prince",
						"Great REKTspectations",
						"Paper Scissors REKT",
						"REKTCraft",
						"Grand REKT Auto V",
						"Call of REKT: Modern Reking 2",
						"Legend Of Zelda: Ocarina of REKT",
						"Left 4 REKT",
						"Pokemon: Fire REKT",
						"The Shawshank REKTemption",
						"The REKTfather",
						"The REKT Knight",
						"Fiddler on the REKT",
						"The REKT Files",
						"The Good, the Bad, and The REKT",
						"ForREKT Gump",
						"The Silence of the REKTs",
						"The Green REKT",
						"GladiREKT",
						"SpiREKTed Away",
						"Terminator 2: REKTment Day",
						"The REKT Knight Rises",
						"The REKT King",
						"REKT-E",
						"Citizen REKT",
						"Requiem for a REKT",
						"REKT TO REKT ass to ass",
						"Star Wars: Episode VI - Return of the REKT",
						"BraveREKT",
						"BatREKT Begins",
						"2001: A REKT Odyssey",
						"The Wolf of REKT Street",
						"REKT's Labyrinth",
						"12 Years a REKT",
						"GraviREKT",
						"Finding REKT",
						"The AREKTers",
						"There Will Be REKT",
						"Christopher REKTellston",
						"Hachi: A REKT Tale",
						"The REKT Ultimatum",
						"ShREKT",
						"REKTal Exam",
						"REKTium for a Dream",
						"EREKTile Dysfunction",
						"www.rekkit.com",
						"www.TREKT.tv",
						"2Girls1REKT",
						"16 and REKT",
						"League of REKT",
						"DegREKT",
						"REKTPing",
						"jQREKT",
						"imsoREKT",
						"Silence of the REKT",
						"Wake me up when REKTember ends",
						"REKT-al cancer",
						"reQt",
						"REKTyourcat",
						"REKTunMi",
						"Santa REKTaus",
						"El REKTo",
						"Welcome to the Recktoning",
						"eREKTion",
						"Eat, sleep, REKT, repeat",
						"The REKTtiticaca",
						"topREKT",
						"REKTification",
						"topkREKT",
						"BanREKT",
						"DiREKTX",
						"SwiftREKT",
						"COR REKT",
						"REKT in pieces",
						"50 shades of REKT",
						"BaREKT Obama",
						"No Country For REKT Men",
						"The REKT Age",
						"Star Wars: Knights of the REKT Republic",
						"REKT my potato pc",
						"harry potter and the deathly REKT",
						"e=mREKT²",
						"REKT Kong",
						"R3KT",
						"REKT'Sai",
						"eREKT",
						"REKTacia",
						"Vaginasaurus REKT",
						"Uncaught TypeError: REKT is not a function",
						"Uncaught REKTError: REKT is not defined",
						"MUM GET THE CAMEREKT",
						"misdiREKT",
						"REKT and Morty",
						"It is a truth universally acknowledged, that a REKT man in possession of a REKT fortune, must be in want of a REKT",
						"sudo apt-get REKT",
						"libREKT.so",
						"https://en.wikipedia.org/wiki/List_of_REKT_centers_in_the_United_States",
						"President-EREKT of the United States",
						"We Will We Will REKT You"
						]

		shuffle(rektMessages)
		rektField = f"☑ {rektMessages[0]}"
		for rekt in rektMessages[1:8]:
			rektField += f"\n☑ {rekt}"

		embed = discord.Embed(title="Are you REKT?")

		embed.add_field(name="NOT REKT", value="⬜ Not Rekt", inline=True)
		embed.add_field(name="REKT", value=rektField, inline=True)

		msg = await ctx.send(embed=embed)
		await utils.set_message_reactions(msg, ["☑", "🇷", "🇪", "🇰", "🇹"])

	@commands.command()
	async def dadjoke(self, ctx):
		r = requestGet("https://icanhazdadjoke.com/", headers = {'Accept': 'application/json'})
		joke = r.json()['joke']
		await ctx.send(content=f"`{joke}`")




def setup(bot):
	bot.add_cog(Fun(bot))