from datetime import datetime
from bot_instance import bot
import discord
import json
import os
from models import *

async def send_it_to_victoria(content: str) -> None:
    victoria_id = int(os.getenv("VICTORIA_ID"))
    victoria = await bot.fetch_user(victoria_id)
    if victoria:
        dm_channel = await victoria.create_dm()
        await dm_channel.send(content)
    else:
        print("Victoria not found.")

# Find character by name across all stored user files and return Character
async def find_character(name: str) -> Character:
    path_to_json_files = "logs/"
    json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

    for json_file_name in json_file_names:
        with open(os.path.join(path_to_json_files, json_file_name), 'r') as f:
            data = json.load(f)
            user = User.from_dict(data)
            for character in user.characters:
                if character.name.lower() == name.lower():
                    return character


async def find_author_by_character(name: str) -> int:
    path_to_json_files = "logs/"
    json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

    for json_file_name in json_file_names:
        with open(os.path.join(path_to_json_files, json_file_name), 'r') as f:
            data = json.load(f)
            user = User.from_dict(data)
            for character in user.characters:
                if character.name.lower() == name.lower():
                    return int(json_file_name[:-5])


def _get_log_path(user_name: str) -> str:
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return os.path.join(logs_dir, f"{user_name}.json")


def load_user_data(user_name: str) -> User:
    log_path = _get_log_path(user_name)
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return User.from_dict(json.load(f))
    except FileNotFoundError:
        return User()


def save_user_data(user_name: str, data: User) -> None:
    log_path = _get_log_path(user_name)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(data.to_dict(), f, indent=2)


# USED FOR THINGS THAT ONLY INTERACT WITH CHARACTERS
def load_user_logs(user_id: int) -> list:
    return load_user_data(user_id).characters


def save_user_logs(user_name: str, logs: list) -> None:
    data = load_user_data(user_name)
    for character_1 in logs:
        for character_2 in data.characters:
            if character_1.name == character_2.name:
                if character_2.xp < 1000:
                    level_2 = character_2.xp // 500 + 1
                else:
                    level_2 = character_2.xp // 1000 + 2
                if character_1.xp < 1000:
                    level_1 = character_1.xp // 500 + 1
                else:
                    level_1 = character_1.xp // 1000 + 2
                if level_1 > level_2:
                    print(f"Character {character_1.name} leveled up from level {level_2} to level {level_1}!")
    data.characters = logs
    save_user_data(user_name, data)


async def write_activity(character: Character, name: str, xp: int, gold: float, label: str, timestamp: str) -> bool:
    character.add_activity(xp, gold, label, timestamp)
    print(f"Logged activity for character '{name}': +{xp} XP, +{gold} Gold, Label: {label}, Timestamp: {timestamp}")
    await send_it_to_victoria(f"Logged activity for character '{name}': +{xp} XP, +{gold} Gold, Label: {label}, Timestamp: {timestamp}")
    return True


async def award_xp_and_gold(character_name: str, xp: int, gold: float, reason: str) -> None:
    owner = await find_author_by_character(character_name)
    logs = load_user_logs(owner)
    for character in logs:
        if character.name == character_name:
            character.add_xp_gold(xp, gold)
            await write_activity(character, character_name, xp, gold, reason, datetime.now().date().isoformat())
            save_user_logs(owner, logs)
    user = await bot.fetch_user(owner)
    await user.send(f"Your character {character_name} has been awarded {xp} XP and {gold} Gold from [{reason}]")

async def level_up_message(interaction: discord.Interaction, user_name: str, logs: list):
    data = load_user_data(user_name)
    for character_1 in logs:
        for character_2 in data.characters:
            if character_1.name == character_2.name:
                if character_2.xp < 1000:
                    level_2 = character_2.xp // 500 + 1
                else:
                    level_2 = character_2.xp // 1000 + 2
                if character_1.xp < 1000:
                    level_1 = character_1.xp // 500 + 1
                else:
                    level_1 = character_1.xp // 1000 + 2
                if level_1 > level_2:
                    await interaction.send_message(f"Woooo!")
