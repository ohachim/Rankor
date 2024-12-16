"""Defines types for our Riot API services."""

import dataclasses


@dataclasses.dataclass
class SummonerDTO:
    """Represent a summoner from the Riot API."""

    encrypted_summoner_id: str
    account_id: str
    puuid: str
    name: str
    profile_icon_id: int
    revision_data: int
    summoner_level: int


@dataclasses.dataclass
class LeagueEntryDTO:
    """Represents a league entry, encapsulating rankned data from Rior API."""

    league_id: str
    summonner_id: str
    summoner_name: str
    queue_type: str
    rank: str
    division: str
    league_points: int
    wins: int
    loses: int
    hot_streak: int
    veteran: bool
    fresh_blood: bool
    inactive: bool
