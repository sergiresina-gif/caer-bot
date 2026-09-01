import json
import discord
from log_funcs import *
from pageview import CharacterPaginationView
from autocompletes import name_autocomplete, true_false_autocomplete, levels_autocomplete
from models import Character

ENTRIES_PER_PAGE = 10


# Helper to format stats
def build_stats_block(log):
    if log.xp < 1000:
        level = log.xp // 500 + 1
        xp_to_show = log.xp % 500
    else:
        level = log.xp // 1000 + 2
        xp_to_show = log.xp % 1000
    return f"**Level:** {level} | **XP:** {xp_to_show} | **Gold:** {log.gold}"

# Helper to format a single history entry
def format_entry(entry):
    return f"- **{entry.label}** | XP: {entry.xp} | Gold: {entry.gold} | ({entry.timestamp})"


def setup(bot: discord.Client, guild_id: int):
    character_group = discord.app_commands.Group(name="character", description="Create, show and remove characters")


    @character_group.command(name="create", description="Create a new character!")
    @discord.app_commands.autocomplete(level=levels_autocomplete)
    async def create(interaction: discord.Interaction, name: str, level: str, pathfinder_class: str):
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
        elif level == "2":
            logs.append(Character(name=name, pathfinder_class=pathfinder_class, xp=500))


    @character_group.command(name="show", description="View your characters!")
    @discord.app_commands.autocomplete(name=name_autocomplete, activity_log=true_false_autocomplete)
    async def show(interaction: discord.Interaction, name: str = None, activity_log: str = "False"):

        user = interaction.user
        logs = load_user_logs(user.name)  # Consider switching to user.id later

        if not logs:
            await interaction.response.send_message(
                "You have no characters yet. Use /create to make one."
            )
            return

        # Filter by name if provided
        if name:
            logs = [log for log in logs if log.name == name]
            if not logs:
                await interaction.response.send_message(
                    f"You have no character named '{name}'."
                )
                return

        # --- Build all embed pages ---
        all_embeds = []

        for log in logs:
            stats = build_stats_block(log)
            history = log.history if activity_log == "True" else []

            # If no history, just show stats on a single page
            if not history:
                desc = f"{stats}\n\n*No activity recorded or activity log disabled.*"
                embed = discord.Embed(
                    title=f"{user.name}'s Characters",
                    description=desc,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"{log.name} | 1/1")
                all_embeds.append(embed)
                continue

            # Calculate total pages for this character
            total_pages = (len(history) + ENTRIES_PER_PAGE - 1) // ENTRIES_PER_PAGE

            # Split history into chunks and create an embed for each chunk
            for i in range(0, len(history), ENTRIES_PER_PAGE):
                page_num = (i // ENTRIES_PER_PAGE) + 1
                batch = history[i:i + ENTRIES_PER_PAGE]
                entries_text = "\n".join([format_entry(e) for e in batch])

                # Page 1 shows "Activity Log:", later pages show "Activity Log (cont.):"
                if page_num == 1:
                    desc = f"{stats}\n\n**Activity Log:**\n{entries_text}"
                else:
                    desc = f"{stats}\n\n**Activity Log:**\n{entries_text}"

                # --- Safety: Discord desc limit is 4096 chars ---
                if len(desc) > 4000:
                    desc = desc[:3990] + "\n... (truncated)"

                embed = discord.Embed(
                    title=f"{user.name}'s Characters",
                    description=desc,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"{log.name} | Page {page_num}/{total_pages}")
                all_embeds.append(embed)

        # --- Send the first page with the pagination view ---
        view = CharacterPaginationView(all_embeds, author_id=user.id)
        await interaction.response.send_message(embed=all_embeds[0], view=view)

    @character_group.command(name="remove", description="Remove your character!")
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def remove(interaction: discord.Interaction, name: str):
        user = interaction.user
        logs = load_user_logs(user.name)

        if not logs:
            await interaction.response.send_message("You have no characters to remove.")
            return

        for log in logs:
            if log.name == name:
                logs.remove(log)
                save_user_logs(user.name, logs)
                await interaction.response.send_message(f"Character '{name}' removed.")
                return

        await interaction.response.send_message(f"You have no character named '{name}'.")
    @character_group.command(name="edit", description="Edit your character!")
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def edit(interaction: discord.Interaction, name: str, new_name: str, new_class: str = None):
        user = interaction.user
        logs = load_user_logs(user.name)

        if not logs:
            await interaction.response.send_message("You have no characters yet. Use /create to make one.")
            return

        for log in logs:
            if log.name == name:
                log.name = new_name
                if new_class:
                    log.pathfinder_class = new_class
                save_user_logs(user.name, logs)
                await interaction.response.send_message(f"Character '{name}' updated to '{new_name}' with class '{log.pathfinder_class}'.")
                return

        await interaction.response.send_message(f"You have no character named '{name}'.")

    bot.tree.add_command(character_group, guild=discord.Object(id=guild_id))

    @bot.tree.command(name="cs", guild=discord.Object(id=guild_id), description="Shorthand for /character show")
    async def cs(interaction: discord.Interaction, name: str = None, activity_log: str = "False"):
        await show(interaction, name, activity_log)
        
