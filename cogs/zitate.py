import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import date, datetime
import random
import os
import database


CHANNEL_ZITATE = int(os.getenv("CHANNEL_ZITATE", 0))

MOTIVATIONS_SPRUECHE = [
    "Jeder Mensch hat 2 Leben. Das zweite beginnt, wenn man versteht, dass man nur 1 hat. ⏳",
    "Das Leben wird vorwärts gelebt und rückwärts verstanden. 🔄",
    "Geld ändert nicht dich, sondern die Menschen um dich. 💰",
    "Niemand kennt deine Geschichte. Keiner weiß, was dich in deinem Leben geprägt hat und wieso du so bist, wie du bist. Also höre nicht auf die anderen. Das, was sie sagen, hat keinerlei Wert. Du bist wundervoll und stark. Geh raus, setz dein Lächeln wieder auf und zeig ihnen, wie stark du bist. 💪😊",
    "Ich besitze vielleicht die Reife, dir zu verzeihen, aber bestimmt nicht die Dummheit, dir nochmal zu vertrauen. 🛡️",
    "Bete nicht für ein leichtes Leben, bete um die Kraft, ein schwieriges Leben zu ertragen. – Bruce Lee 🥋",
    "Ändere deine Gedanken und du wirst deine Welt verändern. – Norman Vincent Peale 🌍",
    "Deine Wünsche werden dann in Erfüllung gehen, wenn du bereit für sie bist. 🌠",
    "Gesund. Lebendig. Glücklich. Frei. 🌿💚",
    "Sobald du deine Gedanken veränderst, verändert sich die Welt um dich. ✨",
    "Du wirst dann frei sein, wenn du verstehst, dass es keine richtige Art gibt, ein Leben zu leben. 🕊️",
    "Weinen bedeutet nicht, dass du schwach bist. Von Geburt an war es immer ein Zeichen dafür, dass du am Leben bist. 💧❤️",
    "Innerer Frieden beginnt in dem Moment, in dem du dich entscheidest, keiner anderen Person oder einem anderen Ergebnis zu erlauben, deine Emotionen zu kontrollieren. – Pema Chödrön 🧘",
    "Wiederhole zu dir selbst: Ich werde nichts überstürzen, mich nicht stressen oder mir Sorgen machen, wie die Dinge für mich laufen werden. 🌊",
    "Ich bin dankbar für Nächte, die zu Morgen wurden, Freunde, die zu Familie wurden, und Träume, die Wirklichkeit wurden. 🌅❤️",
    "Versuche nicht, etwas zu erzwingen. Lasse das Leben ein tiefes Loslassen sein. Gott öffnet jeden Tag Millionen von Blumen, ohne ihre Knospen zu zwingen. – Osho 🌸",
    "Wenn Menschen dich immer wieder verletzen, dann betrachte sie wie Sandpapier. Sie mögen dich ein bisschen kratzen und verletzen, aber am Ende wirst du poliert und sie sind nutzlos. – Chris Colfer 💎",
    "Du bist stark. Du bist schön. Du wirst geliebt. Du bist etwas Besonderes. Du bist nicht schwach. Du bist nicht defekt. Du bist nicht seltsam. Du bist kein hoffnungsloser Fall. 🌟💖",
    "Gib nicht auf. Eines Tages wirst du zurückblicken und froh sein, dass du es nicht getan hast. Deine Vergangenheit ist eine Lektion, keine lebenslange Haftstrafe. Vergib dir und konzentrier dich auf die Zukunft. – Mel Robbins 🔑",
    "Entschuldige dich nie dafür, dass du hohe Standards hast. Menschen, die wirklich in deinem Leben sein wollen, werden aufsteigen, um sie zu erfüllen. 👑",
    "Hör auf, dich für alles zu hassen, was du nicht bist. Fang an, dich für alles zu lieben, was du bist. 💕",
    "Eine der mutigsten Entscheidungen, die du jemals treffen wirst, ist, endlich loszulassen, was dein Herz und deine Seele verletzt. 🦋",
    # ── Klassiker & Zitate ────────────────────────────────────────────────────
    "Der Glaube an eine übernatürliche Quelle des Bösen ist unnötig. Der Mensch allein ist zu jeder möglichen Art des Bösen fähig. – Joseph Conrad 🌑",
    "Alles ist ein Rätsel, und der Schlüssel zu diesem Rätsel ist ein weiteres Rätsel. – Ralph Waldo Emerson 🔑",
    "Je weiter wir in die Vergangenheit schauen können, desto weiter können wir wahrscheinlich in die Zukunft schauen. – Winston Churchill 🔭",
    "Fantasie ist wichtiger als Wissen. Wissen ist begrenzt. Fantasie umfasst die ganze Welt. – Albert Einstein 🌌",
    "Tränen haben etwas Heiliges. Sie sind kein Zeichen von Schwäche, sondern von Stärke. Sie sind die Botschafter überwältigender Trauer und unaussprechlicher Liebe. – Washington Irving 💧❤️",
    "Nichts ist so gewöhnlich wie der Wunsch, bemerkenswert zu sein. – William Shakespeare ✨",
    "Unter Füchsen müssen wir den Fuchs spielen. – Thomas Fuller 🦊",
    "Vögel singen nach einem Sturm. Warum sollten sich die Menschen nicht einfach am Sonnenlicht erfreuen, das ihnen noch bleibt. – Rose Kennedy ☀️🐦",
    "Hat ein guter Mensch Schmerzen, sollten alle, die man gut nennen kann, mit ihm leiden. – Euripides 🤝",
    "Wenn man das Unmögliche ausgeschlossen hat, muss das, was übrig bleibt, wie unwahrscheinlich es auch wirken mag, die Wahrheit sein. – Sherlock Holmes 🔍",
    # ── Ergänzungen ───────────────────────────────────────────────────────────
    "Du bist nicht zu spät. Du bist genau rechtzeitig. ✨",
    "Jeder Schritt zählt — auch der kleinste bringt dich vorwärts. 🚀",
    "Du wächst, auch wenn du es nicht merkst. 🌱",
    "Du hast schon härtere Tage überlebt. Heute ist kein Problem. 🌟",
    "Fehler sind Beweise dafür, dass du es versucht hast. 🎯",
    "Kleine Fortschritte sind immer noch Fortschritte. 📈",
    "Probleme sind verkleidete Chancen. 🎭",
    "Der Unterschied zwischen Traum und Ziel ist ein Plan. 📋",
    "Heute ist ein neuer Versuch mit mehr Erfahrung. 🔄",
    "Dein Strahlen kann jemand anderen retten — also strahle. ✨🌙",
]


