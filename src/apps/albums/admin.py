from django.contrib import admin
from .infrastructure.models import AlbumModel

@admin.register(AlbumModel)
class AlbumModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "artist_name",
        "release_date",
        "total_tracks",
        "play_count",
        "is_active",
        "created_at",
    )
    search_fields = (
        "title",
        "artist_name",
    )
    list_filter = (
        "is_active",
        "release_date",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "play_count")
