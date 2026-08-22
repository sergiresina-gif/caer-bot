import discord
from typing import List

class CharacterPaginationView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], author_id: int, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.total_pages = len(embeds)
        self.author_id = author_id

        # Buttons
        self.prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.primary)
        self.next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.primary)

        # Wire callbacks
        self.prev_button.callback = self.previous_page_callback
        self.next_button.callback = self.next_page_callback

        # Add to view
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.total_pages - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You cannot control this pagination.", ephemeral=True
            )
            return False
        return True

    async def previous_page_callback(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )
        else:
            await interaction.response.defer()

    async def next_page_callback(self, interaction: discord.Interaction):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )
        else:
            await interaction.response.defer()