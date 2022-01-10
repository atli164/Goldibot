from discord.ext import commands
from goldiIO import fetch_data, write_data

def ongoingPoll():
    return fetchAttr('poll_data', 'on')

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def startpoll(self, ctx):
        """Starts a poll. Cannot be used while a poll is still going on.\nTakes input in the form ?startpoll question | option1 | [option2] | ... | [optionn] where the message is displayed alongside the poll, | separate the options (so the options can contain whitespaces and special characters) and there has to be at least one option after the question."""
        if ongoingPoll():
            await ctx.send('There\'s already a poll going on!')
            return
        cmdContent = ctx.message.content[11:].split('|')
        if len(cmdContent) < 2:
            await ctx.send('Your poll has to have a question and at least one option to choose from!')
            return
        if len(cmdContent) > 100:
            await ctx.send('I can\'t handle that many options!')
            return
        if max(map(len, cmdContent)) > 200:
            await ctx.send('Those options are too big for me!')
            return
        changeAttr('poll_data', 'on', True)
        question = cmdContent[0].strip()
        changeAttr('poll_data', 'question', question)
        cmdContent = list(map(str.strip, cmdContent[1:]))
        changeAttr('poll_data', 'options', cmdContent)
        changeAttr('poll_data', 'votes', [0] * len(cmdContent))
        changeAttr('poll_data', 'havevoted', [])
        msg = 'Poll successfully started!\n'
        msg += question + '\n'
        msg += 'Your options are: \n'
        for i in range(len(cmdContent)):
            msg += str(i + 1) + ': ' + cmdContent[i] + '\n'
        await ctx.send(msg)

    @commands.command(pass_context=True)
    async def killpoll(self, ctx):
        """Kills the poll. Will prompt the user if they are sure when used. Will only kill poll if asked to do so by the same user twice.\n This command takes no input."""
        if not ongoingPoll():
            await ctx.send('There is no current poll to kill!')
            return
        shouldKill = fetchAttr('poll_data', 'killsoon')
        if shouldKill == False:
            await ctx.send('Are you sure you want to end the current poll?')
            changeAttr('poll_data', 'killsoon', ctx.message.author.id)
            return
        if shouldKill != ctx.message.author.id:
            await ctx.send('End of poll aborted.')
            changeAttr('poll_data', 'killsoon', False)
            return
        changeAttr('poll_data', 'killsoon', False)
        changeAttr('poll_data', 'on', False)
        await ctx.send('Current poll killed.')

    @commands.command(pass_context=True)
    async def vote(self, ctx):
        """Votes on the current poll.\n Takes input in the form ?vote option num where num is the number of the option you wish to vote for or ?vote optionname where optionname is the name of the option you wish to vote for, to the character."""
        if not ongoingPoll():
            await ctx.send('There is no poll going on currently, sorry!')
            return
        haveVoted = fetchAttr('poll_data', 'havevoted')
        if ctx.message.author.id in haveVoted:
            await ctx.send('You\'ve already voted in this poll!')
            return
        theVote = ctx.message.content[6:]
        if theVote[:6] == "option":
            theVote = theVote[7:]
            try:
                opt = int(theVote)
            except ValueError:
                await ctx.send('That\'s not a proper number')
                return
            votesSoFar = fetchAttr('poll_data', 'votes')
            if opt < 1 or opt > len(votesSoFar):
                await ctx.send('There\'s no option with that number, sorry!')
                return
            votesSoFar[opt - 1] += 1
            changeAttr('poll_data', 'votes', votesSoFar)
            haveVoted.append(ctx.message.author.id)
            changeAttr('poll_data', 'havevoted', haveVoted)
            await ctx.send('Vote recieved!')
            return
        pickFrom = fetchAttr('poll_data', 'options')
        opt = -1
        for i in range(len(pickFrom)):
            if pickFrom[i].strip() == theVote.strip():
                opt = i
                break
        if opt == -1:
            await ctx.send('No option with that name found, sorry! Are you sure you spelled it correctly?')
            return
        votesSoFar = fetchAttr('poll_data', 'votes')
        votesSoFar[opt] += 1
        changeAttr('poll_data', 'votes', votesSoFar)
        haveVoted.append(ctx.message.author.id)
        changeAttr('poll_data', 'havevoted', haveVoted)
        await ctx.send('Vote recieved!')

    @commands.command()
    async def pollstatus(self):
        """Prompts the bot to display the status of the current poll.\nThis command takes no input."""
        if not ongoingPoll():
            await ctx.send('There is no poll going on currently, sorry!')
            return
        question = fetchAttr('poll_data', 'question')
        opts = fetchAttr('poll_data', 'options')
        votesSoFar = fetchAttr('poll_data', 'votes')
        message = question + '\n'
        for i in range(len(opts)):
            message += 'Option ' + str(i + 1) + ': ' + opts[i] + ', currently has ' + str(votesSoFar[i]) + ' votes.\n'
        await ctx.send(message) 

def setup(bot, config):
    bot.add_cog(Poll(bot))
