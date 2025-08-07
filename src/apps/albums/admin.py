from django.contrib import admin

from .infrastructure.models import AlbumModel


@admin.register(AlbumModel)
class AlbumModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "release_date",
        "total_tracks",
        "play_count",
        "created_at",
    )
    search_fields = ("title",)
    list_filter = ("release_date",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "play_count")
