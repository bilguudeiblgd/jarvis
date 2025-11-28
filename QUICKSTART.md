# Quick Start Guide

Get your AI Telegram bot running in 5 minutes!

## Prerequisites

- ✅ Python 3.9+ installed
- ✅ Node.js installed (for Notion MCP)
- ✅ Telegram account

## Step-by-Step Setup

### 1. Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

### 2. Get Your Tokens (2 minutes)

#### Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the token you receive

#### Anthropic API Key
1. Go to https://console.anthropic.com/
2. Sign up/login
3. Go to API Keys section
4. Create a new key and copy it

#### Notion Integration Token
1. Go to https://www.notion.so/my-integrations
2. Click **"+ New integration"**
3. Give it a name (e.g., "Telegram Bot")
4. Copy the **Internal Integration Token**

### 3. Configure .env (30 seconds)

The `.env` file should already exist. Update it with your tokens:

```bash
BOT_TOKEN=your_telegram_token_here
ANTHROPIC_API_KEY=your_anthropic_key_here
NOTION_INTEGRATION_TOKEN=your_notion_token_here
```

### 4. Share Notion Pages (1 minute)

**Important:** The bot can't see any pages until you share them!

1. Open a Notion page you want the bot to access
2. Click **•••** (three dots, top right)
3. Scroll to **Connections**
4. Find and add your integration

Repeat for each page/database you want accessible.

### 5. Run the Bot (10 seconds)

```bash
python ai_bot.py
```

You should see:
```
INFO - 🤖 Starting AI bot...
INFO - 🔌 Initializing MCP client...
INFO - ✅ MCP client connected to Notion!
INFO - Starting bot...
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
- Check the bot is running (`python ai_bot.py`)
- Verify the BOT_TOKEN is correct
- Make sure you started the bot in Telegram with `/start`

## Next Steps

- Share more Notion pages with your integration
- Try complex queries like "Find all TODOs"
- Use `/broadcast` to message all users
- Integrate with cron jobs for scheduled notifications

## Need Help?

Check the full `README.md` for detailed documentation and architecture.
