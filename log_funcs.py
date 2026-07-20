from datetime import datetime
from bot_instance import bot
import discord
import json
import os
from models import User, Character


# Find character by name across all stored user files and return Character
def find_character(name: str) -> Character:
    path_to_json_files = "logs/"
    json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

    for json_file_name in json_file_names:
        with open(os.path.join(path_to_json_files, json_file_name), 'r') as f:
            data = json.load(f)
            user = User.from_dict(data)
            for character in user.characters:
                if character.name.lower() == name.lower():
                    return character


def find_author_by_character(name: str) -> int:
    path_to_json_files = "logs/"
    json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

    for json_file_name in json_file_names:
        with open(os.path.join(path_to_json_files, json_file_name), 'r') as f:
            data = json.load(f)
            user = User.from_dict(data)
            for character in user.characters:
                if character.name.lower() == name.lower():
                    return int(json_file_name[:-5])


def load_user_data(user_name: str) -> User:
    try:
        with open(f"logs/{user_name}.json", "r") as f:
            return User.from_dict(json.load(f))
    except FileNotFoundError:
        return User()


def save_user_data(user_name: str, data: User) -> None:
    with open(f"logs/{user_name}.json", "w") as f:
        json.dump(data.to_dict(), f, indent=2)


# USED FOR THINGS THAT ONLY INTERACT WITH CHARACTERS
def load_user_logs(user_id: int) -> list:
    return load_user_data(user_id).characters


def save_user_logs(user_name: str, logs: list) -> None:
    data = load_user_data(user_name)
    data.characters = logs
    save_user_data(user_name, data)


def write_activity(character: Character, name: str, xp: int, gold: int, label: str, timestamp: str) -> bool:
    character.add_activity(xp, gold, label, timestamp)
    print(f"Logged activity for character '{name}': +{xp} XP, +{gold} Gold, Label: {label}, Timestamp: {timestamp}")
    return True


async def award_xp_and_gold(character_name: str, xp: int, gold: int, reason: str) -> None:
    owner = find_author_by_character(character_name)
    logs = load_user_logs(owner)
    for character in logs:
        if character.name == character_name:
            character.add_xp_gold(xp, gold)
            write_activity(character, character_name, xp, gold, reason, datetime.now().date().isoformat())
            save_user_logs(owner, logs)
    user = await bot.fetch_user(owner)
    await user.send(f"Your character {character_name} has been awarded {xp} XP and {gold} Gold from [{reason}]")