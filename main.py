import asyncio
import amanobot
import amanobot.aio
from amanobot.aio.loop import MessageLoop
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

#####---STATIC VARS---#####
TOKEN = config["BOT"].get("Token")
VERSION = config["BOT"].get("Version")
#####---END---#####

async def handle(msg):
    content_type, chat_type, chat_id = amanobot.glance(msg)
    if content_type != 'text':
        return
    
    if msg['text'] == '/start':
        await bot.sendMessage(chat_id, "Bem vindo "+msg['from']['first_name']+" ainda estou em fase de desenvolvimento.")


bot = amanobot.aio.Bot(TOKEN)
loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot, handle).run_forever())

print('Iniciando...')

loop.run_forever()