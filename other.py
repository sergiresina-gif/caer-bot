import json
import discord
from datetime import datetime
from log_funcs import *
from autocompletes import name_autocomplete
from models import *

def setup(bot: discord.Client, guild_id: int):
    @bot.tree.command(name="xptable", guild=discord.Object(id=guild_id), description="Show xp table")
    async def xptable(interaction: discord.Interaction):
        await interaction.response.send_message("Here you have!", files=[discord.File("quests/xptable.png")], ephemeral=True)