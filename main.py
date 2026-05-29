from datetime import datetime
import random

import discord
from discord.ext import commands
import os
import dotenv

import json


raids = [
    {"xp": 500, "gold": 100},
    {"xp": 1000, "gold": 250},
    {"xp": 2000, "gold": 500},
]

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
        "history": []
    })

    with open(f"logs/{user.id}.json", "w") as f:
        json.dump(logs, f, indent=2)

    await interaction.response.send_message(f"Character '{name}' created!")    


#AUTOCOMPLETE FOR SHOW

async def name_autocomplete(interaction: discord.Interaction, current: str):
    user = interaction.user
    
    # OPEN LOGS OF USER
    try:
        with open(f"logs/{user.id}.json", "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    return [
        discord.app_commands.Choice(name=log["name"], value=log["name"])
        for log in logs if current.lower() in log["name"].lower()
    ]

async def true_false_autocomplete(interaction: discord.Interaction, current: str):
    return [
        discord.app_commands.Choice(name="True", value="True"),
        discord.app_commands.Choice(name="False", value="False")
    ]
# SHOWING CHARACTERS
@bot.tree.command(name="show", guild=discord.Object(id=GUILD_ID), description="View your chracters!")
@discord.app_commands.autocomplete(name=name_autocomplete, activity_log=true_false_autocomplete)
async def show(interaction: discord.Interaction, name: str = None, activity_log: str = "False"):
    user = interaction.user
    
    # OPEN LOGS OF USER
    with open(f"logs/{user.id}.json", "r") as f:
        logs = json.load(f)
    
    if not logs:
        await interaction.response.send_message("You have no characters yet. Use /create to make one.")
        return
    
    if name:
        logs = [log for log in logs if log["name"] == name]
        if not logs:
            await interaction.response.send_message(f"You have no character named '{name}'.")
            return

    # CREATE MESSAGE TO SEND
    message_to_send = ""
    for log in logs:
        if log["xp"] < 1000:
            level = log["xp"] // 500 + 1
            xp_to_show = log["xp"] % 500
        else:
            level = log["xp"] // 1000 + 2
            xp_to_show = log["xp"] % 1000
        
        message_to_send += f"# {log['name']}\n> Level: {level}\n> XP: {xp_to_show} \n> Gold: {log['gold']}\n"
        
        if activity_log == "True":
            message_to_send += f"\nActivity Log: \n"
            for activity in log["history"]:
                message_to_send += f"- **{activity['label']}** | XP: {activity['xp']} | Gold: {activity['gold']} | ({activity['timestamp']})\n"
            message_to_send += "\n"

    


    embed = discord.Embed(
        title=f"{user.name}'s Characters",
        description=message_to_send
    )
    
    await interaction.response.send_message(embed=embed)

# /LOG

log_group = discord.app_commands.Group(name="log", description="Log activities for a character")

async def write_activity(log: list, name: str, xp: int, gold: int, label: str, timestamp: str):
    # FIND THE CHARACTER
    log["history"].append({
        "xp": xp,
        "gold": gold,
        "label": label,
        "timestamp": timestamp
    })
    return True

@log_group.command(name="manual", description="Log an xp and gold manually.")
@discord.app_commands.autocomplete(name=name_autocomplete)
async def manual(interaction: discord.Interaction, name: str, xp: int, gold: int, label: str):
    user = interaction.user

    # OPEN LOGS OF USER
    try:
        with open(f"logs/{user.id}.json", "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    # FIND THE CHARACTER
    for log in logs:
        if log["name"] == name:
            log["xp"] += xp
            log["gold"] += gold
            await write_activity(log, name, xp, gold, label, datetime.now().date().isoformat())
            break
    else:
        await interaction.response.send_message(f"You have no character named '{name}'.")
        return

    # SAVE THE UPDATED LOGS
    with open(f"logs/{user.id}.json", "w") as f:
        json.dump(logs, f, indent=2)

    await interaction.response.send_message(f"Activity logged for '{name}'!")

@log_group.command(name="raid", description="Log a raid completion.")
@discord.app_commands.autocomplete(name=name_autocomplete)
async def raid(interaction: discord.Interaction, name: str, level: int):
    user = interaction.user

    # OPEN LOGS OF USER
    try:
        with open(f"logs/{user.id}.json", "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    # FIND THE CHARACTER
    for log in logs:
        if log["name"] == name:
            log["xp"] += raids[level-1]["xp"]
            log["gold"] += raids[level-1]["gold"]
            await write_activity(log, name, raids[level-1]["xp"], raids[level-1]["gold"], f"Raid Level {level}", timestamp=datetime.now().date().isoformat())
            break
    else:
        await interaction.response.send_message(f"You have no character named '{name}'.")
        return

    # SAVE THE UPDATED LOGS
    with open(f"logs/{user.id}.json", "w") as f:
        json.dump(logs, f, indent=2)

    await interaction.response.send_message(f"Raid logged for '{name}'!")

bot.tree.add_command(log_group, guild=discord.Object(id=GUILD_ID))


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