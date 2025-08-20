import discord
from discord import app_commands
from discord.ext import commands
from services.vehicles import parse_vehicle_page
from services.discord_utils import (
    create_embed,
    create_wiki_view,
    add_fields,
    autocomplete_category
)


class WikiVehiclesCog(commands.Cog):
    """Commands for Fate-Trigger Vehicles"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="wiki-vehicles", description="Get info about a Vehicle")
    @app_commands.describe(name="Select a vehicle")
    async def vehicles(self, interaction: discord.Interaction, *, name: str):
        await interaction.response.defer()

        try:
            data = parse_vehicle_page(name)
        except Exception as e:
            await interaction.followup.send(f"**Error:** {e}", ephemeral=True)
            return

        desc_parts = []
        for key in ["manufacturer", "type"]:
            if val := data.get(key):
                desc_parts.append(f"**{key.capitalize()}:** {val}")

        stats_map = {
            "speed": "Speed",
            "handling": "Handling",
            "mobility": "Mobility",
            "durability": "Durability"
        }
        for stat, label in stats_map.items():
            if val := data.get(stat):
                desc_parts.append(f"**{label}:** {val}")

        if quote := data.get("quote"):
            desc_parts.append(f"\n*{quote}*")

        description = "\n".join(desc_parts)

        embed = create_embed(
            title=name,
            description=description,
            image_url=data.get("image_url"),
            color=discord.Color.blue()
        )

        info_fields = ["Origin", "Capacity", "Crew"]
        add_fields(embed, data, info_fields)

        view = create_wiki_view(name)

        await interaction.followup.send(embed=embed, view=view)

    @vehicles.autocomplete("name")
    async def vehicles_autocomplete(self, interaction: discord.Interaction, current: str):
        return await autocomplete_category("Vehicles", current)


async def setup(bot: commands.Bot):
    await bot.add_cog(WikiVehiclesCog(bot))
