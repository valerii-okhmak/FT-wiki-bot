import json
import os

CONFIG_FILE = "channel_config.json"  

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:  
                return {}
            return json.loads(data)
    except (json.JSONDecodeError, OSError):
        return {}

def save_config(data: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_channel_allowed(guild_id: int, channel_id: int) -> bool:
    config = load_config()
    guild_id = str(guild_id)

    if not config or guild_id not in config:
        return True  

    allowed = config[guild_id]
    if allowed == "ALL":
        return True
    return channel_id in allowed
