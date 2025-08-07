from django.contrib import admin

from .infrastructure.models import SongModel

@admin.register(SongModel)
class SongModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "artist_name",
        "album_title",
        "genre_name",
        "duration_formatted",
        "play_count",
        "favorite_count",
        "is_active",
        "is_premium",
        "audio_quality",
        "release_date",
        "created_at",
    )
    search_fields = (
        "title",
        "artist_name",
        "album_title",
        "genre_name",
        "source_id",
    )
    list_filter = (
        "is_active",
        "is_premium",
        "is_explicit",
        "audio_quality",
        "source_type",
        "created_at",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "last_played_at", "play_count", "favorite_count", "download_count")
