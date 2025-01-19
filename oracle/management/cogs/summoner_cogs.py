"""Module with cogs related to summoner actions."""

import logging

import nextcord
from asgiref.sync import sync_to_async
from nextcord.ext import commands

from player_tracker.services.riot.constants import Region
from player_tracker.services.riot.exceptions import RiotAPIError, SummonerNotFoundError
from player_tracker.services.summoner.service import SummonerProfile, SummonerService

logger = logging.getLogger("nextcord")


class SummonerProfileCog(commands.Cog):
    """Handles summoner profile related commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._summoner_service: SummonerService = bot.summoner_service

    @commands.command(name="register")
    async def register(
        self, ctx: commands.Context, account_identification: str, region: str = "euw"
    ) -> None:
        """Register your League account.

        Usage:
            !register <account_identification> [region]
            Example: !register Faker KR
        """
        try:
            account_parts = account_identification.split("#")
            if len(account_parts) < 2:
                print("Wrong account format")
                ctx.send(
                    "Wrong account format. Please include the name and "
                    "the tagline.\nExample: summoner_name#tagline"
                )
                return

            account_name = account_parts[0]
            account_tagline = account_parts[1]
            await self._summoner_service.update_summoner_profile(
                discord_id=str(ctx.author.id),
                name=account_name,
                tagline=account_tagline,
                region=Region[region],
            )

            await ctx.send("Successfully registered account")

        except SummonerNotFoundError:
            await ctx.send(
                f"Could not find summoner {account_identification} in {region}. "
                "Please check the name and region."
            )
        except Exception as e:
            print("Failed to register summoner: ", e)
            await ctx.send(
                "An error occurred while registering your summoner. "
                "Please try again later."
            )

    @commands.command(name="rank")
    async def get_rank(self, ctx: commands.Context) -> None:
        """Check your current rank."""
        try:
            # First get existing profile
            profile = await sync_to_async(SummonerProfile.objects.get)(
                discord_id=str(ctx.author.id)
            )
            routing_value = profile.server_region[1:-1].split(",")[0][1:-1]
            platform_value = profile.server_region[1:-1].split(",")[1][2:-1]
            try:
                profile = await self._summoner_service.update_summoner_profile(
                    discord_id=str(ctx.author.id),
                    name=profile.summoner_name,
                    tagline=profile.tagline,
                    region=Region(routing_value, platform_value),
                )
            except (RiotAPIError, SummonerNotFoundError) as e:
                # Still show old data if update fails
                logger.error(f"Failed to update profile: {e}")
                await ctx.send("⚠️ Could not fetch fresh data, showing last known ranks")
            rank_icons = {
                "IRON": "⚔️",
                "BRONZE": "🟫",
                "SILVER": "⚪",
                "GOLD": "🟡",
                "PLATINUM": "💠",
                "EMERALD": "🟢",
                "DIAMOND": "💎",
                "MASTER": "🟣",
                "GRANDMASTER": "🔴",
                "CHALLENGER": "🏆",
                "UNRANKED": "❔",
            }

            embed = nextcord.Embed(
                title=f"{profile.summoner_name}#{profile.tagline}", color=0x2B2D31
            )

            # Solo/Duo Queue stats
            solo_rank = (
                f"{rank_icons[profile.current_solo_rank]} {profile.current_solo_rank.title()} {profile.current_solo_division}"
                if profile.current_solo_division
                else f"{rank_icons[profile.current_solo_rank]} {profile.current_solo_rank.title()}"
            )

            solo_stats = ""
            if profile.current_solo_rank != "UNRANKED":
                solo_stats = (
                    f"**Rank:** {solo_rank}\n**LP:** {profile.current_solo_lp}\n"
                )
                if hasattr(profile, "solo_wins") and hasattr(profile, "solo_losses"):
                    total_solo_games = profile.solo_wins + profile.solo_losses
                    wr_solo = (
                        (profile.solo_wins / total_solo_games * 100)
                        if total_solo_games > 0
                        else 0
                    )
                    solo_stats += f"**W/L:** {profile.solo_wins}/{profile.solo_losses} ({wr_solo:.1f}%)"
            else:
                solo_stats = f"{rank_icons['UNRANKED']} **Unranked**"

            embed.add_field(name="🎮 Solo/Duo Queue", value=solo_stats, inline=True)

            # Add a blank field for spacing
            embed.add_field(name="\u200b", value="\u200b", inline=True)

            # Flex Queue stats
            flex_rank = (
                f"{rank_icons[profile.current_flex_rank]} {profile.current_flex_rank.title()} {profile.current_flex_division}"
                if profile.current_flex_division
                else f"{rank_icons[profile.current_flex_rank]} {profile.current_flex_rank.title()}"
            )

            flex_stats = ""
            if profile.current_flex_rank != "UNRANKED":
                flex_stats = (
                    f"**Rank:** {flex_rank}\n**LP:** {profile.current_flex_lp}\n"
                )
                if hasattr(profile, "flex_wins") and hasattr(profile, "flex_losses"):
                    total_flex_games = profile.flex_wins + profile.flex_losses
                    wr_flex = (
                        (profile.flex_wins / total_flex_games * 100)
                        if total_flex_games > 0
                        else 0
                    )
                    flex_stats += f"**W/L:** {profile.flex_wins}/{profile.flex_losses} ({wr_flex:.1f}%)"
            else:
                flex_stats = f"{rank_icons['UNRANKED']} **Unranked**"

            embed.add_field(name="👥 Flex Queue", value=flex_stats, inline=True)

            # Peak Ranks (if any exist)
            peak_ranks = []
            if profile.highest_achieved_rank_solo != "UNRANKED":
                peak_ranks.append(
                    f"**Solo:** {rank_icons[profile.highest_achieved_rank_solo]} "
                    f"{profile.highest_achieved_rank_solo.title()}"
                )
            if profile.highest_achieved_rank_flex != "UNRANKED":
                peak_ranks.append(
                    f"**Flex:** {rank_icons[profile.highest_achieved_rank_flex]} "
                    f"{profile.highest_achieved_rank_flex.title()}"
                )

            if peak_ranks:
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(
                    name="⭐ Peak Ranks", value="\n".join(peak_ranks), inline=False
                )

            embed.set_footer(text="Last updated")
            embed.timestamp = profile.last_check_timestamp

            await ctx.send(embed=embed)

        except SummonerProfile.DoesNotExist:
            await ctx.send(
                "❌ You haven't registered your summoner profile yet. "
                "Use `!register <summoner_name> <tagline>` to register."
            )
        except Exception as e:
            logger.error("Error fetching rank data: %s", str(e))
            print("oh shit ", e)
            await ctx.send(
                "⚠️ An error occurred while fetching your rank data. "
                "Please try again later."
            )

    @commands.command(name="update")
    async def update_profile(self, ctx: commands.Context) -> None:
        """Force an update of your profile data."""
        # TODO: Implement once we have the update logic
        await ctx.send("Profile updating coming soon!")

    @commands.command(name="deactivate")
    async def deactivate(self, ctx: commands.Context) -> None:
        """Deactivate your profile tracking."""
        # TODO: Implement once we have deactivation logic
        await ctx.send("Profile deactivation coming soon!")
