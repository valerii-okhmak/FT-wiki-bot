import discord
from discord.ext import commands
from services.awakeners import get_category_members
from services.cache import save_cache
from discord import app_commands


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear_cache", description="Refresh category cache ")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_cache(self, interaction: discord.Interaction, category: str):        
        await interaction.response.defer()
        try:
            pages = get_category_members(category, use_cache=False)
            await interaction.followup.send(f"Cache for category '{category}' updated! ")
        except Exception as e:
            await interaction.followup.send(f"Error updating cache: {e}")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))