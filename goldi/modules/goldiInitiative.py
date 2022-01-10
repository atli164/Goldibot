import re
import random
from discord.ext import commands
from goldiIO import fetch_data, write_data, clear_data, fetch_all_data
from goldiRolls import rollstrtonum

class Initiative(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def setbonus(self, ctx):
        """
        Sets a player's initiative bonus. Takes input in the format ?setbonus n. 
        The command can also be called as ?setbonus custom [rollstr] where rollstr is a valid string of dice rolls. 
        Thus ?setbonus 1 and ?setbonus custom 1d20 + 1 do the same thing.
        Furthermore, in a custom string, several rolls can be separated by semicolons.
        So if characters act on more than one initiative, perhaps one with bonus 1 and another with initiative 1d16 + 2 the command would be
        ?setbonus custom 1d20 + 1; 1d16 + 2
        """
        param = ctx.message.content.split(None, 1)[1]
        rollstr = ""
        try:
            n = int(param)
            if n > 0:
                rollstr = "1d20+" + str(n)
            elif n < 0:
                rollstr = "1d20-" + str(abs(n))
            else:
                rollstr = "1d20"
        except ValueError:
            param = param.split(None, 1)
            if param[0] != "custom":
                await ctx.send('Your input is invalid!')
                return
            rollstr = param[1]
        name = fetch_data('initiative_names', str(ctx.message.author.id))
        if not name:
            await ctx.send('No name registered yet!')
            return
        if not write_data('initiative_register', name, rollstr):
            await ctx.send('Initiative registration failed.')
            return
        await ctx.send('Initiative registered!')

    @commands.command(pass_context=True)
    async def setname(self, ctx):
        """Sets the user's name in initiative tables."""
        param = ctx.message.content.split(None, 1)[1]
        param.strip()
        if not write_data('initiative_names', ctx.message.author.id, param):
            await ctx.send('Name registration failed.')
            return
        await ctx.send('Name registered!')
    
    @commands.command(pass_context=True)
    async def clearinitiatives(self, ctx):
        """Clears the current initiative table. Takes no input."""
        if not clear_data('initiative_table'):
            await ctx.send('Reset failed.')
            return
        await ctx.send('Reset successful!')

    @commands.command(pass_context=True)
    async def rollinitiative(self, ctx):
        """Rolls initiative for the player. Takes no input."""
        namedat = fetch_data('initiative_names', ctx.message.author.id)
        if namedat is None:
            await ctx.send('No initiative name data found!')
            return
        rollstr = fetch_data('initiative_register', namedat)
        if rollstr is None:
            await ctx.send('No initiative bonus data found!')
            return
        name = fetch_data('initiative_names', ctx.message.author.id)
        if name is None:
            name = '{0.mention}'.format(ctx.message.author)
        allres = rollstrtonum(rollstr)
        for (i, x) in enumerate(allres):
            cur_name = name
            if i != 0:
                cur_name = cur_name + '(' + str(i + 1) + ')'
            if not write_data('initiative_table', cur_name, x):
                await ctx.send('Initiative registration failed.')
        await ctx.send('You rolled ' + ';'.join([str(x) for x in allres]) + '.')

    @commands.command(pass_context=True)
    async def rollinitiatives(self, ctx):
        """Rolls initiatives for all registered players. Takes no input."""
        rolltable = fetch_all_data('initiative_register')
        for name, rollstr in rolltable.items():
            for (i, s) in enumerate(rollstr.split(';')):
                s = s.strip()
                cur_name = name
                if i != 0:
                    cur_name = cur_name + '(' + str(i + 1) + ')'
                rolls, constant = rollstrparse(s)
                result = sum(rolls) + constant
                if not write_data('initiative_table', cur_name, result):
                    await ctx.send('Initiative registration failed.')
        await self.printinitiative(ctx)
    
    @commands.command(pass_context=True)
    async def setinitiative(self, ctx):
        """Sets initiative for a name. Called as ?setinitiative [name] [value]."""
        _, name, val = ctx.message.content.split()
        try:
            val = int(val)
        except ValueError:
            await ctx.send('That is not a valid initiative!')
            return
        if not write_data('initiative_table', name, val):
            await ctx.send('Initiative registration failed.')
            return
        await ctx.send('Initiative registered!')
    
    @commands.command(pass_context=True)
    async def printinitiative(self, ctx):
        """Prints initiative table. Takes no input."""
        table = fetch_all_data('initiative_table')
        if table is None:
            await ctx.send('No table saved!')
            return
        cur = None
        if 'cur' in table:
            cur = table['cur']
        vals = [(v, k) for (k, v) in table.items() if k != 'cur']
        vals.sort()
        vals.reverse()
        mess = ""
        for v, k in vals:
            if k == 'cur':
                continue
            if k == cur:
                mess += k + ": " + str(v) + " (currently acting) \n"
            else:
                mess += k + ": " + str(v) + "\n"
        await ctx.send(mess)
    
    @commands.command(pass_context=True)
    async def nextplayer(self, ctx):
        """Moves onto next player in intiative order. Takes no input."""
        table = fetch_all_data('initiative_table')
        if table is None:
            await ctx.send('No table saved!')
            return
        cur = None
        vals = [(v, k) for (k, v) in table.items() if k != 'cur']
        vals.sort()
        if 'cur' not in table:
            cur = vals[-1][1]
        else:
            for i in range(len(vals)):
                if vals[i][1] == table['cur']:
                    cur = vals[(i - 1 + len(vals)) % len(vals)][1]
                    break
        if not write_data('initiative_table', 'cur', cur):
            await ctx.send("File IO failed!")
            return
        await ctx.send("It is " + cur + "'s turn!")
        return

def setup(bot, config):
    bot.add_cog(Initiative(bot))
