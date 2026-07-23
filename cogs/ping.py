import discord
from discord import app_commands
from discord.ext import commands
import time


class Ping(commands.Cog):
    """Einfacher Test-Command: /ping"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Testet ob der Bot antwortet und zeigt die Latenz.")
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(
            f"🏓 Pong! Latenz: **{latency_ms} ms**"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
