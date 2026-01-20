import os
import re
import asyncio
import requests
import sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# --- WEB SERVER FOR UPTIME ROBOT ---
app = Flask('')
@app.route('/')
def home():
    return "WAR MACHINE IS ALIVE"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# --- CONFIG ---
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHANNEL_ID = os.getenv("CHANNEL_ID")
HELIUS_URL = os.getenv("HELIUS_RPC_URL")
MY_WALLET = os.getenv("SOLANA_WALLET")

# Initialize
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
tg_bot = Bot(token=BOT_TOKEN)

# --- BOT COMMANDS ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ ICE HUB WAR MACHINE ONLINE.\nI am spying on Alpha channels 24/7.")

# --- SPY LOGIC ---
def get_helius_audit(ca):
    try:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getAsset", "params": {"id": ca}}
        r = requests.post(HELIUS_URL, json=payload, timeout=5).json()
        return "✅ VERIFIED" if "result" in r else "⚠️ UNKNOWN"
    except:
        return "🔍 SCANNING..."

TARGETS = ['dexscreener_solana', 'solana_gold_calls', 'SolanaHunters']

@client.on(events.NewMessage(chats=TARGETS))
async def handler(event):
    ca_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', event.raw_text)
    if ca_match:
        ca = ca_match.group(0)
        audit = get_helius_audit(ca)
        msg = (
            f"❄️ **ICE HUB: ELITE ALPHA** ❄️\n\n"
            f"📍 **CA:** `{ca}`\n"
            f"🛡️ **HELIUS:** {audit}\n\n"
            f"💎 **EARLY ACCESS?** Send 0.1 SOL to:\n"
            f"`{MY_WALLET}`\n\n"
            f"🚀 [TRADE](https://dexscreener.com/solana/{ca})"
        )
        await tg_bot.send_message(chat_id=int(MY_CHANNEL_ID), text=msg, parse_mode='Markdown')

async def main():
    # Start the "Speaker" (Bot Commands)
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))

    # Start the "Spy" (Jessica Account)
    await client.start()
    print("🛡️ WAR MACHINE IS ONLINE!")

    # Run both simultaneously
    await asyncio.gather(
        client.run_until_disconnected(),
        application.run_polling()
    )

if __name__ == '__main__':
    # Start the Web Server thread for UptimeRobot
    Thread(target=run_web).start()
    # Start the Bot
    asyncio.run(main())
