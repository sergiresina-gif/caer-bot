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


def setup(bot: discord.Client, guild_id: int, channel_id: int, target_emote: str):
    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.channel_id != channel_id:
            return

        if str(payload.emoji) != target_emote:
            return

        if payload.user_id == bot.user.id:
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

    @bot.tree.command(name="qotd", guild=discord.Object(id=guild_id), description="Get a random QOTD!")
    @discord.app_commands.autocomplete(repeated=true_false_autocomplete)
    async def qotd(interaction: discord.Interaction, repeated: str = "False"):
        qotds = load_qotds()
        if not qotds:
            await interaction.response.send_message("No QOTDs are available yet.")
            return
        
        repeated_qotds = [item for item in qotds if item["times-asked"] > 0]
        not_repeated_qotds = [item for item in qotds if item["times-asked"] == 0]

        if repeated == "True":
            chosen = random.choices(not_repeated_qotds, weights=[1 / (item["times-asked"] + 1) for item in not_repeated_qotds], k=1)[0]
        else:
            chosen = random.choices(qotds, weights=[1 / (item["times-asked"] + 1) for item in qotds], k=1)[0]
        chosen["times-asked"] += 1
        save_qotds(qotds)

        embed = discord.Embed(title=chosen["content"])
        await interaction.response.send_message(embed=embed, content=f"New QOTD <@&1509831193942691910>! Thanks for the suggestion <@{chosen['author-id']}>!")
        save_recap(chosen)

    @bot.tree.command(name="recap", guild=discord.Object(id=guild_id), description="Get a recap of last week's QOTDs!")
    async def recap(interaction: discord.Interaction):
        qotds = load_qotds()
        if not qotds:
            await interaction.response.send_message("No QOTDs are available yet.")
            return
        
        recap = load_recap()

        message_to_send = "New Recap <@&1509831193942691910>! Remember, this will last until next Sunday\n\n"
        embed = discord.Embed(title="Recap")
        embed_description = ""
        idx = recap["index"]
        for item in recap["last_seven"][-7:]:
            idx += 1
            embed_description += f"**{idx}. {item['content']}**\n"
        embed.description = embed_description
        save_recap(None, idx)
        await interaction.response.send_message(embed=embed, content=message_to_send)