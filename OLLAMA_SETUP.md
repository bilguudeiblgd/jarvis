# FREE AI with Ollama - Setup Guide

Run your Telegram bot with **100% FREE local AI** - no API costs!

## Quick Start

### 1. Install Ollama

**Mac:**
```bash
brew install ollama
```

Or download from: https://ollama.com/download

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download installer from: https://ollama.com/download

### 2. Start Ollama Server

```bash
ollama serve
```

Leave this running in the background.

### 3. Pull a Small Model

**Recommended: Qwen2.5 0.5B (500MB - fastest)**
```bash
ollama pull qwen2.5:0.5b
```

**Other options:**
```bash
# Better quality (1GB)
ollama pull qwen2.5:1.5b

# Even better quality (2GB)
ollama pull llama3.2:3b

# Microsoft's model (2GB)
ollama pull phi3:mini
```

### 4. Run the FREE Bot

```bash
python ai_bot_ollama.py
```

That's it! Your bot now runs with **100% FREE local AI**!

## Model Comparison

| Model | Size | Speed | Quality | Recommendation |
|-------|------|-------|---------|----------------|
| **qwen2.5:0.5b** | 500MB | ⚡⚡⚡ | Good | **Best for Telegram bot** |
| qwen2.5:1.5b | 1GB | ⚡⚡ | Better | Good balance |
| qwen2.5:3b | 2GB | ⚡ | Great | If you have RAM |
| llama3.2:1b | 1GB | ⚡⚡ | Good | Fast alternative |
| llama3.2:3b | 2GB | ⚡ | Great | Good quality |
| phi3:mini | 2GB | ⚡ | Great | Microsoft model |

## Cost Comparison

| Provider | Model | Cost (1000 msgs/day) | Setup |
|----------|-------|----------------------|-------|
| **Ollama** | qwen2.5:0.5b | **$0/month** ⭐ | Local |
| **Ollama** | llama3.2:3b | **$0/month** ⭐ | Local |
| Anthropic | Haiku 3.5 | $84/month | Cloud |
| OpenAI | GPT-4o-mini | $13.50/month | Cloud |

## Change Model

### Method 1: Environment Variable

Add to `.env`:
```bash
OLLAMA_MODEL=qwen2.5:1.5b
```

### Method 2: Edit Code

In `ai_bot_ollama.py`, change line 34:
```python
OLLAMA_MODEL = "qwen2.5:1.5b"  # Change model here
```

## Available Bot Versions

| File | AI Provider | Cost | Use Case |
|------|-------------|------|----------|
| `ai_bot_ollama.py` ⭐ | Ollama (local) | **FREE** | Personal use, low traffic |
| `ai_bot.py` | Claude Haiku | $84/mo | Production, best quality |
| `ai_bot_openai.py` | GPT-4o-mini | $13.50/mo | Cheap cloud option |

## Troubleshooting

### "Connection refused" error
Ollama not running. Start it:
```bash
ollama serve
```

### "Model not found" error
Model not installed. Pull it:
```bash
ollama pull qwen2.5:0.5b
```

### Slow responses
Try a smaller model:
```bash
ollama pull qwen2.5:0.5b
```

### Bot says "MCP client not connected"
1. Check Ollama is running: `ollama list`
2. Check model is pulled: `ollama list`
3. Restart bot

## Commands

```bash
# List installed models
ollama list

# Pull a new model
ollama pull qwen2.5:1.5b

# Remove a model
ollama rm qwen2.5:0.5b

# Chat with model directly (for testing)
ollama run qwen2.5:0.5b

# Check Ollama is running
curl http://localhost:11434/api/tags
```

## Performance Tips

### For Fastest Responses:
- Use `qwen2.5:0.5b` (500MB)
- Or `llama3.2:1b` (1GB)

### For Best Quality:
- Use `qwen2.5:3b` (2GB)
- Or `llama3.2:3b` (2GB)

### For Balance:
- Use `qwen2.5:1.5b` (1GB) ⭐

## Hybrid Setup (Best of Both Worlds)

Use Ollama for simple queries, Claude for complex ones:

```python
# In ai_bot.py, add logic:
if query_is_simple:
    use_ollama()  # FREE
else:
    use_claude()  # $$$
```

## System Requirements

| Model | RAM Needed | CPU | Storage |
|-------|------------|-----|---------|
| qwen2.5:0.5b | 2GB | Any | 500MB |
| qwen2.5:1.5b | 4GB | Any | 1GB |
| qwen2.5:3b | 8GB | Modern | 2GB |
| llama3.2:3b | 8GB | Modern | 2GB |

## Why Use Ollama?

✅ **100% FREE** - No API costs ever
✅ **Privacy** - Data never leaves your machine
✅ **No Rate Limits** - Use as much as you want
✅ **Works Offline** - No internet needed
✅ **Fast** - Local inference, low latency

❌ **Lower Quality** - Not as smart as Claude/GPT-4
❌ **Requires Local Resources** - Needs RAM/CPU
❌ **Setup Required** - Must install and manage models

## Recommended Setup

**For Personal Use:**
```bash
python ai_bot_ollama.py  # FREE!
```

**For Production:**
```bash
python ai_bot.py  # Claude Haiku - best quality
```

**For Testing:**
```bash
# Test locally with Ollama first
python mcp-client/mcp_client_ollama.py

# Then deploy with Claude
python ai_bot.py
```

---

**Try it now:** `python ai_bot_ollama.py` 🚀
