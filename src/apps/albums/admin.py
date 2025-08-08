from django.contrib import admin

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

    def get_artist(self, obj):
        # Suponiendo que hay un campo artist o banda relacionado
        return getattr(obj, "artist", None) or getattr(obj, "banda", None) or "-"
    get_artist.short_description = "Artista/Banda"
    search_fields = ("title",)
    list_filter = ("release_date",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "play_count")
