from datetime import datetime
import random

import discord
from discord.ext import commands
import os
import dotenv

import json

# SETTING UP
dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("MINE_ID"))

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


@bot.tree.command(name="ping", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


# LOGS

# CREATE NEW CHAR
@bot.tree.command(name="create", guild=discord.Object(id=GUILD_ID), description="Create a new character!")
async def create(interaction: discord.Interaction, name: str):
    user = interaction.user
    
    # OPEN LOGS OF USER
    try:
        with open(f"logs/{user.id}.json", "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    #CHECK IF IT'S EMPTY
    if not logs:
        logs = []

    # CHECK IF THERE IS A CHARACTER WITH THE SAME NAME
    for log in logs:
        if log["name"] == name:
            await interaction.response.send_message(f"You already have a character named '{name}'!")
            return

    logs.append({
        "name": name,
        "xp": 0,
        "gold": 0,
    })

    with open(f"logs/{user.id}.json", "w") as f:
        json.dump(logs, f)

    await interaction.response.send_message(f"Character '{name}' created!")    

@bot.tree.command(name="show", guild=discord.Object(id=GUILD_ID), description="View your chracters!")
async def show(interaction: discord.Interaction):
    user = interaction.user
    
    # OPEN LOGS OF USER
    with open(f"logs/{user.id}.json", "r") as f:
        logs = json.load(f)
    
    if not logs:
        await interaction.response.send_message("You have no characters yet. Use /create to make one.")
        return

    message_to_send = "Your characters:\n\n"
    for log in logs:
        message_to_send += f"- {log['name']}\n> XP: {log['xp']} \n> Gold: {log['gold']}\n"
    
    await interaction.response.send_message(message_to_send)

# QOTDS

TARGET_EMOTE= "🎯"
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# ADD QOTD TO JSON ON REACTION
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.id != CHANNEL_ID:
        return

    print(reaction.emoji)

    if str(reaction.emoji) != TARGET_EMOTE:
        print("yes")
        return

    message = reaction.message # YOU GET THE ID OF THE MESSAGE
    try:
        message = await message.channel.fetch_message(message.id) # YOU GET THE FULL CONTENTS
    except discord.NotFound:
        print("Message not found (maybe deleted)")
        return
    except discord.Forbidden:
        print("Missing permissions to fetch message")
        return

    # NOW WRITE TO JSON
    with open("qotds/qotds.json", "r") as f:
        qotds = json.load(f)
    
    qotds.append({
        "content": message.content,
        "author": str(message.author),
        "datestamp": datetime.now().isoformat(),
        "times-asked": 0,
        "author-id": message.author.id
    })
    with open("qotds/qotds.json", "w") as f:
        json.dump(qotds, f, indent=2)



@bot.tree.command(name="qotd", guild=discord.Object(id=GUILD_ID), description="Get a random QOTD!")
async def qotd(interaction: discord.Interaction):
    #CHOOSE A QOTD
    with open("qotds/qotds.json", "r") as f:
        qotds = json.load(f)
    
    #Give a random qotd, recent ones have more weight
    qotd = random.choices(qotds, weights=[1/(qotd["times-asked"]+1) for qotd in qotds], k=1)[0]
    qotd["times-asked"] += 1
    with open("qotds/qotds.json", "w") as f:
        json.dump(qotds, f, indent=2)
    

    # CREATE MESSAGE
    message_to_send = discord.Embed(
        title=qotd["content"],
    )
    
    await interaction.response.send_message(embed=message_to_send, content=f"New <@&1509831193942691910>! Thanks for the suggestion <@{qotd['author-id']}>!")

bot.run(TOKEN)