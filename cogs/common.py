import discord
from discord import app_commands
from discord.ext import commands
from services.utils import get_wikitext_page, PageNotFound, parse_quote, clean_wikitext, get_image_url
from services.discord_utils import create_embed, create_wiki_view, truncate_text, autocomplete_category
from services.logger import log_error,log_warning

class WikiCommonCog(commands.Cog):
    """Commands for Items, Lore, and Attachments"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="wiki-items", description="Get info about an Item")
    @app_commands.describe(name="Select an Item")
    async def items(self, interaction: discord.Interaction, *, name: str):
        try:
            wikitext = get_wikitext_page(name)
            quote = parse_quote(wikitext)
            image_url = get_image_url(f"{name}.png")
        except PageNotFound:
            await interaction.response.send_message(f"Page '{name}' not found on the wiki.", ephemeral=True)
            log_warning(interaction.user.id, "wiki-items", f"Page '{name}' not found")
            return
        except Exception as e:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
            log_error(interaction.user.id, "wiki-items", e)
            return

        embed = create_embed(title=name, description=quote, image_url=image_url)
        await interaction.response.send_message(embed=embed, view=create_wiki_view(name))

    @items.autocomplete("name")
    async def items_autocomplete(self, interaction: discord.Interaction, current: str):
        return await autocomplete_category("Items", current)

    @app_commands.command(name="wiki-attachments", description="Get info about an Attachment")
    @app_commands.describe(name="Select an Attachment")
    async def attachments(self, interaction: discord.Interaction, *, name: str):
        try:
            wikitext = get_wikitext_page(name)
            quote = parse_quote(wikitext)
            image_url = get_image_url(f"{name}.png")
        except PageNotFound:
            await interaction.response.send_message(f"Page '{name}' not found on the wiki.", ephemeral=True)
            log_warning(interaction.user.id, "wiki-attachments", f"Page '{name}' not found")
            return
        except Exception as e:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
            log_error(interaction.user.id, "wiki-attachments", e)
            return

        embed = create_embed(title=name, description=quote, image_url=image_url)
        await interaction.response.send_message(embed=embed, view=create_wiki_view(name))

    @attachments.autocomplete("name")
    async def attachments_autocomplete(self, interaction: discord.Interaction, current: str):
        return await autocomplete_category("Attachments", current)

    @app_commands.command(name="wiki-lore", description="Get info about Lore")
    @app_commands.describe(name="Select Lore entry")
    async def lore(self, interaction: discord.Interaction, *, name: str):
        try:
            wikitext = get_wikitext_page(name)
            text = clean_wikitext(wikitext)
        except PageNotFound:
            await interaction.response.send_message(f"Page '{name}' not found on the wiki.", ephemeral=True)
            log_warning(interaction.user.id, "wiki-lore", f"Page '{name}' not found")
            return
        except Exception as e:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
            log_error(interaction.user.id, "wiki-lore", e)
            return

        desc = truncate_text(text, page_name=name)
        embed = create_embed(title=name, description=desc)
        await interaction.response.send_message(embed=embed, view=create_wiki_view(name))

    @lore.autocomplete("name")
    async def lore_autocomplete(self, interaction: discord.Interaction, current: str):
        return await autocomplete_category("Lore", current)


async def setup(bot: commands.Bot):
    await bot.add_cog(WikiCommonCog(bot))
