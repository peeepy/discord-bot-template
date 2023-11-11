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

    def set_stopping_strings(self, stop: Optional[List[str]] = None):
        if self.stopping_strings and stop is not None:
            raise ValueError(
                "`stop` found in both the input and default params.")

        self.params["stopping_strings"] = self.stopping_strings or stop or []
        return self.params["stopping_strings"]

    def create_memory(self, name: str, message_content: str):
        self.memory_dicts.append({"name": name, "message": message_content})
        # print(f"Memory: {self.memory_dicts}")

    def save_memory(self):
        # Ensure the chatlogs directory exists
        if not os.path.exists("chatlogs"):
            os.makedirs("chatlogs")

        # Check if the log file already exists
        mode = "a" if os.path.exists(f"chatlogs/{self.char_name}.log") else "w"

        with open(f"chatlogs/{self.char_name}.log", mode, encoding="utf-8") as file:
            print(f"Appending to log file.")
            for memory in self.memory_dicts[-2:]:
                formatted_message = f"{memory['name']}: {memory['message']}"
                # print(f"formatted message:{formatted_message}")
                file.write(formatted_message + "\n")

    @property
    def history(self):
        stored_memory = []
        with open(f"chatlogs/{self.char_name}.log", "r", encoding="utf-8") as f:
            for line in f:
                line.rsplit("\n")
                stored_memory.append(line)
        memory = "".join(stored_memory[self.bot.lines_to_keep:])

        return memory

    @property
    def prompt_template(self):
        return f"""
        Write {self.char_name}'s next reply in a group chat with other people. Write 1 reply only.\n
        {self.char_persona}

        ### Instruction:
        {self.history}
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
            f"prompt": self.prompt_template,
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
