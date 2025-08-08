from django.contrib import admin

from .infrastructure.models import SongModel


@admin.register(SongModel)
class SongModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "get_artist",
        "get_album",
        "duration_formatted",
        "play_count",
        "favorite_count",
        "audio_quality",
        "release_date",
        "created_at",
    )
    list_per_page = 20

    def get_artist(self, obj):
        return obj.artist if obj.artist else "-"
    get_artist.short_description = "Artista/Banda"

    def get_album(self, obj):
        return obj.album if obj.album else "-"
    get_album.short_description = "Álbum"
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
