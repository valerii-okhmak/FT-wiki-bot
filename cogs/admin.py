import re
import discord
from discord import app_commands
from discord.ext import commands
from services.utils import get_category_members
from services.logger import log_error, log_info
from services.channel_config import load_config, save_config


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear_cache", description="Refresh category cache")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_cache(self, interaction: discord.Interaction, category: str):
        await interaction.response.defer(thinking=True, ephemeral=False)
        try:
            get_category_members(category, use_cache=False)
        except Exception as e:
            await interaction.response.send_message(f"Error updating cache: {e}", ephemeral=True)
            log_error(interaction.user.id, "clear_cache", e)
            return

        await interaction.followup.send(f"Cache for category '{category}' updated!", ephemeral=True)
        log_info(interaction.user.id, "clear_cache", f"Cache for category '{category}' successfully updated")

    @app_commands.command(name="setup-channels", description="Setup allowed channels for wiki commands")
    @app_commands.describe(
        channels="Mention channels (e.g. #general #wiki) or type ALL to allow everywhere"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_channels(self, interaction: discord.Interaction, channels: str):
        await interaction.response.defer(thinking=True, ephemeral=False)

        guild_id = str(interaction.guild.id)
        data = load_config()

        if channels.strip().upper() == "ALL":
            data[guild_id] = "ALL"
            msg = "Wiki commands are now allowed in **ALL channels**."
        else:
            mentioned_channels = re.findall(r"<#(\d+)>", channels)
            mentioned_channels = [int(cid) for cid in mentioned_channels]

            if not mentioned_channels:
                await interaction.response.send_message(
                    "Please mention at least one channel or use `ALL`.",
                    ephemeral=True
                )
                return

            data[guild_id] = mentioned_channels
            channels_list = ", ".join([f"<#{cid}>" for cid in mentioned_channels])
            msg = f"Wiki commands are now allowed only in: {channels_list}"

        save_config(data)

        await interaction.followup.send(msg, ephemeral=True)
        log_info(interaction.user.id, "setup-channels", f"Configured for guild {guild_id}: {data[guild_id]}")


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
