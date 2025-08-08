from django.contrib import admin
from django.utils.html import format_html

from .infrastructure.models import GenreModel


@admin.register(GenreModel)
class GenreModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "popularity_score",
        "get_featured_artists",
        "color_box",
        "created_at",
        "image_preview",
    )
    list_per_page = 20

    def get_featured_artists(self, obj):
        # Suponiendo que hay una relación artists o similar
        artists = getattr(obj, "artists", None)
        if artists:
            from django.urls import reverse
            from django.utils.html import format_html, format_html_join
            links = format_html_join(
                ", ",
                '<a href="{}">{}</a>',
                [
                    (reverse("admin:artists_artistmodel_change", args=[a.id]), str(a))
                    for a in artists.all()[:3]
                ]
            )
            return links or "-"
        return "-"
    get_featured_artists.short_description = "Artistas destacados"
    search_fields = ("name",)
    list_filter = ()
    ordering = ("-popularity_score", "name")
    readonly_fields = ("created_at", "updated_at", "popularity_score")

    @admin.display(description="Imagen")
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.image_url,
            )
        return "-"

    @admin.display(description="Color")
    def color_box(self, obj):
        if obj.color_hex:
            return format_html(
                '<div style="width: 24px; height: 24px; background-color: {}; border: 1px solid #ccc;"></div>',
                obj.color_hex,
            )
        return "-"
