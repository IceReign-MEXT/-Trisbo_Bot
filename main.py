import json
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
WALLETS = config["wallets"]
API_KEYS = config["api_keys"]
OWNER_NAME = config["owner_name"]
SUBSCRIPTION_PRICES = config["subscription_prices"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

scheduler = AsyncIOScheduler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello {OWNER_NAME} 👋\n"
        f"Tracking wallets:\n"
        f"🔹 SOL: {WALLETS['solana']}\n"
        f"🔹 ETH: {WALLETS['ethereum']}\n"
        f"🔹 BNB: {WALLETS['bnb']}"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sol_balance = get_solana_balance(WALLETS['solana'])
    eth_balance = get_eth_balance(WALLETS['ethereum'])
    bnb_balance = get_bnb_balance(WALLETS['bnb'])
    await update.message.reply_text(
        f"💰 Balances:\n"
        f"🔹 SOL: {sol_balance} SOL\n"
        f"🔹 ETH: {eth_balance} ETH\n"
        f"🔹 BNB: {bnb_balance} BNB"
    )

# Helpers to get balances
def get_solana_balance(address):
    try:
        url = "https://api.mainnet-beta.solana.com"
        payload = {
            "jsonrpc":"2.0",
            "id":1,
            "method":"getBalance",
            "params":[address]
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, json=payload, headers=headers)
        lamports = r.json()["result"]["value"]
        return lamports / 1_000_000_000
    except Exception as e:
        return f"Error: {e}"

def get_eth_balance(address):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={API_KEYS['etherscan']}"
        r = requests.get(url)
        wei = int(r.json()["result"])
        return wei / 1e18
    except Exception as e:
        return f"Error: {e}"

def get_bnb_balance(address):
    try:
        url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={API_KEYS['bscscan']}"
        r = requests.get(url)
        wei = int(r.json()["result"])
        return wei / 1e18
    except Exception as e:
        return f"Error: {e}"

# Subscription placeholder (to be expanded with payment processor)
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Subscription options:\n"
        f"3 hours - ${SUBSCRIPTION_PRICES['3_hours']}\n"
        f"6 hours - ${SUBSCRIPTION_PRICES['6_hours']}\n"
        f"12 hours - ${SUBSCRIPTION_PRICES['12_hours']}\n"
        f"24 hours - ${SUBSCRIPTION_PRICES['24_hours']}\n"
        "Reply with your choice to subscribe."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Welcome message\n"
        "/check - Check wallet balances\n"
        "/subscribe - View subscription plans\n"
        "/help - Show this help message"
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and update.message:
        await update.message.reply_text('An error occurred. Please try again later.')

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("help", help_command))
    app.add_error_handler(error_handler)

    # Add scheduler jobs if needed here (like periodic balance updates)

    app.run_polling()

if __name__ == "__main__":
    main()