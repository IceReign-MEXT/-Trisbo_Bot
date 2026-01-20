import os
import re
import asyncio
import requests
import sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# --- CHECKPOINTS ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHANNEL_ID = os.getenv("CHANNEL_ID")
HELIUS_URL = os.getenv("HELIUS_RPC_URL")

if not SESSION_STRING:
    print("❌ ERROR: SESSION_STRING IS MISSING!")
    print("Go to Render -> Environment and add SESSION_STRING.")
    sys.exit(1) # Stop the bot before it asks for a phone number

print("🛡️ WAR MACHINE ATTEMPTING LOGIN...")

# Initialize
client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
tg_bot = Bot(token=BOT_TOKEN)

def get_helius_audit(mint_address):
    try:
        payload = {"jsonrpc": "2.0", "id": "ice", "method": "getAsset", "params": {"id": mint_address}}
        response = requests.post(HELIUS_URL, json=payload).json()
        return "✅ VERIFIED" if "result" in response else "⚠️ HIGH RISK"
    except:
        return "🔍 SCANNING..."

@client.on(events.NewMessage(chats=['@dexscreener_solana', '@solana_gold_calls', '@SolanaHunters']))
async def handler(event):
    ca_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', event.raw_text)
    if ca_match:
        ca = ca_match.group(0)
        audit = get_helius_audit(ca)
        msg = (
            f"❄️ **ICE HUB: ELITE DETECTION** ❄️\n\n"
            f"📍 **CA:** `{ca}`\n"
            f"🛡️ **HELIUS:** {audit}\n\n"
            f"🚀 [TRADE](https://dexscreener.com/solana/{ca})\n"
            f"⚡️ *Bypassing the Cartels.*"
        )
        await tg_bot.send_message(chat_id=int(MY_CHANNEL_ID), text=msg, parse_mode='Markdown')

async def start_bot():
    await client.start() # This will now use the string and NOT ask for a phone
    print("✅ SUCCESS: WAR MACHINE IS ONLINE AND HUNTING!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
