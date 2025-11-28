# AI Telegram Bot with Notion Integration

A Telegram bot powered by Claude AI with access to your Notion workspace via MCP (Model Context Protocol).

## Features

- 🤖 Chat with Claude AI through Telegram
- 📝 AI has access to your Notion pages/databases
- 🔍 Search and query your Notion workspace
- 💬 Natural language interaction

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `.env` and add:

```bash
# Telegram Bot Token (get from @BotFather)
BOT_TOKEN=your_bot_token_here

# Anthropic API Key (get from console.anthropic.com)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Notion Integration Token (get from notion.so/my-integrations)
NOTION_INTEGRATION_TOKEN=your_notion_token_here
```

### 3. Set Up Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click **"+ New integration"**
3. Give it a name and copy the **Internal Integration Token**
4. Add the token to `.env`
5. **Important:** Share your Notion pages with the integration:
   - Open any page you want the bot to access
   - Click **•••** (top right) → **Connections** → Add your integration

### 4. Install Node.js

The Notion MCP server requires Node.js. Download from: https://nodejs.org/

## Usage

### Start the Bot

```bash
python ai_bot.py
```

The bot will:
1. Start the Telegram bot
2. Connect to Notion via MCP (auto-installs on first run)
3. Be ready to answer questions!

### Telegram Commands

- `/start` - Initialize the bot
- `/help` - Show help message
- `/ai <question>` - Ask AI anything with Notion access

### Example Queries

```
/ai What pages do I have in my Notion workspace?
/ai Search for pages about "project planning"
/ai Summarize my recent meeting notes
/ai Find all pages tagged with "important"
```

## Architecture

```
┌─────────────┐
│   Telegram  │
│     User    │
└──────┬──────┘
       │
       │ /ai query
       │
┌──────▼──────┐      ┌──────────────┐      ┌─────────────┐
│  Telegram   │─────▶│  MCP Client  │─────▶│   Notion    │
│     Bot     │      │   + Claude   │      │ MCP Server  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            │
                     ┌──────▼──────┐
                     │   Claude    │
                     │  Sonnet 4   │
                     └─────────────┘
```

## Files

- `ai_bot.py` - Main bot with AI integration
- `bot.py` - Simple bot (original, no AI)
- `mcp-client/main.py` - MCP client for connecting to servers
- `mcp-client/connect_notion.py` - Test Notion connection
- `send_message.py` - Helper to send messages programmatically

## Troubleshooting

### "MCP client not connected"
- Check that Node.js is installed: `node --version`
- Verify NOTION_INTEGRATION_TOKEN in .env
- Make sure you've shared Notion pages with your integration

### "No resources found"
- You haven't shared any Notion pages with the integration
- Go to Notion → Page → ••• → Connections → Add integration

### "npx not found"
- Install Node.js from https://nodejs.org/

### Bot not responding
- Check BOT_TOKEN is correct in .env
- Verify ANTHROPIC_API_KEY is valid
- Check logs for errors

## Development

### Test MCP Connection Separately

```bash
python mcp-client/connect_notion.py
```

### Test MCP Client with CLI

```bash
python mcp-client/main.py
```

This starts an interactive CLI where you can test queries.

## Examples

### Basic Usage

1. Start the bot: `python ai_bot.py`
2. Open Telegram and find your bot
3. Send: `/ai What's in my Notion?`
4. The AI will search your Notion workspace and respond!

### Advanced Queries

```
/ai Create a summary of all pages with tag "work"
/ai What are my TODOs in Notion?
/ai Find pages modified in the last week
/ai Search for "budget" in my databases
```

## License

MIT
