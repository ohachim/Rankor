"""Facade for interactions between django models and Riot API service."""

from django.db import transaction

from ...models import SummonerProfile
from ..riot.constants import QueueType, Region
from ..riot.service import RiotAPIService
from ..riot.types import LeagueEntryDTO, SummonerDTO


class SummonerService:
    """Responsible for manageing relationships between Database and Riot API."""

    def __init__(
        self,
        riot_api: RiotAPIService,
    ) -> None:
        """Intializes the instance with an instance of RiotAPIService."""
        self._riot_api = riot_api

    async def update_summoner_profile(
        self,
        discord_id: str,
        summoner_name: str,
        region: Region = Region.EUW1,
    ) -> SummonerProfile:
        """Update or create a summoner profile with latest data from Riot.

        Args:
            discord_id: Discord ID of the user.
            summoner_name: Summoner name to look up.
            region: Game region for the summoner.

        Returns:
            Updated SummonerProfile instance.

        Raises:
            SummonerNotFoundError: If summoner doesn't exist.
            RiotAPIError: For other API-related errors.
        """
        summoner_dto: SummonerDTO = self._riot_api.get_summoner_by_name(
            summoner_name=summoner_name
        )

        league_entries: LeagueEntryDTO = self._riot_api.get_league_entries(
            summoner_dto.encrypted_summoner_id
        )

        soloq_data = None
        flexq_data = None

        for entry in league_entries:
            if entry.queue_type == QueueType.RANKED_SOLO.value:
                soloq_data = entry
            elif entry.queue_type == QueueType.RANKED_FLEX.value:
                flexq_data = entry

        with (
            transaction.atomic()
        ):  # (TODO(ohachim): Server Transfer, multiple accounts discord/riot)
            profile, _ = SummonerProfile.get_or_create(
                discord_id=discord_id,
                defaults={
                    "summoner_name": summoner_name,
                    "puuid": summoner_dto.puuid,
                    "server_region": region.value,
                },
            )

            profile.summoner_name = summoner_dto.name

            if soloq_data:
                profile.current_solo_rank = soloq_data.rank
                profile.current_solo_division = soloq_data.division
                profile.current_solo_lp = soloq_data.league_points

                if self._is_rank_higher(
                    soloq_data.rank,
                    profile.highest_achieved_rank_solo,
                ):
                    profile.highest_achieved_rank_solo = soloq_data.rank

            if flexq_data:
                profile.current_flex_rank = flexq_data.rank
                profile.current_flex_division = flexq_data.division
                profile.current_flex_lp = flexq_data.league_points

                if self._is_rank_higher(
                    flexq_data.rank,
                    profile.highest_achieved_rank_flex,
                ):
                    profile.highest_achieved_rank_flex = flexq_data.rank

                profile.save()

            return profile

    @staticmethod
    def _is_rank_higher(new_rank: str, current_rank: str) -> bool:
        """Compare two ranks to determine if new rank is higher.

        Args:
            new_rank: The new rank to compare.
            current_rank: The current rank to compare against.

        Returns:
            True if new_rank is higher than current_rank.
        """
        rank_order = {
            "CHALLENGER": 0,
            "GRANDMASTER": 1,
            "MASTER": 2,
            "DIAMOND": 3,
            "EMERALD": 4,
            "PLATINUM": 5,
            "GOLD": 6,
            "SILVER": 7,
            "BRONZE": 8,
            "IRON": 9,
            "UNRANKED": 10,
        }

        return rank_order.get(new_rank, 99) < rank_order.get(current_rank, 99)
