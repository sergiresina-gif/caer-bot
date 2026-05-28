import discord
from discord.ext import commands
import os
import dotenv

dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("MINE_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    synced = await bot.tree.sync(guild=guild)
    print(f"Synced {len(synced)} commands")

@bot.tree.command(name="ping", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.tree.command(name="create", guild=discord.Object(id=GUILD_ID))
async def create(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"Creating {name}!")

bot.run(TOKEN)