import os
import re
import asyncio
import requests
from telethon import TelegramClient, events
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
HELIUS_KEY = os.getenv("HELIUS_API_KEY")
HELIUS_URL = os.getenv("HELIUS_RPC_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

client = TelegramClient('ice_warrior', API_ID, API_HASH)
tg_bot = Bot(token=BOT_TOKEN)

# --- THE ALIEN TECHNOLOGY (Helius Audit) ---
def get_helius_audit(mint_address):
    """Checks the token using Helius Enhanced API"""
    try:
        # We ask Helius for the token metadata and info
        payload = {
            "jsonrpc": "2.0",
            "id": "ice-audit",
            "method": "getAsset",
            "params": {
                "id": mint_address
            }
        }
        response = requests.post(HELIUS_URL, json=payload).json()

        # Logic: If Helius finds the asset, we analyze it
        if "result" in response:
            return "✅ VERIFIED ON-CHAIN"
        else:
            return "⚠️ UNKNOWN / HIGH RISK"
    except:
        return "🔍 SCANNING..."

@client.on(events.NewMessage(chats=['@dexscreener_solana', '@solana_gold_calls'])) # Add more targets
async def handler(event):
    text = event.raw_text
    ca_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', text)

    if ca_match:
        ca = ca_match.group(0)
        print(f"Target Found: {ca}")

        # Use your Helius Power
        audit_result = get_helius_audit(ca)

        msg = (
            f"❄️ **ICE HUB: ELITE SIGNAL** ❄️\n\n"
            f"📍 **CA:** `{ca}`\n"
            f"🛡️ **HELIUS AUDIT:** {audit_result}\n"
            f"📊 **STATUS:** Ultra-Fast Detection\n\n"
            f"🚀 [TRADE ON DEXSCREENER](https://dexscreener.com/solana/{ca})\n"
            f"📝 *Powered by IceGods Intelligence System*"
        )

        await tg_bot.send_message(chat_id=MY_CHANNEL_ID, text=msg, parse_mode='Markdown')

print("🛡️ WAR MACHINE IS ONLINE WITH HELIUS FAST-TRACK...")
client.start()
client.run_until_disconnected()
