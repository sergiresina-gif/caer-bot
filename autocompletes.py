import discord
from log_funcs import *

async def name_autocomplete(interaction: discord.Interaction, current: str):
    user = interaction.user
    logs = load_user_logs(user.id)

    return [
        discord.app_commands.Choice(name=log["name"], value=log["name"])
        for log in logs if current.lower() in log["name"].lower()
    ]


async def true_false_autocomplete(interaction: discord.Interaction, current: str):
    return [
        discord.app_commands.Choice(name="True", value="True"),
        discord.app_commands.Choice(name="False", value="False")
    ]

async def all_characters_autocomplete(interaction: discord.Interaction, current: str):
    path_to_json_files = "logs/"
    json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

    characters = []
    for json_file_name in json_file_names:
        with open(os.path.join(path_to_json_files, json_file_name), 'r') as f:
            data = json.load(f)
            for character in data.get("characters", []):
                if current.lower() in character["name"].lower():
                    characters.append(character["name"])

    return [discord.app_commands.Choice(name=character, value=character) for character in characters]

