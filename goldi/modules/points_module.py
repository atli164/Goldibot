import random
import datetime
from discord.ext import commands
from fetch_file import fetch_data, write_new_data, write_data

class Points():
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def newpointentry(self, ctx):
		"""Creates an entry for a user in the points register so they can use the other point-related commands.\nThis command takes no input."""
		tmp_str = '{0.mention}'.format(ctx.message.author)
		if write_new_data('points_register.txt', ctx.message.author.id, 0):
			await self.bot.say(tmp_str + ' has been added to the points register!')
		else:
			await self.bot.say('Data writing failed. My guess is ' + tmp_str + ' is in the register already.')

	@commands.command(pass_context=True)
	async def haxpoints(self, ctx):
		"""Gives points to a user. Only usable by Goldilocks. Admin abuse at its best.\nTakesinput in the form ?haxpoints recipient_user_id points_to_add."""
		if ctx.message.author.id != str(249293986349580290):
			await self.bot.say('Only my maker can hax!')
			return
		try:
			user_id = ctx.message.content.split()[1]
			point_num = int(ctx.message.content.split()[2])
		except Exception:
			await self.bot.say('Give the input in an acceptable format you dingus!')
			return
		old_points = fetch_data('points_register.txt', ctx.message.author.id)
		if old_points is None:
			await self.bot.say('Coudln\'t find this user in the register!')
			return
		if write_data('points_register.txt', user_id, old_points + point_num):
			await self.bot.say('Haxing complete.')
		else:
			await self.bot.say('Writing data failed, sorry!')

	@commands.command(pass_context=True)
	async def mypoints(self, ctx):
		"""Tells a user their number of points.\nThis command takes no input."""
		tmp_str = '{0.mention}'.format(ctx.message.author)
		point_num = fetch_data('points_register.txt', ctx.message.author.id)
		if point_num is None:
			await self.bot.say('Couldn\'t find ' + tmp_str + ' in the register!')
			return
		if point_num == 1:
			await self.bot.say(tmp_str + ' has 1 point.')
		else:
			await self.bot.say(tmp_str + ' has ' + str(point_num) + ' points.')

	@commands.command(pass_context=True)
	async def claimpoints(self, ctx):
		"""Lets a user claim 10 points per day.\nThis command takes no input."""
		tmp_str = '{0.mention}'.format(ctx.message.author)
		now = datetime.date.today()
		last_t = fetch_data('last_claimed.txt', ctx.message.author.id)
		old_points = fetch_data('points_register.txt', ctx.message.author.id)
		if old_points is None:
			await self.bot.say('Coudln\'t find ' + tmp_str + ' in the register!')
			return
		if last_t is None:
			if not write_new_data('last_claimed.txt', ctx.message.author.id, now):
				await self.bot.say('Time data reading/writing failed, sorry!')
				return
			timediff = 1
		else:
			if not write_data('last_claimed.txt', ctx.message.author.id, now):
				await self.bot.say('Time data reading/writing failed, sorry!')
				return
			timediff = (now-last_t).days
		timediff = max(0, timediff)
		timediff = min(5, timediff)
		if timediff == 0:
			await self.bot.say('You already claimed your points today ' + tmp_str + '!')
			return
		if not write_data('points_register.txt', ctx.message.author.id, old_points + 10 * timediff):
			await self.bot.say('Point data reading/wrinting failed, sorry!')
			return
		await self.bot.say('Enjoy your ' + str(timediff * 10) + ' points ' + tmp_str + '!')

	@commands.command(pass_context=True)
	async def bet(self, ctx):
		"""Lets a user bet points in hopes of getting more. This is almost a zero-sum game, it only rounds down to the nearest whole number away from a zero-sum game.\nTakes input in the form ?bet points_to_bet odds_to_win:odds_to_lose."""
		curr_points = fetch_data('points_register.txt', ctx.message.author.id)
		if curr_points is None:
			await self.bot.say('Point data reading/writing failed, sorry!')
			return
		tmp_str = '{0.mention}'.format(ctx.message.author)
		try:
			wager = int(ctx.message.content.split()[1])
			o1, o2 = map(int, ctx.message.content.split()[2].split(':'))
		except Exception:
			await self.bot.say('Give the input in an orderly format silly!')
			return
		if wager <= 0 or o1 <= 0 or o2 <= 0:
			await self.bot.say('Give the input in an orderly format silly!')
			return
		if wager > curr_points:
			await self.bot.say('You don\'t have that many points!')
			return
		if o1 > 1000 or o2 > 1000:
			await self.bot.say('I\'m not ready to take a bet that big!')
			return
		res = random.randint(1, o1 + o2)
		if res <= o1:
			gain = o2 * wager // o1
			if not write_data('points_register.txt', ctx.message.author.id, curr_points + gain):
				await self.bot.say('Point data reading/writing failed, sorry!')
				return
			if gain == 1:
				await self.bot.say('Yay! You win 1 point!')
			else:
				await self.bot.say('Yay! You win ' + str(gain) + ' points!')
		else:
			if not write_data('points_register.txt', ctx.message.author.id, curr_points - wager):
				await self.bot.say('Point data reading/writing failed, sorry!')
				return
			if wager == 1:
				await self.bot.say('Oh no! You lost 1 point!')
			else:
				await self.bot.say('Oh no! You lost ' + str(wager) + ' points!')	

def setup(bot, config):
	bot.add_cog(Points(bot))
