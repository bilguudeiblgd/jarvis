"""
MCP Client with OpenAI support (cheaper alternative to Anthropic)
"""

import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class MCPClientOpenAI:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = AsyncOpenAI()  # Reads OPENAI_API_KEY from env

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

    async def process_query(self, query: str, model: str = "gpt-4o") -> str:
        """Process a query using OpenAI and available tools

        Args:
            query: The user's question
            model: OpenAI model to use (default: gpt-4o for best tool calling)
                  Options: gpt-4o, gpt-4o-mini, gpt-4-turbo
        """
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # Get MCP tools and convert to OpenAI format
        mcp_response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "No description",
                "parameters": tool.inputSchema
            }
        } for tool in mcp_response.tools]

        print(f"\n[DEBUG] Using model: {model}")
        print(f"[DEBUG] Available tools: {[t['function']['name'] for t in available_tools]}")

        # Initial OpenAI API call
        response = await self.openai.chat.completions.create(
            model=model,
            max_tokens=2000,
            messages=messages,
            tools=available_tools,
            tool_choice="auto"  # Let model decide when to use tools
        )

        # Process response and handle tool calls
        final_text = []
        message = response.choices[0].message

        print(f"[DEBUG] Response finish_reason: {response.choices[0].finish_reason}")
        print(f"[DEBUG] Tool calls: {message.tool_calls}")

        if message.content:
            final_text.append(message.content)

        # Handle tool calls
        if message.tool_calls:
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls
                ]
            })

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name

                # Parse JSON arguments safely
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to parse tool arguments: {e}")
                    print(f"[ERROR] Raw arguments: {tool_call.function.arguments}")
                    continue

                print(f"[DEBUG] Calling tool: {tool_name} with args: {tool_args}")

                # Execute tool call via MCP
                try:
                    result = await self.session.call_tool(tool_name, tool_args)
                    final_text.append(f"[Calling {tool_name}]")

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result.content) if not isinstance(result.content, str) else result.content
                    })
                except Exception as e:
                    print(f"[ERROR] Tool call failed: {e}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error: {str(e)}"
                    })

            # Get final response from OpenAI after tool execution
            response = await self.openai.chat.completions.create(
                model=model,
                max_tokens=2000,
                messages=messages,
                tools=available_tools
            )

            if response.choices[0].message.content:
                final_text.append(response.choices[0].message.content)

        return "\n".join(filter(None, final_text))


async def main():
    """Example usage"""
    import os

    client = MCPClientOpenAI()

    notion_token = os.getenv("NOTION_INTEGRATION_TOKEN")
    if not notion_token:
        print("Set NOTION_INTEGRATION_TOKEN in .env first!")
        return

    env_vars = os.environ.copy()
    env_vars["NOTION_TOKEN"] = notion_token

    try:
        await client.connect_to_server(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env=env_vars
        )

        # Test with GPT-4o (best tool calling)
        print("\n✅ Connected! Ask me anything:\n")
        print("Model: gpt-4o (best for tool calling)")
        print("For cheaper option, change to gpt-4o-mini\n")

        query = input("You: ")
        response = await client.process_query(query, model="gpt-4o")
        print(f"\nAI: {response}\n")

    finally:
        await client.exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(main())
