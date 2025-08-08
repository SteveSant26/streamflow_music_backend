import json
from datetime import timedelta

from django.contrib import admin
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from apps.artists.infrastructure.models.artist_model import ArtistModel
from apps.songs.infrastructure.models.song_model import SongModel

from .models import (
    StatisticsModel,
    UserPlayHistoryModel,
    UserFavoriteArtistModel,
    UserFavoriteSongModel,
    UserListeningSessionModel
)


class StatisticsAdmin(admin.ModelAdmin):
    """Admin personalizado para mostrar estadísticas musicales"""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Vista personalizada para mostrar estadísticas con gráficos mejorados"""

        # Top 10 artistas y canciones
        top_artists = (
            ArtistModel.objects.annotate(total_plays=Sum("songs__play_count"))
            .filter(total_plays__gt=0)
            .order_by("-total_plays")[:10]
        )

        top_songs = (
            SongModel.objects.select_related("artist")
            .filter(play_count__gt=0)
            .order_by("-play_count")[:10]
        )

        artists_data = {
            "labels": [
                artist.name[:30] + "..." if len(artist.name) > 30 else artist.name
                for artist in top_artists
            ],
            "data": [
                artist.__dict__.get("total_plays", 0) or 0 for artist in top_artists
            ],
        }

        songs_data = {
            "labels": [
                f"{song.title[:25]}{'...' if len(song.title) > 25 else ''}"
                for song in top_songs
            ],
            "data": [song.play_count for song in top_songs],
        }

        # === Estadísticas generales ===
        total_songs = SongModel.objects.count()
        total_artists = ArtistModel.objects.count()
        total_plays = SongModel.objects.aggregate(total=Sum("play_count"))["total"] or 0
        avg_plays_per_song = round(
            (total_plays or 0)
            / max(SongModel.objects.filter(play_count__gt=0).count(), 1)
        )

        # === Sparkline y tendencia semanal ===
        today = timezone.now().date()
        days = 14  # 7 días actuales + 7 previos

        # Agrupar reproducciones por día (últimos 14 días)
        plays_by_day_qs = (
            SongModel.objects.filter(
                created_at__date__gte=today - timedelta(days=days - 1)
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .order_by("day")
            .annotate(total=Sum("play_count"))
        )
        # Dict {fecha: total}
        plays_by_day = {item["day"]: item["total"] for item in plays_by_day_qs}

        # Completar días faltantes con 0
        sparkline_labels = []
        sparkline_data = []
        for i in range(days):
            day = today - timedelta(days=days - 1 - i)
            sparkline_labels.append(day.strftime("%d-%b"))
            sparkline_data.append(plays_by_day.get(day, 0))

        # Suma semana actual y anterior
        last_week_sum = sum(sparkline_data[7:14])
        prev_week_sum = sum(sparkline_data[0:7])
        if prev_week_sum > 0:
            trend = round((last_week_sum - prev_week_sum) / prev_week_sum * 100, 1)
        else:
            trend = 0.0

        stats_summary = {
            "total_songs": total_songs,
            "total_artists": total_artists,
            "total_plays": total_plays,
            "avg_plays_per_song": avg_plays_per_song,
            "trend": trend,
            "sparkline_data": sparkline_data,
            "sparkline_labels": sparkline_labels,
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


@admin.register(UserPlayHistoryModel)
class UserPlayHistoryAdmin(admin.ModelAdmin):
    """Admin para historial de reproducciones"""
    list_display = ('user', 'song', 'played_at', 'duration_played', 'completed', 'source')
    list_filter = ('played_at', 'completed', 'source', 'device_type')
    search_fields = ('user__user__username', 'song__title', 'song__artist__name')
    date_hierarchy = 'played_at'
    ordering = ('-played_at',)
    readonly_fields = ('id', 'played_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'song', 'song__artist')


@admin.register(UserFavoriteArtistModel)
class UserFavoriteArtistAdmin(admin.ModelAdmin):
    """Admin para artistas favoritos"""
    list_display = ('user', 'artist', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__user__username', 'artist__name')
    date_hierarchy = 'added_at'
    ordering = ('-added_at',)
    readonly_fields = ('id', 'added_at')


@admin.register(UserFavoriteSongModel)
class UserFavoriteSongAdmin(admin.ModelAdmin):
    """Admin para canciones favoritas"""
    list_display = ('user', 'song', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__user__username', 'song__title', 'song__artist__name')
    date_hierarchy = 'added_at'
    ordering = ('-added_at',)
    readonly_fields = ('id', 'added_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'song', 'song__artist')


@admin.register(UserListeningSessionModel)
class UserListeningSessionAdmin(admin.ModelAdmin):
    """Admin para sesiones de escucha"""
    list_display = ('user', 'started_at', 'ended_at', 'songs_played', 'duration_hours', 'device_type')
    list_filter = ('started_at', 'device_type')
    search_fields = ('user__user__username',)
    date_hierarchy = 'started_at'
    ordering = ('-started_at',)
    readonly_fields = ('id', 'started_at', 'duration_hours')
    
    def duration_hours(self, obj):
        """Muestra duración en horas"""
        return f"{obj.duration_hours:.2f}h"
    duration_hours.short_description = "Duración (horas)"


admin.site.register(StatisticsModel, StatisticsAdmin)
