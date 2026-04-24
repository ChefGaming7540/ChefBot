import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # guild_id: deque of (url, title)
        self.now_playing = {}  # guild_id: (url, title)
        self.voice_clients = {}  # guild_id: voice_client

        # yt-dlp options
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }

    async def get_audio_info(self, url):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return {
                    'url': info['url'],
                    'title': info['title'],
                    'duration': info.get('duration', 0)
                }
            except Exception as e:
                print(f'Error extracting info: {e}')
                return None

    async def play_next(self, guild_id):
        if guild_id in self.queues and self.queues[guild_id]:
            next_song = self.queues[guild_id].popleft()
            self.now_playing[guild_id] = next_song
            voice_client = self.voice_clients.get(guild_id)
            if voice_client:
                voice_client.play(discord.FFmpegPCMAudio(next_song[0]), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(guild_id), self.bot.loop))
        else:
            self.now_playing[guild_id] = None

    @app_commands.command(name='play', description='Play music from a URL or search query')
    @app_commands.describe(query='YouTube URL or search term')
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        if not interaction.user.voice:
            await interaction.followup.send('You need to be in a voice channel!')
            return

        voice_channel = interaction.user.voice.channel
        voice_client = self.voice_clients.get(interaction.guild.id)

        if not voice_client:
            try:
                voice_client = await voice_channel.connect()
                self.voice_clients[interaction.guild.id] = voice_client
            except Exception as e:
                await interaction.followup.send(f'Failed to connect: {e}')
                return

        audio_info = await self.get_audio_info(query)
        if not audio_info:
            await interaction.followup.send('Could not find audio for that query.')
            return

        if interaction.guild.id not in self.queues:
            self.queues[interaction.guild.id] = deque()

        self.queues[interaction.guild.id].append((audio_info['url'], audio_info['title']))

        if not voice_client.is_playing():
            await self.play_next(interaction.guild.id)

        embed = discord.Embed(title='Added to Queue', description=f'[{audio_info["title"]}]({query})', color=0x00ff00)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name='skip', description='Skip the current song')
    async def skip(self, interaction: discord.Interaction):
        voice_client = self.voice_clients.get(interaction.guild.id)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message('Skipped!')
        else:
            await interaction.response.send_message('Nothing playing!')

    @app_commands.command(name='queue', description='Show the current queue')
    async def queue(self, interaction: discord.Interaction):
        if interaction.guild.id not in self.queues or not self.queues[interaction.guild.id]:
            await interaction.response.send_message('Queue is empty!')
            return

        embed = discord.Embed(title='Music Queue', color=0x00ff00)
        for i, (url, title) in enumerate(self.queues[interaction.guild.id], 1):
            embed.add_field(name=f'{i}. {title}', value=url, inline=False)

        if self.now_playing.get(interaction.guild.id):
            embed.set_footer(text=f'Now Playing: {self.now_playing[interaction.guild.id][1]}')

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='stop', description='Stop music and clear queue')
    async def stop(self, interaction: discord.Interaction):
        voice_client = self.voice_clients.get(interaction.guild.id)
        if voice_client:
            voice_client.stop()
            await voice_client.disconnect()
            del self.voice_clients[interaction.guild.id]

        if interaction.guild.id in self.queues:
            self.queues[interaction.guild.id].clear()
        self.now_playing[interaction.guild.id] = None

        await interaction.response.send_message('Stopped and disconnected!')

async def setup(bot):
    await bot.add_cog(Music(bot))