import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}  # Store poll messages and their end tasks

    @app_commands.command(name='poll', description='Create a poll with automatic ending')
    @app_commands.describe(question='Poll question', duration='Duration in minutes', option1='First option', option2='Second option', option3='Third option (optional)', option4='Fourth option (optional)')
    async def poll(self, interaction: discord.Interaction, question: str, duration: int, option1: str, option2: str, option3: str = None, option4: str = None):
        try:
            if duration < 1 or duration > 1440:  # Max 1 day
                await interaction.response.send_message('Duration must be between 1 and 1440 minutes.', ephemeral=True)
                return
            options = [option1, option2]
            if option3:
                options.append(option3)
            if option4:
                options.append(option4)
            emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
            embed = discord.Embed(title='Poll', description=f'{question}\n\nEnds in {duration} minutes.', color=discord.Color.green())
            for i, opt in enumerate(options):
                embed.add_field(name=f'{emojis[i]} {opt}', value='\u200b', inline=False)
            await interaction.response.send_message(embed=embed)
            msg = await interaction.original_response()
            for i in range(len(options)):
                await msg.add_reaction(emojis[i])
            # Store poll info and schedule end
            poll_data = {'question': question, 'options': options, 'emojis': emojis[:len(options)], 'message': msg, 'channel': interaction.channel}
            self.active_polls[msg.id] = poll_data
            # Schedule the end
            task = asyncio.create_task(self.end_poll_after(msg.id, duration * 60))
            poll_data['task'] = task
        except Exception as e:
            await interaction.response.send_message(f'Error creating poll: {e}', ephemeral=True)

    async def end_poll_after(self, poll_id, delay):
        await asyncio.sleep(delay)
        if poll_id in self.active_polls:
            await self.end_poll(poll_id)

    async def end_poll(self, poll_id):
        try:
            poll_data = self.active_polls[poll_id]
            message = poll_data['message']
            channel = poll_data['channel']
            # Fetch updated reactions
            message = await channel.fetch_message(message.id)
            results = {}
            for reaction in message.reactions:
                emoji = str(reaction.emoji)
                if emoji in poll_data['emojis']:
                    results[emoji] = reaction.count - 1  # Subtract bot's reaction
            # Create results embed
            embed = discord.Embed(title='Poll Results', description=poll_data['question'], color=discord.Color.blue())
            for i, opt in enumerate(poll_data['options']):
                emoji = poll_data['emojis'][i]
                votes = results.get(emoji, 0)
                embed.add_field(name=f'{emoji} {opt}', value=f'{votes} votes', inline=False)
            await channel.send(embed=embed)
            # Remove from active polls
            del self.active_polls[poll_id]
        except Exception as e:
            print(f'Error ending poll {poll_id}: {e}')

    @app_commands.command(name='button', description='Test button')
    async def button(self, interaction: discord.Interaction):
        try:
            view = TestView()
            await interaction.response.send_message('Here is a button:', view=view)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

class TestView(discord.ui.View):
    @discord.ui.button(label='Click me!', style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message('Button clicked!', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Fun(bot))