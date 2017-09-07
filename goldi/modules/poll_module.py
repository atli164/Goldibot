from discord.ext import commands
from fetch_file import fetch_data, write_new_data, write_data

def ongoing_poll():
    return fetch_data('poll_data.txt', 'on')

class Poll():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def startpoll(self, ctx):
        """Starts a poll. Cannot be used while a poll is still going on.\nTakes input in the form ?startpoll question | option1 | [option2] | ... | [optionn] where the message is displayed alongside the poll, | separate the options (so the options can contain whitespaces and special characters) and there has to be at least one option after the question."""
        if ongoing_poll():
            await self.bot.say('There\'s already a poll going on!')
            return
        cmdcontent = ctx.message.content[11:].split('|')
        if len(cmdcontent) < 2:
            await self.bot.say('Your poll has to have a question and at least one option to choose from!')
            return
        write_data('poll_data.txt', 'on', True)
        question = cmdcontent[0].strip()
        write_data('poll_data.txt', 'question', question)
        cmdcontent = list(map(str.strip, cmdcontent[1:]))
        write_data('poll_data.txt', 'options', cmdcontent)
        write_data('poll_data.txt', 'votes', [0] * len(cmdcontent))
        write_data('poll_data.txt', 'havevoted', [])
        msg = 'Poll successfully started!\n'
        msg += question + '\n'
        msg += 'Your options are: \n'
        for i in range(len(cmdcontent)):
            msg += str(i + 1) + ': ' + cmdcontent[i] + '\n'
        await self.bot.say(msg)

    @commands.command(pass_context=True)
    async def killpoll(self, ctx):
        """Kills the poll. Will prompt the user if they are sure when used. Will only kill poll if asked to do so by the same user twice.\n This command takes no input."""
        if not ongoing_poll():
            await self.bot.say('There is no current poll to kill!')
            return
        should_kill = fetch_data('poll_data.txt', 'killsoon')
        if should_kill == False:
            await self.bot.say('Are you sure you want to end the current poll?')
            write_data('poll_data.txt', 'killsoon', ctx.message.author.id)
            return
        if should_kill != ctx.message.author.id:
            await self.bot.say('End of poll aborted.')
            write_data('poll_data.txt', 'killsoon', False)
            return
        write_data('poll_data.txt', 'killsoon', False)
        write_data('poll_data.txt', 'on', False)
        await self.bot.say('Current poll killed.')

    @commands.command(pass_context=True)
    async def vote(self, ctx):
        """Votes on the current poll.\n Takes input in the form ?vote option num where num is the number of the option you wish to vote for or ?vote optionname where optionname is the name of the option you wish to vote for, to the character."""
        if not ongoing_poll():
            await self.bot.say('There is no poll going on currently, sorry!')
            return
        havevoted = fetch_data('poll_data.txt', 'havevoted')
        if ctx.message.author.id in havevoted:
            await self.bot.say('You\'ve already voted in this poll!')
            return
        the_vote = ctx.message.content[6:]
        if the_vote[:6] == "option":
            the_vote = the_vote[7:]
            try:
                opt = int(the_vote)
            except ValueError:
                await self.bot.say('That\'s not a proper number')
                return
            votes_so_far = fetch_data('poll_data.txt', 'votes')
            if opt < 1 or opt > len(votes_so_far):
                await self.bot.say('There\'s no option with that number, sorry!')
                return
            votes_so_far[opt - 1] += 1
            write_data('poll_data.txt', 'votes', votes_so_far)
            havevoted.append(ctx.message.author.id)
            write_data('poll_data.txt', 'havevoted', havevoted)
            await self.bot.say('Vote recieved!')
            return
        pickfrom = fetch_data('poll_data.txt', 'options')
        opt = -1
        for i in len(pickfrom):
            if pickfrom[i].strip() == the_vote.strip():
                opt = i
                break
        if opt == -1:
            await self.bot.say('No option with that name found, sorry! Are you sure you spelled it correctly?')
            return
        votes_so_far = fetch_data('poll_data.txt', 'votes')
        votes_so_far[opt] += 1
        write_data('poll_data.txt', 'votes', votes_so_far)
        havevoted.append(ctx.message.author.id)
        write_data('poll_data.txt', 'havevoted', havevoted)
        await self.bot.say('Vote recieved!')

    @commands.command()
    async def pollstatus(self):
        """Prompts the bot to display the status of the current poll.\nThis command takes no input."""
        if not ongoing_poll():
            await self.bot.say('There is no poll going on currently, sorry!')
            return
        question = fetch_data('poll_data.txt', 'question')
        opts = fetch_data('poll_data.txt', 'options')
        votes_so_far = fetch_data('poll_data.txt', 'votes')
        message = question + '\n'
        for i in range(len(opts)):
            message += 'Option ' + str(i + 1) + ', ' + opts[i] + ', currently has ' + str(votes_so_far[i]) + 'votes.\n'
        await self.bot.say(message) 

def setup(bot, config):
    bot.add_cog(Poll(bot))
