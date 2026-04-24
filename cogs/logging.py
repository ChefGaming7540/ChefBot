import discord
from discord import app_commands
from discord.ext import commands
import time

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='logs', description='View logs')
    @app_commands.describe(user='Filter by user', event='Filter by event type')
    async def logs(self, interaction: discord.Interaction, user: discord.Member = None, event: str = None):
        if not interaction.user.guild_permissions.view_audit_log:
            await interaction.response.send_message('You do not have permission to view logs.', ephemeral=True)
            return
        try:
            query = 'SELECT event, details, timestamp FROM logs WHERE guild_id = ?'
            params = [interaction.guild.id]
            if user:
                query += ' AND details LIKE ?'
                params.append(f'%{user.id}%')
            if event:
                query += ' AND event = ?'
                params.append(event)
            query += ' ORDER BY timestamp DESC LIMIT 10'
            cursor = await self.bot.db.execute(query, params)
            rows = await cursor.fetchall()
            if not rows:
                await interaction.response.send_message('No logs found.', ephemeral=True)
                return
            embed = discord.Embed(title='Recent Logs', color=discord.Color.blue())
            for row in rows:
                embed.add_field(name=row[0], value=f'{row[1]} - {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[2]))}', inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Logging(bot))