import discord
from discord.ext import commands
from services.utils import get_category_members
from discord import app_commands
from services.logger import log_error, log_info  

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear_cache", description="Refresh category cache")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_cache(self, interaction: discord.Interaction, category: str):
        try:
            pages = get_category_members(category, use_cache=False)
        except Exception as e:
            await interaction.response.send_message(f"Error updating cache: {e}", ephemeral=True)
            log_error(interaction.user.id, "clear_cache", e)
            return

        await interaction.response.send_message(f"Cache for category '{category}' updated!")
        log_info(interaction.user.id, "clear_cache", f"Cache for category '{category}' successfully updated")


async def setup(bot):
    await bot.add_cog(AdminCog(bot))