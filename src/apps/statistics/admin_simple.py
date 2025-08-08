from django.contrib import admin
from django.db.models import Sum

from apps.artists.infrastructure.models.artist_model import ArtistModel
from apps.songs.infrastructure.models.song_model import SongModel

from .models import StatisticsModel


class StatisticsAdmin(admin.ModelAdmin):
    """Admin simple para estadísticas sin gráficos"""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Vista simple con solo tablas HTML"""

        # Top 10 artistas
        top_artists = (
            ArtistModel.objects.annotate(total_plays=Sum("songs__play_count"))
            .filter(total_plays__gt=0)
            .order_by("-total_plays")[:10]
        )

        # Top 10 canciones
        top_songs = (
            SongModel.objects.select_related("artist")
            .filter(play_count__gt=0)
            .order_by("-play_count")[:10]
        )

        # Crear HTML simple
        html_content = "<h1>Estadísticas Musicales</h1>"

        html_content += "<h2>Top 10 Artistas</h2><table border='1'>"
        for i, artist in enumerate(top_artists, 1):
            html_content += f"<tr><td>{i}</td><td>{artist.name}</td><td>{artist.total_plays}</td></tr>"
        html_content += "</table>"

        html_content += "<h2>Top 10 Canciones</h2><table border='1'>"
        for i, song in enumerate(top_songs, 1):
            html_content += (
                f"<tr><td>{i}</td><td>{song.title}</td><td>{song.play_count}</td></tr>"
            )
        html_content += "</table>"

        from django.http import HttpResponse

        return HttpResponse(html_content)


admin.site.register(StatisticsModel, StatisticsAdmin)
