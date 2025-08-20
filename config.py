import os
from dotenv import load_dotenv

load_dotenv()

WIKI_BASE_URL = os.getenv("WIKI_BASE_URL", "https://fate-trigger.fandom.com/wiki/")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WIKI_API_URL = os.getenv("WIKI_API_URL", "https://fate-trigger.fandom.com/api.php")
