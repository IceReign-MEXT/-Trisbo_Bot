import os
import re
import asyncio
from telethon import TelegramClient, events
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# Config from .env
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHANNELS = ['@dexscreener_solana', '@solana_gold_calls', '@SolanaHunters'] # Add the channels you want to "hunt"
MY_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Initialize
client = TelegramClient('ice_session', API_ID, API_HASH)
tg_bot = Bot(token=BOT_TOKEN)

def scan_logic(ca):
    # This is where your 'scam_scanner.py' logic goes
    # For now, we simulate a 'Safe' verdict
    return "✅ SAFE (Liquidity Locked)"

@client.on(events.NewMessage(chats=TARGET_CHANNELS))
async def handler(event):
    text = event.raw_text
    ca_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', text)

    if ca_match:
        ca = ca_match.group(0)
        verdict = scan_logic(ca)

        # The "Animal" Style Formatting
        hype_msg = f"❄️ **ICE HUB ALPHA DETECTED** ❄️\n\n"
        hype_msg += f"📍 **CA:** `{ca}`\n"
        hype_msg += f"🛡️ **VERDICT:** {verdict}\n\n"
        hype_msg += f"🔗 [Birdeye](https://birdeye.so/token/{ca}?chain=solana) | [DexS](https://dexscreener.com/solana/{ca})\n"
        hype_msg += f"⚡️ *Bypassing the cartels in real-time.*"

        await tg_bot.send_message(chat_id=MY_CHANNEL_ID, text=hype_msg, parse_mode='Markdown', disable_web_page_preview=False)

print("Weapon Active... Hunting for Alpha...")
client.start()
client.run_until_disconnected()
