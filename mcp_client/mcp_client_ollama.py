"""
MCP Client with Ollama support (FREE local models!)

Supports small, fast models like:
- qwen2.5:0.5b (500MB) - Tiny & fast
- qwen2.5:1.5b (1GB) - Small & good quality
- qwen2.5:3b (2GB) - Better quality
- llama3.2:1b (1GB) - Very fast
- llama3.2:3b (2GB) - Good balance
- phi3:mini (2GB) - Microsoft's small model

Installation:
1. Install Ollama: https://ollama.com/download
2. Pull a model: ollama pull qwen2.5:0.5b
3. Run this script!
"""

import asyncio
import json
import logging
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import httpx
from dotenv import load_dotenv

load_dotenv()


class MCPClientOllama:
    def __init__(self, model: str = "llama3.2:latest", base_url: str = "http://localhost:11434"):
        self.model = model
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    @staticmethod
    def _clean_tool_args(args: dict) -> dict:
        """Remove empty strings, empty objects, and None values from tool arguments.

        This is necessary because small Ollama models often include optional parameters
        with empty values, which causes API validation errors.
        """
        cleaned = {}
        for key, value in args.items():
            # Skip None values
            if value is None:
                continue
            # Skip empty strings
            if isinstance(value, str) and value == "":
                continue
            # Skip empty dicts
            if isinstance(value, dict) and not value:
                continue
            # Skip empty lists
            if isinstance(value, list) and not value:
                continue
            # Recursively clean nested dicts
            if isinstance(value, dict):
                cleaned_nested = MCPClientOllama._clean_tool_args(value)
                if cleaned_nested:  # Only include if not empty after cleaning
                    cleaned[key] = cleaned_nested
            else:
                cleaned[key] = value
        return cleaned

    async def connect_to_server(self, server_script_path: str = None, env: dict = None, command: str = None, args: list = None):
        """Connect to an MCP server"""
        if command and args:
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env
            )
        elif server_script_path:
            is_python = server_script_path.endswith('.py')
            is_js = server_script_path.endswith('.js')
            if not (is_python or is_js):
                raise ValueError("Server script must be a .py or .js file")

            cmd = "python" if is_python else "node"
            server_params = StdioServerParameters(
                command=cmd,
                args=[server_script_path],
                env=env
            )
        else:
            raise ValueError("Must provide either (command + args) or server_script_path")

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str, max_iterations: int = 10) -> str:
        """Process a query using Ollama and available tools with agent loop logic

        Args:
            query: The user's question
            max_iterations: Maximum number of agent loop iterations (default: 10)

        Returns:
            Combined response with intermediate tool calls and final answer
        """
        # Get MCP tools and convert to Ollama format
        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]

        # Build system message explaining agent role and available tools
        tool_descriptions = "\n".join([
            f"- {tool['function']['name']}: {tool['function']['description']}"
            for tool in available_tools
        ])

        system_message = f"""You are an AI assistant with access to tools via MCP (Model Context Protocol).

Your role:
- You are an agent that can use tools to answer questions
- When a user asks a question, analyze if you need to use tools to answer it
- Use the available tools to fetch real-time data and information
- After using tools, ALWAYS answer the EXACT question the user asked

Available tools:
{tool_descriptions}

Core Instructions:
1. READ THE USER'S QUESTION CAREFULLY - Remember what they asked
2. Use tools to get the data you need
3. After getting tool results, answer ONLY the original question
4. Extract relevant information from the JSON response
5. Format your answer clearly and concisely

Tool Usage:
- Call tools by their exact name with proper parameters
- IMPORTANT: For optional parameters, DO NOT include them if you don't have a meaningful value
- DO NOT pass empty strings ("") for optional parameters - simply omit them instead
- For search/list operations, you typically only need the required parameters
- For Notion, the token is already set. It's only connected to my account.

Response Guidelines:
- STAY FOCUSED on answering what the user asked - don't change the question
- Extract key information from JSON responses (titles, names, dates, etc.)
- Present information in a clear, readable format (bullet points or numbered lists)
- If the user asks "what pages", list the page titles/names
- If the user asks "what tasks", list the tasks
- If the user asks about specific data, extract and present that data clearly

Examples:
- User asks "what pages do I have?": List all page titles from the search results
- User asks "what's my latest task?": Find and show the most recent task
- To search Notion: Use API-post-search with only the query parameter (omit start_cursor, page_size if not needed)
- To list pages: Use API-post-search with an empty or simple query"""

        messages = [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": query
            }
        ]

        # Track intermediate text responses
        final_text = []

        # Agent loop: continue until no more tool calls or max iterations reached
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            logging.info(f"Agent loop iteration {iteration}/{max_iterations}")

            # Call Ollama API
            payload = {
                "model": self.model,
                "messages": messages,
                "tools": available_tools,
                "stream": False
            }

            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )

            result = response.json()
            message = result["message"]
            logging.info(f"Agent response: {message}")

            # Preserve any text content from this iteration
            if message.get("content"):
                final_text.append(message["content"])

            # Check if there are tool calls to process
            if not message.get("tool_calls"):
                # No more tool calls - agent is done
                logging.info("No tool calls found. Agent loop complete.")
                break

            # Add the assistant's message with tool calls to history
            messages.append(message)

            # Process each tool call
            for tool_call in message["tool_calls"]:
                function = tool_call["function"]
                tool_name = function["name"]
                tool_args = function["arguments"]

                # Clean tool arguments to remove empty values that cause API errors
                cleaned_args = self._clean_tool_args(tool_args)
                logging.info(f"Calling tool: {tool_name}")
                logging.info(f"Original args: {tool_args}")
                logging.info(f"Cleaned args: {cleaned_args}")

                # Execute tool call via MCP
                mcp_result = await self.session.call_tool(tool_name, cleaned_args)

                # Add note about tool call to final text
                final_text.append(f"[Calling tool: {tool_name}]")
                logging.info(f"Tool result: {mcp_result.content}")
                # Add tool result to messages for next iteration
                messages.append({
                    "role": "tool",
                    "content": str(mcp_result.content)
                })

            # Continue loop - agent will process tool results and decide next action

        if iteration >= max_iterations:
            logging.warning(f"Agent loop reached max iterations ({max_iterations})")
            final_text.append(f"[Warning: Reached maximum iteration limit of {max_iterations}]")

        return "\n\n".join(final_text)

    async def cleanup(self):
        """Cleanup resources"""
        await self.client.aclose()
        await self.exit_stack.aclose()

