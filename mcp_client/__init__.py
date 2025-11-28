"""
MCP Client Package

Provides multiple AI provider options:
- MCPClient: Anthropic Claude (Haiku, Sonnet, Opus)
- MCPClientOpenAI: OpenAI GPT models
- MCPClientOllama: Free local models via Ollama
"""

from .mcp_client import MCPClient
from .mcp_client_openai import MCPClientOpenAI
from .mcp_client_ollama import MCPClientOllama

__all__ = [
    "MCPClient",
    "MCPClientOpenAI",
    "MCPClientOllama"
]
