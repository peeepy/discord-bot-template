import json
import requests
from typing import Any, Dict, List, Optional
import os


class Chatbot:
    def __init__(self, char_details: str, bot, stopping_strings: Optional[List[str]] = None):
        self.bot = bot
        self.stopping_strings = stopping_strings
        self.char_details = str
        with open(char_details, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.char_name = data["char_name"]
            self.char_persona = data["char_persona"]

        self.persona = data
        self.input = str
        self.memory_dicts = []
        self.bot.name = self.char_name
        self.params = self.bot.config["extras"]["PARAMS"]

        self.channels = self.bot.channels
        self.channel_id = None
        self.channel_memory = None
        self.channel_specific_memory = {self.channel_id: []
                                        for channel in self.channels}

    def set_stopping_strings(self, stop: Optional[List[str]] = None):
        if self.stopping_strings and stop is not None:
            raise ValueError(
                "`stop` found in both the input and default params.")

        self.params["stopping_strings"] = self.stopping_strings or stop or []
        return self.params["stopping_strings"]

    def set_channel_attributes(self, channel_id, channel_memory):
        self.channel_id = channel_id
        self.channel_memory = channel_memory if channel_memory is not None else []

    async def create_memory(self, name: str, message_content: str, channel_id: int):
        if channel_id not in self.channels:
            raise ValueError(f"Channel ID {channel_id} not found in config.")

        if channel_id not in self.channel_specific_memory:
            self.channel_specific_memory[channel_id] = []

        # Check if the message already exists in the memory list for the user
        existing_memory = next(
            (mem for mem in self.channel_specific_memory[channel_id] if mem["name"] == name and mem["message"] == message_content), None)

        if existing_memory is None:
            # Append the new memory to the list associated with the channel_id
            self.channel_specific_memory[channel_id].append(
                {"name": name, "message": message_content})
        else:
            print("Message already exists in memories. It won't be added.")

        return self.channel_specific_memory

    async def get_specific_memory(self):
        # Check if channel_id is a valid channel and if memories exist for the channel_id
        if self.channel_id in self.channels and self.channel_id in self.channel_specific_memory:
            return self.channel_specific_memory[self.channel_id]
        else:
            # Handle the case when the channel_id is not found or has no associated memories
            return None

    async def save_memory(self):
        # Ensure the chatlogs directory exists
        if not os.path.exists("chatlogs"):
            os.makedirs("chatlogs")

        # Check if the log file already exists
        mode = "a" if os.path.exists(
            f"chatlogs/chnl_{self.channel_id}.log") else "w"

        with open(f"chatlogs/chnl_{self.channel_id}.log", mode, encoding="utf-8") as file:
            print(f"Appending to log file.")
            print(f"channel_specific_memory: {self.channel_specific_memory}")
            for self.channel_id, memories in self.channel_specific_memory.items():
                for memory in memories[-2:]:
                    formatted_message = f"{memory['name']}: {memory['message']}"
                    print(f"formatted message:{formatted_message}")
                    file.write(formatted_message + "\n")

    def get_history(self):
        stored_memory = [
            f"{message['name']}: {message['message']}" for message in self.channel_memory]
        memory = "\n".join(stored_memory[self.bot.lines_to_keep:])
        return memory

    def get_prompt_template(self):
        return f"""
        Write {self.char_name}'s next reply in a group chat with other people. Write 1 reply only.\n
        {self.char_persona}

        ### Instruction:
        {self.get_history()}
        {self.input}

        ### Response:
        {self.char_name}:"""

    def __str__(self):
        return f"The bot's name is {self.char_name}."

    def __call__(self, prompt: str, stop: Optional[List[str]] = None):
        self.input = prompt
        self.stop = stop
        self.set_stopping_strings(stop)

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            f"prompt": self.get_prompt_template(),
            "preset": self.params["preset"],
            "stopping_strings": self.params["stopping_strings"],
        }
        response = requests.post(
            self.bot.endpoint, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()["results"][0]["text"]
            return result
        else:
            print(f"ERROR: response: {response}")
            result = ""
