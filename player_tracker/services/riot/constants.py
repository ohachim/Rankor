"""Defines constants for the service."""

from enum import Enum


class QueueType(Enum):
    """Represents the queue type (flex, ranked)."""

    RANKED_SOLO = "RANKED_SOLO_5x5"
    RANKED_FLEX = "RANKED_FLEX_SR"


class Region(Enum):
    """API targeted region."""

    euw = ("europe", "euw1")
    na = ("americas", "na1")
    kr = ("asia", "kr")
    # Add other regions as needed

    def __init__(self, routing_value: str, platform_value: str) -> None:
        self.routing_value = routing_value
        self.platform_value = platform_value

    @property
    def platform(self) -> str:
        """Get the platform-specific value."""
        return self.platform_value

    @property
    def routing(self) -> str:
        """Get the routing value."""
        return self.routing_value


class APIEndpoint:
    """API endpoints."""

    BASE_URL = "https://{region}.api.riotgames.com"

    # Account Endpoint
    ACCOUNT_BY_SUMMONER_NAME_WITH_TAGLINE = (
        "/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tagline}"
    )

    SUMMONER_BY_PUUID = "/lol/summoner/v4/summoners/by-puuid/{puuid}"
    # Summoner Endpoints
    # SUMMONER_BY_NAME = "/lol/summoner/v4/summoners/by-name/{summoner_name}" ### Obsolete?
    SUMMONER_BY_ID = "/log/summoner/v4/summoners/{encrypted_summoner_id}"

    # league endpoint
    LEAGUE_BY_SUMMONER = "/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"


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
