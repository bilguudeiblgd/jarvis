# OpenAI Tool Calling Fixes

## Issues Fixed

### Problem: GPT-4o struggling to call tools

GPT-4o (including `gpt-4o-2024-11-20`) should support tool calling, but the implementation had several issues:

### 1. **Unsafe JSON Parsing** ❌
```python
# OLD - DANGEROUS!
tool_args = eval(tool_call.function.arguments)
```

**Fix:**
```python
# NEW - SAFE!
tool_args = json.loads(tool_call.function.arguments)
```

### 2. **Incorrect Message Serialization** ❌
```python
# OLD - Doesn't work properly
messages.append(message.model_dump())
```

**Fix:**
```python
# NEW - Proper OpenAI format
messages.append({
    "role": "assistant",
    "content": message.content,
    "tool_calls": [{
        "id": tc.id,
        "type": "function",
        "function": {
            "name": tc.function.name,
            "arguments": tc.function.arguments
        }
    } for tc in message.tool_calls]
})
```

### 3. **Missing Error Handling** ❌
No error handling for JSON parsing or tool execution

**Fix:**
- Try/catch for JSON parsing
- Try/catch for tool execution
- Better error messages

### 4. **No Debug Output** ❌
Hard to diagnose what's happening

**Fix:**
- Added debug prints showing:
  - Model being used
  - Available tools
  - Finish reason
  - Tool calls made
  - Tool arguments

### 5. **Wrong Default Model** ❌
Used `gpt-4o-mini` by default, which is cheaper but worse at tool calling

**Fix:**
- Changed default to `gpt-4o` for best tool calling
- Can still use `gpt-4o-mini` by passing `model="gpt-4o-mini"`

## How to Test

### Test Script:
```bash
python test_openai.py
```

This will:
1. Check for OpenAI API key
2. Connect to Notion MCP
3. Run a test query with GPT-4o
4. Show debug output
5. Display the response

### Direct Usage:
```bash
cd mcp_client
python mcp_client_openai.py
```

Then ask: "What pages do I have in Notion?"

## Key Changes

| Issue | Old Behavior | New Behavior |
|-------|-------------|--------------|
| JSON Parsing | `eval()` - unsafe | `json.loads()` - safe |
| Message Format | `model_dump()` | Proper dict structure |
| Error Handling | None | Try/catch with logs |
| Debug Output | None | Shows model, tools, calls |
| Default Model | gpt-4o-mini | gpt-4o (better) |
| Max Tokens | 1000 | 2000 |
| Tool Choice | Not set | "auto" |

## Debug Output Example

When you run a query, you'll now see:

```
[DEBUG] Using model: gpt-4o
[DEBUG] Available tools: ['API-post-search', 'API-get-user', ...]
[DEBUG] Response finish_reason: tool_calls
[DEBUG] Tool calls: [ChatCompletionMessageToolCall(...)]
[DEBUG] Calling tool: API-post-search with args: {'query': 'pages'}
```

This helps you see:
- ✅ Which model is being used
- ✅ What tools are available
- ✅ If tools are being called
- ✅ What arguments are passed

## Recommended Models

### For Best Tool Calling:
```python
response = await client.process_query(query, model="gpt-4o")
```
- Most reliable tool calling
- Cost: $2.50/$10 per 1M tokens

### For Cheap Option:
```python
response = await client.process_query(query, model="gpt-4o-mini")
```
- Good tool calling, not perfect
- Cost: $0.15/$0.60 per 1M tokens

### For Latest Features:
```python
response = await client.process_query(query, model="gpt-4o-2024-11-20")
```
- Newest version
- Should have best tool calling

## Still Having Issues?

### 1. Check the debug output
Look for:
- `finish_reason: stop` = No tools called (model chose not to)
- `finish_reason: tool_calls` = Tools called (good!)
- `finish_reason: length` = Hit token limit

### 2. Try forcing tool use
```python
# In mcp_client_openai.py, line 93:
tool_choice="required"  # Force tool use
```

### 3. Simplify the query
Some queries are too vague. Try:
- ❌ "Tell me about my workspace"
- ✅ "Search for all pages in Notion"

### 4. Check tool schemas
Make sure the Notion MCP tools have good descriptions:
```python
print(f"[DEBUG] Tools: {available_tools}")
```

## Package Structure

Now using proper Python package:

```
mcp_client/
├── __init__.py          # Package exports
├── mcp_client.py        # Claude (Anthropic)
├── mcp_client_openai.py # OpenAI (GPT)  ✅ FIXED
└── mcp_client_ollama.py # Ollama (FREE)
```

Import easily:
```python
from mcp_client import MCPClientOpenAI
```

No more `sys.path` hacks!

## Summary

The OpenAI client now:
- ✅ Safely parses JSON
- ✅ Properly formats messages
- ✅ Handles errors gracefully
- ✅ Shows debug output
- ✅ Uses best model by default
- ✅ Is a proper Python package

Try it with:
```bash
python test_openai.py
```
