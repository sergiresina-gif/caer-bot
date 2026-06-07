import discord
import json
from quests.quests import loot_log, loot_questions, loot_fields
from log_funcs import *


async def loot_builder(loot_data, message: discord.Message) -> str:
    # loot_data is a Loot instance
    current_label = loot_fields[loot_data.step]
    loot_data.set_field_by_label(current_label, message.content)
    loot_data.step += 1

    if loot_data.step >= len(loot_questions):
        # Create message
        message_to_send = f"__**{loot_data.title}**__\n"

        for i in range(1, 11):
            idx = i - 1
            char_name = loot_data.characters[idx]
            if char_name:
                author = find_author_by_character(char_name)
                message_to_send += f"> <@{author}> as {char_name}\n"

        if loot_data.description and loot_data.description.lower() != "skip":
            message_to_send += f"\n{loot_data.description}\n"
        
        message_to_send += f"\n\n⭐ XP ⭐ \n```{loot_data.xp_breakdown}```\n"
        message_to_send += f"💰  Monies 💰 \n```{loot_data.gold}gp```\n"
        message_to_send += f"💎 Other goodies 💎 \n{loot_data.items}\n"


        await message.channel.send(message_to_send) # TO WHAT CHANNEL

        for i in range(1, 11): # AWARD XP AND GOLD
            idx = i - 1
            char_name = loot_data.characters[idx]
            if char_name:
                await award_xp_and_gold(char_name, int(loot_data.xp), int(loot_data.gold), f"Quest: {loot_data.title}")
        del loot_log[message.author.id]
    else:
        next_question = loot_questions[loot_data.step]
        await message.channel.send(next_question)


def setup(bot: discord.Client, guild_id: int):
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        if message.guild is None and not message.author.bot:
            if loot_log.get(message.author.id):
                await loot_builder(loot_log[message.author.id], message)  


                
                
                



