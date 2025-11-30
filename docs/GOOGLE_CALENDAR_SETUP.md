# Google Calendar Setup Guide

This guide explains how to set up Google Calendar integration using OAuth 2.0 authentication.

## How It Works

The OAuth flow happens **once**:
1. First time: Browser opens, you authenticate with Google
2. Tokens are stored locally (in `~/.config/google-calendar-mcp/`)
3. Future runs: Tokens are reused automatically
4. If tokens expire (after 7 days in test mode): Browser reopens for re-authentication

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a Project** → **New Project**
3. Enter a project name (e.g., "Jarvis Bot")
4. Click **Create**

### 2. Enable Google Calendar API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Google Calendar API"
3. Click on it and press **Enable**

### 3. Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (unless you have a Google Workspace)
3. Fill in the required fields:
   - **App name**: Jarvis Bot
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click **Save and Continue**
5. On **Scopes** page, click **Add or Remove Scopes**
6. Filter for "calendar" and select:
   - `https://www.googleapis.com/auth/calendar` (Manage calendars)
7. Click **Update** and **Save and Continue**
8. On **Test users** page, click **Add Users**
9. Add your Gmail address
10. Click **Save and Continue**

### 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Choose **Desktop app** as the application type
4. Name it (e.g., "Jarvis Desktop Client")
5. Click **Create**
6. Click **Download JSON** (or the download icon)
7. Save the file securely (e.g., `~/google-oauth-credentials.json`)

### 5. Configure Your Bot

Add to your `.env` file:

```bash
GOOGLE_OAUTH_CREDENTIALS=/path/to/your/google-oauth-credentials.json
```

Example:
```bash
GOOGLE_OAUTH_CREDENTIALS=/Users/yourusername/google-oauth-credentials.json
```

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

### 7. First Run - OAuth Authentication

When you first run the bot, it will:

```bash
python main.py --provider anthropic
```

**What happens:**
1. The bot starts and connects to Google Calendar MCP
2. A browser window opens automatically
3. You'll see a Google sign-in page
4. **Important**: You may see a warning "This app isn't verified"
   - Click **Advanced**
   - Click **Go to Jarvis Bot (unsafe)** (it's safe - it's your app!)
5. Sign in with the Gmail account you added as a test user
6. Review permissions and click **Allow**
7. You'll see "Authentication successful!" or similar
8. Close the browser window
9. The bot is now connected!

### 8. Token Storage

After successful authentication, tokens are stored at:
- **macOS/Linux**: `~/.config/google-calendar-mcp/tokens.json`
- **Windows**: `%APPDATA%\google-calendar-mcp\tokens.json`

These tokens are used automatically on subsequent runs - no need to re-authenticate!

## Token Expiration

In **test mode** (default), tokens expire after **7 days**. When they expire:
- The browser will open again for re-authentication
- Simply repeat the OAuth flow

To extend token lifetime, you can publish your OAuth app (not required for personal use).

## Troubleshooting

### "OAuth credentials file not found"

**Solution**:
- Check that `GOOGLE_OAUTH_CREDENTIALS` in `.env` points to the correct path
- Use absolute path (e.g., `/Users/username/file.json` not `~/file.json`)
- Verify the file exists at that location

### "Error 401: invalid_client"

**Solution**:
- Make sure you downloaded the OAuth credentials (not service account)
- Application type should be "Desktop app"
- Re-download the JSON if needed

### "Access blocked: This app hasn't been verified"

**Solution**:
- This is expected for test apps
- Click **Advanced** → **Go to [App Name] (unsafe)**
- This only appears because the app is in testing mode
- It's safe - you're authenticating your own app

### "You don't have permission to access this app"

**Solution**:
- Make sure you added your Gmail address as a test user (Step 3.9)
- The email you're signing in with must match the test user email

### Browser doesn't open

**Solution**:
- Check that you're running the bot on a machine with a browser
- Make sure you're not running in a purely headless environment
- Try running locally first, then deploy to server after tokens are generated

### "Token has been expired or revoked"

**Solution**:
- Delete the token file: `rm ~/.config/google-calendar-mcp/tokens.json`
- Run the bot again - it will prompt for re-authentication

## Available Calendar Operations

Your bot can now:
- **List events**: See upcoming calendar events
- **Create events**: Add new events to your calendar
- **Update events**: Modify existing events
- **Delete events**: Remove events
- **Search events**: Find events by keyword
- **Check free/busy**: See availability

## Example Bot Commands

Once connected, try these commands:

```
/ai What's on my calendar today?
/ai Create a meeting tomorrow at 2pm for 1 hour called "Team Sync"
/ai What events do I have this week?
/ai Find all meetings with "standup" in the title
/ai Am I free tomorrow at 3pm?
```

## Security Best Practices

1. **Keep the OAuth credentials JSON secure**
   - Don't commit to git (add to `.gitignore`)
   - Store in a secure location
   - Use environment variables for the path

2. **Test users only**
   - Only add your own email as a test user
   - Don't publish the app unless needed

3. **Monitor access**
   - Check [Google Account Permissions](https://myaccount.google.com/permissions)
   - You can revoke access anytime

4. **Token security**
   - Tokens are stored locally
   - Keep your machine secure
   - Don't share the tokens file

## Optional: Publishing Your App

If you want tokens to last longer than 7 days:

1. Go to **OAuth consent screen** in Google Cloud Console
2. Click **Publish App**
3. Follow the verification process (if required)

**Note**: For personal use, staying in test mode is fine - just re-authenticate every 7 days.

## Running on a Server

If running on a headless server:

**Option 1: Authenticate locally first**
1. Run bot on your local machine
2. Complete OAuth flow
3. Copy token file to server: `~/.config/google-calendar-mcp/tokens.json`

**Option 2: Use SSH with X11 forwarding**
```bash
ssh -X user@server
python main.py --provider anthropic
```

## Next Steps

- Test basic operations (list, create, update events)
- Explore all available calendar tools
- Set up automatic re-authentication reminders (optional)
