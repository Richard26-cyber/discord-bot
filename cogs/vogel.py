import discord
from discord.ext import commands, tasks
from datetime import date
import random
import os


CHANNEL_BOT_TEST = int(os.getenv("CHANNEL_BOT_TEST", 0))

VOEGEL = [
    {
        "name": "Eisvogel",
        "emoji": "💎",
        "fakt": "Dieser kleine Kerl taucht mit bis zu 40 km/h in Wasser ein — und trifft dabei trotzdem einen Fisch.",
        "geil": "Er sieht aus wie ein fliegendes Juwel. Türkis + Orange = beste Farbkombination der Natur.",
        "wo": "An klaren Flüssen und Seen in Europa.",
        "groesse": "~17 cm — kleiner als deine Hand!",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Alcedo_atthis_3_(Martin_Mecnarowski).jpg/800px-Alcedo_atthis_3_(Martin_Mecnarowski).jpg",
    },
    {
        "name": "Bartgeier",
        "emoji": "🦅",
        "fakt": "Er schmeißt Knochen aus großer Höhe auf Felsen, damit sie zersplittern — und frisst dann das Mark.",
        "geil": "Der einzige Vogel der Welt, der sich fast ausschließlich von Knochen ernährt. Absolut unhinged.",
        "wo": "Alpen, Pyrenäen, Afrika.",
        "groesse": "Flügelspannweite bis zu 2,80 m.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Gypaetus_barbatus_Pope_1.jpg/800px-Gypaetus_barbatus_Pope_1.jpg",
    },
    {
        "name": "Kolibri",
        "emoji": "🌸",
        "fakt": "Sein Herz schlägt bis zu 1.200 Mal pro Minute. Er kann rückwärts fliegen.",
        "geil": "Er ist der einzige Vogel der Welt, der rückwärts fliegen kann. Physics? Kenn ich nicht.",
        "wo": "Amerika — von Kanada bis Feuerland.",
        "groesse": "Manche Arten sind nur 5 cm groß.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Calypte_anna.jpg/800px-Calypte_anna.jpg",
    },
    {
        "name": "Schnee-Eule",
        "emoji": "❄️",
        "fakt": "Sie kann ihren Kopf um 270° drehen und hört Mäuse unter einer dicken Schneeschicht.",
        "geil": "Komplett weiß, lebt im Schnee, dreht den Kopf fast komplett rum. Das ist kein Vogel, das ist ein Geist.",
        "wo": "Arktis, Tundra, manchmal auch Mitteleuropa.",
        "groesse": "Bis zu 65 cm groß.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Snowy_Owl_-_Bubo_scandiacus.jpg/800px-Snowy_Owl_-_Bubo_scandiacus.jpg",
    },
    {
        "name": "Blaupfau",
        "emoji": "🦚",
        "fakt": "Der riesige Schwanz ist eigentlich kein Schwanz — es sind verlängerte Rückenfedern. Und er raschelt damit, um Weibchen anzulocken.",
        "geil": "Er läuft rum mit einem Rad aus 200 Federn auf dem Rücken. Mehr Swagger geht nicht.",
        "wo": "Ursprünglich Indien und Sri Lanka, heute überall.",
        "groesse": "Mit Schwanzfächer bis zu 2,30 m lang.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Peacock_Plumage.jpg/800px-Peacock_Plumage.jpg",
    },
    {
        "name": "Wanderfalke",
        "emoji": "⚡",
        "fakt": "Das schnellste Tier der Erde im Sturzflug — bis zu 389 km/h.",
        "geil": "Kein Auto, kein Zug, kein Flugzeug ohne Triebwerk ist schneller. Er ist einfach Physik.",
        "wo": "Fast auf der ganzen Welt, sogar in Großstädten.",
        "groesse": "~45 cm, aber was für eine 45 cm.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Falco_peregrinus_-_01.jpg/800px-Falco_peregrinus_-_01.jpg",
    },
    {
        "name": "Papageitaucher",
        "emoji": "🐧",
        "fakt": "Er kann bis zu 60 Fische auf einmal im Schnabel tragen und fliegt mit 400 Flügelschlägen pro Minute.",
        "geil": "Sieht aus wie ein Clown, lebt auf Meeresklippen, trägt einen Mundvoll Fische — und macht das seit Millionen Jahren.",
        "wo": "Nordatlantik, Nordsee, Island.",
        "groesse": "~30 cm.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Atlantic_puffin_-_natures_pics.jpg/800px-Atlantic_puffin_-_natures_pics.jpg",
    },
    {
        "name": "Marabu",
        "emoji": "🦩",
        "fakt": "Er kühlt sich durch sein eigenes Bein ab — indem er darauf uriniert. Das nennt sich Urohidrosis.",
        "geil": "Hässlichster Vogel der Welt — und er gibt keinen einzigen Cent darum. Absolute Selbstsicherheit.",
        "wo": "Afrika südlich der Sahara.",
        "groesse": "Bis zu 1,50 m groß.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Leptoptilos_crumenifer_-_Mikumi.jpg/800px-Leptoptilos_crumenifer_-_Mikumi.jpg",
    },
    {
        "name": "Rotmilan",
        "emoji": "🪁",
        "fakt": "Er kann im Gleitflug Stunden lang kreisen, ohne einen einzigen Flügelschlag zu machen.",
        "geil": "Er fliegt buchstäblich auf Thermik — unsichtbare Warmluftsäulen. Gratis-Energie aus der Luft.",
        "wo": "Europa, vor allem Deutschland (weltweites Zentrum!).",
        "groesse": "Flügelspannweite bis 1,80 m.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Red_kite_2.jpg/800px-Red_kite_2.jpg",
    },
    {
        "name": "Schwarzspecht",
        "emoji": "🪵",
        "fakt": "Er hämmert bis zu 20 Mal pro Sekunde auf Holz — und bekommt dabei keine Gehirnerschütterung, weil sein Gehirn federnd gelagert ist.",
        "geil": "Natur hat ihm ein eingebautes Stoßdämpfer-System ins Gehirn gebaut. Die Evolution meinte es gut.",
        "wo": "Alte Wälder in Europa und Asien.",
        "groesse": "~46 cm, größter Specht Europas.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Dryocopus_martius_Picard.jpg/800px-Dryocopus_martius_Picard.jpg",
    },
    {
        "name": "Flamingo",
        "emoji": "🦩",
        "fakt": "Er ist nicht rosa — er wird rosa durch das, was er frisst (Algen und Krebstiere). Im Zoo muss man ihn extra füttern, damit er nicht weiß wird.",
        "geil": "Du bist buchstäblich das, was du isst. Flamingo lebt das.",
        "wo": "Karibik, Südamerika, Afrika, Südeuropa.",
        "groesse": "Bis zu 1,20 m.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flamingos_Laguna_Colorada.jpg/800px-Flamingos_Laguna_Colorada.jpg",
    },
    {
        "name": "Uhu",
        "emoji": "🦉",
        "fakt": "Größte Eule der Welt. Er jagt nachts mit fast lautlosem Flug — seine Federn sind speziell geformt, um Geräusche zu dämpfen.",
        "geil": "Stealth-Modus aktiviert. Er ist der Tarnbomber unter den Vögeln.",
        "wo": "Von Europa bis Japan, fast überall.",
        "groesse": "Bis zu 75 cm, Flügelspannweite 1,90 m.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Bubo_bubo_-_01.jpg/800px-Bubo_bubo_-_01.jpg",
    },
    {
        "name": "Regenbogenlori",
        "emoji": "🌈",
        "fakt": "Er hat eine bürstenartige Zunge, um Nektar aus Blüten zu lecken — und ist einer der lautesten Vögel überhaupt.",
        "geil": "Sieht aus, als wäre er durch einen Regenbogen geflogen und hätte ihn einfach mitgenommen.",
        "wo": "Australien, Neuguinea, Indonesien.",
        "groesse": "~30 cm.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Rainbow_lorikeet_perth.jpg/800px-Rainbow_lorikeet_perth.jpg",
    },
    {
        "name": "Kakapo",
        "emoji": "🥺",
        "fakt": "Er ist der einzige flugunfähige Papagei der Welt, der schwerste Papagei überhaupt — und vom Aussterben bedroht. Nur noch ~250 Tiere existieren.",
        "geil": "Er riecht nach Blumen, ist nachtaktiv, kann nicht fliegen, und ist trotzdem ein Papagei. Ein absoluter Sonderfall der Evolution.",
        "wo": "Neuseeland (nur auf Schutzinseln).",
        "groesse": "Bis zu 4 kg — der schwerste Papagei der Welt.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Kakapo_Sirocco_-_Zealandia_Sanctuary.jpg/800px-Kakapo_Sirocco_-_Zealandia_Sanctuary.jpg",
    },
    {
        "name": "Tukan",
        "emoji": "🌿",
        "fakt": "Sein riesiger Schnabel dient zur Temperaturregulierung — er leitet Wärme ab wie eine Kühlrippe.",
        "geil": "Sieht aus wie ein Cartoon-Charakter, ist aber echt. Natur hat manchmal keinen Plan.",
        "wo": "Regenwälder Mittel- und Südamerikas.",
        "groesse": "~55 cm, davon ~20 cm Schnabel.",
        "bild": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Ramphastos_toco_-Pantanal%2C_Mato_Grosso%2C_Brazil-8.jpg/800px-Ramphastos_toco_-Pantanal%2C_Mato_Grosso%2C_Brazil-8.jpg",
    },
]


