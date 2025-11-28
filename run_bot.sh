#!/bin/bash

# Bot management script

PID_FILE="bot.pid"
LOG_FILE="bot.log"

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

    echo "🚀 Starting bot..."
    nohup python ai_bot_ollama.py > "$LOG_FILE" 2>&1 &
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

case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 2
        start_bot
        ;;
    status)
        status_bot
        ;;
    logs)
        logs_bot
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the bot"
        echo "  stop    - Stop the bot"
        echo "  restart - Restart the bot"
        echo "  status  - Check bot status"
        echo "  logs    - View bot logs (live)"
        exit 1
        ;;
esac
