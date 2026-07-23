import discord
from discord import app_commands
from discord.ext import commands
import database


class Aktivitaet(commands.Cog):
    """Zählt Nachrichten pro User — OHNE Inhalt zu speichern (Datensparsamkeit)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Bots ignorieren, kein Inhalt gespeichert — nur +1 zählen
        if message.author.bot or not message.guild:
            return

        with database.get_conn() as conn:
            conn.execute(
                """INSERT INTO aktivitaet (user_id, guild_id, nachrichten)
                   VALUES (?, ?, 1)
                   ON CONFLICT(user_id, guild_id)
                   DO UPDATE SET nachrichten = nachrichten + 1""",
                (message.author.id, message.guild.id)
            )

    @app_commands.command(name="aktivitaet", description="Zeigt die Nachrichten-Rangliste des Servers.")
    async def aktivitaet(self, interaction: discord.Interaction):
        with database.get_conn() as conn:
            rows = conn.execute(
                """SELECT user_id, nachrichten FROM aktivitaet
                   WHERE guild_id = ?
                   ORDER BY nachrichten DESC LIMIT 10""",
                (interaction.guild_id,)
            ).fetchall()

        if not rows:
            await interaction.response.send_message("Noch keine Daten vorhanden.", ephemeral=True)
            return

        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, row in enumerate(rows):
            member = interaction.guild.get_member(row["user_id"])
            name = member.display_name if member else f"User {row['user_id']}"
            prefix = medals[i] if i < 3 else f"`{i+1}.`"
            lines.append(f"{prefix} **{name}** — {row['nachrichten']:,} Nachrichten")

        embed = discord.Embed(
            title="📊 Aktivitäts-Rangliste",
            description="\n".join(lines),
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Aktivitaet(bot))
