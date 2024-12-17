"""Oracle Discord bot client."""

import logging
from typing import Any

import nextcord

# from django.conf import settings
# from nextcord import Interaction
from nextcord.ext import commands

logger = logging.getLogger(__name__)


class Oracle(commands.Bot):
    """Main bot class for Oracle."""

    def __init__(self) -> None:
        """Initialize the bot with required intents and settings."""
        intents = nextcord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="/",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        """Set up bot cogs and any initialization that needs to be done."""
        logger.info("Setting up Oracle bot...")

        try:
            await self.load_extension("oracle_bot.cogs.registration")
            logger.info("Successfully loaded registration cog.")
        except Exception as e:
            logger.info("Failed to load registration cog: %s", e)

    async def on_ready(self) -> None:
        """Called when the bot is ready and connected to Discord."""
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("Registered commands:")
        for command in self.get_application_commands():
            print(f"- {command.name}")

    async def on_error(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Handle any errors that occur in the bot.

        Args:
            event: The event that caused the error
            args: Positional arguments from the event
            kwargs: Keyword arguments from the event
        """
        logger.error(f"Error in {event}", exc_info=True)
