import os
import logging
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables or use your values here
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "YOUR_ETHERSCAN_API_KEY")
SOLANA_WALLET = os.getenv("SOLANA_WALLET", "3JqvK1ZAt67nipBVgZj6zWvuT8icMWBMWyu5AwYnhVss")
ETH_WALLET = os.getenv("ETH_WALLET", "0x08D171685e51bAf7a929cE8945CF25b3D1Ac9756")
OWNER_NAME = os.getenv("OWNER_NAME", "Mex Robert")

# Subscription pricing (example)
PRICES = {
    '3_hours': 5,
    '6_hours': 9,
    '12_hours': 16,
    '24_hours': 30
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        f"Hello {OWNER_NAME} 👋\n"
        f"Tracking wallets:\n"
        f"🔹 SOL: {SOLANA_WALLET}\n"
        f"🔹 ETH: {ETH_WALLET}\n\n"
        "Use /check to get current balances."
    )
    await update.message.reply_text(message)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eth_balance = await get_eth_balance(ETH_WALLET)
    sol_balance = await get_sol_balance(SOLANA_WALLET)
    message = (
        f"💰 Balances:\n"
        f"🔹 SOL: {sol_balance} SOL\n"
        f"🔹 ETH: {eth_balance} ETH"
    )
    await update.message.reply_text(message)

async def get_eth_balance(address):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(url).json()
        if response['status'] == '1':
            wei_balance = int(response['result'])
            eth_balance = wei_balance / 10**18
            return f"{eth_balance:.6f}"
        else:
            return f"Error: {response.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error fetching ETH balance: {e}")
        return "Error fetching balance"

async def get_sol_balance(address):
    try:
        url = f"https://public-api.solscan.io/account/tokens?account={address}"
        response = requests.get(url).json()
        # Sum all SOL token amounts (adjust if needed)
        sol_balance = 0
        if isinstance(response, list):
            for token in response:
                if token.get('tokenSymbol') == 'SOL':
                    sol_balance += float(token.get('tokenAmount', {}).get('uiAmount', 0))
        return f"{sol_balance:.6f}"
    except Exception as e:
        logger.error(f"Error fetching SOL balance: {e}")
        return "Error fetching balance"

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "Commands:\n"
        "/start - Start the bot\n"
        "/check - Check wallet balances\n"
        "/subscribe - Subscribe for updates\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(message)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "Subscription Plans:\n"
        "3 hours - $5\n"
        "6 hours - $9\n"
        "12 hours - $16\n"
        "24 hours - $30\n\n"
        "Payment & smart contract logic coming soon!"
    )
    await update.message.reply_text(message)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe))

    # Set bot commands shown in Telegram UI
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("check", "Check wallet balances"),
        BotCommand("subscribe", "View subscription plans"),
        BotCommand("help", "Get help info")
    ]
    app.bot.set_my_commands(commands)

    # Scheduler example (expand to polling wallet or updating users)
    scheduler = AsyncIOScheduler()
    scheduler.start()

    app.run_polling()

if __name__ == '__main__':
    main()