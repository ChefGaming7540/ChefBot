import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import aiosqlite
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.voice_states = True

class ChefBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.config = {
            'LOG_CHANNEL_ID': int(os.getenv('LOG_CHANNEL_ID', 0)),
            'STARBOARD_CHANNEL_ID': int(os.getenv('STARBOARD_CHANNEL_ID', 0)),
            'TICKET_CATEGORY_ID': int(os.getenv('TICKET_CATEGORY_ID', 0)),
            'WELCOME_CHANNEL_ID': int(os.getenv('WELCOME_CHANNEL_ID', 0)),
            'LEAVE_CHANNEL_ID': int(os.getenv('LEAVE_CHANNEL_ID', 0)),
            'MOD_CHANNEL_ID': int(os.getenv('MOD_CHANNEL_ID', 0)),
            'AUTOROLE_ID': int(os.getenv('AUTOROLE_ID', 0))
        }
        self.db = None
        self.start_time = time.time()
        self.message_counts = {}  # For spam prevention
        self.join_times = {}  # For raid protection

    async def setup_hook(self):
        # Setup database
        self.db = await aiosqlite.connect('chefbot.db')
        await self.create_tables()
        # Load cogs
        await self.load_extension('cogs.moderation')
        await self.load_extension('cogs.tickets')
        await self.load_extension('cogs.starboard')
        await self.load_extension('cogs.info')
        await self.load_extension('cogs.fun')
        await self.load_extension('cogs.events')
        await self.load_extension('cogs.config')
        await self.load_extension('cogs.reminders')
        await self.load_extension('cogs.vc_mod')
        await self.load_extension('cogs.logging')
        await self.load_extension('cogs.reports')
        await self.load_extension('cogs.music')

    async def create_tables(self):
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS infractions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                guild_id INTEGER,
                type TEXT,
                reason TEXT,
                moderator_id INTEGER,
                timestamp REAL
            )
        ''')
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                event TEXT,
                details TEXT,
                timestamp REAL
            )
        ''')
        await self.db.commit()

bot = ChefBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

bot.run(TOKEN)