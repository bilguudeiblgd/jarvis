"""
Simple Telegram Bot with basic commands.

Before running:
1. Get a bot token from @BotFather on Telegram
2. Copy .env to .env
3. Add your bot token to .env
4. Install dependencies: pip install -r requirements.txt
5. Run: python bot.py
"""

import logging
import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# File to store user chat IDs
USERS_FILE = "users.json"


def load_users():
    """Load registered users from file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_user(chat_id, username, first_name):
    """Save user chat ID to file."""
    users = load_users()
    users[str(chat_id)] = {
        "username": username,
        "first_name": first_name
    }
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    logger.info(f"Saved user {chat_id} ({first_name})")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    user = update.effective_user

    # Save user for later messaging
    save_user(user.id, user.username, user.first_name)

    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\n"
        f"I'm a simple bot that can echo your messages.\n"
        f"Your chat ID is: {user.id}\n\n"
        f"Try sending me a message or use /help to see available commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /help command is issued."""
    help_text = (
        "Available commands:\n\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Show this help message\n"
        "/mychatid - Get your chat ID\n"
        "/broadcast <message> - Send message to all users (admin)\n\n"
        "You can also send me any text message and I'll echo it back to you!"
    )
    await update.message.reply_text(help_text)


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the user's chat ID."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Your chat ID is: {chat_id}\n\n"
        f"Use this ID to send messages from external applications."
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast a message to all registered users."""
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    message = " ".join(context.args)
    users = load_users()

    sent_count = 0
    failed_count = 0

    for chat_id in users.keys():
        try:
            await context.bot.send_message(chat_id=int(chat_id), text=message)
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send to {chat_id}: {e}")
            failed_count += 1

    await update.message.reply_text(
        f"Broadcast complete!\n"
        f"Sent: {sent_count}\n"
        f"Failed: {failed_count}"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(f"You said: {update.message.text}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    # Get bot token from environment variable
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your bot token.")
        logger.error("See .env for reference.")
        return

    # Create the Application
    application = Application.builder().token(bot_token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mychatid", get_chat_id))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Register message handler for echoing text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
