import io
import json
import discord
from datetime import datetime
from log_funcs import *

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
#from autocompletes import 


def setup(bot: discord.Client, guild_id: int):
    stats_group = discord.app_commands.Group(name="stats", description="View the server's character stats")

    @stats_group.command(name="general", description="View general stats for the server's characters.")
    async def general(interaction: discord.Interaction):
        total_characters = 0
        top_3_characters = []

        def get_level(xp: int) -> int:
            if xp < 1000:
                return xp // 500 + 1
            return xp // 1000 + 2

        # open each user's log user's logs and count characters. Keep count of the top 3 characters by level
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        if os.path.isdir(logs_dir):
            for filename in os.listdir(logs_dir):
                if not filename.endswith(".json"):
                    continue

                log_path = os.path.join(logs_dir, filename)
                try:
                    with open(log_path, "r", encoding="utf-8") as handle:
                        data = json.load(handle)
                except (json.JSONDecodeError, OSError):
                    continue

                for character in data.get("characters", []):
                    total_characters += 1
                    top_3_characters.append({
                        "name": character.get("name", "Unknown"),
                        "level": get_level(character.get("xp", 0)),
                        "xp": character.get("xp", 0),
                        "gold": character.get("gold", 0),
                    })

        top_3_characters.sort(key=lambda item: (-item["level"], -item["xp"], item["name"]))
        top_3_characters = top_3_characters[:3]

        lines = [f"Total characters: {total_characters}", "", "Top 3 by level:"]
        if top_3_characters:
            for index, character in enumerate(top_3_characters, start=1):
                lines.append(
                    f"{index}. {character['name']} — Level {character['level']} (XP: {character['xp']}, Gold: {character['gold']})"
                )
        else:
            lines.append("No characters found yet.")

        embed = discord.Embed(
            title="Server Character Stats",
            description="\n".join(lines),
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)

    bot.tree.add_command(stats_group, guild=discord.Object(id=guild_id))

    @stats_group.command(name="classes", description="View the distribution of character classes in the server.")
    async def classes(interaction: discord.Interaction):
        class_counts = {}

        # open each user's log and count character classes
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        if os.path.isdir(logs_dir):
            for filename in os.listdir(logs_dir):
                if not filename.endswith(".json"):
                    continue

                log_path = os.path.join(logs_dir, filename)
                try:
                    with open(log_path, "r", encoding="utf-8") as handle:
                        data = json.load(handle)
                except (json.JSONDecodeError, OSError):
                    continue

                for character in data.get("characters", []):
                    char_class = character.get("pathfinder_class", "Unknown")
                    class_counts[char_class] = class_counts.get(char_class, 0) + 1

        lines = ["Character Class Distribution:"]
        for char_class, count in class_counts.items():
            lines.append(f"- {char_class}: {count}")

        embed = discord.Embed(
            title="Server Character Classes",
            description="\n".join(lines),
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)

    @stats_group.command(name="levels", description="View the distribution of character levels in the server.")
    async def levels(interaction: discord.Interaction):
        level_counts = {}

        def get_level(xp: int) -> int:
            if xp < 1000:
                return xp // 500 + 1
            return xp // 1000 + 2

        # open each user's log and count character levels
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        if os.path.isdir(logs_dir):
            for filename in os.listdir(logs_dir):
                if not filename.endswith(".json"):
                    continue

                log_path = os.path.join(logs_dir, filename)
                try:
                    with open(log_path, "r", encoding="utf-8") as handle:
                        data = json.load(handle)
                except (json.JSONDecodeError, OSError):
                    continue

                for character in data.get("characters", []):
                    level = get_level(character.get("xp", 0))
                    level_counts[level] = level_counts.get(level, 0) + 1

        lines = ["Character Level Distribution:"]
        for level, count in sorted(level_counts.items()):
            lines.append(f"- Level {level}: {count}")

        sorted_levels = sorted(level_counts.items())
        if sorted_levels:
            plt.figure(figsize=(6, 4))
            levels = [level for level, _ in sorted_levels]
            counts = [count for _, count in sorted_levels]
            plt.bar(levels, counts, color="#5865F2")
            plt.xlabel("Level")
            plt.ylabel("Count")
            plt.title("Server Character Levels")
            plt.tight_layout()

            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            plt.close()
            chart_file = discord.File(buffer, filename="character_levels.png")
        else:
            chart_file = None
            plt.close("all")

        embed = discord.Embed(
            title="Server Character Levels",
            description="\n".join(lines),
            color=discord.Color.blurple()
        )
        if chart_file is not None:
            embed.set_image(url="attachment://character_levels.png")

        if chart_file is not None:
            await interaction.response.send_message(embed=embed, file=chart_file)
        else:
            await interaction.response.send_message(embed=embed)
