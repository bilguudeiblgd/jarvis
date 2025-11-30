"""
Google Calendar MCP Server Connection

Uses OAuth 2.0 authentication via nspady/google-calendar-mcp.
The OAuth flow happens once - user authenticates via browser, then tokens are stored locally.
"""

import os
import logging

logger = logging.getLogger(__name__)


async def connect_google_calendar(client, env: dict = None):
    """
    Connect to Google Calendar MCP server using OAuth 2.0.

    The first time you run this, it will:
    1. Open a browser window for Google authentication
    2. Ask you to grant calendar permissions
    3. Store the tokens locally for future use

    After initial setup, tokens are reused automatically.

    Args:
        client: MCP client instance
        env: Optional environment variables to pass to the server

    Returns:
        bool: True if connection successful, False otherwise

    Raises:
        ValueError: If GOOGLE_OAUTH_CREDENTIALS is not set
    """
    google_oauth_creds = os.getenv("GOOGLE_OAUTH_CREDENTIALS")
    if not google_oauth_creds:
        raise ValueError(
            "GOOGLE_OAUTH_CREDENTIALS not set. "
            "See docs/GOOGLE_CALENDAR_SETUP.md for setup instructions."
        )

    # Verify file exists
    if not os.path.exists(google_oauth_creds):
        raise ValueError(f"OAuth credentials file not found: {google_oauth_creds}")

    try:
        logger.info("🔌 Connecting to Google Calendar MCP server...")
        logger.info("📝 First-time setup will open a browser for authentication")

        # Create environment with OAuth credentials
        env_vars = env or os.environ.copy()
        env_vars["GOOGLE_OAUTH_CREDENTIALS"] = google_oauth_creds

        # Connect to Google Calendar MCP server (nspady/google-calendar-mcp)
        # This uses npx to run the npm package
        await client.connect_to_server(
            command="npx",
            args=["-y", "@cocal/google-calendar-mcp"],
            env=env_vars
        )

        logger.info("✅ Connected to Google Calendar MCP server!")
        return True

    except Exception as e:
        logger.error(f"Failed to connect to Google Calendar: {e}")
        logger.error("💡 If this is your first time, make sure you complete the OAuth flow in the browser")
        raise