class Zitate(commands.Cog):
    """Tägliche Motivation + eigene Zitate erstellen/verwalten."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily_motivation.start()

    def cog_unload(self):
        self.daily_motivation.cancel()

    # ── Tägliche Motivation ────────────────────────────────────────────────────

    @tasks.loop(time=discord.utils.utcnow().replace(hour=7, minute=0, second=0, microsecond=0).timetz())
    async def daily_motivation(self):
        """Täglich um 09:00 Uhr (07:00 UTC) einen Motivationsspruch in #zitate."""
        channel = self.bot.get_channel(CHANNEL_ZITATE)
        if not channel:
            return

        spruch = random.choice(MOTIVATIONS_SPRUECHE)
        embed = discord.Embed(
            title="🌅 Gnadenlos Optimistisch — Motivation des Tages",
            description=f"*{spruch}*",
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"📅 {date.today().strftime('%d. %B %Y')}")
        await channel.send(embed=embed)

    @daily_motivation.before_loop
    async def before_motivation(self):
        await self.bot.wait_until_ready()

    # ── /motivation (manuell) ──────────────────────────────────────────────────

    @app_commands.command(name="motivation", description="Einen zufälligen Motivationsspruch anzeigen.")
    async def motivation(self, interaction: discord.Interaction):
        spruch = random.choice(MOTIVATIONS_SPRUECHE)
        embed = discord.Embed(
            description=f"✨ *{spruch}*",
            color=discord.Color.gold(),
        )
        await interaction.response.send_message(embed=embed)

    # ── /zitat-erstellen ───────────────────────────────────────────────────────

    @app_commands.checks.cooldown(1, 60, key=lambda i: i.user.id)
    @app_commands.command(name="zitat-erstellen", description="Ein eigenes Zitat in #zitate posten.")
    @app_commands.describe(text="Dein Zitat oder Lieblingsspruch")
    async def zitat_erstellen(self, interaction: discord.Interaction, text: str):
        if len(text) > 500:
            await interaction.response.send_message(
                "❌ Zitat zu lang (max. 500 Zeichen).", ephemeral=True
            )
            return

        heute = date.today().isoformat()
        with database.get_conn() as conn:
            conn.execute(
                "INSERT INTO zitate (user_id, username, text, datum) VALUES (?,?,?,?)",
                (interaction.user.id, interaction.user.display_name, text, heute)
            )

        channel = self.bot.get_channel(CHANNEL_ZITATE)
        embed = discord.Embed(
            description=f'*„{text}"*',
            color=discord.Color.purple(),
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_footer(text=f"📅 {datetime.now().strftime('%d.%m.%Y')}")

        if channel and channel.id != interaction.channel_id:
            await channel.send(embed=embed)
            await interaction.response.send_message(
                f"✅ Dein Zitat wurde in {channel.mention} gepostet!", ephemeral=True
            )
        else:
            await interaction.response.send_message(embed=embed)

    # ── /zitat-anzeigen ────────────────────────────────────────────────────────

    @app_commands.command(name="zitat-anzeigen", description="Ein zufälliges Zitat aus der Sammlung zeigen.")
    async def zitat_anzeigen(self, interaction: discord.Interaction):
        with database.get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM zitate ORDER BY RANDOM() LIMIT 1"
            ).fetchone()

        if not row:
            await interaction.response.send_message(
                "Noch keine Zitate vorhanden. Benutze `/zitat-erstellen`!", ephemeral=True
            )
            return

        embed = discord.Embed(
            description=f'*„{row["text"]}"*',
            color=discord.Color.purple(),
        )
        embed.set_author(name=row["username"])
        embed.set_footer(text=f"📅 {row['datum']}")
        await interaction.response.send_message(embed=embed)

    # ── /zitat-loeschen ────────────────────────────────────────────────────────

    @app_commands.command(name="zitat-loeschen", description="Eines deiner eigenen Zitate löschen.")
    @app_commands.describe(zitat_id="Die ID des Zitats (aus /zitat-liste)")
    async def zitat_loeschen(self, interaction: discord.Interaction, zitat_id: int):
        with database.get_conn() as conn:
            row = conn.execute(
                "SELECT user_id FROM zitate WHERE id=?", (zitat_id,)
            ).fetchone()

            if not row:
                await interaction.response.send_message("❌ Zitat nicht gefunden.", ephemeral=True)
                return

            # Nur eigene Zitate löschen — oder Admins dürfen alle löschen
            is_admin = interaction.user.guild_permissions.manage_messages
            if row["user_id"] != interaction.user.id and not is_admin:
                await interaction.response.send_message(
                    "❌ Du kannst nur deine eigenen Zitate löschen.", ephemeral=True
                )
                return

            conn.execute("DELETE FROM zitate WHERE id=?", (zitat_id,))

        await interaction.response.send_message(
            f"🗑️ Zitat #{zitat_id} wurde gelöscht.", ephemeral=True
        )

    # ── /zitat-liste (eigene) ──────────────────────────────────────────────────

    @app_commands.command(name="zitat-liste", description="Alle deine Zitate mit IDs anzeigen.")
    async def zitat_liste(self, interaction: discord.Interaction):
        with database.get_conn() as conn:
            rows = conn.execute(
                "SELECT id, text, datum FROM zitate WHERE user_id=? ORDER BY id DESC LIMIT 10",
                (interaction.user.id,)
            ).fetchall()

        if not rows:
            await interaction.response.send_message(
                "Du hast noch keine Zitate erstellt.", ephemeral=True
            )
            return

        lines = [f"`#{r['id']}` ({r['datum']}): {r['text'][:60]}..." for r in rows]
        embed = discord.Embed(
            title="📜 Deine Zitate",
            description="\n".join(lines),
            color=discord.Color.purple(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /alle-zitate ───────────────────────────────────────────────────────────

    @app_commands.command(name="alle-zitate", description="Alle Zitate des Servers anzeigen.")
    async def alle_zitate(self, interaction: discord.Interaction):
        await interaction.response.defer()

        with database.get_conn() as conn:
            rows = conn.execute(
                "SELECT username, text, datum FROM zitate ORDER BY id DESC"
            ).fetchall()

        # Einträge aufbauen — User-Zitate aus DB + Motivationssprüche
        eintraege = []
        for r in rows:
            eintraege.append(f'✏️ **{r["username"]}** `{r["datum"]}`\n*„{r["text"]}"*')

        if not eintraege:
            # Keine User-Zitate → Motivationssprüche zeigen
            for s in MOTIVATIONS_SPRUECHE:
                eintraege.append(f'💫 *„{s}"*')

        gesamt = len(eintraege)

        # In Seiten aufteilen (max ~3800 Zeichen pro Embed)
        seiten: list[str] = []
        aktuelle = ""
        for eintrag in eintraege:
            zeile = eintrag + "\n\n"
            if len(aktuelle) + len(zeile) > 3800:
                seiten.append(aktuelle.strip())
                aktuelle = zeile
            else:
                aktuelle += zeile
        if aktuelle.strip():
            seiten.append(aktuelle.strip())

        for i, seite in enumerate(seiten):
            embed = discord.Embed(
                title=f"📜 Alle Zitate ({gesamt} gesamt)" if i == 0 else None,
                description=seite,
                color=discord.Color.purple(),
            )
            embed.set_footer(text=f"Seite {i+1} von {len(seiten)}")
            await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Zitate(bot))
