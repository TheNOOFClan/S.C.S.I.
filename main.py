import discord
import asyncio
import logging
import json
import time
import io
import sys
import random
import datetime
import re

from discord.ext import commands
from pathlib import Path

description = '''An automod bot for auto modding
'''

reminders = []
polls = []

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

def findServer(ident):
    return bot.get_server(ident)

def findChannel(server, channel):
    '''finds the channel'''
    for all in ds['servers']:
        if all['id'] == server:
            return bot.get_channel(all[channel])

## may not get used but I'm just keeping it
def findUser(id):
    users = list(bot.get_all_members())
    for all in users:
        name = ''.join(str(all).split('#').pop(0))
        if name == id:
            return all
    return -1

def checkRole(user, roleRec):
    '''Checks if the user has the recuired role'''
    ok = False
    for all in list(user.roles):
        if all.name == roleRec:
            ok = True
    return ok

def timeToTicks(time):
    '''converts time into seconds than to ticks'''
    time = time.lower()
    time = time.split(',')
    timeSec = 0
    for all in time:
        if "w" in all or "week" in all or "weeks" in all:
            tmp = all.strip('weks')
            timeSec += datetime.timedelta(weeks=int(tmp)).total_seconds()
        elif "d" in all or "day" in all or "days" in all:
            tmp = all.strip('days')
            timeSec += datetime.timedelta(days=int(tmp)).total_seconds()
        elif "h" in all or "hour" in all or "hours" in all:
            tmp = all.strip('hours')
            timeSec += datetime.timedelta(hours=int(tmp)).total_seconds()
        elif "m" in all or "minute" in all or "minutes" in all:
            tmp = all.strip('minutes')
            timeSec += datetime.timedelta(minutes=int(tmp)).total_seconds()
        elif "s" in all or "second" in all or "seconds" in all:
            tmp = all.strip('second')
            timeSec += int(tmp)
        else:
            tmp = all.strip('ticks')
            timeSec += int(tmp) * ds['bot']['ticklength']
    return timeSec // ds['bot']['ticklength']


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
async def poll(ctx, time, description, *options):
    '''Creates a poll'''
    pollNum = ds['bot']['pollNum']
    ds['bot']['pollNum'] += 1
    try:
##        time = int(time)
        time = timeToTicks(time)
        desc = description
        pos = {}
        server = ctx.message.server.id
        for all in options:
            pos[all] = 0
        polls.append({"time":time, 'pollNum':pollNum, "desc":desc, "pos":pos, "server":server})
        await bot.say("New poll created! #{0}, possibilities: {1}".format(pollNum, pos))
    except:
        await bot.say('Incorrect number format')

@bot.command()
async def vote(number, option):
    '''Votes on a poll'''
    try:
        pollNum = int(number)
        pos = option
        for all in polls:
            if all['pollNum'] == pollNum:
                if pos in all['pos'].keys():
                    all['pos'][pos] += 1
                    break # Why waste valuable processing cycles?
                await bot.say('Invalid option for that poll')
    except ValueError:
        await bot.say('Incorrect number format')

@bot.command()
async def timeto(ticks):
    '''says how much time will pass in <ticks> ticks
    !!obsolite!!'''
    try:
        ticks = int(''.join(ticks))
        seconds = ds['bot']['ticklength'] * ticks
        hours = seconds // 36000
        seconds %= 36000
        minutes = seconds // 60
        seconds %= 60
        seconds = round(seconds, 0)
        msg = "{0} ticks is {1} hours, {2} minutes, {3} seconds long".format(ticks, hours, minutes, seconds)
        await bot.say(msg)
    except ValueError:
        await bot.say("Invalid arguments")

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
async def timeup():
    '''Displays time up'''
    timeUp = time.time() - startTime
    hoursUp = timeUp // 36000
    timeUp %= 36000
    minutesUp = timeUp // 60
    timeUp = round(timeUp % 60, 0)
    msg = "Time up is: *{0} Hours, {1} Minutes and, {2} Seconds*".format(hoursUp, minutesUp, timeUp)
    await bot.say(msg)

#the following code does not work, and so we will not keep it
#@bot.command(pass_context=True)
#async def tts(ctx):
#    '''Turns TTS on or off'''
#    if ctx.message.content[len(prefix) + 4:] == "on":
#        ds['bot']['tts'] = True
#        await bot.say("TTS is now on!")
#    elif ctx.message.content[len(prefix) + 4:] == "off":
#        ds['bot']['tts'] = False
#        await bot.say("TTS is now off!")

@bot.command()
async def echo(*, message):
    '''Echos a message'''
    print('Echoing: ', message)
    logger.info('Echoing: {0}'.format(message))
    await bot.say(message)

@bot.command(pass_context=True)
async def changegame(ctx, *game):
    '''Changes the game being displayed'''
    author = ctx.message.author
    if checkRole(author, ds['bot']['botmin']):
        gameName = ' '.join(game)
        await bot.change_status(game=discord.Game(name=gameName))
        await bot.say("Changing game to: \"{0}\"!".format(gameName))
    else:
        await bot.say("User is not {0}, ask a {0} to use this command!".format(ds['bot']['botmin']))

