#!/usr/bin/env python3
"""
Jarvis - AI Telegram Bot with Notion Integration

A modular Telegram bot that integrates with Notion via MCP (Model Context Protocol)
and supports multiple AI providers.

Usage:
    python main.py --provider anthropic --model claude-3-5-haiku-20241022
    python main.py --provider ollama --model qwen2.5:0.5b
    python main.py --provider openai --model gpt-4o-mini

Environment variables required:
    BOT_TOKEN                    - Telegram bot token from @BotFather
    NOTION_INTEGRATION_TOKEN     - Notion integration token
    ANTHROPIC_API_KEY           - For Anthropic/Claude (if using --provider anthropic)
    OPENAI_API_KEY              - For OpenAI (if using --provider openai)
    OLLAMA_MODEL                 - Default Ollama model (optional, can use --model instead)
"""

import argparse
import logging
import os
import sys
from dotenv import load_dotenv

from mcp_client import MCPClientFactory, get_default_model
from telegram_bot import TelegramBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Jarvis - AI Telegram Bot with Notion Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using Anthropic Claude (requires ANTHROPIC_API_KEY)
  python main.py --provider anthropic --model claude-3-5-haiku-20241022
  python main.py --provider anthropic --model claude-sonnet-4-20250514

  # Using OpenAI (requires OPENAI_API_KEY)
  python main.py --provider openai --model gpt-4o-mini
  python main.py --provider openai --model gpt-4o

  # Using Ollama (FREE - requires Ollama running locally)
  python main.py --provider ollama --model qwen2.5:0.5b
  python main.py --provider ollama --model llama3.2:3b

Default models:
  anthropic: claude-3-5-haiku-20241022
  openai:    gpt-4o-mini
  ollama:    qwen2.5:0.5b
        """
    )

    parser.add_argument(
        '--provider',
        type=str,
        required=True,
        choices=['anthropic', 'openai', 'ollama'],
        help='AI provider to use'
    )

    parser.add_argument(
        '--model',
        type=str,
        help='Model name to use (provider-specific). If not specified, uses provider default.'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )

    return parser.parse_args()


def validate_environment(provider: str):
    """
    Validate that required environment variables are set.

    Args:
        provider: AI provider name

    Returns:
        bool: True if all required variables are set, False otherwise
    """
    # BOT_TOKEN is always required
    if not os.getenv("BOT_TOKEN"):
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        logger.error("   Get a token from @BotFather on Telegram")
        return False

    # NOTION_INTEGRATION_TOKEN is always required
    if not os.getenv("NOTION_INTEGRATION_TOKEN"):
        logger.error("❌ NOTION_INTEGRATION_TOKEN not found in environment variables!")
        logger.error("   Get a token from https://www.notion.so/my-integrations")
        return False

    # Provider-specific validation
    if provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            logger.error("❌ ANTHROPIC_API_KEY not found in environment variables!")
            logger.error("   Get an API key from https://console.anthropic.com")
            return False

    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("❌ OPENAI_API_KEY not found in environment variables!")
            logger.error("   Get an API key from https://platform.openai.com")
            return False

    elif provider == "ollama":
        # Check if Ollama is running
        try:
            import httpx
            response = httpx.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                logger.warning("⚠️  Ollama API returned unexpected status")
        except Exception:
            logger.warning("⚠️  Ollama not detected at http://localhost:11434")
            logger.warning("   Install Ollama: https://ollama.com/download")
            logger.warning("   Start Ollama: ollama serve")
            logger.warning("   Pull a model: ollama pull qwen2.5:0.5b")
            logger.warning("")
            logger.warning("   Continuing anyway - bot will fail if Ollama is not available")

    return True


async def initialize_mcp(provider: str, model: str):
    """
    Initialize MCP client.

    Args:
        provider: AI provider name
        model: Model name

    Returns:
        MCP client instance or None
    """
    return await MCPClientFactory.initialize_mcp_client(provider, model)


async def main_async(args):
    """Async main function."""
    # Set logging level
    logging.getLogger().setLevel(args.log_level)

    # Get model (use argument or default)
    model = args.model or get_default_model(args.provider)

    logger.info("=" * 60)
    logger.info("🤖 Jarvis - AI Telegram Bot")
    logger.info("=" * 60)
    logger.info(f"Provider: {args.provider}")
    logger.info(f"Model:    {model}")
    logger.info("=" * 60)

    # Validate environment
    if not validate_environment(args.provider):
        logger.error("\n❌ Environment validation failed!")
        logger.error("   Please check your .env file and ensure all required variables are set.")
        sys.exit(1)

    # Initialize MCP client
    mcp_client = await initialize_mcp(args.provider, model)

    if not mcp_client:
        logger.error("❌ Failed to initialize MCP client!")
        logger.error("   The bot will start but AI features will not work.")
        logger.error("   Check the logs above for details.")

    # Get bot token
    bot_token = os.getenv("BOT_TOKEN")

    # Create and run Telegram bot
    bot = TelegramBot(
        token=bot_token,
        mcp_client=mcp_client,
        provider_name=args.provider,
        model_name=model
    )

    logger.info("\n✅ Starting Telegram bot...\n")

    # Run the bot
    bot.run()


def main():
    """Main entry point."""
    import asyncio

    # Parse arguments
    args = parse_arguments()

    # Run async main
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        logger.info("\n\n👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
