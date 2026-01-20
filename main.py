import os
import re
import asyncio
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
HELIUS_URL = os.getenv("HELIUS_RPC_URL")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
tg_bot = Bot(token=BOT_TOKEN)

def get_helius_audit(mint_address):
    try:
        payload = {"jsonrpc": "2.0", "id": "ice", "method": "getAsset", "params": {"id": mint_address}}
        response = requests.post(HELIUS_URL, json=payload).json()
        return "✅ VERIFIED ON-CHAIN" if "result" in response else "⚠️ HIGH RISK"
    except:
        return "🔍 SCANNING..."

@client.on(events.NewMessage(chats=['@dexscreener_solana', '@solana_gold_calls', '@SolanaHunters']))
async def handler(event):
    ca_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', event.raw_text)
    if ca_match:
        ca = ca_match.group(0)
        audit = get_helius_audit(ca)
        msg = (
            f"❄️ **ICE HUB: ALREADY DETECTED** ❄️\n\n"
            f"📍 **CA:** `{ca}`\n"
            f"🛡️ **HELIUS:** {audit}\n\n"
            f"🚀 [TRADE](https://dexscreener.com/solana/{ca})\n"
            f"⚡️ *Bypassing the Cartels.*"
        )
        await tg_bot.send_message(chat_id=MY_CHANNEL_ID, text=msg, parse_mode='Markdown')

print("🛡️ WAR MACHINE IS ONLINE. NO LOGIN NEEDED.")
client.start()
client.run_until_disconnected()
