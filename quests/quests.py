import json
import discord
from datetime import datetime
from autocompletes import all_characters_autocomplete

loot_questions = [
    "What is the title for the quest?",
    "Add a description. You can type Skip to not have a description.",
    "How much XP do you want to give? Just type a number.",
    "Add a break down of the XP. The text will be added as is. Example: \n\n Faked being scared by Appricott: 5xp \n Sneaked on the Lions with 4 successes: 60xp \n Combat against Lions!: 130xp \n Succesfully captured the Lion alive: 30xp \n Good RP: 5xp \n TOTAL: 230xp ",
    "How much gold do you want to give? Just type a number. JUST 200. No 200gp.",
    "What items do you want to give? The text will be added as is. Example: Rank 2 Scroll \n Merciful Charm \n Numbing Tonic \n Retrieval Prism \n Quicksilver Mutagen" ]


loot_fields = [
    "Title",
    "Description",
    "XP",
    "XP Breakdown",
    "Gold",
    "Items"
]
loot_log= {}

def setup(bot: discord.Client, guild_id: int):
    @bot.tree.command(name="loot", guild=discord.Object(id=guild_id), description="Sends a DM to the command user")
    @discord.app_commands.autocomplete(character_1=all_characters_autocomplete, character_2=all_characters_autocomplete, character_3=all_characters_autocomplete, character_4=all_characters_autocomplete, character_5=all_characters_autocomplete, character_6=all_characters_autocomplete, character_7=all_characters_autocomplete, character_8=all_characters_autocomplete, character_9=all_characters_autocomplete, character_10=all_characters_autocomplete)
    async def loot_command(interaction: discord.Interaction, character_1: str, character_2: str = None, character_3: str = None, character_4: str = None, character_5: str = None, character_6: str = None, character_7: str = None, character_8: str = None, character_9: str = None, character_10: str = None):
        user = interaction.user
        if user.id in loot_log.keys():
            del loot_log[user.id]
        try:
            dm_channel = await user.create_dm()
            # Send a public confirmation
            await interaction.response.send_message("I've sent you message for the loot log!", ephemeral=True)

            loot_log[user.id] = {
                "character_1": character_1,
                "character_2": character_2,
                "character_3": character_3,
                "character_4": character_4,
                "character_5": character_5,
                "character_6": character_6,
                "character_7": character_7,
                "character_8": character_8,
                "character_9": character_9,
                "character_10": character_10,
                "step": 0,
                "last_activity": datetime.now()
            }
            await dm_channel.send("Hi! Let's do the loot log. These will be helpful:",
                                files=[discord.File("quests/goldbounty.png"), discord.File("quests/goldexcursion.png")])            
            await dm_channel.send(loot_questions[loot_log[user.id]["step"]])
        except discord.Forbidden:
            await interaction.response.send_message("I can't send you a DM. Please check your privacy settings.", ephemeral=True)