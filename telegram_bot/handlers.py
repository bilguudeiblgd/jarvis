"""
Telegram bot command handlers.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from .user_manager import save_user, load_users

logger = logging.getLogger(__name__)


class BotHandlers:
    """Handles all Telegram bot commands and messages."""

    def __init__(self, mcp_client=None, provider_name="Unknown", model_name="Unknown"):
        """
        Initialize handlers.

        Args:
            mcp_client: The MCP client instance for AI queries
            provider_name: Name of the AI provider (anthropic, ollama, openai)
            model_name: Name of the model being used
        """
        self.mcp_client = mcp_client
        self.provider_name = provider_name
        self.model_name = model_name

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a welcome message when the /start command is issued."""
        user = update.effective_user
        save_user(user.id, user.username, user.first_name)

        await update.message.reply_text(
            f"Hello {user.first_name}! 👋\n\n"
            f"I'm an AI-powered bot with access to your Notion workspace.\n"
            f"Provider: {self.provider_name}\n"
            f"Model: {self.model_name}\n\n"
            f"Commands:\n"
            f"  /ai <question> - Ask me anything!\n"
            f"  /help - Show all commands\n\n"
            f"Your chat ID: {user.id}"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a help message when the /help command is issued."""
        help_text = (
            "🤖 Available commands:\n\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/ai <query> - Ask AI with Notion access\n"
            "/mychatid - Get your chat ID\n"
            "/broadcast <message> - Send to all users\n\n"
            f"AI Provider: {self.provider_name}\n"
            f"Model: {self.model_name}\n\n"
            "Examples:\n"
            "• /ai What's in my Notion workspace?\n"
            "• /ai Search for pages about project X\n"
            "• /ai Summarize my recent notes"
        )
        await update.message.reply_text(help_text)

    async def get_chat_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send the user's chat ID."""
        chat_id = update.effective_chat.id
        await update.message.reply_text(
            f"Your chat ID is: {chat_id}\n\n"
            f"Use this ID to send messages from external applications."
        )

    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    async def ai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process AI query with MCP/Notion access."""
        # Check if query provided
        if not context.args:
            await update.message.reply_text(
                "Usage: /ai <your question>\n\n"
                "Example: /ai What pages do I have in Notion?"
            )
            return

        query = " ".join(context.args)

        # Check if MCP is initialized
        if not self.mcp_client or not self.mcp_client.session:
            await update.message.reply_text(
                "⚠️ AI features not available. MCP client not connected.\n"
                "Check server logs for details."
            )
            return

        # Send "thinking" message
        thinking_msg = await update.message.reply_text(
            f"🤔 Thinking... (using {self.provider_name})"
        )

        try:
            # Process query through MCP client
            logger.info(f"Processing AI query with {self.model_name}: {query}")
            response = await self.mcp_client.process_query(query)

            # Update message with response
            await thinking_msg.edit_text(response)

        except Exception as e:
            logger.error(f"Error processing AI query: {e}")
            await thinking_msg.edit_text(
                f"❌ Error processing query: {str(e)}\n\n"
                f"Please try again or check the logs."
            )

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        await update.message.reply_text(
            f"You said: {update.message.text}\n\n"
            f"Tip: Use /ai <question> to ask AI!"
        )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log errors caused by updates."""
        logger.error(f"Update {update} caused error {context.error}")
