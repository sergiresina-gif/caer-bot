import json
import discord
from log_funcs import *
from autocompletes import name_autocomplete, true_false_autocomplete


def setup(bot: discord.Client, guild_id: int):
    @bot.tree.command(name="create", guild=discord.Object(id=guild_id), description="Create a new character!")
    async def create(interaction: discord.Interaction, name: str):
        user = interaction.user
        data = load_user_data(user.id)

        if data["user_name"] is None:
            data["user_name"] = user.name
            data["user_pfp"] = str(user.avatar.url) if user.avatar else None

        logs = data["characters"]

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

        save_user_data(user.id, data)   # saves full structure
        await interaction.response.send_message(f"Character '{name}' created!")

    @bot.tree.command(name="show", guild=discord.Object(id=guild_id), description="View your chracters!")
    @discord.app_commands.autocomplete(name=name_autocomplete, activity_log=true_false_autocomplete)
    async def show(interaction: discord.Interaction, name: str = None, activity_log: str = "False"):
        user = interaction.user
        logs = load_user_logs(user.id)

        if not logs:
            await interaction.response.send_message("You have no characters yet. Use /create to make one.")
            return

        if name:
            logs = [log for log in logs if log["name"] == name]
            if not logs:
                await interaction.response.send_message(f"You have no character named '{name}'.")
                return

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
                message_to_send += "\nActivity Log:\n"
                for activity in log["history"]:
                    message_to_send += f"- **{activity['label']}** | XP: {activity['xp']} | Gold: {activity['gold']} | ({activity['timestamp']})\n"
                message_to_send += "\n"

        embed = discord.Embed(
            title=f"{user.name}'s Characters",
            description=message_to_send
        )

        await interaction.response.send_message(embed=embed)
