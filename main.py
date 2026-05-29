import os
import dotenv
import discord
from discord.ext import commands


dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("MINE_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
TARGET_EMOTE = "🎯"

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    synced = await bot.tree.sync(guild=guild)
    print(f"Synced {len(synced)} commands")


import charater
import log
import qotd

charater.setup(bot, GUILD_ID)
log.setup(bot, GUILD_ID)
qotd.setup(bot, GUILD_ID, CHANNEL_ID, TARGET_EMOTE)

bot.run(TOKEN)
