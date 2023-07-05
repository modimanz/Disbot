import discord
import urllib.request as urllib2
import ffmpy
import asyncio
from bs4 import BeautifulSoup
from discord.ext import commands
import discord
from discord import Intents, app_commands

import asyncio
import youtube_dl

intents = Intents.all()
intents.members = True

"""
Application ID: 977726114652897330
PUBLIC KEY: b61163e4dde6ec94661c1b0553e2385a2480e5228d0dcc65c01bc870b593b1e9
botToken: OTc3NzI2MTE0NjUyODk3MzMw.GR9VCY.Ck7HOigFKvB4wcdwlcbMtS1j1blsS9ZSkjcXBU
"""

d_bot = commands.bot


class DCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

        # TODO Add Intents here
        # commands.Bot.__init__(self, command_prefix=command_prefix, self_bot=self_bot, intents=intents)
        self.message1 = "MobiBot is booted"
        self.message2 = "I am not ready to play yet"

    # def on_ready(self):
    #    print(self.message1)

    @app_commands.command(name="play")
    async def play(self, interaction: discord.Interaction) -> None:
        """ /play """
        await interaction.response.send_message("play what?", ephemeral=True)


# def start():
async def setup(dbot: d_bot, token) -> None:
    # await dbot.add_cog(DCog(dbot))  # GLOBAL
    guild_robomash_id = '562423723555029002'  # TODO ADD Guild ID HERE
    await dbot.add_cog(DCog(dbot), guilds=[discord.Object(id=guild_robomash_id)])  # Guild Only
    dbot.run(token)

def run(token):
    Token = "OTc3NzI2MTE0NjUyODk3MzMw.GR9VCY.Ck7HOigFKvB4wcdwlcbMtS1j1blsS9ZSkjcXBU"
    setup(d_bot, token)

    #async def play(ctx):
    #    """
    #    Play Music
    #    :param ctx:
    #    :return:
    #    """
    #    print(ctx)
    #    # await ctx.channel.send(f'{self.message2}, {ctx.author.name}')
    #        channel = ctx.message.author.voice.channel
    #        # await channel.connect()

    #    @self.command(name="leave", pass_context=True)
    #    async def leave(ctx):
    #        print("Leaving Voice Channel %s" % ctx.message.author.voice.channel.name)
    #        # await ctx.channel.send(f'Bye Bye {ctx.author.name}')
    #        # await ctx.voice_client.disconnect()

