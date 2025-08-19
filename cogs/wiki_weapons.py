import discord
from discord import app_commands
from discord.ext import commands
from services.wiki_common import get_category_members, get_wikitext_page
from services.wiki_weapons import parse_weapons

class WikiWeaponsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wiki-weapons", description="Get info about a Weapon")
    @app_commands.describe(name="Select a Weapon")
    async def wiki_weapons(self, interaction: discord.Interaction, name: str):
        try:
            wikitext = get_wikitext_page(name)
            data = parse_weapons(wikitext)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            return

        embed = discord.Embed(
            title=data.get("title1", name),
            description=f"Type: {data.get('type', 'Unknown')}\nManufacturer: {data.get('manufacturer', 'Unknown')}\nAmmo: {data.get('ammo', 'Unknown')}",
            color=discord.Color.green()
        )

        image_file = data.get("image1")
        if image_file:
            image_file = image_file.replace("[[", "").replace("]]", "").replace(" ", "_")
            embed.set_thumbnail(url=f"https://static.wikia.nocookie.net/fate-trigger/images/{image_file}")

        embed.add_field(name="Firepower", value=data.get("firepower", "Unknown"), inline=True)
        embed.add_field(name="Stability", value=data.get("stability", "Unknown"), inline=True)
        embed.add_field(name="Range", value=data.get("range", "Unknown"), inline=True)
        embed.add_field(name="Mobility", value=data.get("mobility", "Unknown"), inline=True)

        await interaction.response.send_message(embed=embed)

    @wiki_weapons.autocomplete("name")
    async def wiki_weapons_autocomplete(self, interaction: discord.Interaction, current: str):
        pages = get_category_members("Weapons")
        return [app_commands.Choice(name=p, value=p) for p in pages if current.lower() in p.lower()][:25]


async def setup(bot):
    await bot.add_cog(WikiWeaponsCog(bot))
