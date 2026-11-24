# FT Wiki Bot

A Python Discord bot that brings the [Fate Trigger Wiki](https://fate-trigger.fandom.com/wiki/) into server conversations. Look up characters, weapons, vehicles, items, attachments and lore through slash commands, with autocomplete instead of having to remember exact page names.

Built by [Valerii Okhmak](https://github.com/valerii-okhmak) with `discord.py` and the MediaWiki API.

## What it does

- Fetches wiki pages and images, parses game-specific templates, and formats the results as Discord embeds.
- Shows relevant details such as character skills, weapon statistics and vehicle information, with links back to the original wiki page.
- Uses a local category cache for autocomplete. Suggestions match partial names and are limited to 25 results.
- Lets server administrators choose which channels can use wiki commands and refresh cached categories.
- Logs command activity and errors to a rotating log file.

## Commands

| Command | Lookup |
| --- | --- |
| `/wiki-awakeners name:` | Character profile and skills |
| `/wiki-weapons name:` | Weapon details, statistics and attachments |
| `/wiki-vehicles name:` | Vehicle details and statistics |
| `/wiki-items name:` | Item description and image |
| `/wiki-attachments name:` | Attachment description and image |
| `/wiki-lore name:` | Lore excerpt and link to the full page |

Start typing a name to see suggestions from the corresponding wiki category.

**Administrator commands**

- `/setup-channels channels:` — allow wiki commands in the mentioned channels, or enter `ALL` to allow them throughout the server.
- `/clear_cache category:` — reload a category from the wiki, for example `Weapons` or `Awakeners`.

Wiki commands are allowed in all server channels until an administrator configures a restriction.

## Run locally

Requires Python 3.10+ and a Discord application with a bot token.

```bash
git clone https://github.com/valerii-okhmak/FT-wiki-bot.git
cd FT-wiki-bot
python -m venv .venv
```

Activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install discord.py python-dotenv requests
```

Create a `.env` file in the project root:

```dotenv
DISCORD_TOKEN=your_bot_token
WIKI_API_URL=https://fate-trigger.fandom.com/api.php
WIKI_BASE_URL=https://fate-trigger.fandom.com/wiki/
```

`DISCORD_TOKEN` is required. Both wiki URLs have the defaults shown above in `config.py`.

Install the bot on a test server with the `bot` and `applications.commands` scopes. Allow it to view the intended channels, send messages and embed links, then start it from the project root:

```bash
python bot.py
```

The bot synchronizes its slash commands when it connects. They may take a little time to appear in Discord.

## Code structure

- `bot.py` loads the command modules and starts the bot.
- `cogs/` contains slash commands, channel checks and admin actions.
- `services/` handles API requests, wikitext parsing, embeds, autocomplete, caching and logging.
- `config.py` loads environment variables and wiki defaults.

Category names are cached in `category_cache.json`; server channel settings are stored in `channel_config.json`. The bot writes logs to `bot.log`, so the working directory must be writable.

The parsers are tailored to Fate Trigger wiki templates. Page content is fetched on demand; cached category lists are refreshed with `/clear_cache`.
