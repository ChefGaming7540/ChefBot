import discord
from discord import app_commands
from discord.ext import commands

class Reports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='report', description='Report a user to moderators')
    @app_commands.describe(user='User to report', reason='Reason for report')
    async def report(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        try:
            # Send to mod channel
            mod_channel_id = self.bot.config.get('MOD_CHANNEL_ID')  # Add this to config
            if not mod_channel_id:
                await interaction.response.send_message('Reports not configured. Set MOD_CHANNEL_ID.', ephemeral=True)
                return
            mod_channel = self.bot.get_channel(mod_channel_id)
            if not mod_channel:
                await interaction.response.send_message('Mod channel not found.', ephemeral=True)
                return
            embed = discord.Embed(title='User Report', color=discord.Color.red())
            embed.add_field(name='Reported User', value=f'{user.mention} ({user.id})', inline=True)
            embed.add_field(name='Reported By', value=f'{interaction.user.mention} ({interaction.user.id})', inline=True)
            embed.add_field(name='Reason', value=reason, inline=False)
            embed.add_field(name='Channel', value=interaction.channel.mention, inline=True)
            await mod_channel.send(embed=embed)
            await interaction.response.send_message('Report submitted anonymously to moderators.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error submitting report: {e}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Reports(bot))