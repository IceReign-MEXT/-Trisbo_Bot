import os
import re
import asyncio
import requests
import sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# --- 1. THE HEARTBEAT (Flask for Render/UptimeRobot) ---
app = Flask(__name__)
@app.route('/')
def home():
    return "WAR MACHINE IS ALIVE"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# --- 2. CONFIGURATION ---
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
HELIUS_URL = os.getenv("HELIUS_RPC_URL")
MY_WALLET = os.getenv("SOLANA_WALLET")

# --- 3. THE SPY LOGIC (Telethon) ---
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

def get_helius_audit(ca):
    try:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getAsset", "params": {"id": ca}}
        r = requests.post(HELIUS_URL, json=payload, timeout=5).json()
        return "✅ VERIFIED" if "result" in r else "⚠️ UNKNOWN"
    except:
        return "🔍 SCANNING..."

TARGETS = ['dexscreener_solana', 'solana_gold_calls', 'SolanaHunters']

@client.on(events.NewMessage(chats=TARGETS))
async def spy_handler(event):
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
        # Use the application's bot instance to send
        await application.bot.send_message(chat_id=MY_CHANNEL_ID, text=msg, parse_mode='Markdown')

# --- 4. THE COMMAND HANDLERS (Python-Telegram-Bot) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ **ICE HUB WAR MACHINE ONLINE**\nStatus: 24/7 Alpha Spying Active.")

async def alpha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Check the main channel for the latest signals.")

# --- 5. THE UNIFIED ENGINE ---
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("alpha", alpha))

async def run_bot():
    # Start Telethon (The Spy)
    await client.start()
    print("✅ SPY (JESSICA) IS ONLINE")

    # Start the Bot Application (The Broadcaster)
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("✅ BROADCASTER (BOT) IS ONLINE")

        # Keep both running
        await asyncio.gather(
            client.run_until_disconnected(),
            # Wait forever
            asyncio.Event().wait()
        )

if __name__ == '__main__':
    # Start Web Server in a separate thread
    Thread(target=run_web, daemon=True).start()

    # Run the main bot loop
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
