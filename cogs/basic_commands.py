from discord.ext import commands
from discord import app_commands
import discord

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Mostra a latência do bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Ping de cu eh rola, mas toma a minha latência: {round(self.bot.latency * 1000)}ms \n E nao enche me saco")

    @app_commands.command(name="ola", description="Um simples olá")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Ola eh meu cacete, nao enche meu saco nao tio!")

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))