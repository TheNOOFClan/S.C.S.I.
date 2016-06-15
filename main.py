import discord
import logging
import json
import time
import io
import sys

settings = open('settings.json', 'r')
ds = json.load(settings)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='dicord.log', encoding="utf-8", mode='w')
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

logger.info("Starting SCSI {0} using discord.py {1}".format(ds['bot']["version"], discord.__version__))
print("Starting SCSI {0} using discord.py {1}".format(ds['bot']['version'], discord.__version__))
client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content.startswith('!test'):
        logging.debug("'!test' command found!")
        msg = "HELLO WORLD!"
    elif message.content.startswith('!shutdown'):
        msg = "Shuting down now!"
        await client.send_message(message.channel, msg, tts=ds['bot']['tts'])
        client.logout()
        settings.close()
        sys.exit()
    elif message.content.startswith('!help'):
        msg = "Commands: \n!echo <text>: echos text\n!test: says\"HELLO WORLD\"\n!timeup: prints up time"
        msg += "\n!ttsOn: should turn on TTS\n!ttsOff: should turn off TTS\n!help:prints this (hard codded)"
    elif message.content.startswith('!echo '):
        logging.debug("'!echo' command found!")
        msg = message.content[6:]
    elif message.content.startswith('!timeup'):
        logging.debug("'!timeup' command found!")
        timeUp = time.time() - startTime
        hoursUp = timeUp // 36000
        timeUp %= 36000
        minutesUp = timeUp // 60
        timeUp = round(timeUp % 60, 0)
        msg = "Time up is: *{0} Hours, {1} Minutes and, {2} Seconds*".format(hoursUp, minutesUp, timeUp)
    elif message.content.startswith("!ttsOn"):
        ds['bot']['tts'] = True
        msg = "TTS is now on!"
    elif message.content.startswith("!ttsOff"):
        ds['bot']['tts'] = False
        msg = "TTS is now off!"
    elif message.content.startswith("!"):
        msg = "Unknown command \"{0}\"".format(message.content)
    try:
        await client.send_message(message.channel, msg, tts=ds['bot']['tts'])
    except:
        pass
        
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    logger.info('Logged in as')
    logger.info(client.user.name)
    logger.info(client.user.id)
    logger.info('------')
    
startTime = time.time()
client.run(ds['bot']["token"])
settings.close()
