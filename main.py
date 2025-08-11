import json
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Load config from JSON
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
OWNER_NAME = config["owner_name"]
SOL_WALLET = config["wallet_address"]
ETH_WALLET = config["eth_wallet_address"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# In-memory user subscriptions (for production, use a database)
user_subscriptions = {}

# Pricing plans (USD)
PRICES = {
    "3h": 5,
    "6h": 10,
    "12h": 20,
    "24h": 50,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello {OWNER_NAME} 👋\n"
        f"Tracking wallets:\n"
        f"🔹 SOL: {SOL_WALLET}\n"
        f"🔹 ETH: {ETH_WALLET}\n\n"
        f"Use /subscribe to get started with a subscription plan."
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"3 hours - ${PRICES['3h']}", callback_data="subscribe_3h")],
        [InlineKeyboardButton(f"6 hours - ${PRICES['6h']}", callback_data="subscribe_6h")],
        [InlineKeyboardButton(f"12 hours - ${PRICES['12h']}", callback_data="subscribe_12h")],
        [InlineKeyboardButton(f"24 hours - ${PRICES['24h']}", callback_data="subscribe_24h")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your subscription plan:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("subscribe_"):
        plan = data.split("_")[1]
        price = PRICES.get(plan, None)
        if not price:
            await query.edit_message_text("Invalid plan selected.")
            return

        # Simulate payment process
        await query.edit_message_text(f"Processing payment of ${price} for {plan} plan...")

        # Here you would integrate real payment logic (Stripe, Paypal, Crypto, etc.)
        # For now, simulate delay and success
        await asyncio.sleep(2)

        # Store subscription end time (now + plan duration)
        import datetime
        duration_hours = int(plan.replace("h", ""))
        end_time = datetime.datetime.utcnow() + datetime.timedelta(hours=duration_hours)
        user_subscriptions[user_id] = end_time

        await query.edit_message_text(f"✅ Subscription active for {plan}.\nExpires at (UTC): {end_time}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    import datetime

    if user_id not in user_subscriptions:
        await update.message.reply_text("You do not have an active subscription. Use /subscribe to get one.")
        return

    end_time = user_subscriptions[user_id]
    now = datetime.datetime.utcnow()

    if now > end_time:
        await update.message.reply_text("Your subscription has expired. Use /subscribe to renew.")
        del user_subscriptions[user_id]
    else:
        remaining = end_time - now
        await update.message.reply_text(f"Your subscription is active.\nTime remaining: {remaining}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Welcome message\n"
        "/subscribe - Subscribe to a plan\n"
        "/status - Check your subscription status\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()

if __name__ == "__main__":
    main()