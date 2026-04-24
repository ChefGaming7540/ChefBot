import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import time

class VCModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc_bans = {}  # user_id: end_time

    @app_commands.command(name='vcmute', description='Mute a user in voice')
    @app_commands.describe(user='User to mute', duration='Duration in minutes')
    async def vcmute(self, interaction: discord.Interaction, user: discord.Member, duration: int = 10):
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message('You do not have permission to mute members.', ephemeral=True)
            return
        try:
            if user.voice and user.voice.channel:
                await user.edit(mute=True)
                await interaction.response.send_message(f'Voice muted {user.mention} for {duration} minutes.')
                # Schedule unmute
                await asyncio.sleep(duration * 60)
                if user.voice and user.voice.channel:
                    await user.edit(mute=False)
            else:
                await interaction.response.send_message('User is not in a voice channel.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

    @app_commands.command(name='vcunmute', description='Unmute a user in voice')
    @app_commands.describe(user='User to unmute')
    async def vcunmute(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message('You do not have permission to unmute members.', ephemeral=True)
            return
        try:
            if user.voice and user.voice.channel:
                await user.edit(mute=False)
                await interaction.response.send_message(f'Voice unmuted {user.mention}.')
            else:
                await interaction.response.send_message('User is not in a voice channel.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

    @app_commands.command(name='vckick', description='Kick a user from voice')
    @app_commands.describe(user='User to kick')
    async def vckick(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message('You do not have permission to move members.', ephemeral=True)
            return
        try:
            if user.voice and user.voice.channel:
                await user.edit(voice_channel=None)
                await interaction.response.send_message(f'Kicked {user.mention} from voice.')
            else:
                await interaction.response.send_message('User is not in a voice channel.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

    @app_commands.command(name='vcban', description='Ban a user from voice with duration')
    @app_commands.describe(user='User to ban', duration='Duration in minutes')
    async def vcban(self, interaction: discord.Interaction, user: discord.Member, duration: int):
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message('You do not have permission to move members.', ephemeral=True)
            return
        try:
            if user.voice and user.voice.channel:
                await user.edit(voice_channel=None)
            self.vc_bans[user.id] = time.time() + duration * 60
            await interaction.response.send_message(f'Voice banned {user.mention} for {duration} minutes.')
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id in self.vc_bans:
            if self.vc_bans[member.id] > time.time():
                if after.channel:
                    await member.edit(voice_channel=None)
            else:
                del self.vc_bans[member.id]

async def setup(bot):
    await bot.add_cog(VCModeration(bot))