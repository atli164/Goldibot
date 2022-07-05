import re
import random
from discord.ext import commands
from goldiIO import fetch_data, write_data
from goldiRolls import rollstrtostring

slotRes = [':poop:', ':grapes:', ':grapes:', ':grapes:', ':grapes:', ':cherries:',
           ':cherries:', ':cherries:', ':cherries:', ':four_leaf_clover:', ':four_leaf_clover:', ':gem:']

weights = {':poop:': 0, ':grapes:': 10, ':cherries:': 25,
           ':four_leaf_clover:': 40, ':gem:': 164}


def getSlot():
    res = random.sample(range(12), 3)
    res = [slotRes[k] for k in res]
    return res



class RNG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def roll(self, ctx):
        """Rolls dice.\nTakes input in the format ?roll [dicestr].\n Returns total result."""
        try:
            ans = rollstrtostring(ctx.message.content.split(None, 1)[1], False)
        except Exception:
            await ctx.send('That\'s not valid formatting silly!')
            return
        await ctx.send(ans)

    @commands.command(pass_context=True)
    async def rolls(self, ctx):
        """Rolls dice.\nTakes input in the format ?rolls [dicestr].\n Returns individual dice."""
        try:
            ans = rollstrtostring(ctx.message.content.split(None, 1)[1], True)
        except Exception:
            await ctx.send('That\'s not valid formatting silly!')
            return
        await ctx.send(ans)

    @commands.command(pass_context=True)
    async def saveroll(self, ctx):
        """Saves a roll string for later use. ?saveroll name [dicestr]."""
        s = ctx.message.content.split(None, 1)[1]
        name, dice = s.split(None, 1)
        if not write_data('saved_rolls', (ctx.message.author.id, name), dice):
            await ctx.send('File IO failed!')
            return
        await ctx.send('Roll saved!')
    
    @commands.command(pass_context=True)
    async def rollnamed(self, ctx):
        """Rolls a saved roll. ?rollnamed name."""
        name = ctx.message.content.split(None, 1)[1]
        saved = fetch_data('saved_rolls', (ctx.message.author.id, name))
        if not saved:
            await ctx.send('No such roll saved!')
            return
        try:
            ans = rollstrtostring(saved)
        except Exception:
            await ctx.send('That\'s not valid formatting silly!')
            return
        await ctx.send(ans)

    @commands.command(pass_context=True)
    async def crank(self, ctx):  # Should cost about 5 points.
        """Cranks a slot machine. Costs 5 points to play.\nThis command takes no input."""
        currP = fetch_data('points_register', ctx.message.author.id)
        if currP is None:
            await ctx.send('Can\'t find you in the register, sorry!')
            return
        if currP < 5:
            await ctx.send('You can\'t afford that silly!')
            return
        outcome = [getSlot(), getSlot(), getSlot()]
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
        await ctx.send(outcome)
        if win > 0:
            if not write_data('points_register', ctx.message.author.id, currP + win - 5):
                await ctx.send('Point registration failed.')
                return
            await ctx.send('Congratiulations, you win ' + str(win) + ' points!')
        else:
            if not write_data('points_register', ctx.message.author.id, currP - 5):
                await ctx.send('Point registration failed.')
                return
            await ctx.send('No points for you, sorry!')

    @commands.command(pass_context=True)
    async def choose(self, ctx):
        """Makes the bot choose one out of the given options at random. The input is in the form ?choose [option1] [option2] [option3] and so on where the options and the choose command are separated by spaces"""
        try:
            chooseFrom = ctx.message.content.split()[1:]
        except Exception:
            await ctx.send('Your input formatting is invalid! (Or I messed up)')
            return
        if not len(chooseFrom):
            await ctx.send('You have to give me something to work with here!')
            return
        await ctx.send('I choose: ' + random.choice(chooseFrom))


def setup(bot, config):
    bot.add_cog(RNG(bot))
