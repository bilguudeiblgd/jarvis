# Jarvis - AI Telegram Bot with Notion Integration

A modular Telegram bot with Notion workspace integration via MCP (Model Context Protocol). Supports multiple AI providers including Anthropic Claude, OpenAI GPT, and local Ollama models.

## Features

- 🤖 Multiple AI provider support (Anthropic, OpenAI, Ollama, Google Gemini)
- 📝 Direct access to your Notion pages and databases
- 📅 Google Calendar integration (view, create, update, delete events)
- 🔍 Search and query your Notion workspace
- 💬 Natural language interaction
- 🏗️ Modular architecture for easy customization
- 💰 Cost-optimized options from FREE (Ollama) to premium (Claude)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file with the following:

```bash
# Required for all providers
BOT_TOKEN=your_bot_token_here                          # From @BotFather on Telegram
NOTION_INTEGRATION_TOKEN=your_notion_token_here        # From notion.so/my-integrations

# Required for Anthropic/Claude (if using --provider anthropic)
ANTHROPIC_API_KEY=your_anthropic_key_here              # From console.anthropic.com

# Required for OpenAI (if using --provider openai)
OPENAI_API_KEY=your_openai_key_here                    # From platform.openai.com

# Optional for Ollama (if using --provider ollama)
OLLAMA_MODEL=qwen2.5:0.5b                              # Default model if not specified via --model

# Optional for Google Calendar integration
GOOGLE_OAUTH_CREDENTIALS=/path/to/oauth-credentials.json  # See docs/GOOGLE_CALENDAR_SETUP.md
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

### 5. (Optional) Set Up Google Calendar Integration

To enable Google Calendar features, follow the guide at [docs/GOOGLE_CALENDAR_SETUP.md](docs/GOOGLE_CALENDAR_SETUP.md).

Quick summary:
1. Create a Google Cloud project
2. Enable Google Calendar API
3. Configure OAuth consent screen (add yourself as test user)
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the OAuth credentials JSON file
6. Add `GOOGLE_OAUTH_CREDENTIALS` to your `.env`
7. First run: Browser opens for one-time authentication
8. Tokens stored locally for future use

## Usage

### Start the Bot

The bot now uses a unified entry point with command-line arguments:

```bash
# Using Ollama (FREE - local models)
python main.py --provider ollama --model qwen2.5:0.5b

# Using Anthropic Claude
python main.py --provider anthropic --model claude-3-5-haiku-20241022

# Using OpenAI GPT
python main.py --provider openai --model gpt-4o-mini
```

Or use the management script:

```bash
# Start with Ollama
./run_bot.sh start --provider ollama --model qwen2.5:0.5b

# Start with Anthropic
./run_bot.sh start --provider anthropic --model claude-3-5-haiku-20241022

# Stop the bot
./run_bot.sh stop

# Restart with different provider
./run_bot.sh restart --provider openai --model gpt-4o-mini

# Check status
./run_bot.sh status

# View logs
./run_bot.sh logs
```

### Telegram Commands

- `/start` - Initialize the bot
- `/help` - Show help message
- `/ai <question>` - Ask AI anything with Notion access

### Example Queries

**Notion:**
```
/ai What pages do I have in my Notion workspace?
/ai Search for pages about "project planning"
/ai Summarize my recent meeting notes
/ai Find all pages tagged with "important"
```

**Google Calendar** (if enabled):
```
/ai What's on my calendar today?
/ai Create a meeting tomorrow at 2pm for 1 hour
/ai Show me next week's events
/ai Find all meetings with "standup" in the title
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
│     Bot     │      │   Factory    │      │ MCP Server  │
│  (modular)  │      └──────┬───────┘      └─────────────┘
└─────────────┘             │               ┌─────────────┐
                            │──────────────▶│   Google    │
                            │               │  Calendar   │
                            │               │ MCP Server  │
                            │               └─────────────┘
                            │
                            ├──── Anthropic Claude
                            ├──── OpenAI GPT
                            ├──── Ollama (local)
                            └──── Google Gemini
```

### Project Structure

```
jarvis/
├── main.py                      # Single entry point with CLI args
├── run_bot.sh                   # Bot management script
├── telegram_bot/                # Telegram bot logic
│   ├── __init__.py
│   ├── bot.py                   # Main bot class
│   ├── handlers.py              # Command handlers
│   └── user_manager.py          # User management
├── mcp_client/                  # MCP client with AI providers
│   ├── __init__.py
│   ├── factory.py               # Client factory
│   ├── mcp_client.py            # Anthropic implementation
│   ├── mcp_client_openai.py     # OpenAI implementation
│   ├── mcp_client_ollama.py     # Ollama implementation
│   ├── mcp_client_google.py     # Google Gemini implementation
│   └── connections/             # MCP server connections
│       ├── notion.py            # Notion MCP connection
│       └── google_calendar.py   # Google Calendar MCP (OAuth)
├── docs/                        # Documentation
│   └── GOOGLE_CALENDAR_SETUP.md # Calendar setup guide
└── requirements.txt
```

## AI Provider Options

### Anthropic Claude
- Models: `claude-3-5-haiku-20241022`, `claude-sonnet-4-20250514`, `claude-opus-4-20250514`
- Cost: ~$84/month for 1000 msgs/day (Haiku)
- Best for: Production use, complex queries

### OpenAI GPT
- Models: `gpt-4o-mini`, `gpt-4o`
- Cost: ~$13.50/month for 1000 msgs/day (GPT-4o-mini)
- Best for: Cost-effective alternative to Claude

### Ollama (Local)
- Models: `qwen2.5:0.5b`, `qwen2.5:1.5b`, `llama3.2:1b`, `llama3.2:3b`
- Cost: 100% FREE (runs locally)
- Best for: Privacy, development, testing

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

### Running in Development

```bash
# Direct Python execution
python main.py --provider ollama --model qwen2.5:0.5b --log-level DEBUG

# Using management script
./run_bot.sh start --provider anthropic --model claude-3-5-haiku-20241022
```

### Testing Different Providers

```bash
# Test Ollama (requires Ollama running)
python main.py --provider ollama

# Test Anthropic
python main.py --provider anthropic

# Test OpenAI
python main.py --provider openai
```

## Quick Start Examples

### Using Ollama (FREE)

```bash
# Install Ollama
# Visit: https://ollama.com/download

# Pull a model
ollama pull qwen2.5:0.5b

# Start the bot
python main.py --provider ollama --model qwen2.5:0.5b
```

### Using Anthropic Claude

```bash
# Set ANTHROPIC_API_KEY in .env
python main.py --provider anthropic --model claude-3-5-haiku-20241022
```

### Using OpenAI GPT

```bash
# Set OPENAI_API_KEY in .env
python main.py --provider openai --model gpt-4o-mini
```

### Advanced Queries

```
/ai Create a summary of all pages with tag "work"
/ai What are my TODOs in Notion?
/ai Find pages modified in the last week
/ai Search for "budget" in my databases
```

## License

MIT
