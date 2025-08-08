from django.contrib import admin

from .infrastructure.models import ArtistModel


@admin.register(ArtistModel)
class ArtistModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "get_featured_genres",
        "get_main_genre",
        "get_album_count",
        "followers_count",
        "is_verified",
        "created_at",
    )
    def get_featured_genres(self, obj):
        # Simulación de géneros destacados según el nombre del artista
        featured = {
            "Led Zeppelin": "Rock, Hard Rock",
            "Queen": "Rock, Pop Rock",
            "The Beatles": "Rock, Pop",
            "Blake Shelton": "Country",
            "Brett Young": "Country, Pop",
            "Marc Anthony": "Salsa, Latin Pop",
            "Jennie Ruby Jane": "K-Pop, Pop",
            "NATTI NATASHA": "Reggaeton, Latin Pop",
            "SZA": "R&B, Soul",
            "KISS OF LIFE": "K-Pop",
            "H.E.R.": "R&B, Soul",
            "SMTOWN": "K-Pop, Pop",
            "GloRilla": "Hip-Hop, Rap",
        }
        return featured.get(obj.name, "Pop, Rock")
    get_featured_genres.short_description = "Géneros destacados"
    def get_main_genre(self, obj):
        # Suponiendo que hay un campo genre o main_genre
        return getattr(obj, "genre", None) or getattr(obj, "main_genre", None) or "-"
    get_main_genre.short_description = "Género principal"
    list_per_page = 20

    def get_album_count(self, obj):
        # Suponiendo que hay una relación albums
        count = getattr(obj, "albums", None)
        if count is not None:
            total = count.count() if hasattr(count, "count") else len(count)
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse("admin:albums_albummodel_changelist") + f"?artist__id__exact={obj.id}"
            return format_html('<a href="{}">{}</a>', url, total)
        return 0
    get_album_count.short_description = "Álbumes"
    search_fields = ("name",)
    list_filter = ("is_verified",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "followers_count")
