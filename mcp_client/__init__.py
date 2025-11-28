"""
MCP Client Package

Provides multiple AI provider options:
- MCPClient: Anthropic Claude (Haiku, Sonnet, Opus)
- MCPClientOpenAI: OpenAI GPT models
- MCPClientOllama: Free local models via Ollama
- MCPClientFactory: Factory for creating clients based on provider
"""

from .mcp_client import MCPClient
from .mcp_client_openai import MCPClientOpenAI
from .mcp_client_ollama import MCPClientOllama
from .factory import MCPClientFactory, get_default_model

__all__ = [
    "MCPClient",
    "MCPClientOpenAI",
    "MCPClientOllama",
    "MCPClientFactory",
    "get_default_model"
]
