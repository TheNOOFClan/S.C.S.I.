import discord
import asyncio
import logging
import json
import time
import io
import sys
import random
from discord.ext import commands

description = '''An automod bot for auto modding
'''

reminders = []

settings = open('settings.json', 'r')
ds = json.load(settings)

prefix = ds['bot']['prefix']

bot = commands.Bot(command_prefix=prefix, description=description)

loop = bot.loop

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
        if all.name == name:
            return all
        else:
            return -1

def checkRole(user, roleRec):
    ok = False
    for all in list(user.roles):
        if all.name == roleRec:
            ok = True
    return ok

@asyncio.coroutine
async def timer():
    await bot.wait_until_ready()
    while not bot.is_closed:
        loop.create_task(on_tick())
        await asyncio.sleep(ds['bot']['ticklength'])

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
    msg = "Member {0} has left the server!".format(member.name)
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
        '''Prints a test message'''
        await bot.say("HELLO WORLD!")

@bot.command(pass_context=True)
async def shutdown(ctx):
    '''Shuts down the bot'''
    author = ctx.message.author
    if checkRole(author, ds['bot']['botmin']):
        msg = "Shutting down now!"
        await bot.say(msg)
        timerTask.cancel()
        bot.logout()
        settings.close()
        sys.exit()
    else:
        await bot.say("User is not {0}, ask a {0} to use this command!".format(ds['bot']['botmin']))
        
@bot.command()
async def pls():
    '''Exists'''
    await bot.say("I am sorry, I can not be better")


@bot.command()
async def timeup():
    '''Displays time up'''
    timeUp = time.time() - startTime
    hoursUp = timeUp // 36000
    timeUp %= 36000
    minutesUp = timeUp // 60
    timeUp = round(timeUp % 60, 0)
    msg = "Time up is: *{0} Hours, {1} Minutes and, {2} Seconds*".format(hoursUp, minutesUp, timeUp)
    await bot.say(msg)
        
#the following code does not work but we will keep it
@bot.command(pass_context=True)
async def tts(ctx):
    '''Turns TTS on or off'''
    if ctx.message.content[len(prefix) + 4:] == "on":
        ds['bot']['tts'] = True
        await bot.say("TTS is now on!")
    elif ctx.message.content[len(prefix) + 4:] == "off":
        ds['bot']['tts'] = False
        await bot.say("TTS is now off!")

@bot.command(pass_context=True)
async def echo(ctx):
    '''Echos a message'''
    print('Echoing: ', ctx.message.content[len(prefix) + 5:])
    logger.info('Echoing: {0}'.format(ctx.message.content[len(prefix) + 5:]))
    await bot.say(ctx.message.content[len(prefix) + 5:])

@bot.command(pass_context=True)
async def changegame(ctx):
    '''Changes the game being displayed'''
    author = ctx.message.author
    if checkRole(author, ds['bot']['botmin']):
        gameName = ctx.message.content[len(prefix) + 10:]
        await bot.change_status(game=discord.Game(name=gameName))
        await bot.say("Changing game to: \"{0}\"!".format(gameName))
    else:
        await bot.say("User is not {0}, ask a {0} to use this command!".format(ds['bot']['botmin']))

@bot.command(pass_context=True)
async def remind(ctx):
    '''Sets a reminder for several seconds in the future'''
    params = ctx.message.content.split(' ')
    msg = ' '.join(params[2:])
    chan = ctx.message.channel
    try:
        delay = int(float(params[1]) / ds['bot']['ticklength'])
        if delay == 0:
            delay = 1
        reminders.append([delay, chan, msg])
        await bot.say("Reminder set")
    except ValueError:
        await bot.say("Incorrect format for the delay")

@asyncio.coroutine
async def on_tick():
    for rem in reminders:
        rem[0] -= 1
        if rem[0] == 0:
            await bot.send_message(rem[1], rem[2])
            reminders.remove(rem)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('Game set to:')
    print(ds['bot']['game'])
    print('------')
    logger.info('Logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('Game set to:')
    logger.info(ds['bot']['game'])
    logger.info('------')
    await bot.change_status(game=discord.Game(name=ds['bot']['game']))

startTime = time.time()
timerTask = loop.create_task(timer())
bot.run(ds['bot']["token"])
settings.close()
