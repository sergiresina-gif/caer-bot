from datetime import datetime
from bot_instance import bot
import discord
import json
import os

#Find character by name
def find_character(name: str) -> dict:
    path_to_json_files = "logs/"
    json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

    for json_file_name in json_file_names:
        with open(os.path.join(path_to_json_files, json_file_name), 'r') as f:
            data = json.load(f)
            for character in data.get("characters", []):
                if character["name"].lower() == name.lower():
                    return character

def find_author_by_character(name: str) -> int:
    path_to_json_files = "logs/"
    json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

    for json_file_name in json_file_names:
        with open(os.path.join(path_to_json_files, json_file_name), 'r') as f:
            data = json.load(f)
            for character in data.get("characters", []):
                if character["name"].lower() == name.lower():
                    return int(json_file_name[:-5])  # Remove .json and convert to int im a fucking genius


def load_user_data(user_id: int) -> dict:
    try:
        with open(f"logs/{user_id}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"user_name": None, "user_pfp": None, "characters": []}

def save_user_data(user_id: int, data: dict) -> None:
    with open(f"logs/{user_id}.json", "w") as f:
        json.dump(data, f, indent=2)

# USED FOR THINGS THAT ONLY INTERACT WITH CHARACTERS
def load_user_logs(user_id: int) -> list:
    return load_user_data(user_id)["characters"]

def save_user_logs(user_id: int, logs: list) -> None:
    data = load_user_data(user_id)
    data["characters"] = logs
    save_user_data(user_id, data)


def write_activity(log: dict, name: str, xp: int, gold: int, label: str, timestamp: str) -> bool:
    log["history"].append({
        "xp": xp,
        "gold": gold,
        "label": label,
        "timestamp": timestamp
    })
    print(f"Logged activity for character '{name}': +{xp} XP, +{gold} Gold, Label: {label}, Timestamp: {timestamp}")
    return True


async def award_xp_and_gold(character_name: str, xp: int, gold: int, reason: str) -> None:
    owner = find_author_by_character(character_name)
    logs = load_user_logs(owner)
    for log in logs:
        if log["name"] == character_name:
            log["xp"] += xp
            log["gold"] += gold
            write_activity(log, character_name, xp, gold, reason, datetime.now().date().isoformat())
            save_user_logs(owner, logs)
    user = await bot.fetch_user(owner)
    await user.send(f"Your character {character_name} has been awarded {xp} XP and {gold} Gold from [{reason}]")