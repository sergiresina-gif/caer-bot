import os
import dotenv
import discord
from discord.ext import commands
from bot_instance import bot
import stats

dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("MINE_ID"))
CHANNEL_ID_SUG = int(os.getenv("CHANNEL_ID_SUG"))
CHANNEL_ID_QOTD = int(os.getenv("CHANNEL_ID_QOTD"))

TARGET_EMOTE = "🎯"
TARGET_EMOTE_2 = "💠"



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
qotd.setup(bot, GUILD_ID, CHANNEL_ID_SUG, CHANNEL_ID_QOTD, TARGET_EMOTE, TARGET_EMOTE_2)
quests.setup(bot, GUILD_ID)
onMessage.setup(bot, GUILD_ID)
stats.setup(bot, GUILD_ID)

bot.run(TOKEN)


