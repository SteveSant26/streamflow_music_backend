from django.contrib import admin

from apps.playlists.infrastructure.models import PlaylistModel, PlaylistSongModel


@admin.register(PlaylistModel)
class PlaylistModelAdmin(admin.ModelAdmin):
    """Admin para PlaylistModel"""
    
    list_display = ["name", "user", "is_default", "is_public", "total_songs", "created_at"]
    list_filter = ["is_default", "is_public", "created_at"]
    search_fields = ["name", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at", "total_songs"]
    
    fieldsets = (
        ("Información básica", {
            "fields": ("id", "name", "description", "user")
        }),
        ("Configuración", {
            "fields": ("is_default", "is_public")
        }),
        ("Metadatos", {
            "fields": ("total_songs", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(PlaylistSongModel)
class PlaylistSongModelAdmin(admin.ModelAdmin):
    """Admin para PlaylistSongModel"""
    
    list_display = ["playlist", "song", "position", "added_at"]
    list_filter = ["added_at", "playlist__is_default"]
    search_fields = ["playlist__name", "song__title"]
    readonly_fields = ["id", "added_at"]
    
    fieldsets = (
        ("Información básica", {
            "fields": ("id", "playlist", "song", "position")
        }),
        ("Metadatos", {
            "fields": ("added_at",),
            "classes": ("collapse",)
        }),
    )
