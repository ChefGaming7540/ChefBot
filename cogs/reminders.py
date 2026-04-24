import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import re

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='remind', description='Set a reminder')
    @app_commands.describe(time='Time (e.g., 1h, 30m, 10s)', message='Reminder message')
    async def remind(self, interaction: discord.Interaction, time: str, message: str):
        try:
            # Parse time
            match = re.match(r'(\d+)([smhd])', time.lower())
            if not match:
                await interaction.response.send_message('Invalid time format. Use like 1h, 30m, 10s.', ephemeral=True)
                return
            amount, unit = match.groups()
            amount = int(amount)
            if unit == 's':
                seconds = amount
            elif unit == 'm':
                seconds = amount * 60
            elif unit == 'h':
                seconds = amount * 3600
            elif unit == 'd':
                seconds = amount * 86400
            else:
                await interaction.response.send_message('Invalid unit.', ephemeral=True)
                return
            await interaction.response.send_message(f'Reminder set for {time}.', ephemeral=True)
            await asyncio.sleep(seconds)
            await interaction.user.send(f'Reminder: {message}')
        except Exception as e:
            await interaction.response.send_message(f'Error setting reminder: {e}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Reminders(bot))