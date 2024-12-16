"""Defines constants for the service."""

from enum import Enum


class QueueType(Enum):
    """Represents the queue type (flex, ranked)."""

    RANKED_SOLO = "RANKED_SOLO_SR"
    RANKED_FLEX = "RANKNED_FLEX_SR"


class Region(Enum):
    """API targeted region."""

    EUW1 = "euw1"
    NA1 = "na1"
    EUNE1 = "EUNE1"
    TR1 = "tr1"


class APIEndpoint:
    """API endpoints."""

    BASE_URL = "https://{region}.api.riotgames.com"

    # Summoner Endpoints
    SUMMONER_BY_NAME = "/lol/summoner/v4/summoners/by-name/{summoner_name}"
    SUMMONER_BY_ID = "/log/summoner/v4/summoners/{encrypted_summoner_id}"

    # league endpoint
    LEAGUE_BY_SUMMONER = "/lol/league/v4/by-summoner/{encrypted_summoner_id}"


class RateLimit:
    """Rate limits for requests to Riot Api."""

    REQUESTS_PER_SECOND = 20
    REQUESTS_PER_TWO_MINUTES = 100


class APIStatusCode(Enum):
    """HTTP status codes returned by Riot API."""

    TOO_MANY_REQUESTS = 429
    FORBIDDEN = 403
    SERVICE_UNAVAILABLE = 503
    OK = 200
    NOT_FOUND = 404
