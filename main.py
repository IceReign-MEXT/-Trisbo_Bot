import json
import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
CHAT_ID = config["telegram_chat_id"]
SOL_WALLET = config["wallet_address"]
ETH_WALLET = config["eth_wallet_address"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello {config['owner_name']} 👋\n"
        f"Tracking wallets:\n"
        f"🔹 SOL: {SOL_WALLET}\n"
        f"🔹 ETH: {ETH_WALLET}"
    )

# Command: /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sol_balance = get_solana_balance(SOL_WALLET)
    eth_balance = get_eth_balance(ETH_WALLET)
    await update.message.reply_text(
        f"💰 Balances:\n"
        f"🔹 SOL: {sol_balance} SOL\n"
        f"🔹 ETH: {eth_balance} ETH"
    )

# Get Solana balance
def get_solana_balance(address):
    try:
        url = f"https://api.mainnet-beta.solana.com"
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

# Get Ethereum balance
def get_eth_balance(address):
    try:
        api_key = "https://api.etherscan.io/api"
        r = requests.get(
            f"{api_key}?module=account&action=balance&address={address}&tag=latest&apikey=YourEtherscanAPI"
        )
        wei = int(r.json()["result"])
        return wei / 1e18
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.run_polling()