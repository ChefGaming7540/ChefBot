import discord
from discord import app_commands
from discord.ext import commands
import time

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='userinfo', description='Get information about a user')
    @app_commands.describe(user='User to get info about')
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        if user is None:
            user = interaction.user
        try:
            embed = discord.Embed(title=f'Info for {user}', color=user.color)
            embed.add_field(name='ID', value=user.id, inline=True)
            embed.add_field(name='Joined', value=user.joined_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
            embed.add_field(name='Created', value=user.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
            embed.add_field(name='Roles', value=', '.join([role.name for role in user.roles[1:]]), inline=False)
            embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f'Error getting user info: {e}', ephemeral=True)

    @app_commands.command(name='serverinfo', description='Get information about the server')
    async def serverinfo(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            embed = discord.Embed(title=f'Info for {guild.name}', color=discord.Color.blue())
            embed.add_field(name='ID', value=guild.id, inline=True)
            embed.add_field(name='Owner', value=guild.owner, inline=True)
            embed.add_field(name='Members', value=guild.member_count, inline=True)
            embed.add_field(name='Channels', value=len(guild.channels), inline=True)
            embed.add_field(name='Roles', value=len(guild.roles), inline=True)
            embed.add_field(name='Created', value=guild.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f'Error getting server info: {e}', ephemeral=True)

    @app_commands.command(name='ping', description='Check bot latency')
    async def ping(self, interaction: discord.Interaction):
        try:
            latency = round(self.bot.latency * 1000)
            await interaction.response.send_message(f'Pong! Latency: {latency}ms')
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Info(bot))

    @app_commands.command(name='help', description='Get help with commands')
    @app_commands.describe(command='Specific command to get help for')
    async def help(self, interaction: discord.Interaction, command: str = None):
        try:
            if command:
                # Find the specific command
                cmd = self.bot.tree.get_command(command)
                if cmd:
                    embed = discord.Embed(title=f'Help: /{command}', description=cmd.description or 'No description available.', color=discord.Color.blue())
                    if hasattr(cmd, 'parameters') and cmd.parameters:
                        params = '\n'.join([f'`{param.name}`: {param.description or "No description"}' for param in cmd.parameters.values()])
                        embed.add_field(name='Parameters', value=params, inline=False)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(f'Command `/{command}` not found.', ephemeral=True)
            else:
                # List all commands
                commands_list = []
                for cog_name, cog in self.bot.cogs.items():
                    if cog_name in ['Moderation', 'Tickets', 'Starboard', 'Info', 'Fun', 'Events', 'Config', 'Reminders', 'VCModeration', 'Logging']:
                        cog_commands = [f'`/{cmd.name}`' for cmd in cog.get_app_commands()]
                        if cog_commands:
                            commands_list.append(f'**{cog_name}**\n' + ', '.join(cog_commands))
                embed = discord.Embed(title='ChefBot Commands', description='\n\n'.join(commands_list), color=discord.Color.green())
                embed.set_footer(text='Use /help <command> for details on a specific command.')
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)