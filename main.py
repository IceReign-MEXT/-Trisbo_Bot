import json
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
CHAT_ID = config["telegram_chat_id"]
WALLETS = config["wallet_addresses"]
OWNER_NAME = config["owner_name"]

ETHERSCAN_API_KEY = config.get("etherscan_api_key")
BSCSCAN_API_KEY = config.get("bscscan_api_key")
POLYGONSCAN_API_KEY = config.get("polygonscan_api_key")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Pricing tiers in USD
PRICING_TIERS = {
    "3h": 5,
    "6h": 9,
    "12h": 16,
    "24h": 30
}

# Function placeholders for smart contract interaction
def smart_contract_payment_logic(user_id, tier):
    # Here you would add calls to smart contracts or your backend for subscription payments
    logger.info(f"Processing payment for user {user_id} for tier {tier}")
    # For now, just simulate success
    return True

# Balance check helpers
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
        response = requests.post(url, json=payload, headers=headers)
        lamports = response.json()["result"]["value"]
        return lamports / 1_000_000_000
    except Exception as e:
        logger.error(f"Solana balance fetch error for {address}: {e}")
        return f"Error: {e}"

def get_eth_balance(address, chain="ethereum"):
    try:
        api_key = None
        api_url = None
        if chain == "ethereum":
            api_key = ETHERSCAN_API_KEY
            api_url = "https://api.etherscan.io/api"
        elif chain == "bsc":
            api_key = BSCSCAN_API_KEY
            api_url = "https://api.bscscan.com/api"
        elif chain == "polygon":
            api_key = POLYGONSCAN_API_KEY
            api_url = "https://api.polygonscan.com/api"
        else:
            return "Unsupported chain"

        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
            "apikey": api_key
        }
        r = requests.get(api_url, params=params)
        wei = int(r.json()["result"])
        return wei / 1e18
    except Exception as e:
        logger.error(f"{chain.capitalize()} balance fetch error for {address}: {e}")
        return f"Error: {e}"

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallets_info = ""
    for chain, addresses in WALLETS.items():
        for addr in addresses:
            wallets_info += f"🔹 {chain.upper()}: {addr}\n"
    await update.message.reply_text(
        f"Hello {OWNER_NAME} 👋\nTracking wallets:\n{wallets_info}"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = []
    for sol_addr in WALLETS.get("solana", []):
        bal = get_solana_balance(sol_addr)
        results.append(f"🔹 SOL: {bal} SOL")
    for eth_addr in WALLETS.get("ethereum", []):
        bal = get_eth_balance(eth_addr, "ethereum")
        results.append(f"🔹 ETH: {bal} ETH")
    for bnb_addr in WALLETS.get("bnb", []):
        bal = get_eth_balance(bnb_addr, "bsc")
        results.append(f"🔹 BNB: {bal} BNB")
    for poly_addr in WALLETS.get("polygon", []):
        bal = get_eth_balance(poly_addr, "polygon")
        results.append(f"🔹 POLYGON: {bal} MATIC")

    await update.message.reply_text("💰 Balances:\n" + "\n".join(results))

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please specify subscription tier: 3h, 6h, 12h, 24h")
        return
    tier = args[0].lower()
    if tier not in PRICING_TIERS:
        await update.message.reply_text("Invalid tier. Choose from: 3h, 6h, 12h, 24h")
        return

    user_id = update.message.from_user.id
    success = smart_contract_payment_logic(user_id, tier)
    if success:
        price = PRICING_TIERS[tier]
        await update.message.reply_text(f"Subscription successful for {tier} hours at ${price}!")
    else:
        await update.message.reply_text("Subscription payment failed. Please try again.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Show tracked wallets\n"
        "/check - Check wallet balances\n"
        "/subscribe <3h|6h|12h|24h> - Subscribe to bot service\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("help", help_command))

    # Scheduler if you want periodic tasks (like alerts or balance checks)
    scheduler = AsyncIOScheduler()
    scheduler.start()

    logger.info("Bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()