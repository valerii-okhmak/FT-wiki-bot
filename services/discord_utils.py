import discord
from discord import app_commands
from services.utils import get_category_members
from config import WIKI_BASE_URL

FOOTER_ICON_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtzFCeJ--WoEj9W11uVrtgIBH6BwhMfH4jBw&s"
FOOTER_TEXT = "Fate Trigger Wiki"

def create_embed(
    title: str,
    description: str = "",
    image_url: str | None = None,
    color: discord.Color = discord.Color.dark_grey()
) -> discord.Embed:
    """Create a standardized Discord embed with optional image."""
    embed = discord.Embed(title=title, description=description, color=color)
    if image_url:
        embed.set_image(url=image_url)
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON_URL)
    return embed

def create_wiki_view(page_name: str) -> discord.ui.View:
    """Create a View with 'View more' and 'Edit Page' buttons."""
    view = discord.ui.View(timeout=300)
    wiki_url = f"{WIKI_BASE_URL}{page_name.replace(' ', '_')}"
    edit_url = f"{wiki_url}?veaction=editsource"

    view.add_item(discord.ui.Button(
        label="View more on Wiki",
        url=wiki_url,
        emoji='<:fandom_logo:1407326050501005403>',
        style=discord.ButtonStyle.link
    ))
    view.add_item(discord.ui.Button(
        label="Edit Page",
        url=edit_url,
        emoji="✏️",
        style=discord.ButtonStyle.link
    ))
    return view

def truncate_text(text: str, limit: int = 200, page_name: str = "") -> str:
    """Truncate long text and append a 'more' link to the wiki page."""
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...[more]({WIKI_BASE_URL}{page_name.replace(' ', '_')})"

def add_fields(embed: discord.Embed, data: dict, fields: list[str], max_fields: int = 6):
    """Add multiple fields to embed from data dictionary."""
    added = 0
    for field in fields:
        if field in data and data[field] and added < max_fields:
            embed.add_field(name=field, value=data[field], inline=True)
            added += 1


async def autocomplete_category(category: str, current: str) -> list[app_commands.Choice[str]]:
    """Generic autocomplete for a wiki category"""
    try:
        pages = get_category_members(category, use_cache=True)
        if current:
            filtered_pages = [p for p in pages if current.lower() in p.lower()]
            filtered_pages.sort(key=lambda x: (x.lower().find(current.lower()), len(x)))
        else:
            filtered_pages = sorted(pages)
        return [app_commands.Choice(name=p, value=p) for p in filtered_pages[:25]]
    except Exception:
        return []