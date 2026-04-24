import discord
from discord.ext import commands

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starred_messages = {}

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        try:
            star_emoji = '⭐'
            star_threshold = 3
            if reaction.emoji == star_emoji and reaction.count >= star_threshold and not user.bot:
                if reaction.message.id not in self.starred_messages:
                    starboard_channel_id = self.bot.config.get('STARBOARD_CHANNEL_ID')
                    if starboard_channel_id:
                        channel = self.bot.get_channel(starboard_channel_id)
                        if channel:
                            embed = discord.Embed(description=reaction.message.content, color=0xFFD700)
                            embed.set_author(name=reaction.message.author.display_name, icon_url=reaction.message.author.avatar.url if reaction.message.author.avatar else None)
                            embed.add_field(name='Original', value=f'[Jump to message]({reaction.message.jump_url})')
                            await channel.send(embed=embed)
                            self.starred_messages[reaction.message.id] = True
        except Exception as e:
            print(f'Error in starboard: {e}')

async def setup(bot):
    await bot.add_cog(Starboard(bot))