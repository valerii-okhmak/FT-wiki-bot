import discord
from discord import app_commands
from discord.ext import commands
from services.awakeners import parse_awakeners
from services.utils import get_wikitext_page, PageNotFound
from services.discord_utils import create_embed, create_wiki_view, truncate_text, add_fields, autocomplete_category
from services.logger import log_warning, log_error
from services.channel_config import is_channel_allowed  


class WikiAwakenersCog(commands.Cog):
    """Commands for Awakeners"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="wiki-awakeners", description="Get info about an Awakener")
    @app_commands.describe(name="Select an Awakener")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=False)
    async def wiki_awakeners(self, interaction: discord.Interaction, name: str):
        if not is_channel_allowed(interaction.guild.id, interaction.channel.id):
            await interaction.response.send_message(
                "This command is not allowed in this channel.",
                ephemeral=True
            )
            return
        await interaction.response.defer(thinking=True, ephemeral=False)

        try:
            wikitext = get_wikitext_page(name)
            data = parse_awakeners(wikitext, name)
        except PageNotFound:
            await interaction.followup.send(f"Page '{name}' not found on the wiki.", ephemeral=True)
            log_warning(interaction.user.id, "wiki-awakeners", f"Page '{name}' not found")
            return
        except Exception as e:
            await interaction.followup.send("An unexpected error occurred. Please try again later.", ephemeral=True)
            log_error(interaction.user.id, "wiki-awakeners", e)
            return

        description = ""
        if profile := data.get("profile"):
            description = truncate_text(profile, page_name=name)
            if skills := data.get("Skills"):
                description += "\n\n**Skills:** " + ", ".join(skills)

        embed = create_embed(
            title=data.get("awakener_name", name),
            description=description,
            image_url=data.get("image_url"),
            color=discord.Color.dark_grey()
        )

        info_fields = ["Role", "Voice Actor", "Age", "Birthday", "Origin", "Height", "Hobbies"]
        add_fields(embed, data, info_fields)

        view = create_wiki_view(name)

        await interaction.followup.send(embed=embed, view=view)


    @wiki_awakeners.autocomplete("name")
    async def wiki_awakeners_autocomplete(self, interaction: discord.Interaction, current: str):
        return await autocomplete_category("Awakeners", current)


async def setup(bot: commands.Bot):
    await bot.add_cog(WikiAwakenersCog(bot))
