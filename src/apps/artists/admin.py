from django.contrib import admin

from .infrastructure.models import ArtistModel


@admin.register(ArtistModel)
class ArtistModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "followers_count",
        "is_verified",
        "created_at",
    )
    search_fields = ("name",)
    list_filter = ("is_verified",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "followers_count")
