import discord
from discord import app_commands
from discord.ext import commands
import time

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
        if log_channel_id:
            channel = self.bot.get_channel(log_channel_id)
            if channel:
                await channel.send(f'{user} was banned.')
        await self.log_event(guild.id, 'ban', f'User {user} banned')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
        if log_channel_id:
            channel = self.bot.get_channel(log_channel_id)
            if channel:
                await channel.send(f'{member} left the server.')
        await self.log_event(member.guild.id, 'leave', f'User {member} left')

    async def add_infraction(self, user_id, guild_id, inf_type, reason, moderator_id):
        await self.bot.db.execute(
            'INSERT INTO infractions (user_id, guild_id, type, reason, moderator_id, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, guild_id, inf_type, reason, moderator_id, time.time())
        )
        await self.bot.db.commit()

    async def get_infractions(self, user_id, guild_id):
        cursor = await self.bot.db.execute(
            'SELECT type, reason, timestamp FROM infractions WHERE user_id = ? AND guild_id = ? ORDER BY timestamp DESC',
            (user_id, guild_id)
        )
        return await cursor.fetchall()

    @app_commands.command(name='ban', description='Ban a user')
    @app_commands.describe(user='User to ban', duration='Duration in minutes (0 for permanent)', reason='Reason for ban')
    async def ban(self, interaction: discord.Interaction, user: discord.Member, duration: int = 0, reason: str = 'No reason provided'):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message('You do not have permission to ban members.', ephemeral=True)
            return
        try:
            await user.ban(reason=reason)
            await interaction.response.send_message(f'Banned {user.mention} for: {reason}' + (f' (for {duration} minutes)' if duration > 0 else ' (permanent)'))
            await self.add_infraction(user.id, interaction.guild.id, 'ban', reason, interaction.user.id)
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                channel = self.bot.get_channel(log_channel_id)
                if channel:
                    await channel.send(f'{interaction.user} banned {user} for: {reason}' + (f' (for {duration} minutes)' if duration > 0 else ' (permanent)'))
            # DM the user
            dm_message = f'You have been banned from {interaction.guild.name} for: {reason}'
            if duration > 0:
                dm_message += f'\nDuration: {duration} minutes'
            try:
                await user.send(dm_message)
            except:
                pass
            # Schedule unban if temporary
            if duration > 0:
                await asyncio.sleep(duration * 60)
                try:
                    await interaction.guild.unban(user)
                    if log_channel_id:
                        channel = self.bot.get_channel(log_channel_id)
                        if channel:
                            await channel.send(f'{user} unbanned after {duration} minutes.')
                except Exception as e:
                    print(f'Error unbanning {user}: {e}')
        except Exception as e:
            await interaction.response.send_message(f'Error banning user: {e}', ephemeral=True)

    @app_commands.command(name='kick', description='Kick a user')
    @app_commands.describe(user='User to kick', reason='Reason for kick')
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = 'No reason provided'):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message('You do not have permission to kick members.', ephemeral=True)
            return
        try:
            await user.kick(reason=reason)
            await interaction.response.send_message(f'Kicked {user.mention} for: {reason}')
            await self.add_infraction(user.id, interaction.guild.id, 'kick', reason, interaction.user.id)
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                channel = self.bot.get_channel(log_channel_id)
                if channel:
                    await channel.send(f'{interaction.user} kicked {user} for: {reason}')
            # DM the user
            dm_message = f'You have been kicked from {interaction.guild.name} for: {reason}'
            try:
                await user.send(dm_message)
            except:
                pass
        except Exception as e:
            await interaction.response.send_message(f'Error kicking user: {e}', ephemeral=True)

    @app_commands.command(name='mute', description='Mute a user')
    @app_commands.describe(user='User to mute', duration='Duration in minutes', reason='Reason for mute')
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: int = 10, reason: str = 'No reason provided'):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message('You do not have permission to mute members.', ephemeral=True)
            return
        try:
            delta = discord.utils.utcnow() + discord.timedelta(minutes=duration)
            await user.timeout(delta, reason=reason)
            await interaction.response.send_message(f'Muted {user.mention} for {duration} minutes: {reason}')
            await self.add_infraction(user.id, interaction.guild.id, 'mute', reason, interaction.user.id)
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                channel = self.bot.get_channel(log_channel_id)
                if channel:
                    await channel.send(f'{interaction.user} muted {user} for {duration} minutes: {reason}')
            # DM the user
            dm_message = f'You have been muted in {interaction.guild.name} for {duration} minutes: {reason}'
            try:
                await user.send(dm_message)
            except:
                pass
        except Exception as e:
            await interaction.response.send_message(f'Error muting user: {e}', ephemeral=True)

    @app_commands.command(name='unmute', description='Unmute a user')
    @app_commands.describe(user='User to unmute')
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message('You do not have permission to unmute members.', ephemeral=True)
            return
        try:
            await user.timeout(None)
            await interaction.response.send_message(f'Unmuted {user.mention}')
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                channel = self.bot.get_channel(log_channel_id)
                if channel:
                    await channel.send(f'{interaction.user} unmuted {user}')
        except Exception as e:
            await interaction.response.send_message(f'Error unmuting user: {e}', ephemeral=True)

    @app_commands.command(name='clear', description='Clear messages')
    @app_commands.describe(amount='Number of messages to clear')
    async def clear(self, interaction: discord.Interaction, amount: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message('You do not have permission to manage messages.', ephemeral=True)
            return
        if amount < 1 or amount > 100:
            await interaction.response.send_message('Amount must be between 1 and 100.', ephemeral=True)
            return
        try:
            await interaction.response.defer(ephemeral=True)
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f'Cleared {len(deleted)} messages.', ephemeral=True)
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                channel = self.bot.get_channel(log_channel_id)
                if channel:
                    await channel.send(f'{interaction.user} cleared {len(deleted)} messages in {interaction.channel.mention}')
        except Exception as e:
            await interaction.followup.send(f'Error clearing messages: {e}', ephemeral=True)

    @app_commands.command(name='addrole', description='Add a role to a user')
    @app_commands.describe(user='User to add role to', role='Role to add')
    async def addrole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message('You do not have permission to manage roles.', ephemeral=True)
            return
        if interaction.user.top_role <= role:
            await interaction.response.send_message('You cannot assign a role higher than or equal to your own.', ephemeral=True)
            return
        try:
            await user.add_roles(role)
            await interaction.response.send_message(f'Added {role.mention} to {user.mention}')
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                channel = self.bot.get_channel(log_channel_id)
                if channel:
                    await channel.send(f'{interaction.user} added {role.name} to {user}')
        except Exception as e:
            await interaction.response.send_message(f'Error adding role: {e}', ephemeral=True)

    @app_commands.command(name='removerole', description='Remove a role from a user')
    @app_commands.describe(user='User to remove role from', role='Role to remove')
    async def removerole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message('You do not have permission to manage roles.', ephemeral=True)
            return
        if interaction.user.top_role <= role:
            await interaction.response.send_message('You cannot remove a role higher than or equal to your own.', ephemeral=True)
            return
        try:
            await user.remove_roles(role)
            await interaction.response.send_message(f'Removed {role.mention} from {user.mention}')
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                channel = self.bot.get_channel(log_channel_id)
                if channel:
                    await channel.send(f'{interaction.user} removed {role.name} from {user}')
        except Exception as e:
            await interaction.response.send_message(f'Error removing role: {e}', ephemeral=True)

    @app_commands.command(name='lock', description='Lock a channel')
    @app_commands.describe(channel='Channel to lock')
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message('You do not have permission to manage channels.', ephemeral=True)
            return
        channel = channel or interaction.channel
        try:
            await channel.set_permissions(interaction.guild.default_role, send_messages=False)
            await interaction.response.send_message(f'Locked {channel.mention}')
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                log_channel = self.bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(f'{interaction.user} locked {channel.mention}')
        except Exception as e:
            await interaction.response.send_message(f'Error locking channel: {e}', ephemeral=True)

    @app_commands.command(name='unlock', description='Unlock a channel')
    @app_commands.describe(channel='Channel to unlock')
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message('You do not have permission to manage channels.', ephemeral=True)
            return
        channel = channel or interaction.channel
        try:
            await channel.set_permissions(interaction.guild.default_role, send_messages=None)
            await interaction.response.send_message(f'Unlocked {channel.mention}')
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                log_channel = self.bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(f'{interaction.user} unlocked {channel.mention}')
        except Exception as e:
            await interaction.response.send_message(f'Error unlocking channel: {e}', ephemeral=True)

    @app_commands.command(name='slowmode', description='Set slowmode on a channel')
    @app_commands.describe(channel='Channel to set slowmode', seconds='Slowmode delay in seconds')
    async def slowmode(self, interaction: discord.Interaction, channel: discord.TextChannel = None, seconds: int = 0):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message('You do not have permission to manage channels.', ephemeral=True)
            return
        channel = channel or interaction.channel
        try:
            await channel.edit(slowmode_delay=seconds)
            await interaction.response.send_message(f'Set slowmode to {seconds} seconds in {channel.mention}')
            log_channel_id = self.bot.config.get('LOG_CHANNEL_ID')
            if log_channel_id:
                log_channel = self.bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(f'{interaction.user} set slowmode to {seconds}s in {channel.mention}')
        except Exception as e:
            await interaction.response.send_message(f'Error setting slowmode: {e}', ephemeral=True)

    async def log_event(self, guild_id, event, details):
        await self.bot.db.execute(
            'INSERT INTO logs (guild_id, event, details, timestamp) VALUES (?, ?, ?, ?)',
            (guild_id, event, details, time.time())
        )
        await self.bot.db.commit()

async def setup(bot):
    await bot.add_cog(Moderation(bot))