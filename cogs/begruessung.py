import discord
from discord.ext import commands
import os


CHANNEL_WILLKOMMEN = int(os.getenv("CHANNEL_WILLKOMMEN", 0))


class Begruessung(commands.Cog):
    """Begrüßt neue Mitglieder im Willkommens-Channel."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(CHANNEL_WILLKOMMEN)
        if not channel:
            return

        embed = discord.Embed(
            title=f"👋 Willkommen auf {member.guild.name}, {member.display_name}!",
            description=(
                f"Hey {member.mention}! Schön dass du da bist! 😀\n\n"
                "**Schön, dass du da bist!**\n"
                "Bitte lies dir die Regeln durch — danach kannst du sie akzeptieren, "
                "indem du auf den **grünen Haken** ✅ im Regelwerk-Channel klickst.\n\n"
                "Wir freuen uns auf dich! 🎉"
            ),
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Mitglied #{member.guild.member_count}")

        await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Begruessung(bot))
