import json
import logging
import asyncio
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

import requests
import httpx

# Load config
with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
OWNER_ID = config["telegram_owner_id"]
SECRET_KEY = config["secret_key"]
WALLETS = config["wallets"]
SUB_PRICES = config["subscription_prices"]

ETHERSCAN_API_KEY = config["etherscan_api_key"]
BSCSCAN_API_KEY = config["bscscan_api_key"]
POLYGON_API_KEY = config["polygon_api_key"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# In-memory subscriptions: user_id -> expiry datetime
user_subscriptions = {}

# Security check decorator
def authorized(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != OWNER_ID:
            await update.message.reply_text("❌ Unauthorized access. This bot is private.")
            return
        return await func(update, context)
    return wrapper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    reply = (
        f"Hello {user.first_name} 👋\n"
        f"Tracking wallets:\n"
        f"🔹 SOL: {WALLETS['solana']}\n"
        f"🔹 ETH: {WALLETS['ethereum']}\n"
        f"🔹 Polygon: {WALLETS['polygon']}\n"
        f"🔹 BNB: {WALLETS['bnb']}\n\n"
        "Use /check to get wallet balances.\n"
        "Use /subscribe to buy subscription plans.\n"
        "Use /help for assistance."
    )
    await update.message.reply_text(reply)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Show welcome message\n"
        "/check - Show tracked wallet balances\n"
        "/subscribe - View subscription plans\n"
        "/status - Check your subscription status\n"
    )
    await update.message.reply_text(help_text)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user is subscribed
    user_id = update.effective_user.id
    now = datetime.utcnow()
    expiry = user_subscriptions.get(user_id)

    if not expiry or expiry < now:
        await update.message.reply_text(
            "⚠️ You are not subscribed or your subscription has expired.\n"
            "Please use /subscribe to get access."
        )
        return

    sol_balance = get_solana_balance(WALLETS["solana"])
    eth_balance = get_eth_balance(WALLETS["ethereum"])
    polygon_balance = get_polygon_balance(WALLETS["polygon"])
    bnb_balance = get_bnb_balance(WALLETS["bnb"])

    reply = (
        "💰 Wallet Balances:\n"
        f"🔹 SOL: {sol_balance} SOL\n"
        f"🔹 ETH: {eth_balance} ETH\n"
        f"🔹 Polygon: {polygon_balance} MATIC\n"
        f"🔹 BNB: {bnb_balance} BNB\n"
    )
    await update.message.reply_text(reply)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"3 Hours - ${SUB_PRICES['3h']}", callback_data="sub_3h")],
        [InlineKeyboardButton(f"6 Hours - ${SUB_PRICES['6h']}", callback_data="sub_6h")],
        [InlineKeyboardButton(f"12 Hours - ${SUB_PRICES['12h']}", callback_data="sub_12h")],
        [InlineKeyboardButton(f"24 Hours - ${SUB_PRICES['24h']}", callback_data="sub_24h")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your subscription plan:", reply_markup=reply_markup)

async def subscription_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    plan = query.data  # e.g. sub_3h

    if user_id != OWNER_ID:
        await query.edit_message_text("❌ Unauthorized. This bot is private.")
        return

    hours = int(plan.split("_")[1].replace("h", ""))
    price = SUB_PRICES[f"{hours}h"]

    # Here, implement payment check logic or smart contract verification
    # Placeholder: Automatically grant subscription for demo
    expiry_time = datetime.utcnow() + timedelta(hours=hours)
    user_subscriptions[user_id] = expiry_time

    await query.edit_message_text(
        f"✅ Subscription activated for {hours} hours.\n"
        f"Expires at UTC: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Amount charged: ${price}\n\n"
        f"Start using /check now!"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    expiry = user_subscriptions.get(user_id)
    now = datetime.utcnow()

    if expiry and expiry > now:
        remaining = expiry - now
        await update.message.reply_text(
            f"Your subscription is active.\nExpires in: {str(remaining).split('.')[0]}"
        )
    else:
        await update.message.reply_text("You have no active subscription.")

# Wallet balance functions

def get_solana_balance(address: str):
    try:
        url = "https://api.mainnet-beta.solana.com"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        lamports = r.json()["result"]["value"]
        return lamports / 1_000_000_000
    except Exception as e:
        return f"Error: {e}"

def get_eth_balance(address: str):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(url, timeout=10)
        wei = int(r.json()["result"])
        return wei / 1e18
    except Exception as e:
        return f"Error: {e}"

def get_polygon_balance(address: str):
    try:
        url = f"https://api.polygonscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={POLYGON_API_KEY}"
        r = requests.get(url, timeout=10)
        wei = int(r.json()["result"])
        return wei / 1e18
    except Exception as e:
        return f"Error: {e}"

def get_bnb_balance(address: str):
    try:
        url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={BSCSCAN_API_KEY}"
        r = requests.get(url, timeout=10)
        wei = int(r.json()["result"])
        return wei / 1e18
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CallbackQueryHandler(subscription_button, pattern="sub_.*"))
    app.add_handler(CommandHandler("status", status))

    print("Bot is starting...")

    app.run_polling()