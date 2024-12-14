from django.contrib import admin

from .models import SummonerProfile


# Register your models here.
@admin.register(SummonerProfile)
class SummonerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "summoner_name",
        "discord_id",
        "server_region",
        "current_solo_rank",
        "current_flex_rank",
        "is_active",
    )
    list_filter = (
        "server_region",
        "current_solo_rank",
        "current_flex_rank",
        "is_active",
    )
    search_fields = (
        "summoner_name",
        "discord_id",
        "puuid",
    )
    readonly_fields = ("last_check_timestamp",)

    fieldsets = (
        (
            "Player Information",
            {"fields": ("discord_id", "summoner_name", "puuid", "server_region")},
        ),
        (
            "Solo Queue",
            {
                "fields": (
                    "current_solo_rank",
                    "current_solo_division",
                    "current_solo_lp",
                    "highest_achieved_rank_solo",
                )
            },
        ),
        (
            "Flex Queue",
            {
                "fields": (
                    "current_flex_rank",
                    "current_flex_division",
                    "current_flex_lp",
                    "highest_achieved_rank_flex",
                )
            },
        ),
        (
            "Additional Information",
            {"fields": ("last_check_timestamp", "is_active")},
        ),
    )
