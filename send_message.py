"""
Helper script to send messages to Telegram users.

Usage examples:
1. Send to specific user:
   python send_message.py --chat-id 123456789 --message "Hello!"

2. Send to all users:
   python send_message.py --all --message "Broadcast message"

This can be called from cron jobs, FastAPI endpoints, or other scripts.
"""

import asyncio
import os
import json
import argparse
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


def load_users():
    """Load registered users from file."""
    if os.path.exists("users.json"):
        with open("users.json", 'r') as f:
            return json.load(f)
    return {}


async def send_message_to_user(chat_id: int, message: str):
    """Send a message to a specific user."""
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("Error: BOT_TOKEN not found in environment variables!")
        return False

    bot = Bot(token=bot_token)

    try:
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"Message sent to {chat_id}")
        return True
    except Exception as e:
        print(f"Failed to send message to {chat_id}: {e}")
        return False


async def send_to_all_users(message: str):
    """Send a message to all registered users."""
    users = load_users()

    if not users:
        print("No users found. Users must use /start command first.")
        return

    sent_count = 0
    failed_count = 0

    bot_token = os.getenv("BOT_TOKEN")
    bot = Bot(token=bot_token)

    for chat_id, user_info in users.items():
        try:
            await bot.send_message(chat_id=int(chat_id), text=message)
            print(f"✓ Sent to {user_info.get('first_name', chat_id)}")
            sent_count += 1
        except Exception as e:
            print(f"✗ Failed to send to {chat_id}: {e}")
            failed_count += 1

    print(f"\nBroadcast complete! Sent: {sent_count}, Failed: {failed_count}")


def main():
    parser = argparse.ArgumentParser(description="Send messages via Telegram bot")
    parser.add_argument("--chat-id", type=int, help="Specific chat ID to send to")
    parser.add_argument("--all", action="store_true", help="Send to all registered users")
    parser.add_argument("--message", "-m", required=True, help="Message to send")
    parser.add_argument("--list-users", action="store_true", help="List all registered users")

    args = parser.parse_args()

    if args.list_users:
        users = load_users()
        if not users:
            print("No users registered yet.")
        else:
            print("\nRegistered users:")
            for chat_id, info in users.items():
                print(f"  {chat_id}: {info.get('first_name')} (@{info.get('username', 'N/A')})")
        return

    if args.all:
        asyncio.run(send_to_all_users(args.message))
    elif args.chat_id:
        asyncio.run(send_message_to_user(args.chat_id, args.message))
    else:
        print("Error: Please specify either --chat-id or --all")
        parser.print_help()


if __name__ == "__main__":
    main()