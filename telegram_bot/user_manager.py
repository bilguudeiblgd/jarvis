"""
User management utilities for the Telegram bot.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

USERS_FILE = "users.json"


def load_users():
    """Load registered users from file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_user(chat_id, username, first_name):
    """Save user chat ID to file."""
    users = load_users()
    users[str(chat_id)] = {
        "username": username,
        "first_name": first_name
    }
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    logger.info(f"Saved user {chat_id} ({first_name})")
