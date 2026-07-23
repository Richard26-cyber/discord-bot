import discord
from discord import app_commands
from discord.ext import commands


BEFEHLE = [
    ("🏓 Allgemein", [
        ("/ping",                    "Testet ob der Bot antwortet + Latenz"),
        ("/info",                    "Diese Übersicht aller Befehle"),
        ("/aktivitaet",              "Nachrichten-Rangliste des Servers"),
    ]),
    ("🎂 Geburtstage", [
        ("/geburtstag [TT.MM.JJJJ]",          "Deinen Geburtstag eintragen"),
        ("/bevorstehende-geburtstage",         "Alle bevorstehenden Geburtstage anzeigen"),
    ]),
    ("📜 Zitate & Motivation", [
        ("/motivation",              "Einen zufälligen Motivationsspruch anzeigen"),
        ("/zitat-erstellen [text]",  "Ein eigenes Zitat in #zitate posten"),
        ("/zitat-anzeigen",          "Ein zufälliges Zitat aus der Sammlung"),
        ("/zitat-liste",             "Deine eigenen Zitate mit IDs anzeigen"),
        ("/zitat-loeschen [id]",     "Eines deiner Zitate löschen"),
        ("/alle-zitate",             "Alle Zitate des Servers auf einmal anzeigen"),
    ]),
    ("🏆 Erfolge", [
        ("/win [text]",              "Einen Tageserfolg eintragen"),
        ("/meine-wins",              "Deine letzten Erfolge anzeigen"),
    ]),
    ("📻 Radio", [
        ("/radio",                   "Radio-Menü öffnen — Sender auswählen"),
        ("/radio-stop",              "Radio stoppen & Sprachkanal verlassen"),
    ]),
    ("🎭 Abstimmung & Quiz", [
        ("/poll [frage] [optionen]", "Abstimmung erstellen (Optionen mit | trennen)"),
        ("/quiz",                    "Sofort eine Quizfrage starten"),
    ]),
    ("⏰ Erinnerungen", [
        ("/erinnere-mich [zeit] [nachricht]", "Erinnerung per DM (z.B. 2h, 30m, 1d)"),
    ]),
    ("🐦 Vögel", [
        ("/vogel",                   "Einen zufälligen Vogel des Tages anzeigen"),
    ]),
    ("🎭 Rollen", [
        ("/rollen-setup",            "[Admin] Rollen-Auswahl-Menü in #rollen posten"),
    ]),
    ("✍️ Name", [
        ("/name [text]",             "Nickname in cooler Schrift ändern (𝓕𝓪𝓷𝓬𝔂)"),
    ]),
]


class Info(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="info", description="Alle Befehle des Bots auf einen Blick.")
    async def info(self, interaction: discord.Interaction):
        embeds = []

        # Haupt-Embed
        haupt = discord.Embed(
            title="📖 Alle Befehle",
            description="Hier findest du alle verfügbaren Slash-Commands!\nTägliche Automationen laufen im Hintergrund.",
            color=discord.Color.blurple(),
        )
        haupt.set_footer(text="Tipp: Alle Commands mit / beginnen — Discord zeigt Vorschläge!")

        for kategorie, befehle in BEFEHLE:
            wert = "\n".join(f"`{cmd}` — {beschr}" for cmd, beschr in befehle)
            haupt.add_field(name=kategorie, value=wert, inline=False)

        # Automatik-Embed
        auto = discord.Embed(
            title="🤖 Tägliche Automatiken",
            color=discord.Color.green(),
        )
        auto.add_field(
            name="Was der Bot automatisch macht:",
            value=(
                "🎂 **08:00** — Geburtstagskinder werden in #level-geburtstag beglückwünscht\n"
                "💫 **09:00** — Täglicher Motivationsspruch in #zitate\n"
                "🧠 **11:00** — Tagesquiz in #bot-test\n"
                "🐦 **10:00** — Vogel des Tages in #bot-test\n"
                "🚨 **Immer** — Anti-Spam: >5 Nachrichten in 8 Sek. → 5 Min. Timeout\n"
                "👋 **Immer** — Neue Mitglieder werden in #willkommenshalle begrüßt\n"
                "✅ **Immer** — Regelwerk-Reaktion gibt Mensch + Kategorierollen"
            ),
            inline=False,
        )

        await interaction.response.send_message(embeds=[haupt, auto], ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