@bot.command(pass_context=True)
async def remind(ctx, delay, *message):
    '''Sets a reminder for several seconds in the future'''
    msg = ' '.join(message)
    chan = ctx.message.channel
    try:
## following code kept for posterity
##        delay = int(float(delay) / ds['bot']['ticklength'])
##        if delay == 0:
##            delay = 1
##        reminders.append([delay, chan, msg])
##        await bot.say("Reminder set")
        delay = timeToTicks(delay)
        if delay == 0:
            delay = 1
        reminders.append([delay, chan, msg])
        await bot.say("Reminder set")
    except ValueError:
        await bot.say("Incorrect format for the delay")

@bot.command(pass_context=True)
async def backup(ctx, num="1000"):
    '''Backs up <num> messages in the current channel. "all" will back up the entire channel. If num is not provided, defaults to 1000'''
    try:
        msg = ctx.message
        # Assuming not Wham!DOS paths, although those may work as well
        servPath = msg.server.id + ' - ' + msg.server.name + '/'
        chanPath = msg.channel.id + ' - ' + msg.channel.name + '/'
        p = Path(servPath)
        if not p.exists(): p.mkdir()
        p = Path(servPath + chanPath)
        if not p.exists(): p.mkdir()
        newliner = re.compile('\n')
        
        if num.lower() == "all":
            await bot.send_message(msg.channel, "Starting backup")
            count = 1000
            total = 0
            start_time = None
            now_time = None
            # Probably a better way to do this, but I don't know it
            async for m in bot.logs_from(msg.channel, limit=1):
                now_time = m.timestamp
                
            while count == 1000:
                count = 0
                first = True
                f = open(servPath + chanPath + 'temp', 'w')
                
                async for message in bot.logs_from(msg.channel, limit=1000, before=now_time):
                    if first:
                        start_time = message.timestamp
                        first = False
                    
                    m = message.clean_content
                    m = newliner.sub('\n\t', m)
                    f.write(str(message.timestamp) + ': ' + message.author.name + ' (' + str(message.author.nick) + '):\n\t' + m + '\n')
                    f.write('attachments:\n')
                    for a in message.attachments:
                        f.write('\t')
                        f.write(a['url'])
                        f.write('\n')
                    f.write('\n')
                    
                    now_time = message.timestamp
                    count += 1
                    total += 1
            
                f.close()
                Path(servPath + chanPath + 'temp').rename(servPath + chanPath + str(start_time) + ' -- ' + str(now_time) + '.log')
                await bot.say("Backed up " + str(total) + " messages")
            
            await bot.say("Backup finished")
                
        else:
            num = int(num)
            f = open(servPath + chanPath + 'temp', 'w')
            await bot.say('Starting backup')
            first = True
            start_time = None
            end_time = None
            async for message in bot.logs_from(msg.channel, limit=num + 1):
                if first:
                    start_time = message.timestamp
                    first = False
                else:
                    m = message.clean_content
                    m = newliner.sub('\n\t', m)
                    f.write(str(message.timestamp) + ': ' + message.author.name + ' (' + str(message.author.nick) + '):\n\t' + m + '\n')
                    f.write('attachments:\n')
                    for a in message.attachments:
                        f.write('\t')
                        f.write(a['url'])
                        f.write('\n')
                    f.write('\n')
                
                end_time = message.timestamp
            
            f.close()
            Path(servPath + chanPath + 'temp').rename(servPath + chanPath + str(start_time) + ' -- ' + str(end_time) + '.log')
            await bot.say('Backup finished')
    except ValueError:
        await bot.say('Incorrect number format')

@bot.command(pass_context=True)
async def who(ctx, user):
    '''Gives info on a mentioned user'''
    try:
        users = list(bot.get_all_members())
        for all in users:
            if all.mentioned_in(ctx.message):
                user = all
                break
        if user == None:
            await bot.say("mention a user!")
        msg = "Name: {0}\nID: {1}\nDiscriminator: {2}\nBot: {3}\nAvatar URL: {4}\nCreated: {5}\nNickname: {6}".format(user.name, user.id, user.discriminator, user.bot, user.avatar_url, user.created_at, user.display_name)
        await bot.say(msg)
        await bot.say(str(user))
    except:
            await bot.say("Please mention a user!")

@asyncio.coroutine
async def on_tick():
    for rem in reminders:
        rem[0] -= 1
        if rem[0] == 0:
            await bot.send_message(rem[1], rem[2])
            reminders.remove(rem)

    for poll in polls:
        poll["time"] -= 1
        if poll["time"] == 0:
            server = poll['server']
            channel = findChannel(server, "poll")
            await bot.send_message(channel, poll['pos'])
            await bot.send_message(channel, "poll #{0} is now over!".format(poll['pollNum']))
            polls.remove(poll)

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
