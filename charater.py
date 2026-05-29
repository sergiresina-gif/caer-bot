import json
import discord


def load_user_logs(user_id: int) -> list:
    try:
        with open(f"logs/{user_id}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_user_logs(user_id: int, logs: list) -> None:
    with open(f"logs/{user_id}.json", "w") as f:
        json.dump(logs, f, indent=2)


async def name_autocomplete(interaction: discord.Interaction, current: str):
    user = interaction.user
    logs = load_user_logs(user.id)

    return [
        discord.app_commands.Choice(name=log["name"], value=log["name"])
        for log in logs if current.lower() in log["name"].lower()
    ]


async def true_false_autocomplete():
    return [
        discord.app_commands.Choice(name="True", value="True"),
        discord.app_commands.Choice(name="False", value="False")
    ]


def setup(bot: discord.Client, guild_id: int):
    @bot.tree.command(name="create", guild=discord.Object(id=guild_id), description="Create a new character!")
    async def create(interaction: discord.Interaction, name: str):
        user = interaction.user
        logs = load_user_logs(user.id)

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

        save_user_logs(user.id, logs)
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
            message_to_send += f" # {log['name']}\n> Level: {level}\n> XP: {xp_to_show} \n> Gold: {log['gold']}\n"

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
