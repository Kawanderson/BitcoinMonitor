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
                   InlineKeyboardButton(text='Commands 📚', callback_data='COM'),
                   InlineKeyboardButton(text='Configuration ⚙️', callback_data='CONF')],
                   [
                       InlineKeyboardButton(text='Informations ❓', callback_data='INFO'),
                       InlineKeyboardButton(text='Donate ❤️', callback_data='DONATE')
                    ]
        ])

        self.conf_keyboad = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text="TimeMonitor +1", callback_data="TIME_ADD1"),
                   InlineKeyboardButton(text="TimeMonitor -1", callback_data="TIME_SUB1")],
                   [
                       InlineKeyboardButton(text="Switch MonitorType", callback_data="SWMNT")
                   ]
        ])
    
    async def recived_message(self, msg):
        content_type, chat_type, chat_id = amanobot.glance(msg)
        
        pprint(msg)

        if content_type != 'text':
            return
        
        if not "username" in msg['from'].keys():
            await self.sender.sendMessage("To start using my services you need define a username in configurations of telegram.")
            return
        
        if msg['text'] == '/start' or msg['text'] == '/help':
            if not bool(session.query(User).filter_by(chat_id=chat_id).count()):
                temp = User(chat_id, username=msg['from']['username'])
                session.add(temp)
                session.commit()
                await self.sender.sendMessage("Welcome "+msg['from']['username'], reply_markup=self.help_keyboard)
            else:
                await self.sender.sendMessage('Ajuda:', reply_markup=self.help_keyboard)
    
    async def on_callback_query(self, msg):
        query_id, from_id, query_data = amanobot.glance(msg, flavor='callback_query')
        editor = amanobot.aio.helper.Editor(self.bot, (from_id, msg['message']["message_id"]))

        pprint(msg)

        if query_data == "INFO":
            USUARIOS = len(session.query(User).all())
            await editor.editMessageText(f"<b>Creator:</b> <code>@SouSeuDono</code>\n<b>Version:</b> <code>{VERSION}</code>\n<b>Users:</b> <code>{USUARIOS}</code>", parse_mode="html")
        
        if query_data == "CONF":
            await editor.editMessageText("Configuration:", reply_markup=self.conf_keyboad)

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