import discord
from discord import app_commands
from discord.ext import commands


EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


class Poll(commands.Cog):
    """Einfache Abstimmungen mit /poll."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 60, key=lambda i: i.user.id)
    @app_commands.command(name="poll", description="Eine Abstimmung erstellen.")
    @app_commands.describe(
        frage="Die Frage der Abstimmung",
        optionen="Antwortmöglichkeiten, getrennt mit | z.B.: Ja | Nein | Vielleicht"
    )
    async def poll(self, interaction: discord.Interaction, frage: str, optionen: str = "Ja | Nein"):
        choices = [o.strip() for o in optionen.split("|") if o.strip()]

        if len(choices) < 2:
            await interaction.response.send_message(
                "❌ Mindestens 2 Optionen angeben, getrennt mit `|`", ephemeral=True
            )
            return
        if len(choices) > 10:
            await interaction.response.send_message(
                "❌ Maximal 10 Optionen möglich.", ephemeral=True
            )
            return

        beschreibung = "\n".join(
            f"{EMOJIS[i]} {choice}" for i, choice in enumerate(choices)
        )

        embed = discord.Embed(
            title=f"📊 {frage}",
            description=beschreibung,
            color=discord.Color.blue(),
        )
        embed.set_footer(text=f"Abstimmung von {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        for i in range(len(choices)):
            await message.add_reaction(EMOJIS[i])


async def setup(bot: commands.Bot):
    await bot.add_cog(Poll(bot))
