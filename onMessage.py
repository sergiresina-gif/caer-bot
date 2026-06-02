import discord
import json

def setup(bot: discord.Client, guild_id: int):
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        if message.guild is None and not message.author.bot:
            return await message.channel.send(message.content)