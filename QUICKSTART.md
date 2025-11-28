# Quick Start Guide

Get Jarvis running in 5 minutes! Choose your AI provider below.

## Prerequisites

- ✅ Python 3.9+ installed
- ✅ Node.js installed (for Notion MCP)
- ✅ Telegram account
- ✅ Choose one: Anthropic API key, OpenAI API key, OR Ollama (FREE)

## Step-by-Step Setup

### 1. Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

### 2. Get Your Tokens (2 minutes)

#### Required for All Providers

**Telegram Bot Token:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the token you receive

**Notion Integration Token:**
1. Go to https://www.notion.so/my-integrations
2. Click **"+ New integration"**
3. Give it a name (e.g., "Jarvis Bot")
4. Copy the **Internal Integration Token**

#### Choose Your AI Provider

**Option A: Ollama (100% FREE - Recommended for Testing)**
1. Download from https://ollama.com/download
2. Install and run: `ollama serve`
3. Pull a model: `ollama pull qwen2.5:0.5b`
4. No API key needed!

**Option B: Anthropic Claude**
1. Go to https://console.anthropic.com/
2. Sign up/login and create an API key
3. Copy the key (~$84/month for regular use)

**Option C: OpenAI GPT**
1. Go to https://platform.openai.com/
2. Sign up/login and create an API key
3. Copy the key (~$13.50/month for regular use)

### 3. Configure .env (30 seconds)

Create a `.env` file with your tokens:

```bash
# Required for all providers
BOT_TOKEN=your_telegram_token_here
NOTION_INTEGRATION_TOKEN=your_notion_token_here

# Add based on your AI provider choice:
# If using Anthropic:
ANTHROPIC_API_KEY=your_anthropic_key_here

# If using OpenAI:
OPENAI_API_KEY=your_openai_key_here

# If using Ollama (optional):
OLLAMA_MODEL=qwen2.5:0.5b
```

### 4. Share Notion Pages (1 minute)

**Important:** The bot can't see any pages until you share them!

1. Open a Notion page you want the bot to access
2. Click **•••** (three dots, top right)
3. Scroll to **Connections**
4. Find and add your integration

Repeat for each page/database you want accessible.

### 5. Run the Bot (10 seconds)

Choose the command based on your AI provider:

**Using Ollama (FREE):**
```bash
python main.py --provider ollama --model qwen2.5:0.5b
```

**Using Anthropic Claude:**
```bash
python main.py --provider anthropic --model claude-3-5-haiku-20241022
```

**Using OpenAI GPT:**
```bash
python main.py --provider openai --model gpt-4o-mini
```

Or use the management script:
```bash
./run_bot.sh start --provider ollama --model qwen2.5:0.5b
```

You should see:
```
INFO - 🤖 Jarvis - AI Telegram Bot
INFO - Provider: ollama
INFO - Model: qwen2.5:0.5b
INFO - 🔌 Initializing MCP client...
INFO - ✅ MCP client connected to Notion!
INFO - ✅ Starting Telegram bot...
```

### 6. Test It! (30 seconds)

1. Open Telegram
2. Find your bot (search for the name you gave it)
3. Send: `/start`
4. Try: `/ai What pages do I have in Notion?`

🎉 **Done!** Your AI bot is running!

## Example Conversations

```
You: /ai What's in my Notion workspace?
Bot: I found 15 pages in your workspace, including...

You: /ai Search for pages about "project planning"
Bot: I found 3 pages related to project planning: ...

You: /ai Summarize my meeting notes from last week
Bot: Based on your meeting notes, the key points were...
```

## Troubleshooting

### "MCP client not connected"
- Run `node --version` to check Node.js is installed
- Check your NOTION_INTEGRATION_TOKEN is correct

### "No resources found"
- You forgot to share Notion pages with your integration!
- Go to Notion → Page → ••• → Connections → Add your integration

### "BOT_TOKEN not found"
- Make sure `.env` file exists in the project root
- Check there are no spaces around the `=` sign

### Bot doesn't respond
- Check the bot is running with the correct provider
- Verify the BOT_TOKEN is correct
- Make sure you started the bot in Telegram with `/start`
- For Ollama: ensure `ollama serve` is running

### Which AI provider should I choose?
- **Ollama**: FREE, runs locally, great for testing and privacy
- **OpenAI**: Cheapest cloud option (~$13.50/month)
- **Anthropic**: Best quality, higher cost (~$84/month)

## Next Steps

- Share more Notion pages with your integration
- Try complex queries like "Find all TODOs"
- Use `/broadcast` to message all users
- Integrate with cron jobs for scheduled notifications

## Need Help?

Check the full `README.md` for detailed documentation and architecture.
