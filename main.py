import os
import dotenv
import discord
from discord.ext import commands
from bot_instance import bot

dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("MINE_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
TARGET_EMOTE = "🎯"



@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    synced = await bot.tree.sync(guild=guild)
    print(f"Synced {len(synced)} commands")


import charater
import log
import qotd
import quests.quests as quests
import onMessage

charater.setup(bot, GUILD_ID)
log.setup(bot, GUILD_ID)
qotd.setup(bot, GUILD_ID, CHANNEL_ID, TARGET_EMOTE)
quests.setup(bot, GUILD_ID)
onMessage.setup(bot, GUILD_ID)

bot.run(TOKEN)


