import random

import discord
from discord.ext import commands

class chat_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hello", aliases=["Hello", "hi","Hi"], help="replies")
    async def hello(self,ctx):
        await ctx.send("Hello")

    @commands.command(name="preach", aliases=["Preach", "PREACH"], help="replies with a random quote")
    async def preach(self,ctx):
        with open('quotes.txt', 'r') as q:
            quote= q.readlines()
        await ctx.send(quote[random.randint(0, len(quote)-1)])
