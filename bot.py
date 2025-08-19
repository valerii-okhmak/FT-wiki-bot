import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  
    print(f"{bot.user} ready")

async def main():
    async with bot:
        await bot.load_extension("cogs.wiki_awakeners")
        await bot.load_extension("cogs.wiki_weapons")
        await bot.load_extension("cogs.admin")

        await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
