import discord
from discord import app_commands
from discord.ext import commands

import json
import requests
from typing import Any, Dict, List, Optional
import os

from helpers.chatbot import Chatbot


class GenerateText(commands.Cog, name="generate_text"):
    def __init__(self, bot):
        self.bot = bot
        self.chatbot = Chatbot("Beep.json", bot, ["\n", "<|im_end|>"])

    @commands.command(name="respond")
    async def respond(self, message):
        message_content = message.clean_content

        self.chatbot.create_memory(message.author.display_name,
                                   message_content)

        response = self.chatbot(message_content)
        print(f"{message.author.display_name}: {message_content}")
        print(f"{self.bot.name}: {response}")

        self.chatbot.create_memory(self.bot.name, response)

        self.chatbot.save_memory()
        return response

    @app_commands.command(name="memory", description="print log to channel")
    async def memory(self, interaction: discord.Interaction):
        print("memory command called")
        print(self.chatbot.history)
        await interaction.response.send_message(self.chatbot.history, ephemeral=True)


async def setup(bot):
    await bot.add_cog(GenerateText(bot))
