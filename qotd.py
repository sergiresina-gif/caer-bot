import json
import random
import discord


def load_qotds() -> list:
    try:
        with open("qotds/qotds.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_qotds(qotds: list) -> None:
    with open("qotds/qotds.json", "w") as f:
        json.dump(qotds, f, indent=2)


def setup(bot: discord.Client, guild_id: int, channel_id: int, target_emote: str):
    @bot.event
    async def on_reaction_add(reaction, user):
        if reaction.message.channel.id != channel_id:
            return

        if str(reaction.emoji) != target_emote:
            return

        message = reaction.message
        try:
            message = await message.channel.fetch_message(message.id)
        except discord.NotFound:
            print("Message not found (maybe deleted)")
            return
        except discord.Forbidden:
            print("Missing permissions to fetch message")
            return

        qotds = load_qotds()
        qotds.append({
            "content": message.content,
            "author": str(message.author),
            "datestamp": discord.utils.utcnow().isoformat(),
            "times-asked": 0,
            "author-id": message.author.id
        })
        save_qotds(qotds)

    @bot.tree.command(name="qotd", guild=discord.Object(id=guild_id), description="Get a random QOTD!")
    async def qotd(interaction: discord.Interaction):
        qotds = load_qotds()
        if not qotds:
            await interaction.response.send_message("No QOTDs are available yet.")
            return

        chosen = random.choices(qotds, weights=[1 / (item["times-asked"] + 1) for item in qotds], k=1)[0]
        chosen["times-asked"] += 1
        save_qotds(qotds)

        embed = discord.Embed(title=chosen["content"])
        await interaction.response.send_message(embed=embed, content=f"New <@&1509831193942691910>! Thanks for the suggestion <@{chosen['author-id']}>!")
