import json
import discord
from datetime import datetime
from log_funcs import *
from autocompletes import name_autocomplete

skirmishes = [
    {"xp": 100, "gold": 5}, # Level 1
    {"xp": 100, "gold": 7}, # Level 2
    {"xp": 100, "gold": 10}, # Level 3
    {"xp": 100, "gold": 17}, # Level 4
    {"xp": 100, "gold": 25}, # Level 5
    {"xp": 100, "gold": 40}, # Level 6
    {"xp": 100, "gold": 60}, # Level 7
    {"xp": 100, "gold": 82}, # Level 8
    {"xp": 100, "gold": 115}, # Level 9
    {"xp": 100, "gold": 165}, # Level 10
    {"xp": 100, "gold": 232}, # Level 11
    {"xp": 100, "gold": 332}, # Level 12
    {"xp": 100, "gold": 500}, # Level 13
    {"xp": 100, "gold": 750}, # Level 14
    {"xp": 100, "gold": 1125}, # Level 15
    {"xp": 100, "gold": 1700}, # Level 16
    {"xp": 100, "gold": 2650}, # Level 17
    {"xp": 100, "gold": 4150}, # Level 18
    {"xp": 100, "gold": 7000}, # Level 19
    {"xp": 100, "gold": 20000}, # Level 20
]

def setup(bot: discord.Client, guild_id: int):
    log_group = discord.app_commands.Group(name="log", description="Log activities for a character")

    @log_group.command(name="manual", description="Log an xp and gold manually.")
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def manual(interaction: discord.Interaction, name: str, xp: int, gold: int, label: str):
        user = interaction.user
        logs = load_user_logs(user.name)

        for character in logs:
            if character.name == name:
                character.add_xp_gold(xp, gold)
                await write_activity(character, name, xp, gold, label, datetime.now().date().isoformat())
                await save_user_logs(user.name, logs)
                await interaction.response.send_message(f"Activity logged for '{name}'!", ephemeral=True)
                return

        await interaction.response.send_message(f"You have no character named '{name}'.", ephemeral=True)

    @log_group.command(name="skirmish", description="Log a skirmish completion.")
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def skirmish(interaction: discord.Interaction, name: str, level: int):
        user = interaction.user
        logs = load_user_logs(user.name)

        if level < 1 or level > len(skirmishes):
            await interaction.response.send_message(f"Skirmish level must be between 1 and {len(skirmishes)}.", ephemeral=True)
            return

        for character in logs:
            if character.name == name:
                xp_gain = skirmishes[level - 1]["xp"]
                gold_gain = skirmishes[level - 1]["gold"]
                character.add_xp_gold(xp_gain, gold_gain)
                await write_activity(character, name, xp_gain, gold_gain, f"Skirmish Level {level}", datetime.now().date().isoformat())
                await save_user_logs(user.name, logs)
                await interaction.response.send_message(f"Skirmish logged for '{name}'!", ephemeral=True)
                return

        await interaction.response.send_message(f"You have no character named '{name}'.", ephemeral=True)

    @log_group.command(name="qotd", description="Log a qotd completion.")
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def qotd(interaction: discord.Interaction, name: str):
        user = interaction.user
        logs = load_user_logs(user.name)

        for character in logs:
            if character.name == name:
                character.add_xp_gold(10, 0)
                await write_activity(character, name, 10, 0, "QOTD", datetime.now().date().isoformat())
                await save_user_logs(user.name, logs)
                await interaction.response.send_message(f"QOTD logged for '{name}'!", ephemeral=True)
                return

    @log_group.command(name="undo", description="Undo the last activity logged for a character.")
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def undo(interaction: discord.Interaction, name: str):
        user = interaction.user
        logs = load_user_logs(user.name)

        for character in logs:
            if character.name == name:
                if not character.history:
                    await interaction.response.send_message(f"No activities to undo for {name}.", ephemeral=True)
                    return

                last_activity = character.history.pop()
                character.xp -= last_activity.xp
                character.gold -= last_activity.gold
                await save_user_logs(user.name, logs)
                await interaction.response.send_message(f"Last activity undone for {name}!", ephemeral=True)
                return

        await interaction.response.send_message(f"You have no character named {name}.", ephemeral=True)

    bot.tree.add_command(log_group, guild=discord.Object(id=guild_id))
