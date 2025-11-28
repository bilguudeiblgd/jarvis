#!/usr/bin/env python3
"""
Quick test for OpenAI + MCP integration
"""

import asyncio
import os
from dotenv import load_dotenv
from mcp_client import MCPClientOpenAI

load_dotenv()


async def test_openai():
    print("=" * 60)
    print("🧪 TESTING OPENAI + MCP")
    print("=" * 60)

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ OPENAI_API_KEY not found in .env")
        print("   Get one from: https://platform.openai.com/api-keys")
        return

    print(f"\n✓ Found OpenAI API key: {api_key[:20]}...")

    # Check Notion token
    notion_token = os.getenv("NOTION_INTEGRATION_TOKEN")
    if not notion_token:
        print("\n⚠️  NOTION_INTEGRATION_TOKEN not set")
        print("   Will connect without Notion")
        return

    print(f"✓ Found Notion token: {notion_token[:20]}...")

    client = MCPClientOpenAI()

    try:
        print("\n🔌 Connecting to Notion MCP server...")

        env_vars = os.environ.copy()
        env_vars["NOTION_TOKEN"] = notion_token

        await client.connect_to_server(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env=env_vars
        )

        print("\n✅ Connected!")

        # Test query
        print("\n" + "=" * 60)
        print("📝 TEST QUERY")
        print("=" * 60)

        query = "Search for all pages in my Notion workspace"
        print(f"\nQuery: {query}")
        print("\nProcessing with GPT-4o...")

        response = await client.process_query(query, model="gpt-4o")

        print("\n" + "=" * 60)
        print("Response:")
        print("=" * 60)
        print(response)
        print("=" * 60)

        print("\n✅ Test complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(test_openai())
