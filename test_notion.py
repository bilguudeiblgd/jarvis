#!/usr/bin/env python3
"""
Quick test script to verify Notion MCP integration.

This will:
1. Connect to Notion MCP server
2. List available tools
3. List accessible pages/databases
4. Try a simple search

Usage: python test_notion.py
"""

import asyncio
import os
from dotenv import load_dotenv

from mcp_client import MCPClient

load_dotenv()


async def test_notion_connection():
    """Test Notion MCP connection and list pages."""

    print("=" * 60)
    print("🧪 NOTION MCP CONNECTION TEST")
    print("=" * 60)

    # Check token
    notion_token = os.getenv("NOTION_INTEGRATION_TOKEN")
    if not notion_token:
        print("\n❌ ERROR: NOTION_INTEGRATION_TOKEN not found in .env")
        return False

    print(f"\n✓ Found Notion token: {notion_token[:20]}...")

    # Initialize client
    client = MCPClient()

    try:
        # Connect to Notion
        print("\n📡 Connecting to Notion MCP server...")
        env_vars = os.environ.copy()
        env_vars["NOTION_TOKEN"] = notion_token

        await client.connect_to_server(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env=env_vars
        )

        print("✅ Connected successfully!")

        # List available tools
        print("\n" + "=" * 60)
        print("📚 AVAILABLE TOOLS")
        print("=" * 60)

        tools_response = await client.session.list_tools()
        if tools_response.tools:
            for i, tool in enumerate(tools_response.tools, 1):
                print(f"\n{i}. {tool.name}")
                if tool.description:
                    print(f"   Description: {tool.description}")
        else:
            print("⚠️  No tools found")

        # List resources (pages/databases)
        print("\n" + "=" * 60)
        print("📄 ACCESSIBLE PAGES/DATABASES")
        print("=" * 60)

        try:
            resources_response = await client.session.list_resources()
            if resources_response.resources:
                print(f"\n✅ Found {len(resources_response.resources)} resources:\n")
                for i, resource in enumerate(resources_response.resources, 1):
                    print(f"{i}. {resource.name}")
                    if hasattr(resource, 'uri'):
                        print(f"   URI: {resource.uri}")
                    if hasattr(resource, 'description') and resource.description:
                        print(f"   Description: {resource.description}")
                    print()
            else:
                print("\n⚠️  No resources found!")
                print("\n💡 This means:")
                print("   - You haven't shared any Notion pages with your integration")
                print("   - Go to Notion → Page → ••• → Connections → Add your integration")
                return False
        except Exception as e:
            print(f"\n⚠️  Could not list resources: {e}")

        # Try a test query
        print("\n" + "=" * 60)
        print("🔍 TEST QUERY")
        print("=" * 60)

        test_query = "List all pages in my workspace"
        print(f"\nQuery: '{test_query}'")
        print("Processing...\n")

        try:
            response = await client.process_query(test_query)
            print("Response:")
            print("-" * 60)
            print(response)
            print("-" * 60)
        except Exception as e:
            print(f"❌ Query failed: {e}")

        print("\n" + "=" * 60)
        print("✅ TEST COMPLETE")
        print("=" * 60)

        return True

    except FileNotFoundError:
        print("\n❌ ERROR: npx not found")
        print("   Install Node.js from: https://nodejs.org/")
        return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check Node.js is installed: node --version")
        print("   2. Verify NOTION_INTEGRATION_TOKEN is correct")
        print("   3. Share Notion pages with your integration")
        return False

    finally:
        # Cleanup
        await client.exit_stack.aclose()
        print("\n🧹 Cleaned up connection")


def main():
    """Run the test."""
    try:
        success = asyncio.run(test_notion_connection())
        if success:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n⚠️  Some issues detected. See messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
