
import asyncio
import logging
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
    # methods will go here

    async def connect_to_server(self, server_script_path: str = None, env: dict = None, command: str = None, args: list = None):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js) - legacy method
            env: Optional environment variables to pass to the server
            command: Direct command to run (e.g., "npx", "python")
            args: Arguments for the command (e.g., ["@notionhq/notion-mcp-server"])
        """
        # New direct method: command + args
        if command and args:
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env
            )
        # Legacy method: script path
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

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str, max_iterations: int = 10) -> str:
        """Process a query using Claude and available tools with agent loop logic

        Args:
            query: The user's question
            max_iterations: Maximum number of agent loop iterations (default: 10)

        Returns:
            Combined response with intermediate tool calls and final answer
        """
        # Get MCP tools
        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        messages = [
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

            # Call Claude API
            # Models: claude-3-5-haiku-20241022 (cheapest/fastest)
            #         claude-sonnet-4-20250514 (balanced)
            #         claude-opus-4-20250514 (most capable)
            response = self.anthropic.messages.create(
                model="claude-3-5-haiku-20241022",  # Using Haiku - 90% cheaper!
                max_tokens=1000,
                messages=messages,
                tools=available_tools,
            )

            logging.info(f"Claude response: {response}")

            # Collect assistant message content (text + tool uses)
            assistant_message_content = []
            has_tool_calls = False

            # Process response content
            for content in response.content:
                assistant_message_content.append(content)

                if content.type == 'text':
                    # Preserve text content
                    if content.text:
                        final_text.append(content.text)

                elif content.type == 'tool_use':
                    has_tool_calls = True
                    tool_name = content.name
                    tool_args = content.input

                    logging.info(f"Calling tool: {tool_name}")
                    logging.info(f"Tool args: {tool_args}")

                    # Execute tool call via MCP
                    mcp_result = await self.session.call_tool(tool_name, tool_args)

                    # Add note about tool call to final text
                    final_text.append(f"[Calling tool: {tool_name}]")
                    logging.info(f"Tool result: {mcp_result.content}")

            # Check if there are tool calls to process
            if not has_tool_calls:
                # No more tool calls - agent is done
                logging.info("No tool calls found. Agent loop complete.")
                break

            # Add the assistant's message with tool calls to history
            messages.append({
                "role": "assistant",
                "content": assistant_message_content
            })

            # Add tool results to messages
            tool_results = []
            for content in assistant_message_content:
                if content.type == 'tool_use':
                    # Re-execute tool to get result (already executed above for logging)
                    mcp_result = await self.session.call_tool(content.name, content.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": mcp_result.content
                    })

            messages.append({
                "role": "user",
                "content": tool_results
            })

            # Continue loop - agent will process tool results and decide next action

        if iteration >= max_iterations:
            logging.warning(f"Agent loop reached max iterations ({max_iterations})")
            final_text.append(f"[Warning: Reached maximum iteration limit of {max_iterations}]")

        return "\n\n".join(final_text)

async def main():
    """Example main function for standalone usage."""
    import os

    client = MCPClient()

    # Connect to Notion
    notion_token = os.getenv("NOTION_INTEGRATION_TOKEN")
    if not notion_token:
        print("Set NOTION_INTEGRATION_TOKEN in .env first!")
        return

    env_vars = os.environ.copy()
    env_vars["NOTION_API_KEY"] = notion_token

    try:
        await client.connect_to_server(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env=env_vars
        )

        # Interactive query loop
        print("\n✅ Connected! Ask me anything (or 'quit' to exit):\n")
        while True:
            query = input("You: ")
            if query.lower() in ['quit', 'exit', 'q']:
                break

            response = await client.process_query(query)
            print(f"\nAI: {response}\n")

    finally:
        await client.exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(main())