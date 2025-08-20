import re
import re
from services.utils import (
    get_wikitext_page,
    get_image_url,
    parse_quote,
)

def parse_gun_infobox(wikitext: str, gun_name: str) -> dict:
    """Parse gun Infobox"""

    result = {}
    infobox_pattern = r'\{\{Infobox\s+Gun(.*?)\n\}\}'
    infobox_match = re.search(infobox_pattern, wikitext, re.DOTALL | re.IGNORECASE)
    if not infobox_match:
        return result

    content = infobox_match.group(1)
    for line in content.split('\n'):
        line = line.strip()
        if not line.startswith('|') or '=' not in line:
            continue
        key, _, value = line[1:].partition('=')
        key = key.strip().lower()
        value = value.strip()
        if not value:
            continue

        if key in ["firepower", "stability", "range", "mobility", "ammo"]:
            if key == "ammo":
                match = re.search(r'\]\]\s*(.*)', value)
                if match:
                    ammo_name = match.group(1).strip()
                    ammo_name = re.sub(r'\s*Ammo$', '', ammo_name, flags=re.IGNORECASE)
                    value = ammo_name
            else:
                match = re.search(r'text=(\d+)', value)
                if match:
                    value = int(match.group(1))

        result[key] = value

    image_field = result.get('image1', '')
    if '{{PAGENAME}}' in image_field:
        filename = image_field.replace('{{PAGENAME}}', gun_name).replace('[[', '').replace(']]', '')
    else:
        filename = image_field.replace('[[', '').replace(']]', '')

    if filename:
        result["image_url"] = get_image_url(filename)

    result["manufacturer"] = result.get("manufacturer", "")
    result["type"] = result.get("type", "")
    result["ammo"] = result.get("ammo", "")

    return result


def parse_attachments(attachments_wikitext: str, gun_name: str) -> list[str]:
    """Parse attachments for a specific gun"""
    pattern = r'\{\{#ifeq: \{\{\{type\}\}\} \| ' + re.escape(gun_name) + r' \|(.*?)\}\}'
    match = re.search(pattern, attachments_wikitext, re.DOTALL)
    if not match:
        return []
    section = match.group(1)
    attachment_names = re.findall(r'\[\[.*?\]\]<div>\[\[(.*?)\]\]', section)
    return attachment_names

def parse_gun_page(gun_name: str, attachments_wikitext: str) -> dict:
    """Parse full gun info including infobox, quote and attachments"""
    wikitext = get_wikitext_page(gun_name)
    result = parse_gun_infobox(wikitext, gun_name)
    quote = parse_quote(wikitext)
    if quote:
        result["quote"] = quote
    attachments = parse_attachments(attachments_wikitext, gun_name)
    if attachments:
        result["attachments"] = attachments
    return result
