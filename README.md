# Installation

1. Clone the repository:
```bash
git clone <repo-url>
```
2. Create and activate a virtual environment:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate
```
3. Install dependencies:
```bash
discord.py>=2.4.0
dotenv>=1.0.0
requests>=2.30.0

```
4. Create a .env file in the root directory with the following variables:
```bash
WIKI_API_URL=
DISCORD_BOT_TOKEN=
```

# Commands
## Adminc ONLY:
- /setup-channels <channel mentions or ALL> - Setup allowed channels for wiki commands
- /clear_cache category:<Category Name> — Refresh cache for a category

## All:
- /wiki-awakeners name:<Awakener Name> — Get information about an Awakener.
- /wiki-items name:<Item Name> — Get description and image of an item.
- /wiki-attachments name:<Attachment Name> — Get description and image of an attachment.
- /wiki-lore name:<Lore Name> — Get description of a lore entry.
- /wiki-vehicles name:<Vehicle Name> — Get information about a vehicle, including stats.
- /wiki-weapons name:<Weapon Name> — Get information about a weapon, including stats and attachments.

