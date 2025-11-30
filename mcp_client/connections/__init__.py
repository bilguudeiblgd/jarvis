"""
MCP Server Connections

This package contains individual MCP server connection configurations.
Each connection module exports a function to connect to a specific MCP server.
"""

from .notion import connect_notion
from .google_calendar import connect_google_calendar

__all__ = ["connect_notion", "connect_google_calendar"]