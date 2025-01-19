"""Bot responsible for communicating with backend and Discord server."""

import logging

import nextcord
from django.conf import settings
from django.core.management.base import BaseCommand
from nextcord.ext import commands

from player_tracker.services.riot.service import RiotAPIService
from oracle.management.cogs import summoner_cogs
from player_tracker.services.summoner.service import SummonerService

logger = logging.getLogger("nextcord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="nextcord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


class OracleBot(commands.Bot):
    """Main bot class for Oracle."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.riot_service: RiotAPIService | None = None
        self.summoner_service: SummonerService | None = None

    async def on_ready(self):
        """Called when bot is ready."""
        print(f"Bot ready and logged in as {self.user}")
        print(settings.RIOT_API_KEY, "WTf")
        self.riot_service = RiotAPIService(api_key=settings.RIOT_API_KEY)
        self.summoner_service = SummonerService(self.riot_service)
        print(self.summoner_service)

        self.add_cog(summoner_cogs.SummonerProfileCog(self))


class Command(BaseCommand):
    """Django command to run the Discord bot."""

    help = "Runs the Discord bot"

    def handle(self, *args, **options):
        """Command execution."""
        intents = nextcord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.messages = True

        bot = OracleBot(
            command_prefix="!",
            intents=intents,
            description="Oracle - League Player Tracker",
        )
        try:
            bot.run(settings.DISCORD_BOT_TOKEN)
        except Exception as e:
            self.stderr.write(f"Error running bot: {e}")
