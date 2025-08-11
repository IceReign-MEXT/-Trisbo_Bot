import json
import logging
import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Load config
with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
CHAT_ID = config["telegram_chat_id"]
SOL_WALLET = config["wallet_address_solana"]
ETH_WALLET = config["wallet_address_eth"]
ETHERSCAN_API_KEY = config["etherscan_api_key"]
PRICES = config["prices"]
OWNER_NAME = config["owner_name"]

logging.basicConfig(level=logging.INFO)
scheduler = AsyncIOScheduler()

# In-memory subscription store
subscriptions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello {OWNER_NAME} 👋\n"
        f"Tracking wallets:\n"
        f"🔹 SOL: {SOL_WALLET}\n"
        f"🔹 ETH: {ETH_WALLET}\n\n"
        "Use /subscribe <3h|6h|12h|24h> to activate a plan.\n"
        "Use /check to check balances.\n"
        "Use /status to check subscription status.\n"
        "Use /help for commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Welcome message\n"
        "/check - Check wallet balances\n"
        "/subscribe <plan> - Subscribe to a plan (3h, 6h, 12h, 24h)\n"
        "/status - Check subscription status\n"
    )
    await update.message.reply_text(help_text)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sol_balance = get_solana_balance(SOL_WALLET)
    eth_balance = get_eth_balance(ETH_WALLET)
    await update.message.reply_text(
        f"💰 Balances:\n🔹 SOL: {sol_balance} SOL\n🔹 ETH: {eth_balance} ETH"
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or context.args[0] not in PRICES:
        await update.message.reply_text("Usage: /subscribe <3h|6h|12h|24h>")
        return

    plan = context.args[0]
    price = PRICES[plan]
    user_id = update.effective_user.id

    # TODO: Replace with payment verification integration
    expire_time = datetime.utcnow() + timedelta(hours=int(plan[:-1]))
    subscriptions[user_id] = expire_time

    await update.message.reply_text(
        f"Subscription to {plan} plan activated for ${price}. Expires at {expire_time} UTC."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    expire = subscriptions.get(user_id)

    if expire and expire > datetime.utcnow():
        remaining = expire - datetime.utcnow()
        await update.message.reply_text(f"Subscription active. Time left: {remaining}.")
    else:
        await update.message.reply_text("No active subscription found. Use /subscribe.")

def get_solana_balance(address):
    try:
        url = "https://api.mainnet-beta.solana.com"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, json=payload, headers=headers)
        lamports = r.json()["result"]["value"]
        return lamports / 1_000_000_000
    except Exception as e:
        return f"Error: {e}"

def get_eth_balance(address):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(url)
        wei = int(r.json()["result"])
        return wei / 1e18
    except Exception as e:
        return f"Error: {e}"

async def sweep_funds_job():
    # TODO: Implement smart contract sweep logic here
    logging.info("Sweep funds job triggered.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("status", status))

    scheduler.add_job(sweep_funds_job, "interval", hours=1)
    scheduler.start()

    print("Bot started...")
    app.run_polling()