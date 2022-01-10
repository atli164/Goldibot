import random
import datetime
from discord.ext import commands
from goldiIO import write_data, fetch_data

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def newpointentry(self, ctx):
        """Creates an entry for a user in the points register so they can use the other point-related commands.\nThis command takes no input."""
        tmp = '{0.mention}'.format(ctx.message.author)
        if fetch_data('points_register', ctx.message.author.id) is not None:
            await ctx.send(tmp + 'is already in the register!')
        elif write_data('points_register', ctx.message.author.id, 0):
            await ctx.send(tmp + ' has been added to the points register!')
        else:
            await ctx.send('Data writing failed.')

    @commands.command(pass_context=True)
    async def haxpoints(self, ctx):
        """Gives points to a user. Only usable by Goldilocks. Admin abuse at its best.\nTakes input in the form ?haxpoints recipient_user_id points_to_add."""
        if ctx.message.author.id != str(249293986349580290):
            await ctx.send('Only my maker can hax!')
            return
        try:
            userId = ctx.message.content.split()[1]
            pointNum = int(ctx.message.content.split()[2])
        except Exception:
            await ctx.send('Give the input in an acceptable format you dingus!')
            return
        if fetch_data('points_register', ctx.message.author.id) is None:
            await ctx.send('Coudln\'t find this user in the register!')
            return
        if write_data('points_register', userId, oldPoints + pointNum):
            await ctx.send('Haxing complete.')
        else:
            await ctx.send('Writing data failed, sorry!')

    @commands.command(pass_context=True)
    async def mypoints(self, ctx):
        """Tells a user their number of points.\nThis command takes no input."""
        tmp = '{0.mention}'.format(ctx.message.author)
        pointNum = fetch_data('points_register', ctx.message.author.id)
        if pointNum is None:
            await ctx.send('Couldn\'t find ' + tmp + ' in the register!')
            return
        if pointNum == 1:
            await ctx.send(tmp + ' has 1 point.')
        else:
            await ctx.send(tmp + ' has ' + str(pointNum) + ' points.')

    @commands.command(pass_context=True)
    async def claimpoints(self, ctx):
        """Lets a user claim 10 points per day.\nThis command takes no input."""
        tmp = '{0.mention}'.format(ctx.message.author)
        now = datetime.date.today()
        lastStr = fetch_data('last_claimed', ctx.message.author.id)
        oldPoints = fetch_data('points_register', ctx.message.author.id)
        if oldPoints is None:
            await ctx.send('Coudln\'t find ' + tmp + ' in the register!')
            return
        if lastStr is None:
            if not write_data('last_claimed', ctx.message.author.id, str(now)):
                await ctx.send('Time data reading/writing failed, sorry!')
                return
            dt = 1
        else:
            lastArg = list(map(int, lastStr.split('-')))
            lastT = datetime.date(lastArg[0], lastArg[1], lastArg[2])
            if not write_data('last_claimed', ctx.message.author.id, str(now)):
                await ctx.send('Time data reading/writing failed, sorry!')
                return
            dt = (now - lastT).days
        dt = max(0, dt)
        dt = min(5, dt)
        if dt == 0:
            await ctx.send('You already claimed your points today ' + tmp + '!')
            return
        if not write_data('points_register', ctx.message.author.id, oldPoints + 10 * dt):
            await ctx.send('Point data reading/wrinting failed, sorry!')
            return
        await ctx.send('Enjoy your ' + str(10 * dt) + ' points ' + tmp + '!')

    @commands.command(pass_context=True)
    async def bet(self, ctx):
        """Lets a user bet points in hopes of getting more. This is almost a zero-sum game, it only rounds down to the nearest whole number away from a zero-sum game.\nTakes input in the form ?bet points_to_bet odds_to_win:odds_to_lose."""
        currPoints = fetch_data('points_register', ctx.message.author.id)
        if currPoints is None:
            await ctx.send('Point data reading/writing failed, sorry!')
            return
        tmp = '{0.mention}'.format(ctx.message.author)
        try:
            wager = int(ctx.message.content.split()[1])
            o1, o2 = map(int, ctx.message.content.split()[2].split(':'))
        except Exception:
            await ctx.send('Give the input in an orderly format silly!')
            return
        if wager <= 0 or o1 <= 0 or o2 <= 0:
            await ctx.send('Give the input in an orderly format silly!')
            return
        if wager > currPoints:
            await ctx.send('You don\'t have that many points!')
            return
        if o1 > 1000 or o2 > 1000:
            await ctx.send('I\'m not ready to take a bet that big!')
            return
        res = random.randint(1, o1 + o2)
        if res <= o1:
            gain = o2 * wager // o1
            if not write_data('points_register', ctx.message.author.id, currPoints + gain):
                await ctx.send('Point data reading/writing failed, sorry!')
                return
            if gain == 1:
                await ctx.send('Yay! You win 1 point!')
            else:
                await ctx.send('Yay! You win ' + str(gain) + ' points!')
        else:
            if not write_data('points_register', ctx.message.author.id, currPoints - wager):
                await ctx.send('Point data reading/writing failed, sorry!')
                return
            if wager == 1:
                await ctx.send('Oh no! You lost 1 point!')
            else:
                await ctx.send('Oh no! You lost ' + str(wager) + ' points!')	

def setup(bot, config):
    bot.add_cog(Points(bot))
