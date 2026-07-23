import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import asyncio

# Mehr als MAX_NACHRICHTEN in ZEITFENSTER Sekunden = Spam
MAX_NACHRICHTEN = 5
ZEITFENSTER     = 8   # Sekunden
TIMEOUT_DAUER   = 5   # Minuten


class AntiSpam(commands.Cog):
    """Erkennt Spam automatisch, stummt den User und warnt öffentlich."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # {user_id: [timestamp, timestamp, ...]}
        self._nachrichten: dict[int, list[datetime]] = defaultdict(list)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        # Admins und Mods sind ausgenommen
        if message.author.guild_permissions.manage_messages:
            return

        jetzt = datetime.now(timezone.utc)
        uid   = message.author.id

        # Alte Einträge außerhalb des Zeitfensters entfernen
        self._nachrichten[uid] = [
            t for t in self._nachrichten[uid]
            if (jetzt - t).total_seconds() < ZEITFENSTER
        ]
        self._nachrichten[uid].append(jetzt)

        if len(self._nachrichten[uid]) >= MAX_NACHRICHTEN:
            self._nachrichten[uid].clear()
            await self._spam_aktion(message)

    async def _spam_aktion(self, message: discord.Message):
        member = message.author
        bis    = discord.utils.utcnow() + timedelta(minutes=TIMEOUT_DAUER)

        try:
            await member.timeout(bis, reason="Automatische Spam-Erkennung")
        except discord.Forbidden:
            pass  # Bot hat keine Berechtigung — trotzdem öffentlich warnen

        embed = discord.Embed(
            title="🚨 Spam erkannt!",
            description=(
                f"{member.mention} wurde wegen Spam für **{TIMEOUT_DAUER} Minuten** stummgeschaltet.\n\n"
                f"Bitte halte dich an die Serverregeln. Bei Wiederholung drohen weitere Maßnahmen."
            ),
            color=discord.Color.red(),
        )
        embed.set_footer(text="Automatisches Anti-Spam System")
        await message.channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiSpam(bot))
