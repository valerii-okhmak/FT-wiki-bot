import discord
from discord import app_commands
from discord.ext import commands

from services.vehicles import parse_vehicle_page
from services.utils import PageNotFound
from services.discord_utils import create_embed, create_wiki_view, add_fields, autocomplete_category
from services.logger import log_error, log_warning
from services.channel_config import is_channel_allowed  


class WikiVehiclesCog(commands.Cog):
    """Commands for Vehicles"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="wiki-vehicles", description="Get info about a Vehicle")
    @app_commands.describe(name="Select a vehicle")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=False)
    async def vehicles(self, interaction: discord.Interaction, *, name: str):
        if not is_channel_allowed(interaction.guild.id, interaction.channel.id):
            await interaction.response.send_message(
                "This command is not allowed in this channel.",
                ephemeral=True
            )
            return
        await interaction.response.defer(thinking=True)

        try:
            data = parse_vehicle_page(name)
        except PageNotFound:
            await interaction.followup.send(
                f"Page '{name}' not found on the wiki.")
            log_warning(interaction.user.id, "wiki-vehicles", f"Page '{name}' not found")
            return
        except Exception as e:
            await interaction.followup.send(
                "An unexpected error occurred.", ephemeral=True
            )
            log_error(interaction.user.id, "wiki-vehicles", e)
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
            color=discord.Color.dark_grey()
        )

        info_fields = ["Origin", "Capacity", "Crew"]
        add_fields(embed, data, info_fields)

        await interaction.followup.send(embed=embed, view=create_wiki_view(name))

    @vehicles.autocomplete("name")
    async def vehicles_autocomplete(self, interaction: discord.Interaction, current: str):
        return await autocomplete_category("Vehicles", current)


async def setup(bot: commands.Bot):
    await bot.add_cog(WikiVehiclesCog(bot))
