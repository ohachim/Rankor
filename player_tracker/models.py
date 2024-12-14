
from django.db import models


class SummonerProfile(models.Model):
    """Represents a summoner related to a discord id."""

    discord_id = models.CharField(max_length=20, unique=True, db_index=True)
    summoner_name = models.CharField(max_length=100, db_index=True)
    puuid = models.CharField(max_length=100, db_index=True)

    REGIONS = [
        ("EUW1", "Europe West"),
        ("NA1", "North America"),
        ("KR", "Korea"),
        # (TODO: add other regions)
    ]

    server_region = models.CharField(max_length=5, choices=REGIONS, default="EUW1")

    RANKS = [
        ("IRON", "Iron"),
        ("BRONZE", "Bronze"),
        ("SILVER", "Silver"),
        ("GOLD", "Gold"),
        ("PLATINUM", "Platinum"),
        ("EMERALD", "Emerald"),
        ("DIAMOND", "Diamond"),
        ("MASTER", "Master"),
        ("GRANDMASTER", "Grandmaster"),
        ("CHALLENGER", "Challenger"),
        ("UNRANKED", "Unranked"),
    ]

    DIVISIONS = [
        ("I", "I"),
        ("II", "II"),
        ("III", "III"),
        ("IV", "IV"),
    ]

    current_solo_rank = models.CharField(
        max_length=20,
        choices=RANKS,
        default="UNRANKED",
    )

    current_solo_division = models.CharField(
        max_length=20,
        choices=DIVISIONS,
        null=True,
        blank=True,
    )

    highest_achieved_rank_solo = models.CharField(
        max_length=20, choices=RANKS, default="UNRANKED"
    )

    current_solo_lp = models.IntegerField(default=0)

    current_flex_rank = models.CharField(
        max_length=20,
        choices=RANKS,
        default="UNRANKED",
    )

    current_flex_division = models.CharField(
        max_length=20,
        choices=DIVISIONS,
        null=True,
        blank=True,
    )
    highest_achieved_rank_flex = models.CharField(
        max_length=20, choices=RANKS, default="UNRANKED"
    )

    current_flex_lp = models.IntegerField(default=0)

    last_check_timestamp = models.DateTimeField(
        auto_now=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.summoner_name} ({self.server_region})"

    class Meta:
        verbose_name = "Summoner Profile"
        verbose_name_plural = "Summoner Profiles"
