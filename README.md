# ChefBot

A robust all-in-one Discord moderation bot with slash commands, buttons, logging, tickets, starboard, and more.

## Features

- **Moderation Commands**: Ban, kick, mute, unmute, clear, addrole, removerole, lock, unlock, slowmode
- **Slash Commands**: All commands use Discord's slash command system
- **Buttons**: Interactive buttons for user interactions and ticket closing
- **Logging**: Logs member bans, kicks, leaves, and moderation actions to a specified channel and database
- **Tickets**: Create support tickets in a category with close buttons
- **Starboard**: Automatically posts messages with enough star reactions to a starboard channel
- **Info Commands**: User info, server info, ping, uptime
- **Fun Commands**: Polls with auto-ending
- **Events**: Welcome/leave messages, auto-moderation (banned words, spam prevention, raid protection), autoroles
- **Config**: Setup command to configure channels
- **Reminders**: Set personal reminders
- **Voice Moderation**: VC mute, unmute, kick, ban with durations
- **Persistent Infractions**: Database-stored bans, kicks, mutes
- **Advanced Logging**: Searchable logs in database
- **Web Dashboard**: Full web panel for monitoring and management
- **Channel Management**: Lock/unlock channels, set slowmode
- **User Reports**: Anonymous reporting system
- **Music Integration**: Play music from YouTube with queue management

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a Discord bot at https://discord.com/developers/applications

3. Copy the bot token and paste it in `.env` file:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

4. Set the channel and category IDs in `.env` or use `/setup` command:
   - `LOG_CHANNEL_ID`: Channel for logging events
   - `STARBOARD_CHANNEL_ID`: Channel for starboard posts
   - `TICKET_CATEGORY_ID`: Category for ticket channels
   - `WELCOME_CHANNEL_ID`: Channel for welcome messages
   - `LEAVE_CHANNEL_ID`: Channel for leave messages
   - `MOD_CHANNEL_ID`: Channel for user reports
   - `AUTOROLE_ID`: Role to auto-assign on join

5. Invite the bot to your server with appropriate permissions (ban, kick, moderate members, manage channels, etc.)

6. Run the bot:
   ```
   python bot.py
   ```

7. (Optional) Run the dashboard:
   ```
   python dashboard.py
   ```

## Commands

- `/ban <user> [duration] [reason]`: Ban a user (duration in minutes, 0 for permanent)
- `/kick <user> [reason]`: Kick a user
- `/mute <user> [duration] [reason]`: Mute a user for specified minutes
- `/unmute <user>`: Unmute a user
- `/clear <amount>`: Clear messages (1-100)
- `/addrole <user> <role>`: Add role to user
- `/removerole <user> <role>`: Remove role from user
- `/lock [channel]`: Lock a channel (deny send messages)
- `/unlock [channel]`: Unlock a channel
- `/slowmode <seconds> [channel]`: Set slowmode in channel
- `/ticket <issue>`: Create a support ticket
- `/userinfo [user]`: Get user info
- `/serverinfo`: Get server info
- `/ping`: Check bot latency
- `/uptime`: Check bot uptime
- `/help [command]`: Get help with commands
- `/logs [user] [event]`: View recent logs (admin only)
- `/vcmute <user> [duration]`: Mute in voice
- `/vcunmute <user>`: Unmute in voice
- `/vckick <user>`: Kick from voice
- `/vcban <user> <duration>`: Ban from voice with duration
- `/button`: Test button interaction
- `/setup <setting> <value>`: Configure bot settings (admin only)
- `/remind <time> <message>`: Set a reminder (e.g., 1h, 30m)
- `/report <reason>`: Submit an anonymous report to moderators
- `/play <query>`: Play music from YouTube URL or search
- `/skip`: Skip the current song
- `/queue`: Show the music queue
- `/stop`: Stop music and clear queue

## Modular Structure

The bot is organized into cogs for maintainability:
- `moderation.py`: Moderation commands
- `tickets.py`: Ticket system
- `starboard.py`: Starboard feature
- `info.py`: Info commands
- `fun.py`: Fun commands
- `events.py`: Event listeners and autoroles
- `config.py`: Configuration commands
- `reminders.py`: Reminder system
- `vc_mod.py`: Voice moderation
- `logging.py`: Advanced logging
- `reports.py`: User reports
- `music.py`: Music integration

## Auto-Moderation

Edit `cogs/events.py` to customize banned words.

## Web Dashboard

A basic Flask app for viewing bot status. Expand it to include logs and stats.

## Requirements

- Python 3.8+
- discord.py 2.0+
- python-dotenv
- flask</content>
<parameter name="filePath">/workspaces/ChefBot/README.md# ChefBot

A robust all-in-one Discord moderation bot with slash commands, buttons, logging, tickets, and starboard.

## Features

- **Moderation Commands**: Ban, kick, mute, unmute users
- **Slash Commands**: All commands use Discord's slash command system
- **Buttons**: Interactive buttons for user interactions
- **Logging**: Logs member bans and leaves to a specified channel
- **Tickets**: Create support tickets in a category
- **Starboard**: Automatically posts messages with enough star reactions to a starboard channel

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a Discord bot at https://discord.com/developers/applications

3. Copy the bot token and paste it in `.env` file:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

4. Set the channel and category IDs in `.env` or directly in `bot.py`:
   - `LOG_CHANNEL_ID`: Channel for logging events
   - `STARBOARD_CHANNEL_ID`: Channel for starboard posts
   - `TICKET_CATEGORY_ID`: Category for ticket channels

5. Invite the bot to your server with appropriate permissions (ban, kick, moderate members, manage channels, etc.)

6. Run the bot:
   ```
   python bot.py
   ```

## Commands

- `/ban <user> [duration] [reason]`: Ban a user (duration in minutes, 0 for permanent)
- `/kick <user> [reason]`: Kick a user
- `/mute <user> [duration] [reason]`: Mute a user for specified minutes
- `/unmute <user>`: Unmute a user
- `/clear <amount>`: Clear messages (1-100)
- `/ticket <issue>`: Create a support ticket
- `/button`: Test button interaction

## Configuration

Edit the IDs in `bot.py` or `.env` to configure channels and categories.

For starboard, the threshold is set to 3 stars by default. Change `star_threshold` in the code.

## Requirements

- Python 3.8+
- discord.py 2.0+
- python-dotenv