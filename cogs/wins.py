import discord
from discord import app_commands
from discord.ext import commands
from datetime import date
import database


class Wins(commands.Cog):
    """Mini-Erfolgstagebuch: /win und /meine-wins."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 30, key=lambda i: i.user.id)
    @app_commands.command(name="win", description="Einen Tageserfolg eintragen und feiern! 🏆")
    @app_commands.describe(text="Was hast du heute geschafft?")
    async def win(self, interaction: discord.Interaction, text: str):
        if len(text) > 300:
            await interaction.response.send_message(
                "❌ Text zu lang (max. 300 Zeichen).", ephemeral=True
            )
            return

        heute = date.today().isoformat()
        with database.get_conn() as conn:
            conn.execute(
                "INSERT INTO wins (user_id, text, datum) VALUES (?,?,?)",
                (interaction.user.id, text, heute)
            )

        embed = discord.Embed(
            title="🏆 WIN eingetragen!",
            description=f'*„{text}"*',
            color=discord.Color.green(),
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_footer(text=f"📅 {heute}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="meine-wins", description="Deine letzten Tageserfolge anzeigen.")
    async def meine_wins(self, interaction: discord.Interaction):
        with database.get_conn() as conn:
            rows = conn.execute(
                "SELECT text, datum FROM wins WHERE user_id=? ORDER BY id DESC LIMIT 10",
                (interaction.user.id,)
            ).fetchall()

        if not rows:
            await interaction.response.send_message(
                "Du hast noch keine Wins eingetragen. Starte mit `/win`! 💪",
                ephemeral=True
            )
            return

        lines = [f"**{r['datum']}** — {r['text']}" for r in rows]
        embed = discord.Embed(
            title=f"🏆 Die Wins von {interaction.user.display_name}",
            description="\n\n".join(lines),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Wins(bot))
