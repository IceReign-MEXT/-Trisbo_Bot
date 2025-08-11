import json
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
CHAT_ID = config["telegram_chat_id"]
WALLETS = config["wallets"]
ETHERSCAN_API_KEY = config["etherscan_api_key"]
OWNER_NAME = config["owner_name"]
PRICES = config["subscription_prices"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

scheduler = AsyncIOScheduler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"Hello {OWNER_NAME} 👋\n"
        f"Tracking wallets:\n"
        f"🔹 SOL: {WALLETS['solana']}\n"
        f"🔹 ETH: {WALLETS['ethereum']}\n"
        f"🔹 BNB: {WALLETS['bnb']}\n"
        f"\nUse /check to get balances.\n"
        f"Subscription Prices (USD):\n"
        f"3 hours - ${PRICES['3_hours']}\n"
        f"6 hours - ${PRICES['6_hours']}\n"
        f"12 hours - ${PRICES['12_hours']}\n"
        f"24 hours - ${PRICES['24_hours']}\n"
    )
    await update.message.reply_text(msg)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sol_balance = get_solana_balance(WALLETS["solana"])
    eth_balance = get_eth_balance(WALLETS["ethereum"])
    bnb_balance = get_bsc_balance(WALLETS["bnb"])

    msg = (
        f"💰 Balances:\n"
        f"🔹 SOL: {sol_balance} SOL\n"
        f"🔹 ETH: {eth_balance} ETH\n"
        f"🔹 BNB: {bnb_balance} BNB\n"
    )
    await update.message.reply_text(msg)

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

def get_bsc_balance(address):
    try:
        url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(url)
        wei = int(r.json()["result"])
        return wei / 1e18
    except Exception as e:
        return f"Error: {e}"

# Scheduler task example: log wallet balances every 6 hours
def scheduled_balance_check():
    sol = get_solana_balance(WALLETS["solana"])
    eth = get_eth_balance(WALLETS["ethereum"])
    bnb = get_bsc_balance(WALLETS["bnb"])
    logging.info(f"Scheduled check - SOL: {sol}, ETH: {eth}, BNB: {bnb}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    scheduler.add_job(scheduled_balance_check, 'interval', hours=6)
    scheduler.start()
    app.run_polling()