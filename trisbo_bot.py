import telebot
import os

# Load your bot token from environment variable
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables.")

bot = telebot.TeleBot(TOKEN)

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"Hello {message.from_user.first_name}! 🤖\nTrisbo Bot is online and ready.")

# Simple test command
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "Pong! ✅")

# Handle any text messages
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()