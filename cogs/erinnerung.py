import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import re


def parse_zeit(text: str) -> int | None:
    """Wandelt '2h', '30m', '1d', '90s' in Sekunden um."""
    einheiten = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    match = re.fullmatch(r"(\d+)([smhd])", text.strip().lower())
    if not match:
        return None
    wert, einheit = int(match.group(1)), match.group(2)
    return wert * einheiten[einheit]


class Erinnerung(commands.Cog):
    """Persönliche Erinnerungen per DM."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="erinnere-mich", description="Erinnert dich per DM nach einer bestimmten Zeit.")
    @app_commands.describe(
        zeit='Wie lange? z.B. "30m", "2h", "1d", "90s"',
        nachricht="Woran soll ich dich erinnern?"
    )
    async def erinnere_mich(self, interaction: discord.Interaction, zeit: str, nachricht: str):
        sekunden = parse_zeit(zeit)

        if sekunden is None:
            await interaction.response.send_message(
                "❌ Ungültiges Format! Beispiele: `30m`, `2h`, `1d`, `90s`", ephemeral=True
            )
            return

        if sekunden < 10:
            await interaction.response.send_message("❌ Mindestens 10 Sekunden.", ephemeral=True)
            return

        if sekunden > 86400 * 30:
            await interaction.response.send_message("❌ Maximal 30 Tage.", ephemeral=True)
            return

        if len(nachricht) > 200:
            await interaction.response.send_message("❌ Nachricht zu lang (max. 200 Zeichen).", ephemeral=True)
            return

        # Lesbare Zeit für Bestätigung
        if sekunden < 60:
            lesbar = f"{sekunden} Sekunden"
        elif sekunden < 3600:
            lesbar = f"{sekunden // 60} Minuten"
        elif sekunden < 86400:
            lesbar = f"{sekunden // 3600} Stunden"
        else:
            lesbar = f"{sekunden // 86400} Tage"

        await interaction.response.send_message(
            f"⏰ Alles klar! Ich erinnere dich in **{lesbar}** daran:\n*{nachricht}*",
            ephemeral=True
        )

        # Im Hintergrund warten und dann DM senden
        async def sende_erinnerung():
            await asyncio.sleep(sekunden)
            try:
                embed = discord.Embed(
                    title="⏰ Erinnerung!",
                    description=nachricht,
                    color=discord.Color.yellow(),
                )
                embed.set_footer(text=f"Du hast diese Erinnerung in #{interaction.channel.name} gesetzt.")
                await interaction.user.send(embed=embed)
            except discord.Forbidden:
                # User hat DMs deaktiviert — in den Channel schreiben
                try:
                    await interaction.channel.send(
                        f"⏰ {interaction.user.mention} — deine Erinnerung: **{nachricht}**",
                        # nachricht kommt vom Nutzer: nur ihn selbst anpingen
                        allowed_mentions=discord.AllowedMentions(
                            everyone=False, roles=False,
                            users=[interaction.user],
                        ),
                    )
                except Exception:
                    pass

        self.bot.loop.create_task(sende_erinnerung())


async def setup(bot: commands.Bot):
    await bot.add_cog(Erinnerung(bot))
