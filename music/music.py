import asyncio

from discord.ext import commands
import os
import re
import discord
from discord import app_commands
from yt_dlp import YoutubeDL

import settings
import utils.fileman
import json
from .playlist_manager import *  # playlist_manager  # import PlaylistManager
from .downloader import MDownloader


class MusicCog(commands.Cog):

    def __init__(self, dbot: commands.Bot):
        # self.repeat_mode = {}
        self.bot = dbot
        super().__init__()
        self.voice_channel = ""
        self.music_queue = {}
        self.now_playing = {}
        self.playlist_manager = PlaylistManager()
        self.downloader = MDownloader()

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

    def add_to_queue(self, ctx, song: Song):
        guild_id = ctx.guild.id

        if guild_id in self.music_queue:
            self.music_queue[guild_id].append(song)
        else:
            self.music_queue[guild_id] = [song]

    def save_current_queue_as_playlist(self, guild_id, playlist_name, uid, uname):
        self.playlist_manager.create_playlist(playlist_name, uid, uname, self.music_queue[guild_id])

    def load_playlist_to_queue(self, guild_id, playlist_name, append=False):
        if append:
            self.music_queue[guild_id] = self.music_queue[guild_id] + self.playlist_manager.load_playlist(playlist_name).songs
        else:
            self.music_queue[guild_id] = self.playlist_manager.load_playlist(playlist_name).songs

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
        """ Sync the bot commands """
        # TODO Only Allow ME (Morgan) to run this command
        await self.bot.tree.sync()

    @commands.hybrid_command(name="stop")
    async def stop_audio(self, ctx: commands.Context):
        """ Stop the playing audio """
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Stopped Playing.")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.hybrid_command(name="mrando")
    async def mrando(self, ctx: commands.Context) -> None:
        """ Play a random song from Mobi's collection.... careful """
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

    @commands.hybrid_command(name="save_queue", help="Saves the current queue to a file")
    async def save_queue(self, ctx, playlist_name):
        self.save_current_queue_as_playlist(ctx.guild.id, playlist_name, ctx.author.id, ctx.author.name)
        await ctx.send(f"Saved current queue as playlist {playlist_name}")

    @commands.hybrid_command(name="start_playing", help="Start Playing Music")
    async def start_playing(self, ctx):
        await self.join(ctx)
        self.play_next(ctx)
        await ctx.send(f"Started Music... Hopefully")

    @commands.hybrid_command(name="load_queue", help="Loads a queue from a file")
    async def load_queue(self, ctx: commands.context, playlist_name):
        await ctx.send("Loading %s into queue" % playlist_name)
        self.load_playlist_to_queue(ctx.guild.id, playlist_name)
        await self.join(ctx)
        self.play_next(ctx)
        await ctx.send(f"Loaded playlist {playlist_name} into queue")

    # def play_next(self, ctx):
    #    if ctx.guild.id in self.music_queue and len(self.music_queue[ctx.guild.id]) > 0:
    #        if not ctx.voice_client.is_playing():
    #            next_song = self.music_queue[ctx.guild.id].pop(0)
    #            self.now_playing[ctx.guild.id] = next_song
    #            ctx.voice_client.play(discord.FFmpegPCMAudio(source=next_song), after=lambda e: self.play_next(ctx))
    #    else:
    #        asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect(), self.bot.loop)

    # def play_next(self, ctx):
    #    if ctx.voice_client is not None and not ctx.voice_client.is_playing():
    #        if ctx.guild.id in self.music_queue and len(self.music_queue[ctx.guild.id]) > 0:
    #            if ctx.guild.id in self.repeat_mode and self.repeat_mode[ctx.guild.id] == True:
    #                next_song = self.now_playing[ctx.guild.id]
    #            else:
    #                next_song = self.music_queue[ctx.guild.id].pop(0)
    #                self.now_playing[ctx.guild.id] = next_song
    #            ctx.voice_client.play(discord.FFmpegPCMAudio(source=next_song), after=lambda e: self.play_next(ctx))
    #        else:
    #            asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect(), self.bot.loop)

    def play_next(self, ctx):
        if ctx.voice_client is not None and not ctx.voice_client.is_playing():
            # Check for repeat mode first, repeat the current song if repeat mode is on
            if self.playlist_manager.is_repeat(ctx.guild.id):
                next_song = self.now_playing[ctx.guild.id]
                next_song.increment()
                ctx.voice_client.play(discord.FFmpegPCMAudio(source=next_song.file_path), after=lambda e: self.play_next(ctx))
            elif ctx.guild.id in self.music_queue and len(self.music_queue[ctx.guild.id]) > 0:
                # Repeat mode is off or not set, pop the next song from the queue and play it
                next_song = self.music_queue[ctx.guild.id].pop(0)
                self.now_playing[ctx.guild.id] = next_song
                next_song.increment()
                ctx.voice_client.play(discord.FFmpegPCMAudio(source=next_song.file_path), after=lambda e: self.play_next(ctx))
                if "thumbnail" in next_song.info:
                    # await ctx.send(next_song.info["thumbnail"])
                    asyncio.create_task(ctx.send(next_song.info["thumbnail"]))
            else:
                asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect(), self.bot.loop)

    @commands.hybrid_command(name='now_playing')
    async def current_song(self, ctx: commands.Context):
        """ Show the current song playing """
        if ctx.guild.id in self.now_playing:
            await ctx.send(f"Currently playing: {self.now_playing[ctx.guild.id].raw_title}")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.hybrid_command(name='mqueue')
    async def show_queue(self, ctx: commands.Context) -> None:
        """ Show the queue """
        if ctx.guild.id in self.music_queue and len(self.music_queue[ctx.guild.id]) > 0:
            queue_list = "\n".join([f"{i + 1}. {song.raw_title}" for i, song in enumerate(self.music_queue[ctx.guild.id])])
            await ctx.send(f"Queue:\n{queue_list}")
        else:
            await ctx.send("The queue is empty.")

    @commands.hybrid_command(name='skip')
    async def skip_song(self, ctx: commands.Context) -> None:
        """ Skip the current track """
        if ctx.voice_client.is_playing():
            #self.repeat_mode[ctx.guild.id] = False
            self.playlist_manager.repeat[ctx.guild.id] = False
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

    @commands.hybrid_command(name='remove', help="Remove a song at <position> from the queue")
    async def remove_song(self, ctx: commands.Context, position: int) -> None:
        if ctx.guild.id in self.music_queue and 1 <= position <= len(self.music_queue[ctx.guild.id]):
            removed_song = self.music_queue[ctx.guild.id].pop(position - 1)  # Subtract 1 because lists are 0-indexed
            await ctx.send(f"Removed song at position {position} from the queue.")
        else:
            await ctx.send("There is no song at that position in the queue.")

    @commands.hybrid_command(name="repeat", help="Repeat the song forever")
    async def repeat(self, ctx: commands.Context):
        if ctx.guild.id not in self.playlist_manager.repeat:
            self.playlist_manager.repeat[ctx.guild.id] = False
        self.playlist_manager.repeat[ctx.guild.id] = not self.playlist_manager.repeat[ctx.guild.id]
        if self.playlist_manager.repeat[ctx.guild.id]:
            await ctx.send("Repeat mode is now ON.")
        else:
            await ctx.send("Repeat mode is now OFF.")

    @commands.hybrid_command(name="shuffle", help="Shuffle any playlists loaded in the future (toggle)")
    async def shuffle(self, ctx: commands.Context):
        if ctx.guild.id not in self.playlist_manager.shuffle:
            self.playlist_manager.shuffle[ctx.guild.id] = False
        self.playlist_manager.shuffle[ctx.guild.id] = not self.playlist_manager.shuffle[ctx.guild.id]
        if self.playlist_manager.shuffle[ctx.guild.id]:
            await ctx.send("Shuffle mode is now ON.")
        else:
            await ctx.send("Shuffle mode is now OFF.")

    @commands.hybrid_command(name='mplay', help="Play a song from you know...")
    async def download_and_play_from_youtube(self, ctx: commands.Context, *, search_string):
        await ctx.send("Searching and downloading your request. This might take a moment.")
        self.bot.loop.create_task(self.download_and_play(ctx, search_string))

    @commands.hybrid_command(name='move', help="Move a song from <current_index> to <new_index> in the queue")
    async def move(self, ctx, current_index: int, new_index: int):
        """Move a song in the queue from one position to another"""
        # Check if there is a music queue for the current guild
        if ctx.guild.id in self.music_queue and len(self.music_queue[ctx.guild.id]) > 0:
            # Make sure the current_index and new_index are within the queue length
            if 0 <= current_index < len(self.music_queue[ctx.guild.id]) and 0 <= new_index < len(
                    self.music_queue[ctx.guild.id]):
                # Move the song in the queue
                song = self.music_queue[ctx.guild.id].pop(current_index)
                self.music_queue[ctx.guild.id].insert(new_index, song)
                await ctx.send(f"Moved song from position {current_index} to {new_index}")
            else:
                await ctx.send("Invalid index!")
        else:
            await ctx.send("The music queue is empty!")

    async def download_and_play(self, ctx, search_string):
        print("WORKING \n")

        song = None

        song = self.downloader.download(ctx.author.id, ctx.author.name, search_string)
        song.save()

        if not song:
            await ctx.send("Error: Song not found.")
            return

        try:
            await self.join(ctx)

            self.add_to_queue(ctx, song)
            if not ctx.voice_client.is_playing():
                self.play_next(ctx)
            await ctx.send(f"Added {song.raw_title} to the queue.")
        except Exception as e:
            print(e)
            await ctx.send("Error: Unable to add the song to queue.")

    @commands.hybrid_command(name="create_playlist", help="Create a playlist")
    async def create_playlist(self, ctx, playlist_name: str):
        """
        This command creates a new playlist
        """
        user_id = ctx.author.id  # or replace with your way to get user id
        username = ctx.author.name  # or replace with your way to get username
        self.playlist_manager.create_playlist(playlist_name, user_id, username)
        await ctx.send(f"Playlist {playlist_name} has been created.")

    async def _add_to_playlist(self, ctx, playlist_name, str):
        song = self.downloader.download(ctx.author.id, ctx.author.name, str)
        song.save()
        self.playlist_manager.add_to_playlist(ctx, playlist_name, song)
        await ctx.send(f"Song {song.title} has been added to the playlist {playlist_name}.")

    @commands.hybrid_command(name="add_to_playlist", help="Add a song to playlist <playlist_name> <search query>")
    async def add_to_playlist(self, ctx, playlist_name: str, song_query: str):
        """
        This command adds a song to a playlist
        """
        # Assuming that your bot has a function 'search_and_download_song'
        # which downloads the song from YouTube and returns the Song object.

        await ctx.send("Loading song and adding to playlist. This might take a moment.")
        self.bot.loop.create_task(self._add_to_playlist(ctx, playlist_name, song_query))

    @commands.hybrid_command(name="remove_from_playlist")
    async def remove_from_playlist(self, ctx, playlist_name: str, song_index: int):
        """
        This command removes a song from a playlist
        """
        removed_song = self.playlist_manager.remove_from_playlist(playlist_name, song_index)
        playlist = self.playlist_manager.load_playlist(playlist_name)
        self.playlist_manager.save_playlist(playlist)
        if removed_song is None:
            await ctx.send("Failed to remove the song from the playlist. Please check the song index.")
        else:
            await ctx.send(f"Song {removed_song.title} has been removed from the playlist {playlist_name}.")


async def setup(dbot: commands.Bot) -> None:
    await dbot.add_cog(MusicCog(dbot))
