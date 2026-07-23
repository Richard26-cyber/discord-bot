import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, date
import os
import database


CHANNEL_GEBURTSTAG = int(os.getenv("CHANNEL_GEBURTSTAG", 0))


class Geburtstage(commands.Cog):
    """Geburtstage speichern und täglich um 08:00 gratulieren."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.geburtstag_check.start()

    def cog_unload(self):
        self.geburtstag_check.cancel()

    # ── Slash-Command ──────────────────────────────────────────────────────────

    @app_commands.command(name="geburtstag", description="Deinen Geburtstag eintragen, z.B. 01.01.2000")
    @app_commands.describe(datum="Dein Geburtstag im Format TT.MM.JJJJ")
    async def geburtstag(self, interaction: discord.Interaction, datum: str):
        try:
            dt = datetime.strptime(datum.strip(), "%d.%m.%Y")
        except ValueError:
            await interaction.response.send_message(
                "❌ Falsches Format! Bitte so eingeben: `01.01.2000`", ephemeral=True
            )
            return

        if dt.year < 1900 or dt > datetime.now():
            await interaction.response.send_message(
                "❌ Das Datum sieht komisch aus. Bitte ein echtes Geburtsdatum eingeben.", ephemeral=True
            )
            return

        with database.get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO geburtstage (user_id, tag, monat, jahr) VALUES (?,?,?,?)",
                (interaction.user.id, dt.day, dt.month, dt.year)
            )

        await interaction.response.send_message(
            f"🎂 Dein Geburtstag wurde gespeichert: **{dt.strftime('%d. %B %Y')}** — ich vergess dich nicht! 😄",
            ephemeral=True
        )

    # ── Löschen ────────────────────────────────────────────────────────────────

    @app_commands.command(name="geburtstag-loeschen",
                          description="Löscht deinen gespeicherten Geburtstag wieder.")
    async def geburtstag_loeschen(self, interaction: discord.Interaction):
        """Wer Daten eintragen kann, muss sie auch wieder entfernen können.

        Ein Geburtsdatum ist ein personenbezogenes Datum — ohne diesen Befehl
        bliebe es für immer in der bot.db, auch nach dem Verlassen des Servers.

        Die user_id ist der Primärschlüssel der Tabelle, die Abfrage kann also
        gar nichts anderes treffen als den eigenen Eintrag — eine zusätzliche
        Besitzprüfung wie bei den Zitaten braucht es hier nicht. Bewusst auch
        ohne Admin-Sonderweg: fremde Geburtstage zu löschen ist keine
        Moderationsaufgabe.
        """
        with database.get_conn() as conn:
            geloescht = conn.execute(
                "DELETE FROM geburtstage WHERE user_id=?", (interaction.user.id,)
            ).rowcount

        if geloescht:
            text = ("🗑️ Dein Geburtstag wurde gelöscht. Ich gratuliere dir "
                    "nicht mehr automatisch — mit `/geburtstag` kannst du ihn "
                    "jederzeit neu eintragen.")
        else:
            text = "Du hast gar keinen Geburtstag eingetragen — es gibt nichts zu löschen."

        await interaction.response.send_message(text, ephemeral=True)

    # ── Täglicher Check um 08:00 ───────────────────────────────────────────────

    @tasks.loop(time=discord.utils.utcnow().replace(hour=6, minute=0, second=0, microsecond=0).timetz())
    async def geburtstag_check(self):
        """Läuft täglich um 08:00 Uhr (06:00 UTC = 08:00 DE-Sommerzeit)."""
        channel = self.bot.get_channel(CHANNEL_GEBURTSTAG)
        if not channel:
            return

        heute = date.today()
        with database.get_conn() as conn:
            # Jahr direkt mit abfragen — ein Query statt N+1
            rows = conn.execute(
                "SELECT user_id, jahr FROM geburtstage WHERE tag=? AND monat=?",
                (heute.day, heute.month)
            ).fetchall()

        for row in rows:
            member = channel.guild.get_member(row["user_id"])
            if not member:
                continue

            alter = heute.year - row["jahr"]
            await channel.send(
                f"🎉🎂 Herzlichen Glückwunsch zum Geburtstag, {member.mention}! "
                f"Du wirst heute **{alter} Jahre** alt! 🥳🎊\n"
                f"Wir wünschen dir einen wunderschönen Tag voller Freude und Liebe! ❤️"
            )

    @app_commands.command(name="bevorstehende-geburtstage", description="Zeigt alle bevorstehenden Geburtstage der Server-Mitglieder.")
    async def bevorstehende_geburtstage(self, interaction: discord.Interaction):
        await interaction.response.defer()

        heute = date.today()

        with database.get_conn() as conn:
            rows = conn.execute("SELECT user_id, tag, monat, jahr FROM geburtstage").fetchall()

        # Nur Mitglieder die noch auf dem Server sind
        eintraege = []
        for row in rows:
            member = interaction.guild.get_member(row["user_id"])
            if not member:
                continue

            tag, monat, jahr = row["tag"], row["monat"], row["jahr"]

            # Nächster Geburtstag berechnen
            try:
                naechster = date(heute.year, monat, tag)
            except ValueError:
                naechster = date(heute.year, monat, 28)  # 29. Feb Fallback

            if naechster < heute:
                naechster = naechster.replace(year=heute.year + 1)

            tage_bis = (naechster - heute).days
            alter_dann = naechster.year - jahr

            eintraege.append((tage_bis, naechster, member, tag, monat, alter_dann))

        if not eintraege:
            await interaction.followup.send("Noch keine Geburtstage eingetragen.", ephemeral=True)
            return

        eintraege.sort(key=lambda x: x[0])

        # Heute feiernde
        heute_lines = [
            f"🎂 {e[2].mention} — wird heute **{e[5]} Jahre** alt!"
            for e in eintraege if e[0] == 0
        ]

        # Nächste 30 Tage
        bald_lines = [
            f"`{e[1].strftime('%d.%m.')}` **{e[2].display_name}** — wird **{e[5]}** 🎈 (in {e[0]} Tagen)"
            for e in eintraege if 0 < e[0] <= 30
        ]

        # Rest dieses Jahr / nächstes Jahr
        spaeter_lines = [
            f"`{e[1].strftime('%d.%m.%Y')}` **{e[2].display_name}** — wird **{e[5]}**"
            for e in eintraege if e[0] > 30
        ]

        embed = discord.Embed(title="🎂 Geburtstags-Kalender", color=discord.Color.pink())

        if heute_lines:
            embed.add_field(name="🎉 Heute!", value="\n".join(heute_lines), inline=False)
        if bald_lines:
            embed.add_field(name="📅 Nächste 30 Tage", value="\n".join(bald_lines[:10]), inline=False)
        if spaeter_lines:
            embed.add_field(name="🗓️ Später", value="\n".join(spaeter_lines[:10]), inline=False)

        embed.set_footer(text=f"Nur Mitglieder die noch auf dem Server sind • {heute.strftime('%d.%m.%Y')}")
        await interaction.followup.send(embed=embed)

    @geburtstag_check.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Geburtstage(bot))
