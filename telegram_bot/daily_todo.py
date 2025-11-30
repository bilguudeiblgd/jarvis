"""
Daily todo reminder functionality.
"""

import logging
from datetime import datetime
from telegram_bot.user_manager import load_users

logger = logging.getLogger(__name__)


async def daily_todo_reminder(bot_application, mcp_client):
    """
    Run daily at 8 AM to prompt users for todos.

    This function:
    1. Loads all registered users
    2. For each user, calls the AI to create a Notion toggle list for today
    3. Sends the AI's response (asking for todos) to the user via Telegram

    Args:
        bot_application: Telegram bot Application instance
        mcp_client: MCP client instance for AI queries
    """
    logger.info("🔔 Running daily todo reminder...")

    # Check if MCP client is available
    if not mcp_client or not mcp_client.session:
        logger.error("❌ Cannot send daily reminder: MCP client not connected")
        return

    # Load registered users
    try:
        users = load_users()
        logger.info(f"📋 Sending reminders to {len(users)} user(s)")
    except Exception as e:
        logger.error(f"❌ Failed to load users: {e}")
        return

    # For each user, send a personalized reminder
    sent_count = 0
    failed_count = 0

    for chat_id, user_data in users.items():
        try:
            # Get today's date for the toggle list title
            today = datetime.now().strftime("%Y-%m-%d")

            # Create prompt for AI to create Notion toggle list and ask for todos
            prompt = (
                f'In my Notion workspace, find the "Daily Todo" page and create a new '
                f'toggle list titled "{today}". Then ask me what todos I want to add for today.'
            )

            # Call AI to process the prompt
            logger.info(f"💭 Processing reminder for user {chat_id}")
            response = await mcp_client.process_query(prompt)

            # Send AI response to user via Telegram
            await bot_application.bot.send_message(
                chat_id=int(chat_id),
                text=response
            )

            sent_count += 1
            logger.info(f"✅ Sent reminder to {chat_id}")

        except Exception as e:
            failed_count += 1
            logger.error(f"❌ Failed to send reminder to {chat_id}: {e}")
            continue

    logger.info(
        f"🎉 Daily reminder complete! Sent: {sent_count}, Failed: {failed_count}"
    )
