import async_timeout
import aiohttp

def get_channel(bot, name):
	for server in bot.servers:
		for channel in server.channels:
			if channel.name == name:
				return channel
	return None

def get_channels(bot, names):
	names = set(names)
	res = []
	for server in bot.servers:
		for channel in server.channels:
			if channel.name in names:
				res.append(channel)
	return res
