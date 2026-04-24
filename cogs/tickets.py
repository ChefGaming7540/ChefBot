import discord
from discord import app_commands
from discord.ext import commands

class CloseTicketView(discord.ui.View):
    def __init__(self, ticket_channel: discord.TextChannel, creator: discord.User):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel
        self.creator = creator

    @discord.ui.button(label='Close Ticket', style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.guild_permissions.manage_channels or interaction.user == self.creator:
                await interaction.response.send_message('Closing ticket...')
                await self.ticket_channel.delete()
            else:
                await interaction.response.send_message('You do not have permission to close this ticket.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error closing ticket: {e}', ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ticket', description='Create a support ticket')
    @app_commands.describe(issue='Describe your issue')
    async def ticket(self, interaction: discord.Interaction, issue: str):
        ticket_category_id = self.bot.config.get('TICKET_CATEGORY_ID')
        if not ticket_category_id:
            await interaction.response.send_message('Tickets not configured.', ephemeral=True)
            return
        try:
            category = self.bot.get_channel(ticket_category_id)
            if not category:
                await interaction.response.send_message('Ticket category not found.', ephemeral=True)
                return
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await interaction.guild.create_text_channel(f'ticket-{interaction.user.name}', category=category, overwrites=overwrites)
            view = CloseTicketView(channel, interaction.user)
            await channel.send(f'{interaction.user.mention} created a ticket: {issue}', view=view)
            await interaction.response.send_message(f'Ticket created: {channel.mention}', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error creating ticket: {e}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))