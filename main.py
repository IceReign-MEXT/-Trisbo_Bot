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

# --- DEFENSIVE CONFIG ---
# .strip() removes accidental spaces from Render environment variables
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHANNEL_ID = os.getenv("CHANNEL_ID")
HELIUS_URL = os.getenv("HELIUS_RPC_URL")
MY_WALLET = os.getenv("SOLANA_WALLET")

if not SESSION_STRING:
    print("❌ ERROR: SESSION_STRING is empty in Render settings.")
    sys.exit(1)

try:
    # Initialize Spy (Jessica Account)
    client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
    # Initialize Broadcaster (Old Bot)
    tg_bot = Bot(token=BOT_TOKEN)
except Exception as e:
    print(f"❌ FATAL ERROR STARTING CLIENT: {e}")
    print("This means your SESSION_STRING is still corrupted. Re-generate it in Termux.")
    sys.exit(1)

def get_helius_audit(ca):
    try:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getAsset", "params": {"id": ca}}
        r = requests.post(HELIUS_URL, json=payload, timeout=5).json()
        return "✅ VERIFIED" if "result" in r else "⚠️ UNKNOWN"
    except:
        return "🔍 SCANNING..."

TARGETS = ['dexscreener_solana', 'solana_gold_calls', 'SolanaHunters', 'unibotsolana']

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
            f"🚀 [TRADE](https://dexscreener.com/solana/{ca})\n"
            f"⚡️ *Bypassing the Cartels.*"
        )
        try:
            await tg_bot.send_message(chat_id=int(MY_CHANNEL_ID), text=msg, parse_mode='Markdown')
        except Exception as e:
            print(f"Broadcast Error: {e}")

async def main():
    print("🛡️ WAR MACHINE STARTING...")
    try:
        await client.start()
        print("✅ SUCCESS: WAR MACHINE IS ONLINE!")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ LOGIN FAILED: {e}")
        print("Your session string is likely expired or copied incorrectly.")

if __name__ == '__main__':
    asyncio.run(main())
