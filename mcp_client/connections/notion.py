"""
Notion MCP Server Connection
"""

import os
import logging

logger = logging.getLogger(__name__)


async def connect_notion(client, env: dict = None):
    """
    Connect to Notion MCP server.

    Args:
        client: MCP client instance
        env: Optional environment variables to pass to the server

    Returns:
        bool: True if connection successful, False otherwise

    Raises:
        ValueError: If NOTION_INTEGRATION_TOKEN is not set
    """
    notion_token = os.getenv("NOTION_INTEGRATION_TOKEN")
    if not notion_token:
        raise ValueError("NOTION_INTEGRATION_TOKEN not set")

    try:
        logger.info("🔌 Connecting to Notion MCP server...")

        # Create environment with Notion token
        env_vars = env or os.environ.copy()
        env_vars["NOTION_TOKEN"] = notion_token

        # Connect to Notion MCP server
        await client.connect_to_server(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env=env_vars
        )

        logger.info("✅ Connected to Notion MCP server!")
        return True

    except Exception as e:
        logger.error(f"Failed to connect to Notion: {e}")
        raise