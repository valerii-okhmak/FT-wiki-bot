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
    filename = filename.replace("[[File:", "").replace("]]", "").strip().split("|")[0]
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
    if "imageinfo" not in page:
        return None
    return page["imageinfo"][0]["url"]


def clean_wikitext(text: str) -> str:
    """Clean wikitext formatting"""
    if not text:
        return ""
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    text = re.sub(r'\[\[Category:[^\]]+\]\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_quote(wikitext: str) -> str:
    """Parse Quote template"""
    match = re.search(r'\{\{Quote\|(.+?)\}\}', wikitext, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def get_category_members(category: str, use_cache=True) -> list[str]:
    """Get all pages in a category with optional caching"""
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
