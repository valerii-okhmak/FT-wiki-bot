import re
from services.wiki_common import get_wikitext_page

def parse_weapons(wikitext: str) -> dict:
    """Parse Weapon infobox."""
    result = {}

    infobox_match = re.search(r"\{\{Infobox Gun(.*?)\}\}", wikitext, re.DOTALL)
    if not infobox_match:
        raise ValueError("Infobox Gun not found")
    infobox_text = infobox_match.group(1)

    fields = [ "image1", "manufacturer", "type", "ammo", "firepower", "stability", "range", "mobility", "link"]
    for field in fields:
        m = re.search(rf"\|\s*{field}\s*=\s*(.*)", infobox_text)
        if m:
            result[field] = m.group(1).strip()

    return result
