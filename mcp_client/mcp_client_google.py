"""
MCP Client with Google Gemini support using official SDK

Supports Google Generative AI models:
- gemini-2.5-flash (recommended) - Latest stable model
- gemini-1.5-flash - Fast and cost-effective
- gemini-1.5-pro - Most capable

Setup:
1. Install: pip install google-genai
2. Get API key: https://aistudio.google.com/app/apikey
3. Add to .env: GOOGLE_API_KEY=your_key_here
4. Run: python main.py --provider google --model gemini-2.5-flash
"""

import asyncio
import json
import logging
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class MCPClientGoogle:
    def __init__(self, model: str = "gemini-2.5-flash", api_key: str = None):
        """
        Initialize Google Gemini MCP client using official SDK.

        Args:
            model: Gemini model name (default: gemini-2.5-flash)
            api_key: Google API key (if None, reads from GOOGLE_API_KEY or GEMINI_API_KEY env var)
        """
        self.model = model
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set and no api_key provided")

        # Initialize the Google GenAI client
        self.client = genai.Client(api_key=self.api_key)

        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    @staticmethod
    def _clean_tool_args(args: dict) -> dict:
        """Remove empty strings, empty objects, and None values from tool arguments.

        This is necessary because models may include optional parameters
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
                cleaned_nested = MCPClientGoogle._clean_tool_args(value)
                if cleaned_nested:  # Only include if not empty after cleaning
                    cleaned[key] = cleaned_nested
            else:
                cleaned[key] = value
        return cleaned

    @staticmethod
    def _convert_mcp_tools_to_google_format(mcp_tools) -> list:
        """
        Convert MCP tools to Google Gemini Tool format using SDK types.

        Args:
            mcp_tools: List of MCP tool objects with name, description, inputSchema

        Returns:
            List of genai.types.Tool objects
        """
        if not mcp_tools:
            return []

        # Convert to Google's Tool format
        function_declarations = []
        for tool in mcp_tools:
            func_decl = types.FunctionDeclaration(
                name=tool.name,
                description=tool.description or "No description provided",
                parameters=tool.inputSchema
            )
            function_declarations.append(func_decl)

        return [types.Tool(function_declarations=function_declarations)]

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
        """Process a query using Google Gemini SDK and available tools with agent loop logic

        Args:
            query: The user's question
            max_iterations: Maximum number of agent loop iterations (default: 10)

        Returns:
            Combined response with intermediate tool calls and final answer
        """
        # Get MCP tools and convert to Google format
        await self.session.initialize()
        response = await self.session.list_tools()
        mcp_tools = response.tools

        google_tools = self._convert_mcp_tools_to_google_format(mcp_tools)

        # Build tool descriptions for system instruction
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in mcp_tools
        ])

        # Simplified system prompt for Gemini
        system_instruction = f"""You are an AI assistant with access to Notion tools via MCP.

Available tools:
{tool_descriptions}

When the user asks a question:
1. Use the appropriate tool to get the needed information
2. Answer their question based on the tool results
3. Be clear and concise in your response"""

        # Initialize conversation history
        history = []

        # Track intermediate text responses
        final_text = []

        # Agent loop: continue until no more tool calls or max iterations reached
        iteration = 0
        user_message = query

        while iteration < max_iterations:
            iteration += 1
            logging.info(f"Agent loop iteration {iteration}/{max_iterations}")

            try:
                # Call Gemini API using SDK
                logging.info(f"Calling Gemini API with model: {self.model}")

                # Generate content with tools
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=[self.session],
                        temperature=0.7,
                        max_output_tokens=2048
                    )
                )

                logging.info(f"Response received: {response}")

                # Check if response has function calls
                if not response.candidates:
                    logging.error("No candidates in response")
                    break

                candidate = response.candidates[0]

                # Check for safety blocks
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                    if 'SAFETY' in str(candidate.finish_reason):
                        return "Response blocked by safety filters. Please rephrase your query."

                # Extract content parts
                if not candidate.content or not candidate.content.parts:
                    logging.error("No content parts in response")
                    break

                parts = candidate.content.parts
                has_function_calls = False
                function_calls_in_iteration = []

                # Process parts - extract text and function calls
                for part in parts:
                    if hasattr(part, 'text') and part.text:
                        text_content = part.text.strip()
                        if text_content:
                            final_text.append(text_content)
                    elif hasattr(part, 'function_call') and part.function_call:
                        has_function_calls = True
                        function_calls_in_iteration.append(part.function_call)

                # If no function calls, we're done
                if not has_function_calls:
                    logging.info("No function calls found. Agent loop complete.")
                    break

                # Add assistant's response to history
                history.append({"role": "model", "parts": [{"function_call": fc} for fc in function_calls_in_iteration]})

                # Process each function call
                function_responses = []
                for function_call in function_calls_in_iteration:
                    tool_name = function_call.name
                    tool_args = dict(function_call.args) if hasattr(function_call, 'args') else {}

                    # Clean tool arguments
                    cleaned_args = self._clean_tool_args(tool_args)
                    logging.info(f"Calling tool: {tool_name}")
                    logging.info(f"Original args: {tool_args}")
                    logging.info(f"Cleaned args: {cleaned_args}")

                    # Execute tool via MCP
                    mcp_result = await self.session.call_tool(tool_name, cleaned_args)

                    # Add note about tool call to final text
                    final_text.append(f"[Calling tool: {tool_name}]")
                    logging.info(f"Tool result: {mcp_result.content}")

                    # Build function response for next iteration
                    function_responses.append(
                        types.Part.from_function_response(
                            name=tool_name,
                            response={"content": str(mcp_result.content)}
                        )
                    )

                # Prepare next iteration with function responses
                user_message = types.Content(
                    role="user",
                    parts=function_responses
                )
                history.append({"role": "user", "parts": function_responses})

            except Exception as e:
                logging.error(f"Error in Gemini API call: {e}", exc_info=True)
                if "429" in str(e) or "rate limit" in str(e).lower():
                    return "Error: Rate limit exceeded. Please try again later."
                elif "401" in str(e) or "unauthorized" in str(e).lower():
                    return "Error: Invalid API key."
                elif "400" in str(e):
                    logging.error(f"Bad request error. Iteration {iteration}")
                    return f"Error: Invalid request to API."
                raise

        if iteration >= max_iterations:
            logging.warning(f"Agent loop reached max iterations ({max_iterations})")
            final_text.append(f"[Warning: Reached maximum iteration limit of {max_iterations}]")

        return "\n\n".join(final_text)

    async def cleanup(self):
        """Cleanup resources"""
        await self.exit_stack.aclose()
