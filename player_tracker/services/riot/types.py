"""Defines types for our Riot API services."""

import dataclasses


@dataclasses.dataclass
class RiotAccountDTO:
    """Represents account data from Riot Account-V1 API."""

    puuid: str
    gameName: str
    tagLine: str


@dataclasses.dataclass
class SummonerDTO:
    """Represent a summoner from the Riot API."""

    id: str  # encrypted summoner id
    accountId: str
    puuid: str
    profileIconId: int
    revisionDate: int
    summonerLevel: int
    name: str | None = None
    tagline: str | None = None


@dataclasses.dataclass
class LeagueEntryDTO:
    """Represents a league entry from Riot API."""

    leagueId: str
    queueType: str
    tier: str
    rank: str  # I, II, III, IV
    summonerId: str
    leaguePoints: int
    wins: int
    losses: int
    veteran: bool
    inactive: bool
    freshBlood: bool
    hotStreak: bool
