"""
Telegram Bot with AI capabilities powered by Claude and MCP (Notion integration).

This bot combines:
- Telegram bot for user interaction
- Claude AI for intelligent responses
- MCP Notion server for accessing Notion workspace

Commands:
- /start - Initialize the bot
- /help - Show help message
- /ai <query> - Ask AI a question (with Notion access)

Setup:
1. Add to .env:
   - BOT_TOKEN (from @BotFather)
   - ANTHROPIC_API_KEY (from console.anthropic.com)
   - NOTION_INTEGRATION_TOKEN (from notion.so/my-integrations)

2. Share Notion pages with your integration

3. Run: python ai_bot.py
"""

import logging
import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from mcp_client import MCPClient

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

# Global MCP client instance
mcp_client = None


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


async def initialize_mcp():
    """Initialize MCP client and connect to Notion."""
    global mcp_client

    notion_token = os.getenv("NOTION_INTEGRATION_TOKEN")
    if not notion_token:
        logger.warning("NOTION_INTEGRATION_TOKEN not set. AI features will be limited.")
        return None

    try:
        logger.info("🔌 Initializing MCP client...")
        mcp_client = MCPClient()

        # Create environment with Notion token
        env_vars = os.environ.copy()
        env_vars["NOTION_TOKEN"] = notion_token

        # Connect to Notion MCP server
        await mcp_client.connect_to_server(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env=env_vars
        )

        logger.info("✅ MCP client connected to Notion!")
        return mcp_client

    except Exception as e:
        logger.error(f"Failed to initialize MCP: {e}")
        logger.warning("AI features will be limited without MCP.")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    user = update.effective_user

    # Save user for later messaging
    save_user(user.id, user.username, user.first_name)

    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\n"
        f"I'm an AI-powered bot with access to your Notion workspace.\n\n"
        f"Commands:\n"
        f"  /ai <question> - Ask me anything!\n"
        f"  /help - Show all commands\n\n"
        f"Your chat ID: {user.id}"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /help command is issued."""
    help_text = (
        "🤖 Available commands:\n\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Show this help message\n"
        "/ai <query> - Ask AI with Notion access\n"
        "/mychatid - Get your chat ID\n"
        "/broadcast <message> - Send to all users\n\n"
        "Examples:\n"
        "• /ai What's in my Notion workspace?\n"
        "• /ai Search for pages about project X\n"
        "• /ai Summarize my recent notes"
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


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process AI query with MCP/Notion access."""
    global mcp_client

    # Check if query provided
    if not context.args:
        await update.message.reply_text(
            "Usage: /ai <your question>\n\n"
            "Example: /ai What pages do I have in Notion?"
        )
        return

    query = " ".join(context.args)

    # Check if MCP is initialized
    if not mcp_client or not mcp_client.session:
        await update.message.reply_text(
            "⚠️ AI features not available. MCP client not connected.\n"
            "Check server logs for details."
        )
        return

    # Send "thinking" message
    thinking_msg = await update.message.reply_text("🤔 Thinking...")

    try:
        # Process query through MCP client
        logger.info(f"Processing AI query: {query}")
        response = await mcp_client.process_query(query)

        # Update message with response
        await thinking_msg.edit_text(response)

    except Exception as e:
        logger.error(f"Error processing AI query: {e}")
        await thinking_msg.edit_text(
            f"❌ Error processing query: {str(e)}\n\n"
            f"Please try again or check the logs."
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(
        f"You said: {update.message.text}\n\n"
        f"Tip: Use /ai <question> to ask AI!"
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


async def post_init(application: Application) -> None:
    """Initialize MCP after bot application is created."""
    await initialize_mcp()


def main() -> None:
    """Start the bot."""
    # Get bot token from environment variable
    bot_token = os.getenv("BOT_TOKEN")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables!")
        logger.error("Please add it to .env file.")
        return

    if not anthropic_key:
        logger.error("ANTHROPIC_API_KEY not found in environment variables!")
        logger.error("Please add it to .env file.")
        return

    # Create the Application
    application = Application.builder().token(bot_token).post_init(post_init).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("mychatid", get_chat_id))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Register message handler for echoing text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("🤖 Starting AI bot...")
    logger.info("Bot will initialize MCP connection on startup...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
