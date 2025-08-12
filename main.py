import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Wallets
SOLANA_WALLET = os.getenv('SOLANA_WALLET')
ETHEREUM_WALLET = os.getenv('ETHEREUM_WALLET')

# Receiving wallets for payments
RECEIVING_ETH_WALLET = os.getenv('RECEIVING_ETH_WALLET')
RECEIVING_SOL_WALLET = os.getenv('RECEIVING_SOL_WALLET')

# API Keys
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')
POLYGONSCAN_API_KEY = os.getenv('POLYGONSCAN_API_KEY')

# Prices (USD)
PRICES = {
    "3h": int(os.getenv('SUBSCRIPTION_PRICES_3H', 5)),
    "6h": int(os.getenv('SUBSCRIPTION_PRICES_6H', 8)),
    "12h": int(os.getenv('SUBSCRIPTION_PRICES_12H', 12)),
    "24h": int(os.getenv('SUBSCRIPTION_PRICES_24H', 20)),
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"Hello {update.effective_user.first_name} 👋\n"
        "Tracking wallets:\n"
        f"🔹 SOL: {SOLANA_WALLET}\n"
        f"🔹 ETH: {ETHEREUM_WALLET}\n\n"
        "Use /check to see balances.\n"
        "Use /subscribe <3h|6h|12h|24h> to subscribe."
    )
    await update.message.reply_text(msg)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Call Etherscan API for ETH balance
    eth_balance = await fetch_eth_balance(ETHEREUM_WALLET)
    # Call Solana API for SOL balance
    sol_balance = await fetch_sol_balance(SOLANA_WALLET)

    msg = (
        f"💰 Balances:\n"
        f"🔹 SOL: {sol_balance} SOL\n"
        f"🔹 ETH: {eth_balance} ETH"
    )
    await update.message.reply_text(msg)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        duration = context.args[0]
        price = PRICES.get(duration)
        if not price:
            await update.message.reply_text("Invalid subscription duration. Use 3h, 6h, 12h or 24h.")
            return

        # Here add payment logic, smart contract call, or payment address display
        # For demo, we send payment info:
        await update.message.reply_text(
            f"Subscription for {duration} costs ${price}. "
            f"Please send payment to:\nETH: {RECEIVING_ETH_WALLET}\nSOL: {RECEIVING_SOL_WALLET}"
        )
    except IndexError:
        await update.message.reply_text("Usage: /subscribe <3h|6h|12h|24h>")

async def fetch_eth_balance(address: str):
    url = (
        f"https://api.etherscan.io/api?module=account&action=balance&address={address}"
        f"&tag=latest&apikey={ETHERSCAN_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        if data['status'] == '1':
            # Balance is in Wei, convert to ETH
            return round(int(data['result']) / 10**18, 6)
        else:
            return f"Error: {data.get('message', 'Unknown')}"

async def fetch_sol_balance(address: str):
    # Using public Solana API for demo - replace with a reliable API if needed
    url = f"https://api.mainnet-beta.solana.com"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [address]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        data = response.json()
        if 'result' in data:
            lamports = data['result']['value']
            sol = lamports / 10**9
            return sol
        else:
            return "Error"

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("subscribe", subscribe))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()