import asyncio
import amanobot
import amanobot.aio
import configparser
import amanobot.aio
import amanobot.aio.helper
from amanobot.aio.loop import MessageLoop
from amanobot.aio.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)
from amanobot.delegate import chain
from amanobot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from Database.database import User, Session
from pprint import pprint

config = configparser.ConfigParser()
config.read('config.ini')

#####---STATIC VARS---#####
TOKEN = config["BOT"].get("Token")
VERSION = config["BOT"].get("Version")
CREATOR = config["BOT"].get("Creator")
BTC_ADDR = config["WALLETS"].get("BTC")
ETH_ADDR = config["WALLETS"].get("ETH")
BTC_CASH_ADDR = config["WALLETS"].get("BTC_CASH")
session = Session()
#####---END---#####

class Bitcoin(amanobot.aio.helper.ChatHandler):

    def __init__(self, *args, **kwargs):
        super(Bitcoin, self).__init__(*args, **kwargs)
        
        self.help_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Configuration ⚙️', callback_data='CONF')],
                   [
                       InlineKeyboardButton(text='Informations ❓', callback_data='INFO'),
                       InlineKeyboardButton(text='Donate ❤️', callback_data='DONATE')
                    ]
        ])

        self.conf_keyboad = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text="TimeMonitor ➕", callback_data="CONF_TIME_ADD"),
                   InlineKeyboardButton(text="TimeMonitor ➖", callback_data="CONF_TIME_SUB")],
                   [
                   InlineKeyboardButton(text="LossPercent ➕", callback_data="CONF_LOSS_ADD"),
                   InlineKeyboardButton(text="LossPercent ➖", callback_data="CONF_LOSS_SUB")],
                   [
                   InlineKeyboardButton(text="WinPercent ➕", callback_data="CONF_WIN_ADD"),
                   InlineKeyboardButton(text="WinPercent ➖", callback_data="CONF_WIN_SUB")],
                   [
                       InlineKeyboardButton(text="Back ⬅️", callback_data="RETURN_HOME")
                   ]
        ])

        self.return_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Back ⬅️', callback_data='RETURN_HOME')]
        ])
    
    async def on__idle(self, event):
        await self.editor.editMessageText('To save processing I will close this section')
        self.close()
    
    async def recived_message(self, msg):
        content_type, chat_type, chat_id = amanobot.glance(msg)
        
        pprint(msg)

        if content_type != 'text':
            return
        
        if not "username" in msg['from'].keys():
            await self.sender.editMessageText("To start using this bot you need set a username in configurations of the telegram")
            return
        
        if msg['text'] == '/start' or msg['text'] == '/help':
            if not bool(session.query(User).filter_by(chat_id=chat_id).count()):
                temp = User(chat_id, username=msg['from']['username'])
                session.add(temp)
                session.commit()
                await self.sender.sendMessage("Welcome "+msg['from']['username'], reply_markup=self.help_keyboard)
            else:
                await self.sender.sendMessage('Help:', reply_markup=self.help_keyboard)
    
    async def on_callback_query(self, msg):
        query_id, from_id, query_data = amanobot.glance(msg, flavor='callback_query')
        self.editor = amanobot.helper.Editor(self.bot, (from_id, msg['message']["message_id"]))

        pprint(msg)

        if query_data == "INFO":
            USUARIOS = len(session.query(User).all())
            await self.editor.editMessageText(f"<b>Creator:</b> <code>@SouSeuDono</code>\n<b>Version:</b> <code>{VERSION}</code>\n<b>Users:</b> <code>{USUARIOS}</code>", parse_mode="html", reply_markup=self.return_keyboard)
        
        elif query_data.startswith("CONF"):
            TIME_TO_MONITOR = session.query(User).filter_by(chat_id=from_id).one_or_none().time_monitor
            WIN_PERCENT = session.query(User).filter_by(chat_id=from_id).one_or_none().win_percent
            LOSS_PERCENT = session.query(User).filter_by(chat_id=from_id).one_or_none().loss_percent

            if query_data == "CONF":
                await self.editor.editMessageText(f"<b>Time to Monitor:</b> <code>{TIME_TO_MONITOR} Minutes</code>\n<b>Price up percent:</b> <code>{WIN_PERCENT}%</code>\n<b>Price loss percent:</b> <code>{LOSS_PERCENT}%</code>", reply_markup=self.conf_keyboad, parse_mode="html")
            
            elif "_".join(query_data.split("_")[1::]) == "TIME_SUB":
                if TIME_TO_MONITOR > 15:

                    session.query(User).filter_by(chat_id=from_id).update({"time_monitor": TIME_TO_MONITOR-1})
                    session.commit()
                    TIME_TO_MONITOR = session.query(User).filter_by(chat_id=from_id).one_or_none().time_monitor
                    await self.editor.editMessageText(f"<b>Time to Monitor:</b> <code>{TIME_TO_MONITOR} Minutes</code>\n<b>Price up percent:</b> <code>{WIN_PERCENT}%</code>\n<b>Price loss percent:</b> <code>{LOSS_PERCENT}%</code>", reply_markup=self.conf_keyboad, parse_mode="html")
                else:
                    await self.bot.answerCallbackQuery(query_id, text='This is the minimum time!')

            elif "_".join(query_data.split("_")[1::]) == "TIME_ADD":
                session.query(User).filter_by(chat_id=from_id).update({"time_monitor": TIME_TO_MONITOR+1})
                session.commit()
                TIME_TO_MONITOR = session.query(User).filter_by(chat_id=from_id).one_or_none().time_monitor
                await self.editor.editMessageText(f"<b>Time to Monitor:</b> <code>{TIME_TO_MONITOR} Minutes</code>\n<b>Price up percent:</b> <code>{WIN_PERCENT}%</code>\n<b>Price loss percent:</b> <code>{LOSS_PERCENT}%</code>", reply_markup=self.conf_keyboad, parse_mode="html")
            
            elif "_".join(query_data.split("_")[1::]) == "LOSS_ADD":
                session.query(User).filter_by(chat_id=from_id).update({"loss_percent": LOSS_PERCENT+1})
                session.commit()
                LOSS_PERCENT = session.query(User).filter_by(chat_id=from_id).one_or_none().loss_percent
                await self.editor.editMessageText(f"<b>Time to Monitor:</b> <code>{TIME_TO_MONITOR} Minutes</code>\n<b>Price up percent:</b> <code>{WIN_PERCENT}%</code>\n<b>Price loss percent:</b> <code>{LOSS_PERCENT}%</code>", reply_markup=self.conf_keyboad, parse_mode="html")
            
            elif "_".join(query_data.split("_")[1::]) == "LOSS_SUB":
                if LOSS_PERCENT > 1:
                    session.query(User).filter_by(chat_id=from_id).update({"loss_percent": LOSS_PERCENT-1})
                    session.commit()
                    LOSS_PERCENT = session.query(User).filter_by(chat_id=from_id).one_or_none().loss_percent
                    await self.editor.editMessageText(f"<b>Time to Monitor:</b> <code>{TIME_TO_MONITOR} Minutes</code>\n<b>Price up percent:</b> <code>{WIN_PERCENT}%</code>\n<b>Price loss percent:</b> <code>{LOSS_PERCENT}%</code>", reply_markup=self.conf_keyboad, parse_mode="html")
                else:
                    await self.bot.answerCallbackQuery(query_id, text='This is the minimum loss!')
            
            elif "_".join(query_data.split("_")[1::]) == "WIN_ADD":
                session.query(User).filter_by(chat_id=from_id).update({"win_percent": WIN_PERCENT+1})
                session.commit()
                WIN_PERCENT = session.query(User).filter_by(chat_id=from_id).one_or_none().win_percent
                await self.editor.editMessageText(f"<b>Time to Monitor:</b> <code>{TIME_TO_MONITOR} Minutes</code>\n<b>Price up percent:</b> <code>{WIN_PERCENT}%</code>\n<b>Price loss percent:</b> <code>{LOSS_PERCENT}%</code>", reply_markup=self.conf_keyboad, parse_mode="html")
            
            elif "_".join(query_data.split("_")[1::]) == "WIN_SUB":
                if WIN_PERCENT > 1:
                    session.query(User).filter_by(chat_id=from_id).update({"win_percent": WIN_PERCENT-1})
                    session.commit()
                    WIN_PERCENT = session.query(User).filter_by(chat_id=from_id).one_or_none().win_percent
                    await self.editor.editMessageText(f"<b>Time to Monitor:</b> <code>{TIME_TO_MONITOR} Minutes</code>\n<b>Price up percent:</b> <code>{WIN_PERCENT}%</code>\n<b>Price loss percent:</b> <code>{LOSS_PERCENT}%</code>", reply_markup=self.conf_keyboad, parse_mode="html")
                else:
                    await self.bot.answerCallbackQuery(query_id, text='This is the minimum win!')
        
        elif "RETURN" in query_data:
            if query_data.split("_")[1] == "HOME":
                await self.editor.editMessageText("Help", reply_markup=self.help_keyboard)
        
        elif "DONATE" == query_data:
            await self.editor.editMessageText(f"🎁 <b>Wallets</b> 🎁\n\n<b>Bitcoin:</b> <code>{BTC_ADDR}</code>\n<b>Etherium:</b> <code>{ETH_ADDR}</code>\n<b>Bitcoin Cash:</b> <code>{BTC_CASH_ADDR}</code>\n\n<b>Note</b>\n<code>If you need other types of address please tell in my telegram: {CREATOR}</code>", parse_mode="html", reply_markup=self.return_keyboard)
        
    async def on_chat_message(self, msg):
        await self.recived_message(msg)      

bot = amanobot.aio.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['private']), create_open, Bitcoin, timeout=30),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())

print('Listening ...')

loop.run_forever()