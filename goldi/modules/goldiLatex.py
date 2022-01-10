import os
import sys
from discord.ext import commands
import discord

class LaTeX(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context = True)
	async def latex(self, ctx):
		"""Takes latex equation code and sends an image of the rendered equation into the chat.\nTakes input in the form ?latex equation [w] where equation follows latex equation syntax and adding w at the end forces the background of the equation to be white."""
		formul = ctx.message.content[7:]
		if formul.count('(') != formul.count(')') or formul.count('{') != formul.count('}'):
			await ctx.send('Your message contains unpaired parentheses!')
			return
		if '\\ ' in formul or formul[-1] == '\\':
			await ctx.send('Your message contains rogue backslashes!')
			return
		transparent = True
		if formul[-2:] == ' w':
			formul = formul[:-2]
			transparent = False
		if len(formul) > 100:
			await ctx.send('That\'s too big for me to handle!')
			return
		os.chdir(os.getcwd() + '/data/latex_storage')
		try:
			ecode = os.system('pdflatex -halt-on-error \"\\def\\formula{' + formul + '}\\input{formula.tex}\" > /dev/null')
			if ecode != 0:
				await ctx.send('That\'s not a valid formula!')
				for i in range(4):
					os.chdir('..')
				return
			if transparent:
				os.system('convert -density 300 formula.pdf -quality 90 formula.png')
			else:
				os.system('convert -flatten -density 300 formula.pdf -quality 90 formula.png')
		except Exception:
			await ctx.send('That\'s not a valid formula!')
			for i in range(4):
				os.chdir('..')
			return
		with open('formula.png', 'rb') as handle:
			await ctx.send(file=discord.File('formula.png'))
		for i in range(4):
			os.chdir('..')

def setup(bot, config):
	bot.add_cog(LaTeX(bot))
