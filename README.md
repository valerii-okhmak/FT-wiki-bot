# Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd FT-wiki-bot
```
2. Create and activate a virtual environment:
```bash
python -m venv .venv
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Create a .env file in the root directory with the following variables:
```bash
WIKI_API_URL=
DISCORD_BOT_TOKEN=
```


# Commands

All commands are available as Slash Commands (/command).

Awakeners
- /wiki-awakeners name:<Awakener Name> — Get information about an Awakener.
  Autocomplete is available for the name.

Items
- /wiki-items name:<Item Name> — Get description and image of an item.

Attachments
- /wiki-attachments name:<Attachment Name> — Get description and image of an attachment.

Lore
- /wiki-lore name:<Lore Name> — Get description of a lore entry.

Vehicles
- /wiki-vehicles name:<Vehicle Name> — Get information about a vehicle, including stats.

Weapons
- /wiki-weapons name:<Weapon Name> — Get information about a weapon, including stats and attachments.

Admin
- /clear_cache category:<Category Name> — Refresh cache for a category (administrator only).


