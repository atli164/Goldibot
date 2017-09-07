import random
from discord.ext import commands
from fetch_file import fetch_data, write_new_data, write_data

slot_res = [':poop:',':grapes:',':grapes:',':grapes:',':grapes:',':cherries:',':cherries:',':cherries:',':cherries:',':four_leaf_clover:',':four_leaf_clover:',':gem:']

weights = {':poop:':0,':grapes:':10,':cherries:':25,':four_leaf_clover:':40,':gem:':164}

def get_slot():
	res = random.sample(range(12), 3)
	res = [slot_res[k] for k in res]
	return res	

class RNG():
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(pass_context=True)
	async def roll(self, ctx):
		"""Rolls dice.\nTakes input in the format ?roll NdM [s] where N are the number of dice to roll, M is the number of sides on dice and the s is added to obtain the sum of the rolls instead of each individual roll."""
		try:
			command_given = ctx.message.content.split()
			if len(command_given) == 2:
				rolls, limit = map(int, command_given[1].split('d'))
				separate = True
			elif len(command_given) == 3:
				rolls, limit = map(int, command_given[1].split('d'))
				separate = command_given[2] != 's'
			else:
				await self.bot.say('That\'s not valid formatting silly!')
				return
		except Exception:
			await self.bot.say('That\'s not valid formatting silly!')
			return
		if separate:
			result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
			await self.bot.say(result)
		else:
			result = str(sum(random.randint(1, limit) for r in range(rolls)))
			await self.bot.say(result)

	@commands.command(pass_context=True)
	async def crank(self, ctx): # Should cost about 5 points.
		"""Cranks a slot machine. Costs 5 points to play.\nThis command takes no input."""
		curr_p = fetch_data('points_register.txt', ctx.message.author.id)
		if curr_p is None:
			await self.bot.say('Can\'t find you in the register, sorry!')
			return
		if curr_p < 5:
			await self.bot.say('You can\'t afford that silly!')
			return
		outcome = [get_slot(), get_slot(), get_slot()]
		outcome = list(zip(*outcome[::-1]))
		win = 0
		for i in range(3):
			if len(set(outcome[i])) == 1:
				win += weights[outcome[i][0]]
		if outcome[0][0] == outcome[1][1] and outcome[1][1] == outcome[2][2]:
			win += weights[outcome[1][1]]
		if outcome[0][2] == outcome[1][1] and outcome[1][1] == outcome[2][0]:
			win += weights[outcome[1][1]]
		outcome = [' '.join(k) for k in outcome]
		outcome = '\n'.join(outcome)
		await self.bot.say(outcome)
		if win > 0:
			if not write_data('points_register.txt', ctx.message.author.id, curr_p + win - 5):
				await self.bot.say('Point registration failed.')
				return
			await self.bot.say('Congratiulations, you win ' + str(win) + ' points!')
		else:
			if not write_data('points_register.txt', ctx.message.author.id, curr_p - 5):
				await self.bot.say('Point registration failed.')
				return
			await self.bot.say('No points for you, sorry!')

	@commands.command(pass_context=True)
	async def choose(self, ctx):
		"""Makes the bot choose one out of the given options at random. The input is in the form ?choose [option1] [option2] [option3] and so on where the options and the choose command are separated by spaces"""
		try:
			choose_from = ctx.message.content.split()[1:]
		except Exception:
			await self.bot.say('Your input formatting is invalid! (Or I messed up)')
			return
		if not len(choose_from):
			await self.bot.say('You have to give me something to work with here!')
			return
		await self.bot.say('I choose: ' + random.choice(choose_from))

def setup(bot, config):
	bot.add_cog(RNG(bot))
