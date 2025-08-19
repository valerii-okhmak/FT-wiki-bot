import re
import requests
import config
from .cache import load_cache, save_cache

def get_wikitext_page(title: str) -> str:
    """Get raw wikitext content for a page"""
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "rvprop": "content",
        "titles": title
    }
    resp = requests.get(config.WIKI_API_URL, params=params)
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page:
        raise ValueError(f"Page '{title}' not found on the wiki")
    return page["revisions"][0]["*"]

def get_image_url(filename: str) -> str | None:
    """Get the direct URL for an image file"""
    if not filename:
        return None
    
    filename = filename.replace("[[File:", "").replace("]]", "").strip()
    filename = filename.split("|")[0].strip()
    
    if "{{PAGENAME}}" in filename:
        return None 
    
    params = {
        "action": "query",
        "format": "json",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url"
    }
    resp = requests.get(config.WIKI_API_URL, params=params)
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page or "imageinfo" not in page:
        return None
    return page.get("imageinfo", [{}])[0].get("url")

def clean_wikitext(text: str) -> str:
    """Clean wikitext formatting"""
    if not text:
        return ""
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[\[File:[^\]]+\]\]', '', text)
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    text = re.sub(r'\[\[Category:[^\]]+\]\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

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


def get_category_members(category: str, use_cache=True) -> list[str]:
    if use_cache:
        cached = load_cache(category)
        if cached:
            return cached

    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": "500",
        "format": "json"
    }
    resp = requests.get(config.WIKI_API_URL, params=params)
    resp.raise_for_status()
    members = resp.json().get("query", {}).get("categorymembers", [])
    titles = [m["title"] for m in members]

    save_cache(category, titles)
    return titles