import json
import logging
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from web3 import Web3

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
CHAT_ID = config["telegram_chat_id"]
SOL_WALLET = config["wallet_address"]
ETH_WALLET = config["eth_wallet_address"]
ETHERSCAN_API_KEY = config["etherscan_api_key"]
SUBSCRIPTION_PRICES = config["subscription_prices"]

w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))  # Replace or add your own RPC if needed

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello {config['owner_name']} 👋\n"
        f"Tracking wallets:\n"
        f"🔹 SOL: {SOL_WALLET}\n"
        f"🔹 ETH: {ETH_WALLET}\n\n"
        f"Use /subscribe <duration> to subscribe. Example: /subscribe 3h\n"
        f"Prices:\n" +
        "\n".join([f"{k} : ${v}" for k,v in SUBSCRIPTION_PRICES.items()])
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sol_balance = get_solana_balance(SOL_WALLET)
    eth_balance = await get_eth_balance(ETH_WALLET, ETHERSCAN_API_KEY)
    await update.message.reply_text(
        f"💰 Balances:\n"
        f"🔹 SOL: {sol_balance} SOL\n"
        f"🔹 ETH: {eth_balance} ETH"
    )

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

async def get_eth_balance(address, api_key):
    try:
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
            "apikey": api_key
        }
        r = requests.get(url, params=params)
        wei = int(r.json()["result"])
        return round(wei / 1e18, 6)
    except Exception as e:
        return f"Error: {e}"

# Subscription storage (for demo, simple in-memory dictionary)
# In production, use a DB or file
subscriptions = {}

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /subscribe <duration> (3h, 6h, 12h, 24h)")
        return
    
    duration = context.args[0].lower()
    if duration not in SUBSCRIPTION_PRICES:
        await update.message.reply_text("Invalid duration! Choose from 3h, 6h, 12h, 24h")
        return
    
    price = SUBSCRIPTION_PRICES[duration]
    # Here you should implement payment logic:
    # e.g. sending invoice, checking payment, etc.
    # For demo, we simply accept subscription
    
    # Save subscription expiry timestamp
    import time
    from datetime import datetime, timedelta
    
    now = datetime.now()
    if duration.endswith('h'):
        hours = int(duration[:-1])
        expiry = now + timedelta(hours=hours)
    else:
        expiry = now
    
    subscriptions[user_id] = expiry
    await update.message.reply_text(
        f"Subscription for {duration} accepted at price ${price}.\n"
        f"Expires at {expiry.strftime('%Y-%m-%d %H:%M:%S')}"
    )

async def send_periodic_updates(application):
    while True:
        for user_id, expiry in list(subscriptions.items()):
            from datetime import datetime
            if datetime.now() > expiry:
                del subscriptions[user_id]
                continue
            # Send balance update to subscribed users
            sol_balance = get_solana_balance(SOL_WALLET)
            eth_balance = await get_eth_balance(ETH_WALLET, ETHERSCAN_API_KEY)
            try:
                await application.bot.send_message(
                    chat_id=user_id,
                    text=f"⏰ Periodic Update:\nSOL Balance: {sol_balance} SOL\nETH Balance: {eth_balance} ETH"
                )
            except Exception as e:
                print(f"Failed to send update to {user_id}: {e}")
        await asyncio.sleep(3600)  # Send every hour

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("subscribe", subscribe))
    
    import threading
    import asyncio
    
    # Run the periodic updates in a separate thread
    def start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_periodic_updates(app))
    
    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_loop, args=(new_loop,))
    t.start()
    
    app.run_polling()