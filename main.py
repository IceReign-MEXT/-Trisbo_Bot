import os
import re
import asyncio
import requests
import json
import websockets
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# --- 1. HEARTBEAT (For UptimeRobot) ---
app = Flask(__name__)
@app.route('/')
def home(): return "GHOST PROTOCOL: ACTIVE"
def run_web(): app.run(host='0.0.0.0', port=8080)

# --- 2. CONFIG ---
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
HELIUS_URL = os.getenv("HELIUS_RPC_URL")
MY_WALLET = os.getenv("SOLANA_WALLET")
# Extract API Key from URL for WSS
HELIUS_KEY = "1b0094c2-50b9-4c97-a2d6-2c47d4ac2789"
HELIUS_WSS = f"wss://mainnet.helius-rpc.com/?api-key={HELIUS_KEY}"

# --- 3. CORE ENGINES ---
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
application = ApplicationBuilder().token(BOT_TOKEN).build()

def get_helius_audit(ca):
    try:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getAsset", "params": {"id": ca}}
        r = requests.post(HELIUS_URL, json=payload, timeout=5).json()
        return ("✅ VERIFIED", 95) if "result" in r else ("⚠️ HIGH RISK", 30)
    except: return ("🔍 SCANNING...", 50)

async def send_alert(ca, source="ON-CHAIN GHOST"):
    audit, score = get_helius_audit(ca)
    text = (
        f"❄️ **ICE HUB | {source}**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **NEW TARGET ACQUIRED**\n\n"
        f"📍 **CA:** `{ca}`\n"
        f"🛡️ **SECURITY:** {audit}\n"
        f"📊 **ALPHA SCORE:** {score}/100\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚡️ *Bypassing the Cartels in real-time.*"
    )
    kb = [[InlineKeyboardButton("📈 DexScreener", url=f"https://dexscreener.com/solana/{ca}")],
          [InlineKeyboardButton("💳 GET PREMIUM (1s Faster)", callback_data='p')]]

    await application.bot.send_message(
        chat_id=MY_CHANNEL_ID,
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(kb)
    )

# --- 4. THE GHOST (Blockchain Websocket) ---
async def start_ghost_hunter():
    print("🛰️ GHOST HUNTER: Connecting to Solana Websocket...")
    while True:
        try:
            async with websockets.connect(HELIUS_WSS) as ws:
                subscribe_msg = {
                    "jsonrpc": "2.0", "id": 1, "method": "logsSubscribe",
                    "params": [{"mentions": ["675kPX9MHTjS2zt1qnk1fzM9z822Wcx2W39BKU65AST5"]}, {"commitment": "processed"}]
                }
                await ws.send(json.dumps(subscribe_msg))
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if "initialize2" in str(data): # Raydium New Pool instruction
                        ca_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', str(data))
                        if ca_match:
                            await send_alert(ca_match.group(0), source="ON-CHAIN GHOST")
        except Exception as e:
            print(f"Websocket lost. Reconnecting... ({e})")
            await asyncio.sleep(5)

# --- 5. THE SPY (Jessica) ---
TARGETS = ['dexscreener_solana', 'solana_gold_calls', 'SolanaHunters', 'unibotsolana', 'SolanaNewListings']
@client.on(events.NewMessage(chats=TARGETS))
async def spy_handler(event):
    ca_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', event.raw_text)
    if ca_match:
        await send_alert(ca_match.group(0), source="ELITE CHANNEL LEAK")

# --- 6. COMMANDS ---
async def start(u, c):
    await u.message.reply_text("❄️ **ICE HUB ONLINE**\nStatus: Ghost Protocol Active.")

application.add_handler(CommandHandler("start", start))

# --- 7. START ENGINE ---
async def run_war_machine():
    await client.start()
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("✅ WAR MACHINE IS FULLY OPERATIONAL!")
        await asyncio.gather(
            client.run_until_disconnected(),
            start_ghost_hunter(),
            asyncio.Event().wait()
        )

if __name__ == '__main__':
    Thread(target=run_web, daemon=True).start()
    try:
        asyncio.run(run_war_machine())
    except KeyboardInterrupt:
        pass
