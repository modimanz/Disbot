from dbot import dbot
from dcog import dcog
import settings
import asyncio

bot = dbot.DBot('$')


async def load_extensions():
    await bot.load_extension('dcog.dcog')
    await bot.load_extension('music.music')


async def main():
    async with bot:
        await load_extensions()
        await bot.start(settings.TOKEN, reconnect=True)


asyncio.run(main())
