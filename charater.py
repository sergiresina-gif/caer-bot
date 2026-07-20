import json
import discord
from log_funcs import *
from autocompletes import name_autocomplete, true_false_autocomplete, levels_autocomplete
from models import Character


def setup(bot: discord.Client, guild_id: int):
    @bot.tree.command(name="create", guild=discord.Object(id=guild_id), description="Create a new character!")
    @discord.app_commands.autocomplete(level=levels_autocomplete)
    async def create(interaction: discord.Interaction, name: str, level: str = "1", pathfinder_class: str = None):
        user = interaction.user
        data = load_user_data(user.name)

        if data.user_name is None:
            data.user_name = user.name
            data.user_pfp = str(user.avatar.url) if user.avatar else None

        logs = data.characters

        for log in logs:
            if log.name == name:
                await interaction.response.send_message(f"You already have a character named '{name}'!")
                return

        # Also check all other user logs in the logs folder to prevent duplicate character names
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        if os.path.isdir(logs_dir):
            for fname in os.listdir(logs_dir):
                fpath = os.path.join(logs_dir, fname)
                if not os.path.isfile(fpath):
                    continue
                # expect filenames like <userid>.json
                stem = os.path.splitext(fname)[0]
                if not stem.isdigit():
                    continue
                try:
                    other_logs = load_user_logs(int(stem))
                except Exception:
                    # fallback: try to read raw json and inspect
                    try:
                        with open(fpath, "r", encoding="utf-8") as fh:
                            raw = json.load(fh)
                            for ch in raw.get("characters", []):
                                if ch.get("name") == name:
                                    await interaction.response.send_message(f"A character named '{name}' already exists in the logs.")
                                    return
                    except Exception:
                        continue

                for oth in other_logs:
                    if getattr(oth, "name", None) == name:
                        await interaction.response.send_message(f"A character named '{name}' already exists in the logs.")
                        return
        

        if level == "3":
            logs.append(Character(name=name, pathfinder_class=pathfinder_class, xp=1000))
        else:
            logs.append(Character(name=name, pathfinder_class=pathfinder_class, xp=0))
        save_user_data(user.name, data)   # saves full structure
        await interaction.response.send_message(f"Character '{name}' created!")


    @bot.tree.command(name="show", guild=discord.Object(id=guild_id), description="View your chracters!")
    @discord.app_commands.autocomplete(name=name_autocomplete, activity_log=true_false_autocomplete)
    async def show(interaction: discord.Interaction, name: str = None, activity_log: str = "False"):
        user = interaction.user
        logs = load_user_logs(user.name)

        if not logs:
            await interaction.response.send_message("You have no characters yet. Use /create to make one.")
            return

        if name:
            logs = [log for log in logs if log.name == name]
            if not logs:
                await interaction.response.send_message(f"You have no character named '{name}'.")
                return

        message_to_send = ""
        for log in logs:
            if log.xp < 1000:
                level = log.xp // 500 + 1
                xp_to_show = log.xp % 500
            else:
                level = log.xp // 1000 + 2
                xp_to_show = log.xp % 1000
            message_to_send += f"# {log.name}\n> Level: {level}\n> XP: {xp_to_show} \n> Gold: {log.gold}\n"

            if activity_log == "True":
                message_to_send += "\nActivity Log:\n"
                for activity in log.history:
                    message_to_send += f"- **{activity.label}** | XP: {activity.xp} | Gold: {activity.gold} | ({activity.timestamp})\n"
                message_to_send += "\n"

        embed = discord.Embed(
            title=f"{user.name}'s Characters",
            description=message_to_send
        )

        await interaction.response.send_message(embed=embed)
