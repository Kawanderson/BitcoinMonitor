import asyncio
import amanobot
import amanobot.aio
import configparser
import amanobot.aio
import amanobot.aio.helper
from amanobot.aio.loop import MessageLoop
from amanobot.aio.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)
from amanobot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from Database.database import User, Session
from pprint import pprint

config = configparser.ConfigParser()
config.read('config.ini')

#####---STATIC VARS---#####
TOKEN = config["BOT"].get("Token")
VERSION = config["BOT"].get("Version")
session = Session()
#####---END---#####



class Bitcoin(amanobot.aio.helper.ChatHandler):

    def __init__(self, *args, **kwargs):
        super(Bitcoin, self).__init__(*args, **kwargs)
        
        self.help_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Comandos 📚', callback_data='COM'),
                   InlineKeyboardButton(text='Configurações ⚙️', callback_data='CONF')],
                   [
                       InlineKeyboardButton(text='Informações ❓', callback_data='INFO'),
                       InlineKeyboardButton(text='Doar ❤️', callback_data='DONATE')
                    ]
        ])
    

    async def recived_message(self, msg):
        content_type, chat_type, chat_id = amanobot.glance(msg)
        
        pprint(msg)

        if content_type != 'text':
            return
        
        if not "username" in msg['from'].keys():
            await self.sender.sendMessage("Para começar a usar meus serviços você precisa definir um Username.")
            return
        
        if msg['text'] == '/start' or msg['text'] == '/help':
            if not bool(session.query(User).filter_by(chat_id=chat_id).count()):
                temp = User(chat_id, username=msg['from']['username'])
                session.add(temp)
                session.commit()
                await self.sender.sendMessage("Bem vindo "+msg['from']['username']+"", reply_markup=self.help_keyboard)
            else:
                await self.sender.sendMessage('Ajuda:', reply_markup=self.help_keyboard)

    async def on_chat_message(self, msg):
        await self.recived_message(msg)      

bot = amanobot.aio.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['private']), create_open, Bitcoin, timeout=10),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()