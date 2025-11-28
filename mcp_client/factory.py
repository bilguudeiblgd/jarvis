"""
MCP Client Factory

Creates the appropriate MCP client based on provider and model configuration.
"""

import os
import logging
from typing import Optional

from .mcp_client import MCPClient
from .mcp_client_openai import MCPClientOpenAI
from .mcp_client_ollama import MCPClientOllama

logger = logging.getLogger(__name__)


class MCPClientFactory:
    """Factory for creating MCP clients based on provider."""

    @staticmethod
    def create_client(provider: str, model: Optional[str] = None):
        """
        Create an MCP client based on the provider.

        Args:
            provider: AI provider name ('anthropic', 'openai', 'ollama')
            model: Model name (provider-specific)

        Returns:
            MCPClient instance for the specified provider

        Raises:
            ValueError: If provider is not supported
        """
        provider = provider.lower()

        if provider == "anthropic":
            # Anthropic/Claude - model is set in the client's process_query
            # Default models: claude-3-5-haiku-20241022, claude-sonnet-4-20250514, claude-opus-4-20250514
            if model:
                logger.info(f"Note: Model '{model}' will be used in process_query")
            return MCPClient()

        elif provider == "openai":
            # OpenAI - model is passed to process_query
            # Default models: gpt-4o, gpt-4o-mini
            return MCPClientOpenAI()

        elif provider == "ollama":
            # Ollama - local models
            # Default: qwen2.5:0.5b
            # Common models: qwen2.5:0.5b, qwen2.5:1.5b, llama3.2:1b, llama3.2:3b
            model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
            return MCPClientOllama(model=model)

        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: anthropic, openai, ollama"
            )

    @staticmethod
    async def initialize_mcp_client(provider: str, model: Optional[str] = None):
        """
        Create and initialize an MCP client with Notion connection.

        Args:
            provider: AI provider name
            model: Model name (optional)

        Returns:
            Initialized MCP client or None if initialization fails
        """
        notion_token = os.getenv("NOTION_INTEGRATION_TOKEN")
        if not notion_token:
            logger.warning("NOTION_INTEGRATION_TOKEN not set. AI features will be limited.")
            return None

        try:
            logger.info(f"🔌 Initializing MCP client with {provider}...")

            # Create client
            client = MCPClientFactory.create_client(provider, model)

            # Create environment with Notion token
            env_vars = os.environ.copy()
            env_vars["NOTION_TOKEN"] = notion_token

            # Connect to Notion MCP server
            await client.connect_to_server(
                command="npx",
                args=["-y", "@notionhq/notion-mcp-server"],
                env=env_vars
            )

            logger.info(f"✅ MCP client connected to Notion using {provider}!")
            return client

        except Exception as e:
            logger.error(f"Failed to initialize MCP: {e}")
            logger.warning("AI features will be limited without MCP.")
            return None


def get_default_model(provider: str) -> str:
    """
    Get the default model for a provider.

    Args:
        provider: AI provider name

    Returns:
        Default model name for the provider
    """
    defaults = {
        "anthropic": "claude-3-5-haiku-20241022",
        "openai": "gpt-4o-mini",
        "ollama": "qwen2.5:0.5b"
    }
    return defaults.get(provider.lower(), "")
