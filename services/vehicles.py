import re
from services.utils import (
    get_wikitext_page,
    get_image_url,
    parse_quote,
)



def parse_vehicle_infobox(wikitext: str, vehicle_name: str) -> dict:
    """Parse Infobox Vehicle"""
    result = {}
    infobox_pattern = r'\{\{Infobox\s+Vehicle(.*?)\n\}\}'
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

        if key in ["speed", "handling", "mobility", "durability"]:
            match = re.search(r'%=(\d+)', value)
            if match:
                value = int(match.group(1))

        result[key] = value

    image_field = result.get("image1", "")
    if image_field:
        if "{{PAGENAME}}" in image_field:
            filename = image_field.replace("{{PAGENAME}}", vehicle_name).replace("[[", "").replace("]]", "")
        else:
            filename = image_field.replace("[[", "").replace("]]", "")
    else:
        filename = f"{vehicle_name}.png"

    if filename:
        result["image_url"] = get_image_url(filename)


    result["vehicle_skill"] = result.get("vehicle_skill", "")
    return result



def parse_vehicle_page(vehicle_name: str) -> dict:
    """Parse full vehicle info including infobox and quote"""
    wikitext = get_wikitext_page(vehicle_name)
    result = parse_vehicle_infobox(wikitext, vehicle_name)
    quote = parse_quote(wikitext)
    if quote:
        result["quote"] = quote
    return result
