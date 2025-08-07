from django.contrib import admin
from django.utils.html import format_html

from .infrastructure.models import GenreModel


@admin.register(GenreModel)
class GenreModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "popularity_score",
        "color_box",
        "created_at",
        "image_preview",
    )
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
