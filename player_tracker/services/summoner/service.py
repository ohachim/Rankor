"""Facade for interactions between django models and Riot API service."""

from django.db import transaction

from ...models import SummonerProfile
from ..riot.constants import QueueType, Region
from ..riot.service import RiotAPIService
from ..riot.types import LeagueEntryDTO, SummonerDTO, RiotAccountDTO
from asgiref.sync import sync_to_async


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
        name: str,
        tagline: str,
        region: Region = Region.euw,
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
        account_dto: RiotAccountDTO = await self._riot_api.get_summoner_account(
            summoner_name=name, tagline=tagline, region=region
        )
        summoner_dto: SummonerDTO = await self._riot_api.get_summoner_by_puuid(
            puuid=account_dto.puuid, name=name, tagline=tagline
        )
        league_entries: list[LeagueEntryDTO] = await self._riot_api.get_league_entries(
            encrypted_summoner_id=summoner_dto.id,
        )
        print(league_entries)
        profile, _ = await sync_to_async(SummonerProfile.objects.get_or_create)(
            discord_id=discord_id,
            defaults={
                "summoner_name": name,
                "tagline": tagline,
                "puuid": account_dto.puuid,
                "server_region": region.value,
            },
        )
        # Reset ranks if no entries (unranked)
        if not league_entries:
            profile.current_solo_rank = "UNRANKED"
            profile.current_solo_division = None
            profile.current_solo_lp = 0
            profile.solo_wins = 0
            profile.solo_losses = 0
            profile.solo_league_id = None

            profile.current_flex_rank = "UNRANKED"
            profile.current_flex_division = None
            profile.current_flex_lp = 0
            profile.flex_wins = 0
            profile.flex_losses = 0
            profile.flex_league_id = None

            profile.summoner_id = summoner_dto.id
        else:
            profile.summoner_id = summoner_dto.id
            for entry in league_entries:
                if entry.queueType == QueueType.RANKED_SOLO.value:
                    profile.solo_league_id = entry.leagueId
                    profile.current_solo_division = entry.rank
                    profile.current_solo_lp = entry.leag
                    profile.current_solo_rank = entry.tier
                    profile.solo_wins = entry.wins
                    profile.solo_losses = entry.losses

                    if self._is_rank_higher(
                        entry.tier, profile.highest_achieved_rank_solo
                    ):
                        profile.highest_achieved_rank_solo = entry.tier

                elif entry.queueType == QueueType.RANKED_FLEX.value:
                    profile.flex_league_id = entry.leagueId
                    profile.current_flex_division = entry.rank
                    profile.current_flex_lp = entry.leaguePoints
                    profile.current_flex_rank = entry.tier
                    profile.flex_wins = entry.wins
                    profile.flex_losses = entry.losses

                    if self._is_rank_higher(
                        entry.tier, profile.highest_achieved_rank_flex
                    ):
                        profile.highest_achieved_rank_flex = entry.tier

        await sync_to_async(profile.save)()
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
