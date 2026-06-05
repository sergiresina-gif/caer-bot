import discord
import json
from quests.quests import loot_log, loot_questions, loot_fields
from log_funcs import *


async def loot_builder(loot_data: dict, message: discord.Message) -> str:
    loot_log[message.author.id][loot_fields[loot_log[message.author.id]["step"]]] = message.content
    loot_log[message.author.id]["step"] += 1

    if loot_log[message.author.id]["step"] >= len(loot_questions):
        # Create message
        message_to_send = f"__**{loot_log[message.author.id]['Title']}**__\n"

        for i in range(1, 11):
            character_key = f"character_{i}"
            if loot_log[message.author.id][character_key]:
                author = find_author_by_character(loot_log[message.author.id][character_key])
                message_to_send += f"> <@{author}> as {loot_log[message.author.id][character_key]}\n"

        if loot_log[message.author.id]['Description'].lower() != "skip":
            message_to_send += f"\n{loot_log[message.author.id]['Description']}\n"
        
        message_to_send += f"\n\n⭐ XP ⭐ \n```{loot_log[message.author.id]['XP Breakdown']}```\n"
        message_to_send += f"💰  Monies 💰 \n```{loot_log[message.author.id]['Gold']}gp```\n"
        message_to_send += f"💎 Other goodies 💎 \n{loot_log[message.author.id]['Items']}\n"


        await message.channel.send(message_to_send) # TO WHAT CHANNEL

        for i in range(1, 11): # AWARD XP AND GOLD
            character_key = f"character_{i}"
            if loot_log[message.author.id][character_key]:
                await award_xp_and_gold(loot_log[message.author.id][character_key], int(loot_log[message.author.id]['XP']), int(loot_log[message.author.id]['Gold']), f"Quest: {loot_log[message.author.id]['Title']}")
        del loot_log[message.author.id]
    else:
        next_question = loot_questions[loot_log[message.author.id]["step"]]
        await message.channel.send(next_question)


def setup(bot: discord.Client, guild_id: int):
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        if message.guild is None and not message.author.bot:
            if loot_log.get(message.author.id):
                await loot_builder(loot_log[message.author.id], message)  


                
                
                



