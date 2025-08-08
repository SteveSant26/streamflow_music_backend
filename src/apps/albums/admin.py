
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .infrastructure.models import AlbumModel


@admin.register(AlbumModel)
class AlbumModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "get_artist",
        "release_date",
        "total_tracks",
        "play_count",
        "created_at",
    )
    list_per_page = 20

    from django.utils.html import format_html
    from django.urls import reverse

    def get_artist(self, obj):
        artist = getattr(obj, "artist", None) or getattr(obj, "banda", None)
        if artist:
            url = reverse("admin:artists_artistmodel_change", args=[artist.id])
            return format_html('<a href="{}">{}</a>', url, artist)
        return "-"
    get_artist.short_description = "Artista/Banda"
    search_fields = ("title",)
    list_filter = ("release_date",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "play_count")
