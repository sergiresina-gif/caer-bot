import json
import discord
from datetime import datetime
from log_funcs import *
from autocompletes import name_autocomplete

raids = [
    {"xp": 500, "gold": 100},
    {"xp": 1000, "gold": 250},
    {"xp": 2000, "gold": 500},
]

def setup(bot: discord.Client, guild_id: int):
    log_group = discord.app_commands.Group(name="log", description="Log activities for a character")

    @log_group.command(name="manual", description="Log an xp and gold manually.")
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def manual(interaction: discord.Interaction, name: str, xp: int, gold: int, label: str):
        user = interaction.user
        logs = load_user_logs(user.id)

        for log in logs:
            if log["name"] == name:
                log["xp"] += xp
                log["gold"] += gold
                write_activity(logs, name, xp, gold, label, datetime.now().date().isoformat())
                save_user_logs(user.id, logs)
                await interaction.response.send_message(f"Activity logged for '{name}'!")
                return

        await interaction.response.send_message(f"You have no character named '{name}'.")

    @log_group.command(name="raid", description="Log a raid completion.")
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def raid(interaction: discord.Interaction, name: str, level: int):
        user = interaction.user
        logs = load_user_logs(user.id)

        if level < 1 or level > len(raids):
            await interaction.response.send_message(f"Raid level must be between 1 and {len(raids)}.")
            return

        for log in logs:
            if log["name"] == name:
                xp_gain = raids[level - 1]["xp"]
                gold_gain = raids[level - 1]["gold"]
                log["xp"] += xp_gain
                log["gold"] += gold_gain
                write_activity(logs, name, xp_gain, gold_gain, f"Raid Level {level}", datetime.now().date().isoformat())
                save_user_logs(user.id, logs)
                await interaction.response.send_message(f"Raid logged for '{name}'!")
                return

        await interaction.response.send_message(f"You have no character named '{name}'.")

    bot.tree.add_command(log_group, guild=discord.Object(id=guild_id))
