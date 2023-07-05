import asyncio

from discord.ext import commands
import os
import re
import discord
from discord import app_commands
from yt_dlp import YoutubeDL

import settings
import utils.fileman


class MusicCog(commands.Cog):

    def __init__(self, dbot: commands.Bot):
        self.bot = dbot
        super().__init__()
        self.voice_channel = ""
        self.music_queue = {}
        self.now_playing = {}

    # @app_commands.command(name="mplay")
    # async def mplay(self, interaction: discord.Interaction) -> None:
    #    """ /mplay """
    #    await interaction.response.send_message("Ok i can't do that yet sorry buddy", ephemeral=True)

    async def join(self, ctx: commands.Context):

        if self.is_connected(ctx):
            print("Already Connected")
            return

        if not ctx.message.author.voice:
            # await ctx.response.send_message("{} ain't connected YO!".format(ctx.message.author.name))
            await ctx.send("{} ain't connected YO!".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
            # text_channel = ctx.message.channel

        print("Connecting to %s" % channel.name)
        await channel.connect()
        print("Connected to %s" % channel.name)

        # await ctx.response.send_message("YO!")
        # TODO This send "YO!" command is not working!
        await ctx.send("YO!")
        self.voice_channel = channel
        return

    def add_to_queue(self, guild_id, filename):
        if guild_id in self.music_queue:
            self.music_queue[guild_id].append(filename)
        else:
            self.music_queue[guild_id] = [filename]

    async def leave(self, ctx: commands.Context):
        voice_client = ctx.voice_client  # .guild.voice_client
        if self.is_connected(ctx):
            await voice_client.disconnect()
            await ctx.send("bye bye buddy")
        else:
            await ctx.send("I ain't connected to no voice channel buddy!")

    # @app_commands.command(name="mrando")

    def is_connected(self, ctx):

        voice_state = ctx.guild.me.voice

        if voice_state:
            # If the bot is connected to a voice channel, print the channel's name
            print("is_connected: True")
            return True
            # voice_channel = voice_state.channel
            # await ctx.send(f'I am currently connected to the voice channel: {voice_channel.name}')
        else:
            # If the bot is not connected to any voice channel
            print("is_connected: False")
            return False
            # await ctx.send('I am not connected to any voice channel.')

    @commands.hybrid_command(name="sync")
    async def sync(self, ctx: commands.Context) -> None:
        # TODO Only Allow ME (Morgan) to run this command
        await self.bot.tree.sync()

    @commands.hybrid_command(name="stop")
    async def stop_audio(self, ctx: commands.Context):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Stopped Playing.")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.hybrid_command(name="mrando")
    async def mrando(self, ctx: commands.Context) -> None:
        """ /mrando """
        await self.join(ctx)

        voice_client = ctx.voice_client  # .client

        # if voice_client.is_playing():
        # //    voice_client.stop()

        print("Finding mp3 file\n")

        mp3_file = utils.fileman.get_random_music_file(settings.music_dir,
                                                       True)  # "C:\\Users\\mreg\\Music\\DJ Music\\BLACKPINK, Selena Gomez - Ice Cream (with Selena Gomez).stem.m4a"

        print("Found: %s\n" % mp3_file)

        if not voice_client.is_playing():
            print("Voice Client is playing\n")
            try:
                # TODO Get a random file
                self.add_to_queue(ctx.guild.id, mp3_file)
                # self.music_queue[ctx.guild.id].append(mp3_file)
                # voice_client.play(discord.FFmpegPCMAudio(source=mp3_file))  # , **FFMPEG_OPTIONS)
                # self.music_queue[ctx.guild.id] = [mp3_file]
                self.play_next(ctx)
                await ctx.send("Playing")
                # if self.is_connected(ctx):

            except Exception as e:
                print(e)
                await ctx.send("I ain't able to play right now buddy!")

        else:
            print("Voice Client is not playing\n")
            try:
                self.add_to_queue(ctx.guild.id, mp3_file)

                await ctx.send("Song added to the queue.")
            except Exception as e:
                print(e)
                await ctx.send("I ainit able to add that to queue buddy!")

        # Change the second property to True to have it rescan for new mp3 files

        # TODO Set the FFMPEG_OPTIONS - 'before_options' is not a valid property!!
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

    def play_next(self, ctx):
        if ctx.guild.id in self.music_queue and len(self.music_queue[ctx.guild.id]) > 0:
            if not ctx.voice_client.is_playing():
                next_song = self.music_queue[ctx.guild.id].pop(0)
                self.now_playing[ctx.guild.id] = next_song
                ctx.voice_client.play(discord.FFmpegPCMAudio(source=next_song), after=lambda e: self.play_next(ctx))
        else:
            asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect(), self.bot.loop)

    @commands.hybrid_command(name='now_playing')
    async def current_song(self, ctx: commands.Context):
        if ctx.guild.id in self.now_playing:
            await ctx.send(f"Currently playing: {self.now_playing[ctx.guild.id]}")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.hybrid_command(name='mqueue')
    async def show_queue(self, ctx: commands.Context) -> None:
        if ctx.guild.id in self.music_queue and len(self.music_queue[ctx.guild.id]) > 0:
            queue_list = "\n".join([f"{i + 1}. {song}" for i, song in enumerate(self.music_queue[ctx.guild.id])])
            await ctx.send(f"Queue:\n{queue_list}")
        else:
            await ctx.send("The queue is empty.")

    @commands.hybrid_command(name='skip')
    async def skip_song(self, ctx: commands.Context) -> None:
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped to the next song.")
        else:
            await ctx.send("Nothing is playing to skip.")

    @commands.hybrid_command(name="mhelp", help="Displays all available commands.")
    async def help_command(self, ctx):
        help_embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
        for command in self.bot.commands:
            # We can also check if the user can run the command using command.can_run()
            # and only display commands that can be run.
            if not command.hidden:
                help_embed.add_field(name=f"{command.name}", value=command.help, inline=False)
        await ctx.send(embed=help_embed)

    @commands.hybrid_command(name='remove')
    async def remove_song(self, ctx: commands.Context, position: int) -> None:
        if ctx.guild.id in self.music_queue and 1 <= position <= len(self.music_queue[ctx.guild.id]):
            removed_song = self.music_queue[ctx.guild.id].pop(position - 1)  # Subtract 1 because lists are 0-indexed
            await ctx.send(f"Removed song at position {position} from the queue.")
        else:
            await ctx.send("There is no song at that position in the queue.")

    @commands.hybrid_command(name='old_mplay_old')
    async def download_and_play_from_moob(self, ctx: commands.Context, *, search_string) -> None:
        YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': 'True',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'default_search': 'auto',
        }

        with YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(search_string, download=False)
                raw_title = info['entries'][0]['title']
                title = re.sub('[^a-zA-Z0-9 ]', '', raw_title)  # Remove special characters
                filename = f"downloads/{title}.mp3"

                # Check if the file exists before downloading it
                if not os.path.isfile(filename):
                    url = info['entries'][0]['webpage_url']
                    ydl.download([url])
            except Exception:
                await ctx.send("Error: Song not found.")
                return

            try:
                self.add_to_queue(ctx.guild.id, filename)
                if not ctx.voice_client.is_playing():
                    self.play_next(ctx)
                await ctx.send(f"Added {title} to the queue.")
            except Exception:
                await ctx.send("Error: Unable to add the song to queue.")

    @commands.hybrid_command(name='mplay')
    async def download_and_play_from_youtube(self, ctx: commands.Context, *, search_string):
        YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': 'True',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'default_search': 'auto',
        }
        await ctx.send("Searching and downloading your request. This might take a moment.")
        self.bot.loop.create_task(self.download_and_play(ctx, search_string, YDL_OPTIONS))

    async def download_and_play(self, ctx, search_string, YDL_OPTIONS):
        print("WORKING \n")
        with YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(search_string, download=False)
                raw_title = info['entries'][0]['title']
                title = re.sub('[^a-zA-Z0-9\-_ .]', '', raw_title)  # Remove special characters
                title = title.replace(" ", "_")
                filename = f"downloads/{title}.mp3"

                print("Filename: %s\n" % filename)

                # Check if the file exists before downloading it
                if not os.path.isfile(filename):
                    url = info['entries'][0]['webpage_url']
                    #YDL_OPTIONS['outtmpl'] = 'downloads/%(title)s.%(ext)s'  # Update output template
                    YDL_OPTIONS['restrictfilenames'] = True
                    ydl.download([url])
            except Exception as e:
                print(e)
                await ctx.send("Error: Song not found.")
                return

            try:
                await self.join(ctx)
                self.add_to_queue(ctx.guild.id, filename)
                if not ctx.voice_client.is_playing():
                    self.play_next(ctx)
                await ctx.send(f"Added {title} to the queue.")
            except Exception as e:
                print(e)
                await ctx.send("Error: Unable to add the song to queue.")


async def setup(dbot: commands.Bot) -> None:
    await dbot.add_cog(MusicCog(dbot))
