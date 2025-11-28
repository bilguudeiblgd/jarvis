"""
Simple script to connect to Notion MCP server.

Setup:
1. Get your Notion integration token from: https://www.notion.so/my-integrations
   - Create a new integration
   - Copy the Internal Integration Token
   - Share your Notion pages with the integration

2. Add your token to .env:
   NOTION_INTEGRATION_TOKEN=your_token_here

3. Run:
   python mcp-client/connect_notion.py

No installation needed - npx will auto-download the server!
"""

import asyncio
import os
from mcp_client import MCPClient


async def connect_to_notion(client: MCPClient):
    # Get Notion token
    notion_token = os.getenv("NOTION_INTEGRATION_TOKEN")

    if not notion_token or notion_token == "your_notion_token_here":
        print("\n❌ Error: NOTION_INTEGRATION_TOKEN not set in .env file")
        print("\nTo set up:")
        print("1. Go to https://www.notion.so/my-integrations")
        print("2. Click '+ New integration'")
        print("3. Copy the Internal Integration Token")
        print("4. Add to .env: NOTION_INTEGRATION_TOKEN=your_token_here")
        return

    try:
        print("🔌 Connecting to Notion MCP server...")
        print("   (First run may take a moment as npx downloads the server)")

        # Create environment with Notion token
        env_vars = os.environ.copy()
        env_vars["NOTION_TOKEN"] = notion_token

        # Connect directly using npx - no installation needed!
        await client.connect_to_server(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env=env_vars
        )

        print("✅ Connected to Notion!")

        # List available tools
        if client.session:
            tools_response = await client.session.list_tools()
            print(f"\n📚 Available tools ({len(tools_response.tools)}):")
            for tool in tools_response.tools:
                print(f"  • {tool.name}")
                if tool.description:
                    print(f"    └─ {tool.description}")

            # Example: Get a list of resources (pages/databases)
            print("\n📄 Available resources:")
            try:
                resources_response = await client.session.list_resources()
                if resources_response.resources:
                    for resource in resources_response.resources:
                        print(f"  • {resource.name}")
                else:
                    print("  No resources found. Make sure you've shared Notion pages with your integration!")
            except Exception as e:
                print(f"  Could not list resources: {e}")

    except FileNotFoundError as e:
        print("\n❌ Error: npx not found")
        print("Make sure Node.js is installed: https://nodejs.org/")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Node.js is installed")
        print("2. Check your NOTION_INTEGRATION_TOKEN is valid")
        print("3. Share your Notion pages with the integration")
        print("4. Make sure you have internet connection (npx needs to download)")

    finally:
        # Cleanup
        await client.exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(connect_to_notion())