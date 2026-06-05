# bot_instance.py
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
bot = commands.Bot(command_prefix="/", intents=intents)