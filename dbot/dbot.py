import discord
from discord.ext.commands import Bot  # , DefaultHelpCommand
from discord import Intents

import settings

intents = Intents.all()
intents.members = True
# TODO - Add Logging


class DBot(Bot):
    """
    Load this bot and use ../main.py to load_extensions

    """
    def __init__(self, command_prefix, *args,  **kwargs):
        super().__init__(command_prefix, intents=intents, *args, **kwargs)
        self.prefix = command_prefix

        self.message1 = "MobiBot is booted"
        self.message2 = "I am not ready to play yet"

        self.guild_id = settings.guild_id
        self.synced = False

        @self.event
        async def on_ready():
            print(self.message1)
            print(f'\n\nLogged in as: {self.user.name} - {self.user.id}\nVersion: {discord.__version__}\n')
            # self.synced = True
            if not self.synced:
                """
                sync commands if not synced
                """

                command_list = await self.tree.sync()  # guild=self.guild_id)
                self.synced = True
