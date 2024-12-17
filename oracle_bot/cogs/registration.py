"""Registration cog for handling summoner registration commands."""

import logging
from typing import TYPE_CHECKING

import nextcord
from django.conf import settings
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from oracle_bot.constants import BotColors, MessageConstants
from player_tracker.services.riot.constants import Region
from player_tracker.services.summoner.service import SummonerService

if TYPE_CHECKING:
    from oracle_bot.client import Oracle

logger = logging.getLogger(__name__)


class Registration(commands.Cog):
    """Handles summoner registration and management."""

    def __init__(self, bot: "Oracle") -> None:
        """Initialize the cog.

        Args:
            bot: The Oracle bot instance.
        """
        self.bot = bot

    @nextcord.slash_command(
        name="register",
        description=MessageConstants.REGISTER,
        guild_ids=[settings.DISCORD_GUILD_ID],  # Add this line
    )
    async def register(
        self,
        interaction: Interaction,
        summoner_name: str = SlashOption(description="Your summoner name"),
    ) -> None:
        await interaction.response.send_message(f"Trying to register: {summoner_name}")

    # @nextcord.slash_command(
    #     name="register",
    #     description=MessageConstants.REGISTER,
    #     guild_ids=[settings.DISCORD_GUILD_ID],  # Add this line

    # )
    # async def register(
    #     self,
    #     interaction: Interaction,
    #     summoner_name: str = SlashOption(
    #         description="Your League of Legends summoner name",
    #         required=True,
    #     ),
    #     region: str = SlashOption(
    #         description="Your server region",
    #         choices={"EUW": "EUW1", "NA": "NA1", "EUNE": "EUNE1"}, # TODO(ohachim): add more
    #         required=True,
    #     ),
    # ) -> None:
    #     """Register a summoner to a Discord user.

    #     Args:
    #         interaction: The slash command interaction.
    #         summoner_name: The summoner name to register.
    #         region: The server region of the summoner.
    #     """
    #     await interaction.response.defer()

    #     try:
    #         # Create service instance and update profile
    #         summoner_service = SummonerService()  # We'll need to modify this later
    #         await summoner_service.update_summoner_profile(
    #             discord_id=str(interaction.user.id),
    #             summoner_name=summoner_name,
    #             region=Region(region),
    #         )

    #         embed = nextcord.Embed(
    #             title="Registration Successful",
    #             description=MessageConstants.SUMMONER_REGISTERED.format(
    #                 summoner_name=summoner_name
    #             ),
    #             color=BotColors.SUCCESS.value,
    #         )

    #     except Exception as e:
    #         logger.error(
    #             "Failed to register summoner",
    #             extra={
    #                 "discord_id": interaction.user.id,
    #                 "summoner_name": summoner_name,
    #                 "region": region,
    #             },
    #             exc_info=True,
    #         )
    #         embed = nextcord.Embed(
    #             title="Registration Failed",
    #             description=MessageConstants.GENERIC_ERROR,
    #             color=BotColors.ERROR.value,
    #         )

    #     await interaction.followup.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    bot.add_cog(Registration(bot))
