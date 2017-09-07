import datetime
from discord.ext import commands

class Calendar():
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command()
	async def time(self):
		"""Tells the current date and time.\nThis command takes no input."""
		weeks = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
		months = ['January','February','March','April','May','June','July','August','September','October','November','December']
		now = datetime.datetime.now()
		to_say = 'The current time is ' + str(now.hour) + ':' + str(now.minute) + ':'
		to_say += str(now.second) + ', the date is ' + weeks[now.weekday()]
		to_say += ' the ' + str(now.day)
		if now.day == 1:
			to_say += 'st'
		elif now.day == 2:
			to_say += 'nd'
		elif now.day == 3:
			to_say += 'rd'
		else:
			to_say += 'th'
		to_say += ' of ' + months[now.month] + ', ' + str(now.year) + '.'
		await self.bot.say(to_say)

def setup(bot, config):
	bot.add_cog(Calendar(bot))
