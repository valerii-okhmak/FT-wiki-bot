import discord
from discord import app_commands
from discord.ext import commands
from services.weapons import parse_gun_page
from services.utils import (
    get_wikitext_page,
    get_category_members
)

class WikiWeapons(commands.Cog):
    """Commands for Fate-Trigger weapons"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.attachments_wikitext = None

    async def ensure_attachments_loaded(self):
        """Load the Attachments template once and cache it"""
        if not self.attachments_wikitext:
            loop = self.bot.loop
            self.attachments_wikitext = await loop.run_in_executor(
                None, lambda: get_wikitext_page("Template:Attachments")
            )

    @app_commands.command(name="wiki-weapons", description="Get info about a Weapon")
    @app_commands.describe(name="Select a Weapon")
    async def weapon(self, interaction: discord.Interaction, *, name: str):
        await interaction.response.defer()
        await self.ensure_attachments_loaded()

        try:
            data = parse_gun_page(name, self.attachments_wikitext)
        except Exception as e:
            await interaction.followup.send(f"**Error:** {e}", ephemeral=True)
            return

        embed = discord.Embed(title=name, color=discord.Color.green())
        if img := data.get("image_url"):
            embed.set_image(url=img)

        desc_parts = []

        if manufacturer := data.get("manufacturer"):
            desc_parts.append(f"**Manufacturer:** {manufacturer}")
        if type_ := data.get("type"):
            desc_parts.append(f"**Type:** {type_}")
        if ammo := data.get("ammo"):
            desc_parts.append(f"**Ammo:** {ammo}")

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

        embed.description = "\n".join(desc_parts)
        embed.set_footer(
            text="Fate Trigger Wiki",
            icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtzFCeJ--WoEj9W11uVrtgIBH6BwhMfH4jBw&s"
        )

        view = discord.ui.View(timeout=300)
        wiki_url = f"https://fate-trigger.fandom.com/wiki/{name.replace(' ', '_')}"
        edit_url = f"{wiki_url}?veaction=editsource"

        view.add_item(discord.ui.Button(
            label="View more on Wiki",
            url=wiki_url,
            style=discord.ButtonStyle.link,
            emoji='<:fandom_logo:1407326050501005403>'
        ))
        view.add_item(discord.ui.Button(
            label="Edit Page",
            url=edit_url,
            style=discord.ButtonStyle.link,
            emoji="✏️"
        ))

        await interaction.followup.send(embed=embed, view=view)

    @weapon.autocomplete("name")
    async def weapon_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            pages = get_category_members("Weapons", use_cache=True)
            if current:
                filtered_pages = [p for p in pages if current.lower() in p.lower()]
                filtered_pages.sort(key=lambda x: (x.lower().find(current.lower()), len(x)))
            else:
                filtered_pages = sorted(pages)
            return [app_commands.Choice(name=p, value=p) for p in filtered_pages[:25]]
        except Exception:
            return []


async def setup(bot: commands.Bot):
    await bot.add_cog(WikiWeapons(bot))
