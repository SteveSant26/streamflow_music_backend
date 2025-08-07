from django.contrib import admin

from .infrastructure.models import SongModel


@admin.register(SongModel)
class SongModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "duration_formatted",
        "play_count",
        "favorite_count",
        "audio_quality",
        "release_date",
        "created_at",
    )
    search_fields = (
        "title",
        "source_id",
    )
    list_filter = (
        "audio_quality",
        "source_type",
        "created_at",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "last_played_at",
        "play_count",
        "favorite_count",
        "download_count",
    )
