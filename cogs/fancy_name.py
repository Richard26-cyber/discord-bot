"""
Fancy-Name-Feature:
  Im Channel #real-name-und-rolle-vergabe:
  Jemand tippt:  /name Jacky
  Bot:
    1. Ändert den Server-Nickname zu 𝓙𝓪𝓬𝓴𝔂
    2. Reagiert mit ✅ auf die Nachricht (Nachricht bleibt für andere sichtbar)
    3. Schickt eine kurze Bestätigung (ephemeral = nur für den User sichtbar)
"""
import discord
from discord import app_commands
from discord.ext import commands
import os


CHANNEL_REAL_NAME = int(os.getenv("CHANNEL_REAL_NAME", 0))

# ── Unicode Bold Script Konverter ─────────────────────────────────────────────
# Verwendet direkte Unicode-Codepoints — zuverlässiger als Literal-Zeichen
# Mathematical Bold Script: Großbuchstaben ab U+1D4D0, Kleinbuchstaben ab U+1D4EA

def to_fancy(text: str) -> str:
    result = []
    for ch in text:
        if "A" <= ch <= "Z":
            result.append(chr(0x1D4D0 + ord(ch) - ord("A")))
        elif "a" <= ch <= "z":
            result.append(chr(0x1D4EA + ord(ch) - ord("a")))
        else:
            result.append(ch)  # Zahlen, Leerzeichen, Sonderzeichen bleiben gleich
    return "".join(result)


# ── Cog ───────────────────────────────────────────────────────────────────────

class FancyName(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 30, key=lambda i: i.user.id)
    @app_commands.command(
        name="name",
        description="Setzt deinen Server-Nickname in cooler Schrift, z.B. /name Jacky"
    )
    @app_commands.describe(name="Dein Name (Buchstaben A-Z)")
    async def name_cmd(self, interaction: discord.Interaction, name: str):
        # Nur im richtigen Channel erlauben
        if CHANNEL_REAL_NAME and interaction.channel_id != CHANNEL_REAL_NAME:
            channel = self.bot.get_channel(CHANNEL_REAL_NAME)
            hinweis = f"Bitte benutze diesen Command in {channel.mention}!" if channel else "Falscher Channel!"
            await interaction.response.send_message(f"❌ {hinweis}", ephemeral=True)
            return

        if len(name) > 32:
            await interaction.response.send_message(
                "❌ Name zu lang (max. 32 Zeichen).", ephemeral=True
            )
            return

        fancy = to_fancy(name)

        # Nickname setzen (der Bot braucht die Berechtigung "Nicknames verwalten")
        try:
            await interaction.user.edit(nick=fancy, reason="Fancy-Name via /name Command")
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Ich habe keine Berechtigung, deinen Nickname zu ändern.\n"
                "(Admins und Server-Owner können vom Bot nicht umbenannt werden.)",
                ephemeral=True,
            )
            return
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)
            return

        # Bestätigung senden (nur für den User sichtbar)
        await interaction.response.send_message(
            f"✅ Dein Nickname wurde zu **{fancy}** geändert!", ephemeral=True
        )

        # ✅ als Reaktion auf die Slash-Command-Nachricht (Discord macht das automatisch
        # bei ephemeral responses — wir holen die original_response und reagieren)
        try:
            msg = await interaction.original_response()
            # Slash-Commands sind keine normalen Nachrichten, daher fügen wir
            # eine sichtbare Nachricht als Bestätigung im Channel hinzu
            await interaction.channel.send(
                f"✅ {interaction.user.mention} heißt jetzt **{fancy}**! 🎉",
                delete_after=10,  # verschwindet nach 10 Sekunden automatisch
                # fancy stammt aus Nutzereingabe: nur den Aufrufer anpingen
                allowed_mentions=discord.AllowedMentions(
                    everyone=False, roles=False,
                    users=[interaction.user],
                ),
            )
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(FancyName(bot))
