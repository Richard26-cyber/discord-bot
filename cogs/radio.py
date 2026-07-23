import discord
from discord import app_commands
from discord.ext import commands
import asyncio

STATIONEN = {
    "JAM FM":              {"url": "https://stream.jam.fm/jam-fm/mp3-192/",                                     "emoji": "🎵", "info": "Aktuelle Hits"},
    "BigFM LoFi":          {"url": "https://streams.bigfm.de/bigfm-lofi-128-mp3",                               "emoji": "🌙", "info": "Chill Beats zum Entspannen"},
    "HitRadio N1":         {"url": "https://edge11.streamonkey.net/fhn-hitradion1/stream/mp3",                   "emoji": "🔥", "info": "Nummer 1 für Hits – Nürnberg"},
    "Rock Classics":       {"url": "https://stream.oldie-antenne.de/oldie-antenne-rock-classics/stream/mp3",     "emoji": "🎸", "info": "80er & 90er Kultrock nonstop"},
    "Planet Black Beats":  {"url": "http://mp3.planetradio.de/plrchannels/hqblackbeats.mp3",                    "emoji": "🎤", "info": "Hip-Hop, R&B & Black Music"},
    "FFH":                 {"url": "http://mp3.ffh.de/radioffh/hqlivestream.mp3",                               "emoji": "📡", "info": "Hessen – Hits & Nachrichten"},
    "Radio Bollerwagen":   {"url": "https://stream.ffn.de/radiobollerwagen/mp3-192/stream.mp3",                 "emoji": "🍺", "info": "Partyhits & gute Laune"},
    "JAM FM Deutschrap":   {"url": "https://stream.jam.fm/deutschrap/mp3-192/",                                 "emoji": "🎙️", "info": "Deutschrap nonstop"},
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -analyzeduration 0 -probesize 32",
    "options": "-vn -bufsize 128k",
}


def _menu_embed(aktueller_sender: str | None = None) -> discord.Embed:
    """Basis-Embed für das Radio-Menü."""
    zeilen = "\n".join(f"{s['emoji']} **{n}** — {s['info']}" for n, s in STATIONEN.items())
    status = f"\n\n▶️ **Läuft gerade:** {aktueller_sender}" if aktueller_sender else "\n\n⏹ Kein Sender aktiv"
    return discord.Embed(
        title="📻 Radio",
        description=f"Tritt einem **Sprachkanal** bei und wähle einen Sender!\n\n{zeilen}{status}",
        color=discord.Color.orange() if aktueller_sender else discord.Color.greyple(),
    )


class RadioSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=s["info"], emoji=s["emoji"], value=name)
            for name, s in STATIONEN.items()
        ]
        super().__init__(custom_id="radio_station_select", placeholder="📻 Sender auswählen...", options=options)

    async def callback(self, interaction: discord.Interaction):
        cog: Radio = interaction.client.cogs.get("Radio")
        if cog:
            await cog.spiele_sender(interaction, self.values[0])


class RadioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RadioSelect())

    @discord.ui.button(label="⏹ Stop & Verlassen", style=discord.ButtonStyle.red, custom_id="radio_stop")
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog: Radio = interaction.client.cogs.get("Radio")
        if cog:
            await cog.stoppe(interaction)


class Radio(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.aktueller_sender: str | None = None
        self._radio_msg: discord.Message | None = None
        bot.add_view(RadioView())

    async def _update_msg(self):
        """Editiert die bestehende Radio-Nachricht — postet NIE eine neue."""
        if self._radio_msg:
            try:
                await self._radio_msg.edit(embed=_menu_embed(self.aktueller_sender), view=RadioView())
            except Exception:
                self._radio_msg = None

    async def spiele_sender(self, interaction: discord.Interaction, name: str):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                "❌ Du musst zuerst einem Sprachkanal beitreten!", ephemeral=True
            )
            return

        kanal = interaction.user.voice.channel
        vc    = interaction.guild.voice_client

        await interaction.response.defer(ephemeral=True)

        if vc:
            if vc.channel != kanal:
                await vc.move_to(kanal)
            if vc.is_playing():
                vc.stop()
        else:
            vc = await kanal.connect()

        sender = STATIONEN[name]
        source = discord.FFmpegPCMAudio(sender["url"], **FFMPEG_OPTS)
        vc.play(
            discord.PCMVolumeTransformer(source, volume=0.8),
            after=lambda e: self.bot.loop.create_task(self._nach_ende(interaction.guild))
        )
        self.aktueller_sender = name

        # Bestehende Nachricht EDITIEREN — keine neue posten
        await self._update_msg()
        await interaction.followup.send(f"{sender['emoji']} Wechsle zu **{name}**!", ephemeral=True)

    async def _nach_ende(self, guild: discord.Guild):
        vc = guild.voice_client
        if vc:
            await asyncio.sleep(2)
            if not vc.is_playing():
                await vc.disconnect()
                self.aktueller_sender = None
                await self._update_msg()

    async def stoppe(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
            await vc.disconnect()
            self.aktueller_sender = None
            await self._update_msg()
            await interaction.response.send_message("⏹ Radio gestoppt.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Kein Radio läuft gerade.", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        """Bot wurde aus Voice geworfen — Status aktualisieren."""
        if member.id != self.bot.user.id:
            return
        if before.channel and not after.channel:
            self.aktueller_sender = None
            await self._update_msg()

    @app_commands.command(name="radio", description="Öffnet das Radio-Menü zum Sender auswählen.")
    async def radio(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=_menu_embed(self.aktueller_sender), view=RadioView())
        # Diese Nachricht merken — sie wird bei Senderwechsel editiert
        self._radio_msg = await interaction.original_response()

    @app_commands.command(name="radio-stop", description="Stoppt das Radio und verlässt den Sprachkanal.")
    async def radio_stop(self, interaction: discord.Interaction):
        await self.stoppe(interaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(Radio(bot))
