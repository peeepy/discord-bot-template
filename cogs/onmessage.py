from discord.ext import commands


class ListenerCog(commands.Cog, name="listener"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from the bot itself and messages starting with a dot or slash
        if message.author == self.bot.user or message.content.startswith((".", "/")):
            return
        # Ignore messages from channels not in the channel list
        if message.channel.id not in [
            int(channel_id) for channel_id in self.bot.channels
        ]:
            return

        print(message.content)


async def setup(bot):
    await bot.add_cog(ListenerCog(bot))
