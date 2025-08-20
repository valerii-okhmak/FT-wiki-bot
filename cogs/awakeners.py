import discord
from discord import app_commands
from discord.ext import commands
from services.awakeners import get_wikitext_page, parse_awakeners, get_category_members

class WikiAwakenersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wiki-awakeners", description="Get info about an Awakener")
    @app_commands.describe(name="Select an Awakener")
    async def wiki_awakeners(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer() 
        
        try:
            wikitext = get_wikitext_page(name)
            data = parse_awakeners(wikitext, name)
        except Exception as e:
            await interaction.followup.send(f"**Error:** {e}", ephemeral=True)
            return

        embed = discord.Embed(
            title=data.get("awakener_name", name),
            color=discord.Color.blue()
        )

        if data.get("image_url"):
            embed.set_image(url=data["image_url"])



        profile = data.get("profile", "")
        if profile:
            embed.description = profile[:200] + f"...[more](https://fate-trigger.fandom.com/wiki/{name.replace(' ', '_')})"
            embed.description += "\n\n**Skills:** " + ", ".join(data["Skills"])


        info_fields = ["Role", "Voice Actor", "Age", "Birthday", "Origin", "Height", "Hobbies"]
        added_fields = 0
        for field in info_fields:
            if field in data and data[field] and added_fields < 6: 
                embed.add_field(name=field, value=data[field], inline=True)
                added_fields += 1


        embed.set_footer(text="Fate Trigger Wiki", 
                        icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtzFCeJ--WoEj9W11uVrtgIBH6BwhMfH4jBw&s")

        view = discord.ui.View(timeout=300)
        
        wiki_url = f"https://fate-trigger.fandom.com/wiki/{name.replace(' ', '_')}"
        view.add_item(discord.ui.Button(
            label="View more on Wiki", 
            url=wiki_url, 
            emoji='<:fandom_logo:1407326050501005403>',
            style=discord.ButtonStyle.link
        ))
        
        edit_url = f"https://fate-trigger.fandom.com/wiki/{name.replace(' ', '_')}?veaction=editsource"
        view.add_item(discord.ui.Button(
            label="Edit Page", 
            url=edit_url, 
            emoji="✏️",
            style=discord.ButtonStyle.link
        ))

        await interaction.followup.send(embed=embed, view=view)

    @wiki_awakeners.autocomplete("name")
    async def wiki_awakeners_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            pages = get_category_members("Awakeners", True)
            if current:
                filtered_pages = [p for p in pages if current.lower() in p.lower()]
                filtered_pages.sort(key=lambda x: (x.lower().find(current.lower()), len(x)))
            else:
                filtered_pages = sorted(pages)
            
            return [app_commands.Choice(name=p, value=p) for p in filtered_pages[:25]]
        except Exception:
            return []

async def setup(bot):
    await bot.add_cog(WikiAwakenersCog(bot))