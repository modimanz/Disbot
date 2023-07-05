from discord.ext import commands
import discord
from discord import app_commands
from utils.chat_gpt import ChatBot, generate_response

class Dcog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()
        self.chatBot = ChatBot()



    @commands.hybrid_command(name="mjoin")
    async def mjoin(self, ctx: commands.Context) -> None:
        if not ctx.message.author.voice:
            await ctx.send("{} is not connected to a voice channel".
                           format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send("Yo!")

    @commands.hybrid_command(name="mleave")
    async def mleave(self, ctx: commands.Context) -> None:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.send("bye bye buddy")
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    async def ask_chat_gpt(self, ctx, question):
        try:
            response = self.chatBot.generate_response(question)
            print(response)
            await ctx.send(response)
        except Exception as e:
            print(e)
            await ctx.send("I can't talk to chat GPT right now")

    @commands.hybrid_command(name="ask")
    async def ask(self, ctx: commands.Context, question: str = "") -> None:

        await ctx.send("Asking your question. This might take a moment.")
        self.bot.loop.create_task(self.ask_chat_gpt(ctx, question))


async def setup(dbot: commands.Bot) -> None:
    await dbot.add_cog(Dcog(dbot))   # GLOBAL

    # await dbot.add_cog(Dcog(dbot), guilds=[discord.Object(id=guild_robomash_id)])  # Guild Only

"""
# - EXAMPLES -
  @commands.hybrid_group(name="parent")
  async def parent_command(self, ctx: commands.Context) -> None:
    '''
    We even have the use of parents. This will work as usual for ext.commands but will be un-invokable for app commands.
    This is a discord limitation as groups are un-invokable.
    '''
    ...   # nothing we want to do in here, I guess!
    
  @parent_command.command(name="sub")
  async def sub_command(self, ctx: commands.Context, argument: str) -> None:
    '''
    This subcommand can now be invoked with `?parent sub <arg>` or `/parent sub <arg>` (once synced).
    '''

    await ctx.send(f"Hello, you sent {argument}!")
"""