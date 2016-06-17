import discord
import logging
import json
import time
import io
import sys
import random
from discord.ext import commands

description = '''An automod bot for auto modding
'''

bot = commands.Bot(command_prefix="!", description=description)

settings = open('settings.json', 'r')
ds = json.load(settings)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='dicord.log', encoding="utf-8", mode='w')
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

logger.info("Starting SCSI {0} using discord.py {1}".format(ds['bot']["version"], discord.__version__))
print("Starting SCSI {0} using discord.py {1}".format(ds['bot']['version'], discord.__version__))

def findChannel(name):
	channels = list(bot.get_all_channels())
	for all in channels:
		if all.name = name
			return all
		else:
			return -1
			
@bot.event
async def on_channel_delete(channel):
	msg = "Channel {0} has been deleted!".format(channel.mention)
	await bot.send_message(findChannel(ds['server']['announcements']), msg, tts=ds['bot']['tts'])
	
@bot.event
async def on_channel_create(channel):
    msg = "Channel {0} has been created!".format(channel.mention)
    await bot.send_message(findChannel(ds['server']['announcements']), msg, tts=ds['bot']['tts'])

@bot.event
async def on_member_join(member):
    msg = "New member {0} has joined the server!".format(member.mention)
    await bot.send_message(findChannel(ds['server']['announcements']), msg, tts=ds['bot']['tts'])

@bot.event
async def on_member_remove(member):
    msg = "New member {0} has left the server!".format(member.mention)
await bot.send_message(findChannel(ds['server']['announcements']), msg, tts=ds['bot']['tts'])

@bot.event
async def on_command(command, ctx):
	message = ctx.message
	destination = None
	if message.channel.is_private:
		destination = "Private Message"
	else:
		destination = "#{0.channel.name} ({0.server.name})".format(message)
		
@bot.command()
async def test():
	await bot.say("HELLO WORLD!")
	
@bot.command()
async def 
	
@bot.command(pass_context=True)
async def echo(ctx):
	await bot.say("

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    logger.info('Logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('------')
            
startTime = time.time()
bot.run(ds['bot']["token"])
settings.close()
