from discord.ext import commands

class Basics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def hello(self, ctx):
        """Greets the person greeting her!\nThis command takes no input."""
        await ctx.send('Hello {0.mention}!'.format(ctx.message.author))
	
    @commands.command(pass_context=True)
    async def suggest(self, ctx):
        """Sends a suggestion to my maker as a private message!\nThis command takes a string as input in the form of ?suggest string_here. The string is allowed to contain spaces and special characters."""
        curr_server = ctx.message.server
        atli = curr_server.get_member('249293986349580290')
        await self.bot.send_message(atli, ctx.message.content[9:])
        await ctx.send('Suggestion sent!')
	
    @commands.command(pass_context=True)
    async def echo(self, ctx):
        """Repeats what the user asked to repeat.\nThis command takes a string as input in the form of ?echo string_here. The string is allowed to contain spaces and special characters."""
        await ctx.send(ctx.message.content[6:])

def setup(bot, config):
    bot.add_cog(Basics(bot))
