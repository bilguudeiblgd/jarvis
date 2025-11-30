"""
Main Telegram bot implementation.
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .handlers import BotHandlers

logger = logging.getLogger(__name__)


class TelegramBot:
    """Main Telegram bot class."""

    def __init__(self, token: str, mcp_client=None, provider_name="Unknown", model_name="Unknown"):
        """
        Initialize the Telegram bot.

        Args:
            token: Telegram bot token
            mcp_client: MCP client instance for AI functionality
            provider_name: Name of the AI provider
            model_name: Name of the AI model
        """
        self.token = token
        self.mcp_client = mcp_client
        self.provider_name = provider_name
        self.model_name = model_name
        self.handlers = BotHandlers(mcp_client, provider_name, model_name)
        self.application = None


    def setup_handlers(self, application: Application) -> None:
        """Register all command and message handlers."""
        # Register command handlers
        application.add_handler(CommandHandler("start", self.handlers.start))
        application.add_handler(CommandHandler("help", self.handlers.help_command))
        application.add_handler(CommandHandler("ai", self.handlers.ai_command))
        application.add_handler(CommandHandler("mychatid", self.handlers.get_chat_id))
        application.add_handler(CommandHandler("broadcast", self.handlers.broadcast))

        # Register message handler for echoing text messages
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.echo)
        )

        # Register error handler
        application.add_error_handler(self.handlers.error_handler)

    async def initialize(self) -> None:
        """Initialize the bot application."""
        logger.info("🤖 Initializing Telegram bot...")
        logger.info(f"   Provider: {self.provider_name}")
        logger.info(f"   Model: {self.model_name}")

        # Create the Application
        self.application = Application.builder().token(self.token).build()

        # Setup all handlers
        self.setup_handlers(self.application)

    async def run(self) -> None:
        """Start the bot."""
        if not self.application:
            raise RuntimeError("Bot not initialized. Call initialize() first.")

        # Initialize and start the bot
        async with self.application:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

            logger.info("✅ Bot is running!")

            # Keep the bot running
            import asyncio
            try:
                # Run forever until interrupted
                await asyncio.Event().wait()
            except (KeyboardInterrupt, SystemExit):
                pass
            finally:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
