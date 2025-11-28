#!/bin/bash

# Jarvis Bot Management Script
#
# Usage:
#   ./run_bot.sh start --provider ollama --model qwen2.5:0.5b
#   ./run_bot.sh start --provider anthropic --model claude-3-5-haiku-20241022
#   ./run_bot.sh start --provider openai --model gpt-4o-mini
#   ./run_bot.sh stop
#   ./run_bot.sh restart --provider ollama --model llama3.2:3b
#   ./run_bot.sh status
#   ./run_bot.sh logs

PID_FILE="bot.pid"
LOG_FILE="bot.log"

# Parse arguments after the command
parse_bot_args() {
    BOT_ARGS=""
    shift # Skip the command (start/restart)

    while [[ $# -gt 0 ]]; do
        case $1 in
            --provider|--model|--log-level)
                BOT_ARGS="$BOT_ARGS $1 $2"
                shift 2
                ;;
            *)
                echo "Unknown argument: $1"
                exit 1
                ;;
        esac
    done
}

start_bot() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "❌ Bot is already running (PID: $PID)"
            return 1
        else
            echo "Removing stale PID file..."
            rm "$PID_FILE"
        fi
    fi

    # Parse additional arguments
    parse_bot_args "$@"

    if [ -z "$BOT_ARGS" ]; then
        echo "❌ Missing required arguments!"
        echo ""
        echo "Usage: $0 start --provider <provider> [--model <model>]"
        echo ""
        echo "Examples:"
        echo "  $0 start --provider ollama --model qwen2.5:0.5b"
        echo "  $0 start --provider anthropic --model claude-3-5-haiku-20241022"
        echo "  $0 start --provider openai --model gpt-4o-mini"
        return 1
    fi

    echo "🚀 Starting bot with: $BOT_ARGS"
    nohup python main.py $BOT_ARGS > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "✅ Bot started (PID: $(cat $PID_FILE))"
    echo "📄 Logs: tail -f $LOG_FILE"
}

stop_bot() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Bot is not running (no PID file found)"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🛑 Stopping bot (PID: $PID)..."
        kill "$PID"
        rm "$PID_FILE"
        echo "✅ Bot stopped"
    else
        echo "❌ Bot process not found (PID: $PID)"
        rm "$PID_FILE"
    fi
}

status_bot() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Bot is not running"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Bot is running (PID: $PID)"
        echo "📄 Logs: tail -f $LOG_FILE"
    else
        echo "❌ Bot is not running (stale PID file)"
        rm "$PID_FILE"
    fi
}

logs_bot() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "❌ No log file found"
    fi
}

show_usage() {
    echo "Jarvis Bot Management Script"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs} [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start   - Start the bot (requires --provider)"
    echo "  stop    - Stop the bot"
    echo "  restart - Restart the bot (requires --provider)"
    echo "  status  - Check bot status"
    echo "  logs    - View bot logs (live)"
    echo ""
    echo "Options for start/restart:"
    echo "  --provider <name>   AI provider (anthropic|openai|ollama)"
    echo "  --model <name>      Model name (optional, uses provider default)"
    echo "  --log-level <level> Logging level (DEBUG|INFO|WARNING|ERROR)"
    echo ""
    echo "Examples:"
    echo "  $0 start --provider ollama --model qwen2.5:0.5b"
    echo "  $0 start --provider anthropic --model claude-3-5-haiku-20241022"
    echo "  $0 start --provider openai --model gpt-4o-mini"
    echo "  $0 restart --provider ollama"
    echo "  $0 stop"
    echo "  $0 status"
    echo "  $0 logs"
}

case "$1" in
    start)
        start_bot "$@"
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 2
        start_bot "$@"
        ;;
    status)
        status_bot
        ;;
    logs)
        logs_bot
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
