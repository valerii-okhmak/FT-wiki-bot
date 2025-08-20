import re
import requests
import config
from .cache import load_cache, save_cache
from services.logger import logger  

class WikiError(Exception):
    """Base class for Wiki-related errors"""
    pass

class PageNotFound(WikiError):
    """Raised when a wiki page is not found"""
    pass

def get_wikitext_page(title: str) -> str:
    """Get raw wikitext content for a page"""
    try:
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "rvprop": "content",
            "titles": title
        }
        resp = requests.get(config.WIKI_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        page = next(iter(pages.values()))
        if "missing" in page:
            raise PageNotFound(f"Page '{title}' not found on the wiki")
        return page["revisions"][0]["*"]
    except requests.RequestException as e:
        logger.error("Network error while fetching page '%s': %s", title, e)
        raise WikiError(f"Network error while fetching page '{title}'") from e

def get_image_url(filename: str) -> str | None:
    """Get the direct URL for an image file"""
    if not filename:
        return None
    try:
        filename = filename.replace("[[File:", "").replace("]]", "").strip().split("|")[0]
        params = {
            "action": "query",
            "format": "json",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url"
        }
        resp = requests.get(config.WIKI_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        page = next(iter(pages.values()))
        if "imageinfo" not in page:
            return None
        return page["imageinfo"][0]["url"]
    except requests.RequestException as e:
        logger.error("Network error while fetching image '%s': %s", filename, e)
        return None

def clean_wikitext(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    text = re.sub(r'\[\[Category:[^\]]+\]\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_quote(wikitext: str) -> str:
    match = re.search(r'\{\{Quote\|(.+?)\}\}', wikitext, re.DOTALL)
    if match:
        quote = match.group(1).strip()
        if '||' in quote:
            quote = quote.split('||')[0].strip()
        return quote
    return ""

def get_category_members(category: str, use_cache=True) -> list[str]:
    if use_cache:
        cached = load_cache(category)
        if cached:
            return cached
    try:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": "500",
            "format": "json"
        }
        resp = requests.get(config.WIKI_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        members = resp.json().get("query", {}).get("categorymembers", [])
        titles = [m["title"] for m in members]
        save_cache(category, titles)
        return titles
    except requests.RequestException as e:
        logger.error("Failed to get category '%s': %s", category, e)
        raise WikiError(f"Failed to get category '{category}'") from e
