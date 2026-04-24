import discord
from discord import app_commands
from discord.ext import commands

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='setup', description='Configure bot settings')
    @app_commands.describe(setting='Setting to configure', value='Value to set')
    async def setup(self, interaction: discord.Interaction, setting: str, value: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('You need administrator permissions to use this command.', ephemeral=True)
            return
        try:
            if setting.upper() in ['LOG_CHANNEL_ID', 'STARBOARD_CHANNEL_ID', 'TICKET_CATEGORY_ID', 'WELCOME_CHANNEL_ID', 'LEAVE_CHANNEL_ID']:
                self.bot.config[setting.upper()] = int(value)
                await interaction.response.send_message(f'Set {setting} to {value}', ephemeral=True)
            else:
                await interaction.response.send_message('Invalid setting.', ephemeral=True)
        except ValueError:
            await interaction.response.send_message('Value must be a number.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Config(bot))