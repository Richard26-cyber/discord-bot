import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import logging

import database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

load_dotenv()
TOKEN    = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN fehlt in der .env-Datei!")


class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        # message_content bleibt False: Aktivitätszähler braucht nur das Event,
        # nicht den Inhalt der Nachricht — Datensparsamkeit!
        super().__init__(
            command_prefix="!",
            intents=intents,
            # Der Bot gibt Nutzertext weiter (Erinnerungen, Namen). Ohne das
            # hier koennte jemand @everyone in seinen Text schreiben und der
            # Bot pingt den ganzen Server. Einzelne Stellen duerfen Mentions
            # explizit wieder erlauben.
            allowed_mentions=discord.AllowedMentions.none(),
        )

    async def setup_hook(self):
        # Datenbank-Tabellen anlegen (falls noch nicht vorhanden)
        database.init_db()
        log.info("Datenbank initialisiert.")

        # Alle Cogs laden
        cogs_dir = "./cogs"
        for filename in sorted(os.listdir(cogs_dir)):
            if filename.endswith(".py") and not filename.startswith("_"):
                cog_name = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(cog_name)
                    log.info(f"Cog geladen: {cog_name}")
                except Exception as e:
                    log.error(f"Fehler beim Laden von {cog_name}: {e}", exc_info=True)

        # Slash-Commands synchronisieren (guild = sofort, global = bis 1 Stunde)
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info(f"Slash-Commands mit Guild {GUILD_ID} synchronisiert.")
        else:
            await self.tree.sync()
            log.info("Slash-Commands global synchronisiert.")

    async def on_tree_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ Kurz warten! Du kannst diesen Command erst in **{error.retry_after:.0f} Sekunden** wieder nutzen.",
                ephemeral=True
            )
        else:
            raise error

    async def on_ready(self):
        log.info(f"Bot ist online als: {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="dem Treiben zu 👀"
            )
        )


async def main():
    async with DiscordBot() as bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