class Vogel(commands.Cog):
    """Täglich einen Vogel des Tages in #bot-test posten."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._vogel_index = 0
        self.vogel_des_tages.start()

    def cog_unload(self):
        self.vogel_des_tages.cancel()

    @tasks.loop(time=discord.utils.utcnow().replace(hour=8, minute=0, second=0, microsecond=0).timetz())
    async def vogel_des_tages(self):
        """Täglich um 10:00 (08:00 UTC) einen Vogel posten."""
        channel = self.bot.get_channel(CHANNEL_BOT_TEST)
        if not channel:
            return

        vogel = random.choice(VOEGEL)
        embed = discord.Embed(
            title=f"{vogel['emoji']} Vogel des Tages: **{vogel['name']}**",
            color=discord.Color.from_rgb(34, 197, 94),
        )
        embed.add_field(
            name="🤔 Was ist das Geile an diesem Vogel?",
            value=vogel["geil"],
            inline=False,
        )
        embed.add_field(
            name="📖 Cooler Fakt",
            value=vogel["fakt"],
            inline=False,
        )
        embed.add_field(name="📍 Wo lebt er?", value=vogel["wo"], inline=True)
        embed.add_field(name="📏 Größe", value=vogel["groesse"], inline=True)
        if vogel.get("bild"):
            embed.set_image(url=vogel["bild"])
        embed.set_footer(text=f"🗓️ {date.today().strftime('%d. %B %Y')} • Vogel-Ecke 🐦")

        await channel.send(embed=embed)

    @discord.app_commands.command(name="vogel", description="Zeigt einen zufälligen Vogel des Tages!")
    async def vogel_cmd(self, interaction: discord.Interaction):
        vogel = random.choice(VOEGEL)
        embed = discord.Embed(
            title=f"{vogel['emoji']} Zufälliger Vogel: **{vogel['name']}**",
            color=discord.Color.from_rgb(34, 197, 94),
        )
        embed.add_field(name="🤔 Was ist das Geile an diesem Vogel?", value=vogel["geil"], inline=False)
        embed.add_field(name="📖 Cooler Fakt", value=vogel["fakt"], inline=False)
        embed.add_field(name="📍 Wo lebt er?", value=vogel["wo"], inline=True)
        embed.add_field(name="📏 Größe", value=vogel["groesse"], inline=True)
        if vogel.get("bild"):
            embed.set_image(url=vogel["bild"])
        await interaction.response.send_message(embed=embed)

    @vogel_des_tages.before_loop
    async def before_vogel(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Vogel(bot))
