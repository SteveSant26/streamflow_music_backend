from django.contrib import admin
from .infrastructure.models import GenreModel
from django.utils.html import format_html


@admin.register(GenreModel)
class GenreModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "popularity_score",
        "color_box",
        "is_active",
        "created_at",
        "image_preview",
    )
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("-popularity_score", "name")
    readonly_fields = ("created_at", "updated_at", "popularity_score")

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.image_url
            )
        return "-"
    image_preview.short_description = "Imagen"

    def color_box(self, obj):
        if obj.color_hex:
            return format_html(
                '<div style="width: 24px; height: 24px; background-color: {}; border: 1px solid #ccc;"></div>',
                obj.color_hex
            )
        return "-"
    color_box.short_description = "Color"
