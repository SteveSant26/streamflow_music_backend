
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

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

    from django.utils.html import format_html
    from django.urls import reverse

    def get_artist(self, obj):
        if obj.artist:
            url = reverse("admin:artists_artistmodel_change", args=[obj.artist.id])
            return format_html('<a href="{}">{}</a>', url, obj.artist)
        return "-"
    get_artist.short_description = "Artista/Banda"

    def get_album(self, obj):
        if obj.album:
            url = reverse("admin:albums_albummodel_change", args=[obj.album.id])
            return format_html('<a href="{}">{}</a>', url, obj.album)
        return "-"
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
