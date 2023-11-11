import discord
from discord.ext.commands import Bot
import os
import asyncio
import json

# Initialize bot
intents = discord.Intents.all()
bot = Bot(command_prefix="/", intents=intents, help_command=None)

# Load configuration from config.json
with open("config.json", "r") as file:
    bot.config = json.load(file)


bot.token = bot.config["required"]["TOKEN"]
bot.endpoint = bot.config["required"]["ENDPOINT"].split("/api")[0]
bot.channels = [int(x) for x in bot.config["required"]["CHANNELS"].split(",")]
bot.mention = bot.config["extras"]["MENTION"].lower()


# Load cogs
async def load_cogs() -> None:
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
            except Exception as e:
                # log the error and continue with the next file
                error_info = f"Failed to load {extension}. {type(e).__name__}: {e}"
                print(error_info)


asyncio.run(load_cogs())
bot.run(bot.token)
