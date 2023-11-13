from discord.ext import commands


class ListenerCog(commands.Cog, name="listener"):
    def __init__(self, bot):
        self.bot = bot
        self.chatbot = self.bot.character
        self.channel_id = None

    @commands.Cog.listener()
    async def on_message(self, message):
        self.channel_id = message.channel.id

        # Ignore messages from the bot itself and messages starting with a dot or slash
        if message.author == self.bot.user or message.content.startswith((".", "/")):
            return
        # Ignore messages from channels not in the channel list
        if message.channel.id not in [
            int(channel_id) for channel_id in self.bot.channels
        ]:
            return

        self.chatbot.set_channel_attributes(self.channel_id, None)
        channel_memory = await self.chatbot.get_specific_memory()
        self.chatbot.set_channel_attributes(self.channel_id, channel_memory)

        self.chatbot.get_history()
        print(f"""
              -------------------------------
              HISTORY: [{self.chatbot.get_history()}]
              -------------------------------
              """)
        self.chatbot.get_prompt_template()

        print(f"{message.author.display_name}: {message.clean_content}")
        await self.chatbot.create_memory(message.author.display_name, message.clean_content, self.channel_id)

        response = await self.bot.get_cog("generate_text").respond(message)
        await self.chatbot.save_memory()
        if response != "" or response is not None:
            await message.channel.send(response)
        else:
            print("ERROR: response is empty")


async def setup(bot):
    await bot.add_cog(ListenerCog(bot))
