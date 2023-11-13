import discord
from discord import app_commands
from discord.ext import commands

import json
import requests
from typing import Any, Dict, List, Optional
import os


class GenerateText(commands.Cog, name="generate_text"):
    def __init__(self, bot):
        self.bot = bot
        self.chatbot = self.bot.character
        self.channel_id = None

    @commands.command(name="respond")
    async def respond(self, message):
        message_content = message.clean_content
        self.channel_id = message.channel.id

        response = self.chatbot(message_content)

        print(f"{self.bot.name}: {response}")

        await self.chatbot.create_memory(self.bot.name, response, self.channel_id)

        return response

    @app_commands.command(name="memory", description="print log to channel")
    async def memory(self, interaction: discord.Interaction):
        file_path = f"chatlogs/chnl_{self.channel_id}.log"

        if not os.path.exists(file_path):
            print("No log found. Send a message to create one.")
            await interaction.response.send_message("No log found. Send a message to create one.", ephemeral=True)
            return

        with open(file_path, 'r', encoding="utf-8") as file:
            if os.path.getsize(file_path) == 0:
                print("Log is empty.")
                await interaction.response.send_message("Log is empty.", ephemeral=True)
                return
            else:
                content = file.read()
                print(content)
                await interaction.response.send_message(content[self.bot.lines_to_keep:], ephemeral=True)

    @app_commands.command(name="clear_memory", description="clears memory log")
    async def clear_memory(self, interaction: discord.Interaction):
        file_path = f"chatlogs/chnl_{self.channel_id}.log"

        if not os.path.exists(file_path):
            print("No log found.")
            await interaction.response.send_message("No log found.", ephemeral=True)
            return

        with open(file_path, 'w', encoding="utf-8") as file:
            file.close()
            print("Memory log cleared.")
            await interaction.response.send_message("Memory log cleared.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(GenerateText(bot))
