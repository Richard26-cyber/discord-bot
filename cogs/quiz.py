import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import date
import random
import uuid
import os

CHANNEL_BOT_TEST = int(os.getenv("CHANNEL_BOT_TEST", 0))

FRAGEN = [
    {"frage": "Welches Tier ist das schnellste Landtier der Welt?",        "antworten": ["Gepard", "Löwe", "Pferd", "Adler"],               "richtig": 0},
    {"frage": "Wie viele Planeten hat unser Sonnensystem?",                 "antworten": ["7", "8", "9", "10"],                              "richtig": 1},
    {"frage": "Was ist die Hauptstadt von Australien?",                     "antworten": ["Sydney", "Melbourne", "Canberra", "Brisbane"],    "richtig": 2},
    {"frage": "Welches Element hat das chemische Symbol 'Au'?",             "antworten": ["Silber", "Aluminium", "Gold", "Kupfer"],          "richtig": 2},
    {"frage": "Wie viele Saiten hat eine Standard-Gitarre?",                "antworten": ["4", "5", "6", "7"],                              "richtig": 2},
    {"frage": "In welchem Land wurde Pizza erfunden?",                      "antworten": ["Frankreich", "Spanien", "Italien", "Griechenland"], "richtig": 2},
    {"frage": "Welcher Planet ist der größte in unserem Sonnensystem?",     "antworten": ["Saturn", "Jupiter", "Neptun", "Uranus"],          "richtig": 1},
    {"frage": "Wie viele Herzkammern hat ein Mensch?",                      "antworten": ["2", "3", "4", "5"],                              "richtig": 2},
    {"frage": "Wer hat die Relativitätstheorie entwickelt?",                "antworten": ["Newton", "Tesla", "Einstein", "Hawking"],         "richtig": 2},
    {"frage": "Welche Farbe entsteht wenn man Blau und Gelb mischt?",       "antworten": ["Orange", "Lila", "Grün", "Braun"],               "richtig": 2},
    {"frage": "Wie viele Kontinente gibt es auf der Erde?",                 "antworten": ["5", "6", "7", "8"],                              "richtig": 2},
    {"frage": "Was ist die härteste natürliche Substanz der Welt?",         "antworten": ["Granit", "Stahl", "Diamant", "Quarz"],           "richtig": 2},
    {"frage": "In welcher Stadt steht der Eiffelturm?",                     "antworten": ["London", "Berlin", "Paris", "Madrid"],           "richtig": 2},
    {"frage": "Welches Tier kann seinen Kopf um 270 Grad drehen?",          "antworten": ["Eule", "Katze", "Chamäleon", "Giraffe"],         "richtig": 0},
    {"frage": "Wie viele Nullen hat eine Million?",                         "antworten": ["5", "6", "7", "8"],                              "richtig": 1},
    {"frage": "Welcher Ozean ist der größte der Welt?",                     "antworten": ["Atlantik", "Indik", "Pazifik", "Arktis"],        "richtig": 2},
    {"frage": "Wer schrieb 'Romeo und Julia'?",                             "antworten": ["Goethe", "Schiller", "Shakespeare", "Dickens"],  "richtig": 2},
    {"frage": "Wie viele Beine hat eine Spinne?",                           "antworten": ["6", "8", "10", "12"],                            "richtig": 1},
    {"frage": "Was ist die Landessprache Brasiliens?",                      "antworten": ["Spanisch", "Englisch", "Portugiesisch", "Französisch"], "richtig": 2},
    {"frage": "Welches Tier legt die größten Eier der Welt?",               "antworten": ["Krokodil", "Strauß", "Albatros", "Wal"],         "richtig": 1},
    {"frage": "Welches chemische Symbol steht für Wasser?",                 "antworten": ["CO2", "H2O", "NaCl", "O2"],                     "richtig": 1},
    {"frage": "Was ist der höchste Berg der Welt?",                         "antworten": ["K2", "Mont Blanc", "Mount Everest", "Kilimandscharo"], "richtig": 2},
    {"frage": "Wie viele Töne hat eine Oktave?",                            "antworten": ["6", "7", "8", "12"],                             "richtig": 2},
    {"frage": "Welches Land hat die meisten Einwohner?",                    "antworten": ["USA", "Indien", "China", "Russland"],            "richtig": 1},
    {"frage": "Was ist die Hauptstadt von Japan?",                          "antworten": ["Osaka", "Kyoto", "Tokio", "Hiroshima"],          "richtig": 2},
]

