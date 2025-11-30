"""
MCP Client Factory

Creates the appropriate MCP client based on provider and model configuration.
"""

import os
import logging
from typing import Optional, List

from .mcp_client import MCPClient
from .mcp_client_openai import MCPClientOpenAI
from .mcp_client_ollama import MCPClientOllama
from .mcp_client_google import MCPClientGoogle
from .connections import connect_notion

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

        elif provider == "google" or provider == "gemini":
            # Google Gemini - cloud-based models
            # Default: gemini-2.5-flash
            # Options: gemini-2.5-flash, gemini-1.5-flash, gemini-1.5-pro
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            model = model or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
            return MCPClientGoogle(model=model, api_key=api_key)

        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: anthropic, openai, ollama, google"
            )

    @staticmethod
    async def initialize_mcp_client(
        provider: str,
        model: Optional[str] = None,
        connections: Optional[List[str]] = None
    ):
        """
        Create and initialize an MCP client with specified connections.

        Args:
            provider: AI provider name
            model: Model name (optional)
            connections: List of connection names to enable (e.g., ['notion', 'google_calendar'])
                        If None, defaults to ['notion'] only

        Returns:
            Initialized MCP client or None if initialization fails
        """
        # Default to Notion only if no connections specified
        if connections is None:
            connections = ['notion']

        try:
            logger.info(f"🔌 Initializing MCP client with {provider}...")

            # Create client
            client = MCPClientFactory.create_client(provider, model)

            # Connect to each requested MCP server
            connected_services = []

            for connection in connections:
                try:
                    if connection == 'notion':
                        await connect_notion(client)
                        connected_services.append('Notion')
                    else:
                        logger.warning(f"Unknown connection type: {connection}")
                except ValueError as e:
                    logger.warning(f"Skipping {connection}: {e}")
                except Exception as e:
                    logger.error(f"Failed to connect to {connection}: {e}")

            if not connected_services:
                logger.warning("No MCP services connected. AI features will be limited.")
                return None

            logger.info(f"✅ MCP client connected to: {', '.join(connected_services)} using {provider}!")
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
        "ollama": "qwen2.5:0.5b",
        "google": "gemini-2.5-flash",
        "gemini": "gemini-2.5-flash"
    }
    return defaults.get(provider.lower(), "")
