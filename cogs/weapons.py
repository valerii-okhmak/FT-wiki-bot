import discord
from discord import app_commands
from discord.ext import commands
from services.weapons import parse_gun_page
from services.discord_utils import create_embed, create_wiki_view, add_fields, autocomplete_category
from services.utils import get_wikitext_page, PageNotFound
from services.logger import log_error ,log_warning

class WikiWeaponsCog(commands.Cog):
    """Commands for Weapons"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.attachments_wikitext = None

    async def ensure_attachments_loaded(self):
        if not self.attachments_wikitext:
            loop = self.bot.loop
            self.attachments_wikitext = await loop.run_in_executor(
                None, lambda: get_wikitext_page("Template:Attachments")
            )

    @app_commands.command(name="wiki-weapons", description="Get info about a Weapon")
    @app_commands.describe(name="Select a Weapon")
    async def weapon(self, interaction: discord.Interaction, *, name: str):
        await self.ensure_attachments_loaded()

        try:
            data = parse_gun_page(name, self.attachments_wikitext)
        except PageNotFound:
            await interaction.response.send_message(f"Page '{name}' not found on the wiki.", ephemeral=True)
            log_warning(interaction.user.id, "wiki-weapons", f"Page '{name}' not found")
            return
        except Exception as e:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
            log_error(interaction.user.id, "wiki-weapons", e)
            return

        desc_parts = []
        for key in ["manufacturer", "type", "ammo"]:
            if val := data.get(key):
                desc_parts.append(f"**{key.capitalize()}:** {val}")

        stats_map = {
            "firepower": "Firepower",
            "stability": "Stability",
            "range": "Range",
            "mobility": "Mobility"
        }
        for stat, label in stats_map.items():
            if val := data.get(stat):
                desc_parts.append(f"**{label}:** {val}")

        if quote := data.get("quote"):
            desc_parts.append(f"\n*{quote}*")
        if attachments := data.get("attachments"):
            desc_parts.append(f"\n**Attachments:** {', '.join(attachments)}")

        description = "\n".join(desc_parts)

        embed = create_embed(
            title=name,
            description=description,
            image_url=data.get("image_url"),
            color=discord.Color.green()
        )

        info_fields = ["Origin", "Capacity", "Notes"]
        add_fields(embed, data, info_fields)

        await interaction.response.send_message(embed=embed, view=create_wiki_view(name))

    @weapon.autocomplete("name")
    async def weapon_autocomplete(self, interaction: discord.Interaction, current: str):
        return await autocomplete_category("Weapons", current)


async def setup(bot: commands.Bot):
    await bot.add_cog(WikiWeaponsCog(bot))
