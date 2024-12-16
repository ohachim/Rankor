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
from .types import LeagueEntryDTO, SummonerDTO


class RiotAPIService:
    """Service for making requests to the Riot API."""

    _shared_session: ClassVar[aiohttp.ClientSession | None] = None

    def __init__(
        self,
        api_key: str,
        region: Region = Region.EUW1,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Service Initializer.
        Args:
            api_key: The Riot API key.
            region: The region to make requests to. Defaults to EUW1.
            session: Optional aiohttp session. If not provided, one will be created.
        """

        self._API_KEY = api_key
        self._session: aiohttp.ClientSession = session
        self._base_url: str = APIEndpoint.BASE_URL.format(region=region.value)

    @classmethod
    async def create(
        cls, api_key: str, region: Region = Region.EUW1
    ) -> "RiotAPIService":
        """Create a service instance with shared session management.

        Args:
            api_key: The Riot API key.
            region: The region to make requests to.

        Returns:
            A configured RiotAPIService instance.
        """
        if cls._shared_session is None or cls._shared_session.closed:
            cls._shared_session = aiohttp.ClientSession()
        return cls(api_key, region, session=cls._shared_session)

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the aiohttp session.

        Returns:
            The shared session if available, otherwise creates a new session.
        """
        if self._session is None or self._session.closed:
            if self._shared_session is not None and not self._shared_session.closed:
                self._session = self._shared_session
            else:
                self._session = aiohttp.ClientSession()
        return self._session

    @classmethod
    async def close_shared_session(cls) -> None:
        """Close the shared session if it exists."""
        if cls._shared_session and not cls._shared_session.closed:
            await cls._shared_session.close()
            cls._shared_session = None

    async def close(self) -> None:
        """Close the service's session if it's not the shared session."""
        if (
            self._session
            and not self._session.closed
            and self._session is not self._shared_session
        ):
            await self._session.close()

    async def _make_request(
        self,
        endpoint: str,
        *,
        params: dict | None = None,
    ) -> dict:
        """Make a request to the Riot API.

        Args:
            endpoint: The API endpoint to request.
            params: Optional query parameters.

        Returns:
            The JSON response from the API.

        Raises:
            RateLimitError: If the API rate limit is exceeded.
            AuthenticationError: If there are API key issues.
            ServiceUnavailableError: If the Riot API is unavailable.
            RiotAPIError: For other API-related errors.
        """
        headers = {
            "X-Riot-Token": self._API_KEY,
        }

        url = f"{self._base_url}{endpoint}"

        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == APIStatusCode.TOO_MANY_REQUESTS:
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=response.status,
                )
            elif response.status == APIStatusCode.FORBIDDEN:
                raise AuthenticationError(
                    "Invalid API key",
                    status_code=response.status,
                )
            elif response.status == APIStatusCode.SERVICE_UNAVAILABLE:
                raise ServiceUnavailableError(
                    "Riot API is unavailable",
                    status_code=response.status,
                )
            elif response.status != APIStatusCode.OK:
                raise RiotAPIError(
                    f"API request failed with status {response.status}",
                    status_code=response.status,
                )

            return await response.json()

    async def get_summoner_by_name(
        self,
        summoner_name: str,
    ) -> SummonerDTO:
        """Fetch summoner information by summoner name.

        Args:
            summoner_name: The name of the summoner to look up.

        Returns:
            SummonerDTO containing the summoner's information.

        Raises:
            SummonerNotFoundError: If the summoner doesn't exist.
            RiotAPIError: For other API-related errors.
        """
        endpoint = APIEndpoint.SUMMONER_BY_NAME.format(summoner_name=summoner_name)

        try:
            data = await self._make_request(endpoint)
            return SummonerDTO(**data)
        except aiohttp.ClientResponseError as e:
            if e.status == APIStatusCode.NOT_FOUND:
                raise SummonerNotFoundError(
                    f"Summoner {summoner_name} not found"
                ) from e
            raise

    async def get_league_entries(
        self,
        encrypted_summoner_id: str,
    ) -> list[LeagueEntryDTO]:
        """Fetch league entries for a summoner.

        Args:
            encrypted_summoner_id: The encrypted summoner ID from SummonerDTO.

        Returns:
            List of LeagueEntryDTO containing rank information.

        Raises:
            RiotAPIError: For API-related errors.
        """
        endpoint = APIEndpoint.LEAGUE_BY_SUMMONER.format(
            encrypted_summoner_id=encrypted_summoner_id
        )

        data = await self._make_request(endpoint)
        return [LeagueEntryDTO(**entry) for entry in data]