EMOJIS_ANTWORT = ["🇦", "🇧", "🇨", "🇩"]


class QuizView(discord.ui.View):
    def __init__(self, frage_data: dict):
        super().__init__(timeout=60)
        self.frage_data  = frage_data
        self.beantwortet: set[int] = set()
        self.message: discord.Message | None = None
        # Einzigartiger Prefix pro Quiz-Instanz — verhindert Interferenz bei mehreren aktiven Quizzen
        prefix = uuid.uuid4().hex[:8]

        for i, antwort in enumerate(frage_data["antworten"]):
            btn = discord.ui.Button(
                label=f"{EMOJIS_ANTWORT[i]} {antwort}",
                custom_id=f"quiz_{prefix}_{i}",
                style=discord.ButtonStyle.secondary,
            )
            btn.callback = self._make_callback(i)
            self.add_item(btn)

    def _make_callback(self, index: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id in self.beantwortet:
                await interaction.response.send_message("❌ Du hast schon geantwortet!", ephemeral=True)
                return

            self.beantwortet.add(interaction.user.id)
            richtig          = index == self.frage_data["richtig"]
            richtige_antwort = self.frage_data["antworten"][self.frage_data["richtig"]]

            if richtig:
                await interaction.response.send_message(
                    f"✅ **Richtig!** Die Antwort war: **{richtige_antwort}** — gut gemacht, {interaction.user.mention}! 🎉"
                )
                self.stop()
                # Buttons deaktivieren nach richtiger Antwort
                for item in self.children:
                    item.disabled = True
                if self.message:
                    await self.message.edit(view=self)
            else:
                await interaction.response.send_message(
                    f"❌ Falsch! Versuch es nochmal.",
                    ephemeral=True
                )
        return callback

    async def on_timeout(self):
        richtige_antwort = self.frage_data["antworten"][self.frage_data["richtig"]]
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(
                    content=f"⏰ Zeit abgelaufen! Die richtige Antwort war: **{richtige_antwort}**",
                    view=self,
                )
            except Exception:
                pass


class Quiz(commands.Cog):
    """Tägliches Quiz mit Multiple-Choice Buttons."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily_quiz.start()

    def cog_unload(self):
        self.daily_quiz.cancel()

    @tasks.loop(time=discord.utils.utcnow().replace(hour=9, minute=0, second=0, microsecond=0).timetz())
    async def daily_quiz(self):
        channel = self.bot.get_channel(CHANNEL_BOT_TEST)
        if not channel:
            return
        frage = random.choice(FRAGEN)
        embed = discord.Embed(
            title="🧠 Tages-Quiz — Wer weiß es?",
            description=f"**{frage['frage']}**\n\nDu hast 60 Sekunden!",
            color=discord.Color.blue(),
        )
        embed.set_footer(text=f"📅 {date.today().strftime('%d.%m.%Y')} • Klick auf die richtige Antwort!")
        view     = QuizView(frage)
        msg      = await channel.send(embed=embed, view=view)
        view.message = msg

    @daily_quiz.before_loop
    async def before_quiz(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="quiz", description="Startet sofort eine zufällige Quizfrage!")
    async def quiz_manuell(self, interaction: discord.Interaction):
        frage = random.choice(FRAGEN)
        embed = discord.Embed(
            title="🧠 Quiz!",
            description=f"**{frage['frage']}**\n\nDu hast 60 Sekunden!",
            color=discord.Color.blue(),
        )
        view = QuizView(frage)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()  # Bug-Fix: message für on_timeout setzen


async def setup(bot: commands.Bot):
    await bot.add_cog(Quiz(bot))
