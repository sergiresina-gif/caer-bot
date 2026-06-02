import json
import discord
import onMessage


def setup(bot: discord.Client, guild_id: int):
    @bot.tree.command(name="dm-me", guild=discord.Object(id=guild_id), description="Sends a DM to the command user")
    async def dm_command(interaction: discord.Interaction):
        user = interaction.user
        try:
            dm_channel = await user.create_dm()
            # Send a public confirmation
            await interaction.response.send_message("I've sent you message!", ephemeral=True)

            await dm_channel.send("Fuck u.")

            message_to_send = onMessage.on_message()
            await dm_channel.send(message_to_send)
        except discord.Forbidden:
            await interaction.response.send_message("I can't send you a DM. Please check your privacy settings.", ephemeral=True)