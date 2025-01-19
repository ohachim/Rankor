"""Service for interacting with Riot API."""

from typing import ClassVar

import aiohttp

from .constants import APIEndpoint, APIStatusCode, Region
from .exceptions import (
    AuthenticationError,
    RateLimitError,
    RiotAPIError,
    ServiceUnavailableError,
    SummonerNotFoundError,
)
from .types import LeagueEntryDTO, SummonerDTO, RiotAccountDTO


class RiotAPIService:
    """Service for making requests to the Riot API."""

    _shared_session: ClassVar[aiohttp.ClientSession | None] = None

    def __init__(
        self,
        api_key: str,
        region: Region = Region.euw,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Service Initializer.
        Args:
            api_key: The Riot API key.
            region: The region to make requests to. Defaults to EUW.
            session: Optional aiohttp session. If not provided, one will be created.
        """
        self._API_KEY = api_key
        self._session: aiohttp.ClientSession = session
        self._region = region
        # Don't set base_url in init as it depends on the endpoint

    @classmethod
    async def create(
        cls, api_key: str, region: Region = Region.euw
    ) -> "RiotAPIService":
        """Create a service instance with shared session management."""
        if cls._shared_session is None or cls._shared_session.closed:
            cls._shared_session = aiohttp.ClientSession()
        return cls(api_key, region, session=cls._shared_session)

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the aiohttp session."""
        if self._session is None or self._session.closed:
            if self._shared_session is not None and not self._shared_session.closed:
                self._session = self._shared_session
            else:
                self._session = aiohttp.ClientSession()
        return self._session

    def _get_base_url(self, use_routing: bool = False) -> str:
        """Get the appropriate base URL based on endpoint type.

        Args:
            use_routing: If True, use routing value (e.g., 'europe'),
                        otherwise use platform value (e.g., 'euw1')
        """
        region_value = self._region.routing if use_routing else self._region.platform
        return APIEndpoint.BASE_URL.format(region=region_value)

    async def _make_request(
        self,
        endpoint: str,
        *,
        use_routing: bool = False,
        params: dict | None = None,
    ) -> dict:
        """Make a request to the Riot API.

        Args:
            endpoint: The API endpoint to request.
            use_routing: Whether to use routing value instead of platform.
            params: Optional query parameters.
        """
        headers = {
            "X-Riot-Token": self._API_KEY,
        }
        print(self._API_KEY)
        base_url = self._get_base_url(use_routing)
        url = f"{base_url}{endpoint}"
        print("base_url", url)
        print("We try?")
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == APIStatusCode.TOO_MANY_REQUESTS.value:
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=response.status,
                )
            elif response.status == APIStatusCode.FORBIDDEN.value:
                raise AuthenticationError(
                    "Invalid API key",
                    status_code=response.status,
                )
            elif response.status == APIStatusCode.SERVICE_UNAVAILABLE.value:
                raise ServiceUnavailableError(
                    "Riot API is unavailable",
                    status_code=response.status,
                )
            elif response.status != APIStatusCode.OK.value:
                raise RiotAPIError(
                    f"API request failed with status {response.status}",
                    status_code=response.status,
                )
            return await response.json()

    async def get_summoner_account(
        self, summoner_name: str, tagline: str, region: Region
    ) -> RiotAccountDTO:
        """Gets account data and puuid using name and tagline."""
        self._region = region  # Update region for this request
        endpoint = APIEndpoint.ACCOUNT_BY_SUMMONER_NAME_WITH_TAGLINE.format(
            summoner_name=summoner_name, tagline=tagline
        )

        try:
            data = await self._make_request(endpoint, use_routing=True)
            return RiotAccountDTO(**data)
        except aiohttp.ClientResponseError as e:
            if e.status == APIStatusCode.NOT_FOUND.value:
                raise SummonerNotFoundError(
                    f"Summoner {summoner_name} not found"
                ) from e
            raise

    async def get_summoner_by_puuid(
        self,
        puuid: str,
        name: str,
        tagline: str,
    ) -> SummonerDTO:
        """Fetch summoner information by PUUID."""
        endpoint = APIEndpoint.SUMMONER_BY_PUUID.format(puuid=puuid)

        try:
            data = await self._make_request(endpoint, use_routing=False)
            print(data)
            data["name"] = name
            data["tagline"] = tagline
            return SummonerDTO(**data)
        except aiohttp.ClientResponseError as e:
            if e.status == APIStatusCode.NOT_FOUND.value:
                raise SummonerNotFoundError(
                    f"Summoner with PUUID {puuid} not found"
                ) from e
            raise

    async def get_league_entries(
        self,
        encrypted_summoner_id: str,
    ) -> list[LeagueEntryDTO]:
        """Fetch league entries for a summoner."""
        endpoint = APIEndpoint.LEAGUE_BY_SUMMONER.format(
            encrypted_summoner_id=encrypted_summoner_id
        )

        data = await self._make_request(endpoint, use_routing=False)
        return [LeagueEntryDTO(**entry) for entry in data]

    async def close(self) -> None:
        """Close the service's session if it's not the shared session."""
        if (
            self._session
            and not self._session.closed
            and self._session is not self._shared_session
        ):
            await self._session.close()
