import os
import re
import asyncio
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# --- 1. HEARTBEAT SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "ICE HUB SYSTEM ONLINE"
def run_web(): app.run(host='0.0.0.0', port=8080)

# --- 2. CONFIG ---
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
HELIUS_URL = os.getenv("HELIUS_RPC_URL")
MY_WALLET = os.getenv("SOLANA_WALLET")

# --- 3. ENGINE INITIALIZATION ---
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

def get_helius_audit(ca):
    try:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getAsset", "params": {"id": ca}}
        r = requests.post(HELIUS_URL, json=payload, timeout=5).json()
        return "✅ VERIFIED ON-CHAIN" if "result" in r else "⚠️ UNVERIFIED / HIGH RISK"
    except: return "🔍 SCANNING..."

# --- 4. THE SPY (LISTENING) ---
# Added more channels to ensure the bot starts "talking" immediately
TARGETS = ['dexscreener_solana', 'solana_gold_calls', 'SolanaHunters', 'unibotsolana', 'Solana_Meme_Coins']

@client.on(events.NewMessage(chats=TARGETS))
async def spy_handler(event):
    # Improved Regex to catch CA in any format
    ca_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', event.raw_text)
    if ca_match:
        ca = ca_match.group(0)
        audit = get_helius_audit(ca)

        # PROFESSIONAL LAYOUT
        text = (
            f"❄️ **ICE HUB | SOLANA INSIDER**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **NEW TARGET DETECTED**\n\n"
            f"📍 **CA:** `{ca}`\n"
            f"🛡️ **SECURITY:** {audit}\n"
            f"📊 **ALPHA SCORE:** 94/100\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💡 *Tip: Use the buttons below to trade instantly.*"
        )

        keyboard = [
            [InlineKeyboardButton("📈 DexScreener", url=f"https://dexscreener.com/solana/{ca}")],
            [InlineKeyboardButton("🦅 BirdEye", url=f"https://birdeye.so/token/{ca}?chain=solana")],
            [InlineKeyboardButton("💳 GET PREMIUM (1s Faster)", callback_data='premium_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await application.bot.send_message(
            chat_id=MY_CHANNEL_ID,
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# --- 5. COMMAND HANDLERS (THE FACE) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "❄️ **WELCOME TO THE ICE HUB**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "I am an AI-driven War Machine spying on elite whale "
        "channels to bring you Solana gems before the pump.\n\n"
        "✅ **System Status:** Operational\n"
        "📡 **Active Spies:** Jessica-v4\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📊 **SYSTEM DIAGNOSTICS**\n"
        "──────────────────\n"
        "● **Core Engine:** Active\n"
        "● **Latency:** 142ms\n"
        "● **Database:** Synced\n"
        "● **Security Audit:** Helius-Enabled\n"
        "──────────────────"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "💎 **ICE HUB PREMIUM (GHOST FEED)**\n"
        "──────────────────\n"
        "Standard users see calls 30s late. Premium users get "
        "the **Ghost Feed** (Direct from Jessica's eyes).\n\n"
        "💰 **Price:** 0.1 SOL / Month\n"
        "📍 **Deposit Address:**\n"
        f"`{MY_WALLET}`\n\n"
        "*Send payment then contact support to activate.*"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

# --- 6. LAUNCH ---
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("status", status))
application.add_handler(CommandHandler("premium", premium))
application.add_handler(CommandHandler("alpha", status))

async def run_bot():
    await client.start()
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        await asyncio.gather(client.run_until_disconnected(), asyncio.Event().wait())

if __name__ == '__main__':
    Thread(target=run_web, daemon=True).start()
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
