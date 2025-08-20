import re
from services.utils import (
    get_image_url,
    clean_wikitext,
)



def parse_infobox(wikitext: str) -> dict:
    """Parse the Infobox Awakener template"""
    result = {}
    
    infobox_pattern = r'\{\{Infobox\s+Awakener(.*?)\n\}\}'
    infobox_match = re.search(infobox_pattern, wikitext, re.DOTALL | re.IGNORECASE)
    
    if not infobox_match:
        return result
    
    infobox_content = infobox_match.group(1)
    
    for line in infobox_content.split('\n'):
        line = line.strip()
        if not line or not line.startswith('|'):
            continue
            
        line = line[1:].strip()
        
        if '=' not in line:
            continue
            
        key, _, value = line.partition('=')
        key = key.strip().lower()
        value = value.strip()
        
        if value:
            result[key] = value
    
    return result


def parse_profile(wikitext: str) -> str:
    """Parse the Profile section"""
    profile_pattern = r'===\s*Profile\s*===(.*?)(?=\n===|\n==|\[\[Category:|\Z)'
    profile_match = re.search(profile_pattern, wikitext, re.DOTALL | re.IGNORECASE)
    
    if profile_match:
        profile_text = profile_match.group(1).strip()
        return clean_wikitext(profile_text)
    
    return ""


def parse_awakeners(wikitext: str, awakener_name: str) -> dict:
    """Parse awakener information from wikitext"""
    result = {}
    
    infobox_data = parse_infobox(wikitext)
    
    alias = infobox_data.get('alias', '')
    if alias:
        result["awakener_name"] = f"{awakener_name} ({alias})"
    else:
        result["awakener_name"] = awakener_name
    
    field_mapping = {
        'role': 'Role',
        'skills': 'Skills',
        'voice_actor': 'Voice Actor',
        'age': 'Age',
        'birthday': 'Birthday',
        'origin': 'Origin',
        'height': 'Height',
        'hobbies': 'Hobbies'
    }
    
    for field, display_name in field_mapping.items():
        if field in infobox_data:
            value = clean_wikitext(infobox_data[field])
            if field == "skills":
                result[display_name] = [s.strip() for s in value.split(",") if s.strip()]
            else:
                result[display_name] = value

    
    profile = parse_profile(wikitext)
    
    if profile :
        result["profile"] = f"**Profile:**\n{profile}\n"
    elif profile:
        result["profile"] = profile

    image_field = infobox_data.get('image', '')
    if image_field:
        if '{{PAGENAME}}' in image_field:
            image_filename = image_field.replace('{{PAGENAME}}', awakener_name)
        else:
            image_filename = image_field
        
        image_url = get_image_url(image_filename)
        if image_url:
            result["image_url"] = image_url
    else:
        default_image = f"{awakener_name}.png"
        image_url = get_image_url(default_image)
        if image_url:
            result["image_url"] = image_url
    
    return result

