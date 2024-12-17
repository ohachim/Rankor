"""Constants for the Discord bot."""

from enum import Enum


class BotColors(Enum):
    """Colors used for Discord embeds."""

    SUCCESS = 0x57F287  # Discord green
    ERROR = 0xED4245  # Discord red
    INFO = 0x3498DB  # Blue
    WARNING = 0xFEE75C  # Yellow


class MessageConstants:
    """Constants for bot messages."""

    # Registration messages
    SUMMONER_REGISTERED = (
        "Successfully registered `{summoner_name}` to your Discord account."
    )
    SUMMONER_ALREADY_REGISTERED = (
        "You already have a registered summoner. Use /update to change it."
    )
    SUMMONER_NOT_FOUND = (
        "Could not find summoner `{summoner_name}`` in region {region}."
    )

    # Rank messages
    RANK_NOT_FOUND = "No ranked data found for {summoner_name}."

    # Error messages
    GENERIC_ERROR = "An error occurred. Please try again later."
    RIOT_API_ERROR = "Unable to connect to Riot servers. Please try again later."


class CommandDescription:
    """Help text for commands."""

    REGISTER = "Register your League of Legends account"
    RANK = "Display your current rank"
    UPDATE = "Update your registered summoner name"
