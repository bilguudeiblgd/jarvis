# Connecting to Notion MCP Server

This guide shows you how to connect your MCP client to Notion.

## Quick Start

### 1. Install Node.js (if not already installed)
Download from: https://nodejs.org/

### 2. Get Your Notion Integration Token

1. Go to https://www.notion.so/my-integrations
2. Click **"+ New integration"**
3. Give it a name (e.g., "MCP Client")
4. Copy the **Internal Integration Token**
5. Click **Submit**

### 3. Share Notion Pages with Your Integration

**Important:** Your integration won't see any pages until you share them!

1. Open a Notion page you want to access
2. Click the **•••** menu (top right)
3. Scroll to **Connections**
4. Search for your integration name
5. Click to add it

Repeat for each page/database you want to access.

### 4. Add Token to .env File

Edit `.env` and replace `your_notion_token_here` with your actual token:

```
NOTION_INTEGRATION_TOKEN=secret_abc123...
```

### 5. Run the Connection Script

```bash
python mcp-client/connect_notion.py
```

This will:
- Auto-install the Notion MCP server (via npx)
- Connect to Notion
- List available tools and resources

## How It Works

The setup uses these components:

1. **notion-mcp-wrapper.js** - Wrapper script that runs the Notion MCP server via npx
2. **connect_notion.py** - Example script showing how to connect
3. **main.py** - Your MCP client with updated `connect_to_server()` that accepts environment variables

## Using Notion in Your Code

```python
import os
from mcp_client.main import MCPClient

async def use_notion():
    client = MCPClient()

    # Setup environment with Notion token
    env_vars = os.environ.copy()
    env_vars["NOTION_API_KEY"] = os.getenv("NOTION_INTEGRATION_TOKEN")

    # Connect
    await client.connect_to_server(
        server_script_path="notion-mcp-wrapper.js",
        env=env_vars
    )

    # Now use Notion tools via client.session
    tools_response = await client.session.list_tools()

    # Call a tool (example)
    # result = await client.session.call_tool("search_pages", {"query": "todo"})

    # Cleanup
    await client.exit_stack.aclose()
```

## Available Notion MCP Tools

Once connected, you'll have access to tools like:
- Search pages
- Read page content
- Update pages
- Query databases
- And more

Run `connect_notion.py` to see the full list of available tools.

## Troubleshooting

### "Node.js not found"
Install Node.js from https://nodejs.org/

### "No resources found"
Make sure you've shared Notion pages with your integration (see step 3 above)

### "Invalid token"
- Check your token in .env is correct
- Make sure there are no extra spaces
- Token should start with `secret_`

### Connection errors
- Ensure Node.js is installed and in PATH
- The Notion MCP server will auto-install via npx on first run
- Check your internet connection

## Integration with Telegram Bot

You can combine this with your Telegram bot to:
- Search Notion pages via bot commands
- Get page content
- Create/update pages from Telegram

Example integration coming soon!