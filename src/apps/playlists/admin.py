from django.contrib import admin

from apps.playlists.infrastructure.models import PlaylistModel, PlaylistSongModel


@admin.register(PlaylistModel)
class PlaylistModelAdmin(admin.ModelAdmin):
    """Admin para PlaylistModel"""

    list_display = [
        "name",
        "user",
        "is_default",
        "is_public",
        "total_songs",
        "get_song_titles",
        "created_at",
    ]
    list_filter = ["is_default", "is_public", "created_at"]
    search_fields = ["name", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at", "total_songs"]
    list_per_page = 20

    fieldsets = (
        ("Información básica", {"fields": ("id", "name", "description", "user")}),
        ("Configuración", {"fields": ("is_default", "is_public")}),
        (
            "Metadatos",
            {
                "fields": ("total_songs", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_song_titles(self, obj):
        # Suponiendo que hay una relación songs
        songs = getattr(obj, "songs", None)
        if songs:
            return ", ".join([str(s) for s in songs.all()[:3]])
        return "-"
    get_song_titles.short_description = "Canciones destacadas"


@admin.register(PlaylistSongModel)
class PlaylistSongModelAdmin(admin.ModelAdmin):
    """Admin para PlaylistSongModel"""

    list_display = ["playlist", "song", "position", "added_at", "get_song_artist"]
    list_filter = ["added_at", "playlist__is_default"]
    search_fields = ["playlist__name", "song__title"]
    readonly_fields = ["id", "added_at"]
    list_per_page = 20

    fieldsets = (
        ("Información básica", {"fields": ("id", "playlist", "song", "position")}),
        ("Metadatos", {"fields": ("added_at",), "classes": ("collapse",)}),
    )

    def get_song_artist(self, obj):
        # Suponiendo que song tiene un campo artist
        song = getattr(obj, "song", None)
        if song and hasattr(song, "artist"):
            return str(song.artist)
        return "-"
    get_song_artist.short_description = "Artista/Banda"
