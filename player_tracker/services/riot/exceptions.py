"""Exceptions for the Riot API service."""

from typing import Any


class RiotAPIError(Exception):
    """Base exception for all Riot API related errors."""


class RiotAPIResponseError(RiotAPIError):
    """Base exception for API response errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: Any | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: The error message.
            status_code: The HTTP status code from the API response.
            response_data: The raw response data from the API.
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimitError(RiotAPIResponseError):
    """Raised when API rate limits are exceeded."""


class AuthenticationError(RiotAPIResponseError):
    """Raised when there are API key issues."""


class SummonerNotFoundError(RiotAPIResponseError):
    """Raised when a summoner cannot be found."""


class InvalidRegionError(RiotAPIError):
    """Raised when an invalid region is provided."""


class ServiceUnavailableError(RiotAPIResponseError):
    """Raised when Riot's services are unavailable."""
