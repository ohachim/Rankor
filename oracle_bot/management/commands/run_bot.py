"""Management command to run the Oracle bot."""

import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from oracle_bot.client import Oracle

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to run the Discord bot."""

    help = "Runs the Oracle Discord bot"

    def handle(self, *args, **options) -> None:
        """Run the bot."""
        try:
            bot = Oracle()
            logger.info("Starting Oracle bot...")
            bot.run(settings.DISCORD_BOT_TOKEN)
        except Exception as e:
            logger.error("Failed to start bot", exc_info=True)
            raise
