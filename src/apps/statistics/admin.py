import json

from django.contrib import admin
from django.db.models import Sum
from django.shortcuts import render

from apps.artists.infrastructure.models.artist_model import ArtistModel
from apps.songs.infrastructure.models.song_model import SongModel

from .models import StatisticsModel


class StatisticsAdmin(admin.ModelAdmin):
    """Admin personalizado para mostrar estadísticas musicales"""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Vista personalizada para mostrar estadísticas con gráficos"""

        # Obtener top 10 artistas más escuchados
        top_artists = (
            ArtistModel.objects.annotate(total_plays=Sum("songs__play_count"))
            .filter(total_plays__gt=0)
            .order_by("-total_plays")[:10]
        )

        # Obtener top 10 canciones más reproducidas
        top_songs = (
            SongModel.objects.select_related("artist")
            .filter(play_count__gt=0)
            .order_by("-play_count")[:10]
        )

        # Preparar datos para gráficos (truncar nombres largos)
        artists_data = {
            "labels": [
                artist.name[:30] + "..." if len(artist.name) > 30 else artist.name
                for artist in top_artists
            ],
            "data": [artist.total_plays or 0 for artist in top_artists],
        }

        songs_data = {
            "labels": [
                f"{song.title[:25]}{'...' if len(song.title) > 25 else ''}"
                for song in top_songs
            ],
            "data": [song.play_count for song in top_songs],
        }

        # Estadísticas generales
        stats_summary = {
            "total_songs": SongModel.objects.count(),
            "total_artists": ArtistModel.objects.count(),
            "total_plays": SongModel.objects.aggregate(total=Sum("play_count"))["total"]
            or 0,
            "avg_plays_per_song": round(
                (SongModel.objects.aggregate(total=Sum("play_count"))["total"] or 0)
                / max(SongModel.objects.filter(play_count__gt=0).count(), 1)
            ),
        }

        extra_context = extra_context or {}
        extra_context.update(
            {
                "title": "Estadísticas Musicales",
                "top_artists": top_artists,
                "top_songs": top_songs,
                "artists_chart_data": json.dumps(artists_data),
                "songs_chart_data": json.dumps(songs_data),
                "stats_summary": stats_summary,
            }
        )

        return render(
            request, "admin/statistics/statistics_dashboard.html", extra_context
        )


# Registrar el modelo proxy con el admin personalizado
admin.site.register(StatisticsModel, StatisticsAdmin)
