import json
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
CHAT_ID = config["telegram_chat_id"]
SOL_WALLET = config["wallet_address"]
ETH_WALLET = config["eth_wallet_address"]
ETHERSCAN_API_KEY = config["etherscan_api_key"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

CHAINS = [1, 42161, 56, 137, 10]  # Ethereum mainnet + Arbitrum + BSC + Polygon + Optimism chain IDs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello {config['owner_name']} 👋\n"
        f"Tracking wallets:\n"
        f"🔹 SOL: {SOL_WALLET}\n"
        f"🔹 ETH: {ETH_WALLET}"
    )

def get_sol_balance(address):
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

def get_eth_balances(address):
    balances = {}
    for chain_id in CHAINS:
        try:
            url = (
                f"https://api.etherscan.io/v2/api?"
                f"chainid={chain_id}&module=account&action=balance"
                f"&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
            )
            r = requests.get(url)
            data = r.json()
            if data.get("status") == "1":
                wei = int(data["result"])
                balances[chain_id] = wei / 1e18
            else:
                balances[chain_id] = f"Error: {data.get('message')}"
        except Exception as e:
            balances[chain_id] = f"Exception: {e}"
    return balances

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sol_balance = get_sol_balance(SOL_WALLET)
    eth_balances = get_eth_balances(ETH_WALLET)

    message = f"💰 Balances:\n🔹 SOL: {sol_balance} SOL\n"
    for chain_id, balance in eth_balances.items():
        message += f"🔹 Chain {chain_id}: {balance} ETH\n"

    await update.message.reply_text(message)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.run_polling()