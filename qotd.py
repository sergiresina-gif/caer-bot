from enum import member
import json
import random
import discord

from autocompletes import true_false_autocomplete


def load_qotds() -> list:
    try:
        with open("qotds/qotds.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_qotds(qotds: list) -> None:
    with open("qotds/qotds.json", "w") as f:
        json.dump(qotds, f, indent=2)


def select_qotd(qotds: list, repeated: str = "False") -> dict | None:
    if repeated == "True":
        pool = qotds
    else:
        pool = [item for item in qotds if item["times-asked"] == 0]

    if not pool:
        return None

    weights = [1 / (item["times-asked"] + 1) for item in pool]
    return random.choices(pool, weights=weights, k=1)[0]


def save_recap(qotd: dict, index: int = None) -> None:
    try:
        with open("qotds/recap.json", "r") as f:
            recap = json.load(f)
    except FileNotFoundError:
        recap = {"index": 0, "last_seven": []}
    
    if index is not None:
        recap["index"] = index
    if qotd:
        recap["last_seven"].append({
            "content": qotd["content"],
            "author": qotd["author"],
            "datestamp": qotd["datestamp"],
            "times-asked": qotd["times-asked"],
            "author-id": qotd["author-id"]
        })
    else:
        recap["last_seven"] = []

    with open("qotds/recap.json", "w") as f:
        json.dump(recap, f, indent=2)

def load_recap() -> dict:
    try:
        with open("qotds/recap.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"index": 0, "last_seven": []}


def setup(bot: discord.Client, guild_id: int, channel_id_sug: int, channel_id_qotd: int, target_emote: str, target_emote_2: str):
    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.channel_id != channel_id_sug and payload.channel_id != channel_id_qotd:
            return

        if str(payload.emoji) != target_emote and str(payload.emoji) != target_emote_2:
            return

        channel = bot.get_channel(payload.channel_id)
        if channel is None:
            try:
                channel = await bot.fetch_channel(payload.channel_id)
            except discord.NotFound:
                print("Channel not found", payload.channel_id)
                return
            except discord.Forbidden:
                print("Missing permissions to fetch channel", payload.channel_id)
                return
            except Exception as e:
                print("Failed fetching channel:", e)
                return

        if channel.id == channel_id_sug:
            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.NotFound:
                print("fetch_message NotFound for", payload.message_id)
                return
            except discord.Forbidden:
                print("fetch_message Forbidden for", payload.message_id)
                return
            except Exception as e:
                print("fetch_message exception:", type(e), e)
                return

            qotds = load_qotds()
            for qotd in qotds:
                if qotd["content"] == message.content:
                    print("QOTD already exists:", message.content)
                    return
            qotds.append({
                "content": message.content,
                "author": str(message.author),
                "datestamp": discord.utils.utcnow().isoformat(),
                "times-asked": 0,
                "author-id": message.author.id
            })
            print(f"Added QOTD: {message.content} by {message.author} (ID: {message.author.id})")
            save_qotds(qotds)

        if channel.id == channel_id_qotd:
            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.NotFound:
                print("fetch_message NotFound for", payload.message_id)
                return
            except discord.Forbidden:
                print("fetch_message Forbidden for", payload.message_id)
                return
            except Exception as e:
                print("fetch_message exception:", type(e), e)
                return

            recap = load_recap()
            for item in recap["last_seven"]:
                if item["content"] == message.content:
                    print("QOTD already in recap:", message.content)
                    return
            qotd_entry = {
                "content": message.content,
                "author": str(message.author),
                "datestamp": discord.utils.utcnow().isoformat(),
                "times-asked": 0,
                "author-id": message.author.id
            }
            print(f"Added QOTD to recap: {message.content} by {message.author} (ID: {message.author.id})")
            save_recap(qotd_entry)

    @bot.tree.command(name="qotd", guild=discord.Object(id=guild_id), description="Get a random QOTD!")
    @discord.app_commands.autocomplete(repeated=true_false_autocomplete)
    async def qotd(interaction: discord.Interaction, repeated: str = "False"):
        allowed_roles = [1510715535136915523, 1510715535136915521, 1510715535128658073, 1516407439996489758]

        if not any(role.id in allowed_roles for role in interaction.user.roles):
            await interaction.response.send_message("You do not have access to this command.")
            return
        
        qotds = load_qotds()
        if not qotds:
            await interaction.response.send_message("No QOTDs are available yet.")
            return

        chosen = select_qotd(qotds, repeated=repeated)
        if chosen is None:
            await interaction.response.send_message("All QOTDs have already been used. Use /qotd repeated True to include previously asked ones.")
            return

        chosen["times-asked"] += 1
        save_qotds(qotds)

        embed = discord.Embed(title=chosen["content"])
        await interaction.response.send_message(embed=embed, content=f"New QOTD <@&1510715535116206298>! Thanks for the suggestion <@{chosen['author-id']}>!")
        save_recap(chosen)

    @bot.tree.command(name="recap", guild=discord.Object(id=guild_id), description="Get a recap of last week's QOTDs!")
    async def recap(interaction: discord.Interaction):
        qotds = load_qotds()
        if not qotds:
            await interaction.response.send_message("No QOTDs are available yet.")
            return

        allowed_roles = [1510715535136915523, 1510715535136915521, 1510715535128658073, 1516407439996489758]
        if not any(role.id in allowed_roles for role in interaction.user.roles):
            await interaction.response.send_message("You do not have access to this command.")
            return
        
        recap = load_recap()

        message_to_send = "New Recap <@&1510715535116206298>! Remember, this will last until next Sunday\n\n"
        embed = discord.Embed(title="Recap")
        embed_description = ""
        idx = recap["index"]
        for item in recap["last_seven"][-7:]:
            idx += 1
            embed_description += f"**{idx}. {item['content']}**\n"
        embed.description = embed_description
        save_recap(None, idx)
        await interaction.response.send_message(embed=embed, content=message_to_send)