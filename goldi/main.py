#! /usr/bin/python3

import discord
from discord.ext import commands
import os
import importlib
import sys
import config
import secrets

bot = commands.Bot(command_prefix = commands.when_mentioned_or(*config.prefixes), 
		   description = config.description) 

@bot.event
async def on_ready():
	print('Login successful')
	print('User: ' + str(bot.user.name))
	print('ID: ' + str(bot.user.id))
	await bot.change_presence(game=discord.Game(name='by herself'))

@bot.command(pass_context=True)
async def kill(ctx):
	"""Turns off the bot. Only usable by Goldilocks.\nThis command takes no input."""
	if ctx.message.author.id == '249293986349580290':
		print('Turning off... Bye!')
		sys.exit()

def load_ext(bot, name, settings):
	if name in bot.extensions:
		return

	lib = importlib.import_module(name)
	if not hasattr(lib, 'setup'):
		raise discord.ClientException('Extension does not have a setup function.')

	lib.setup(bot, settings)
	bot.extensions[name] = lib

sys.path.append(os.path.join(os.getcwd(),'packages/'))

for mod, settings in config.packages.items():
    if settings['enabled']:
        try:
            importlib.import_module(mod)
        except ImportError as err:
            print('Couldn\'t load {} because of {}'.format(mod, str(err)))

sys.path.append(os.path.join(os.getcwd(),'modules/'))

for mod, settings in config.modules.items():
    if settings['enabled']:
        try:
            load_ext(bot, mod, settings)
        except (ImportError, AttributeError) as err:
            print('Couldn\'t load {} because of {}'.format(mod, str(err)))

bot.run(secrets.secret_token)
