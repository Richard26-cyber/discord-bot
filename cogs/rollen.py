"""
Rollen-System:
  1. Wer im #regelwerk mit ✅ reagiert → bekommt: Mensch + ----Beziehungsebene---- + ----Charakter Definitionen----
  2. /rollen-setup  → postet ein Select-Menü in #rollen (Discord-native UI)
     Dort können User sich selbst Rollen geben/wegnehmen.
"""
import discord
from discord import app_commands
from discord.ext import commands
import os


MESSAGE_REGELWERK_ID = int(os.getenv("MESSAGE_REGELWERK_ID", 0))
CHANNEL_ROLLEN       = int(os.getenv("CHANNEL_ROLLEN", 0))

# Alle drei Rollen die jeder beim ✅ bekommt (exakte Namen wie auf dem Server)
ROLLEN_BEI_AKZEPTIERUNG = [
    "Mensch",
    "----Beziehungsebene----",
    "----Charakter Definitionen----",
]

# ── Selbst-wählbare Rollen (Name exakt wie auf dem Server) ────────────────────
# Passe diese Listen an deine Server-Rollen an!

GAMING_ROLLEN = [
    ("🔫", "Ready or not",    "Spielst du Ready or not?"),
    ("👻", "Phasmo",          "Phasmophobia-Spieler"),
    ("🚛", "ATS/ETS",         "American/Euro Truck Simulator"),
    ("✈️", "Flight Simulator", "Microsoft Flight Simulator"),
    ("💥", "Warzone mit MW",   "Warzone mit Modern Warfare"),
    ("🎯", "Nur Warzone",      "Nur Warzone ohne MW"),
]

CHARAKTER_ROLLEN = [
    ("💻", "Dev",            "Entwickler/Coder"),
    ("💕", "Love",           "Für die Romantiker"),
    ("👻", "Geisterjäger",   "Paranormale Aktivität? Sign me up"),
    ("✍️", "Schriftsteller", "Kreativ mit Worten"),
    ("🎤", "Bester Sänger",  "Dusche-Karaoke-Weltmeister"),
    ("⚽", "Bayern",         "FC Bayern München"),
]


# ── View: Gaming-Rollen Auswahl ───────────────────────────────────────────────

class GamingRollenSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=desc, emoji=emoji)
            for emoji, name, desc in GAMING_ROLLEN
        ]
        super().__init__(
            custom_id="gaming_rollen_select",
            placeholder="🎮 Wähle deine Gaming-Rollen...",
            min_values=0,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await _apply_roles(interaction, self.values, [name for _, name, _ in GAMING_ROLLEN])


class CharakterRollenSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=desc, emoji=emoji)
            for emoji, name, desc in CHARAKTER_ROLLEN
        ]
        super().__init__(
            custom_id="charakter_rollen_select",
            placeholder="🎭 Wähle deine Charakter-Rollen...",
            min_values=0,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await _apply_roles(interaction, self.values, [name for _, name, _ in CHARAKTER_ROLLEN])


async def _apply_roles(
    interaction: discord.Interaction,
    selected: list[str],
    all_names: list[str],
):
    """Gibt gewählte Rollen, entfernt nicht-gewählte — aus der jeweiligen Kategorie."""
    await interaction.response.defer(ephemeral=True)
    member = interaction.user

    added, removed = [], []

    for role_name in all_names:
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            continue

        if role_name in selected and role not in member.roles:
            await member.add_roles(role, reason="Selbst-Zuweisung via Bot")
            added.append(role_name)
        elif role_name not in selected and role in member.roles:
            await member.remove_roles(role, reason="Selbst-Entfernung via Bot")
            removed.append(role_name)

    lines = []
    if added:
        lines.append(f"✅ Hinzugefügt: {', '.join(added)}")
    if removed:
        lines.append(f"🗑️ Entfernt: {', '.join(removed)}")
    if not lines:
        lines.append("Keine Änderungen.")

    await interaction.followup.send("\n".join(lines), ephemeral=True)


class RollenView(discord.ui.View):
    """Persistente View — überlebt Bot-Neustart durch custom_ids."""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GamingRollenSelect())
        self.add_item(CharakterRollenSelect())


# ── Cog ───────────────────────────────────────────────────────────────────────

class Rollen(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Persistente View beim Start registrieren!
        bot.add_view(RollenView())

    # Wer ✅ im Regelwerk reagiert → Mensch-Rolle
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != "✅":
            return
        if MESSAGE_REGELWERK_ID and payload.message_id != MESSAGE_REGELWERK_ID:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        rollen = [discord.utils.get(guild.roles, name=n) for n in ROLLEN_BEI_AKZEPTIERUNG]
        rollen = [r for r in rollen if r and r not in member.roles]
        if rollen:
            await member.add_roles(*rollen, reason="Regelwerk akzeptiert ✅")

    # Wer ✅ entfernt → alle drei Rollen weg
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != "✅":
            return
        if MESSAGE_REGELWERK_ID and payload.message_id != MESSAGE_REGELWERK_ID:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        rollen = [discord.utils.get(guild.roles, name=n) for n in ROLLEN_BEI_AKZEPTIERUNG]
        rollen = [r for r in rollen if r and r in member.roles]
        if rollen:
            await member.remove_roles(*rollen, reason="Regelwerk-Reaktion entfernt")

    # Admin-Command: Rollen-Auswahl-Nachricht posten
    @app_commands.command(name="rollen-setup", description="[Admin] Postet das Rollen-Auswahl-Menü in #rollen.")
    @app_commands.checks.has_permissions(administrator=True)
    async def rollen_setup(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(CHANNEL_ROLLEN)
        if not channel:
            await interaction.response.send_message(
                "❌ `CHANNEL_ROLLEN` fehlt in der .env!", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🎭 Rollen-Auswahl",
            description=(
                "Wähle hier deine Rollen aus!\n\n"
                "**🎮 Gaming-Rollen** — Welche Spiele spielst du?\n"
                "**🎭 Charakter-Rollen** — Wer bist du auf diesem Server?\n\n"
                "Du kannst mehrere auswählen. Abwählen entfernt die Rolle wieder."
            ),
            color=discord.Color.blurple(),
        )

        await channel.send(embed=embed, view=RollenView())
        await interaction.response.send_message(
            f"✅ Rollen-Menü wurde in {channel.mention} gepostet!", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Rollen(bot))
