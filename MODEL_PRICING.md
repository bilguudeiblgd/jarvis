# AI Model Pricing & Options for MCP

## Current Setup
✅ **Now using:** Claude Haiku 3.5 (90% cheaper than Sonnet!)

## 🎉 NEW: FREE Option with Ollama!

You can now run the bot with **100% FREE local AI** using Ollama!

See: `OLLAMA_SETUP.md` for setup instructions.

Run: `python ai_bot_ollama.py`

## Cost Comparison

### Ollama (FREE - Local AI) ⭐⭐⭐

| Model | Cost | Size | Quality | Speed |
|-------|------|------|---------|-------|
| **qwen2.5:0.5b** | **$0** | 500MB | Good | ⚡⚡⚡ |
| **qwen2.5:1.5b** | **$0** | 1GB | Better | ⚡⚡ |
| qwen2.5:3b | **$0** | 2GB | Great | ⚡ |
| llama3.2:1b | **$0** | 1GB | Good | ⚡⚡ |
| llama3.2:3b | **$0** | 2GB | Great | ⚡ |

### Anthropic (What you're using)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Speed | Use Case |
|-------|----------------------|------------------------|-------|----------|
| **Haiku 3.5** ⭐ | **$0.80** | **$4.00** | ⚡ Fast | **Telegram bot (current)** |
| Sonnet 4 | $3.00 | $15.00 | Medium | Complex tasks |
| Opus 4 | $15.00 | $75.00 | Slow | Very complex tasks |

**Your bot now uses Haiku 3.5** - changed in `mcp_client.py`

### OpenAI (Alternative)

| Model | Input | Output | Speed | Use Case |
|-------|-------|--------|-------|----------|
| **GPT-4o-mini** ⭐ | **$0.15** | **$0.60** | ⚡ Fast | **Cheapest option!** |
| GPT-4o | $2.50 | $10.00 | Medium | Good balance |
| GPT-4 Turbo | $10.00 | $30.00 | Medium | Most capable |

### Google Gemini

| Model | Input | Output | Speed |
|-------|-------|--------|-------|
| **Flash 1.5** ⭐ | **$0.075** | **$0.30** | ⚡ Fast |
| Pro 1.5 | $1.25 | $5.00 | Medium |

### Groq (Fastest & Cheapest!)

| Model | Input | Output | Speed |
|-------|-------|--------|-------|
| **Llama 3.1 8B** ⭐ | **$0.05** | **$0.08** | 🚀 **Super Fast** |
| Llama 3.1 70B | $0.59 | $0.79 | 🚀 Very Fast |
| Mixtral 8x7B | $0.24 | $0.24 | 🚀 Very Fast |

## Cost Examples (1000 messages/day)

Assume each message = 1000 input tokens + 500 output tokens

| Provider | Model | Daily Cost | Monthly Cost |
|----------|-------|------------|--------------|
| **Ollama** 🏆 | qwen2.5:0.5b | **$0** | **$0** ⭐⭐⭐ |
| **Ollama** 🏆 | llama3.2:3b | **$0** | **$0** ⭐⭐⭐ |
| **Groq** | Llama 3.1 8B | **$0.09** | **$2.70** ⭐⭐ |
| **Google** | Flash 1.5 | **$0.23** | **$6.75** ⭐⭐ |
| **OpenAI** | GPT-4o-mini | **$0.45** | **$13.50** ⭐ |
| **Anthropic** | Haiku 3.5 | **$2.80** | **$84** |
| Anthropic | Sonnet 4 | $10.50 | $315 |
| OpenAI | GPT-4o | $7.50 | $225 |

## How to Switch Models

### Option 1: Use Haiku (Already Done!)
The bot now uses Claude Haiku 3.5 - no changes needed!

### Option 2: Switch to OpenAI GPT-4o-mini

1. Install OpenAI:
```bash
pip install openai
```

2. Add to `.env`:
```bash
OPENAI_API_KEY=sk-...your-key...
```

3. In `ai_bot.py`, change:
```python
from mcp_client import MCPClient
# to
from mcp_client_openai import MCPClientOpenAI as MCPClient
```

That's it! The bot will now use GPT-4o-mini.

### Option 3: Make Model Configurable

You can easily add a config option to switch models:

```python
# In .env
AI_MODEL=haiku  # or: sonnet, opus, gpt-4o-mini, gpt-4o
```

## Recommendations

### For Telegram Bot (Current Use Case):
1. 🏆 **Ollama qwen2.5:0.5b** - 100% FREE, good quality, fast
2. ✅ **Claude Haiku 3.5** (current) - Best cloud option
3. 💰 **OpenAI GPT-4o-mini** - Very cheap cloud option
4. 🚀 **Groq Llama 3.1 8B** - Fast & cheap

### For Complex Queries:
- **Claude Sonnet 4** - Best reasoning
- **GPT-4o** - Good alternative

### For Production at Scale:
- **GPT-4o-mini** or **Gemini Flash** - Lowest cost
- **Groq Llama 3.1 70B** - Fastest response times

## Current Configuration

Your bot (`ai_bot.py`) now uses:
- **Model:** Claude Haiku 3.5 (`claude-3-5-haiku-20241022`)
- **Cost:** ~$0.80 input / $4.00 output per 1M tokens
- **Speed:** Fast ⚡
- **Savings:** 90% cheaper than Sonnet 4

## Next Steps

1. **Test the bot** with Haiku - it should work great for most queries
2. **If you want even cheaper:** Install OpenAI and use GPT-4o-mini
3. **Monitor usage:** Check your Anthropic dashboard to see actual costs

## Available Bot Scripts

| File | AI Provider | Cost | Setup |
|------|-------------|------|-------|
| **ai_bot_ollama.py** 🏆 | Ollama (local) | **$0/month** | See OLLAMA_SETUP.md |
| **ai_bot.py** | Claude Haiku | $84/month | Active now |
| **ai_bot_openai.py** | GPT-4o-mini | $13.50/month | Need OpenAI key |

## How to Switch

### Switch to FREE Ollama:
```bash
# Install Ollama
brew install ollama  # or download from ollama.com

# Start Ollama
ollama serve

# Pull a model
ollama pull qwen2.5:0.5b

# Run FREE bot!
python ai_bot_ollama.py
```

### Switch to OpenAI GPT-4o-mini:
```bash
pip install openai
# Add OPENAI_API_KEY to .env
python ai_bot.py  # (modify to use OpenAI client)
```

Want me to help you set up Ollama or another provider?
