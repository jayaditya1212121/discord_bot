import discord
from discord.ext import commands
import asyncio




#import music cog class
from music_cog import music_cog
from chat_cog import chat_cog

# intents to give bot permission to read messages etc, need to enable intents in discord website too??
intents = discord.Intents().all()

# setup bot with commands and intents(???? changed with update)
bot = commands.Bot(command_prefix='$', intents= intents)


#register the class with the bot
async def setup(bot):
    await bot.add_cog(chat_cog(bot))
    await bot.add_cog(music_cog(bot))

asyncio.run(setup(bot))

#start the bot with discord token
with open('token.txt', 'r') as t:
    try:
        bot.run(t.read())
    except Exception:
        print('recheck discord token or internet connection')