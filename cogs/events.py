import discord
from discord.ext import commands
import time

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_words = ['badword1', 'badword2']  # Add your banned words here

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            # Raid protection
            now = time.time()
            if member.guild.id not in self.bot.join_times:
                self.bot.join_times[member.guild.id] = []
            self.bot.join_times[member.guild.id].append(now)
            # Remove old joins (>10 seconds)
            self.bot.join_times[member.guild.id] = [t for t in self.bot.join_times[member.guild.id] if now - t < 10]
            if len(self.bot.join_times[member.guild.id]) > 5:  # More than 5 joins in 10s
                # Lockdown or kick
                await member.kick(reason='Raid protection')
                log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
                if log_channel_id:
                    channel = self.bot.get_channel(log_channel_id)
                    if channel:
                        await channel.send(f'Raider {member} kicked.')

            welcome_channel_id = self.bot.config.get('WELCOME_CHANNEL_ID')
            if welcome_channel_id:
                channel = self.bot.get_channel(welcome_channel_id)
                if channel:
                    await channel.send(f'Welcome {member.mention} to {member.guild.name}!')

            # Autorole
            autorole_id = self.bot.config.get('AUTOROLE_ID')
            if autorole_id:
                role = member.guild.get_role(autorole_id)
                if role:
                    try:
                        await member.add_roles(role)
                    except Exception as e:
                        print(f'Error adding autorole: {e}')
        except Exception as e:
            print(f'Error in welcome: {e}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            leave_channel_id = self.bot.config.get('LEAVE_CHANNEL_ID')
            if leave_channel_id:
                channel = self.bot.get_channel(leave_channel_id)
                if channel:
                    await channel.send(f'{member} has left the server.')
        except Exception as e:
            print(f'Error in leave: {e}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        try:
            # Spam prevention
            now = time.time()
            user_id = message.author.id
            if user_id not in self.bot.message_counts:
                self.bot.message_counts[user_id] = []
            self.bot.message_counts[user_id].append(now)
            # Keep only last 10 seconds
            self.bot.message_counts[user_id] = [t for t in self.bot.message_counts[user_id] if now - t < 10]
            if len(self.bot.message_counts[user_id]) > 5:  # More than 5 messages in 10s
                await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=5), reason='Spam')
                await message.channel.send(f'{message.author.mention} muted for spamming.')
                log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
                if log_channel_id:
                    channel = self.bot.get_channel(log_channel_id)
                    if channel:
                        await channel.send(f'{message.author} muted for spam.')

            # Auto-mod: check for banned words
            content = message.content.lower()
            if any(word in content for word in self.banned_words):
                await message.delete()
                await message.channel.send(f'{message.author.mention}, your message contained a banned word and was deleted.')
                log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
                if log_channel_id:
                    channel = self.bot.get_channel(log_channel_id)
                    if channel:
                        await channel.send(f'{message.author} used a banned word in {message.channel.mention}: {message.content}')
        except Exception as e:
            print(f'Error in on_message: {e}')

async def setup(bot):
    await bot.add_cog(Events(bot))