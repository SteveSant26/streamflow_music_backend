from django.contrib import admin
from .infrastructure.models import ArtistModel


@admin.register(ArtistModel)
class ArtistModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "country",
        "followers_count",
        "is_verified",
        "is_active",
        "created_at",
    )
    search_fields = (
        "name",
        "country",
    )
    list_filter = (
        "is_verified",
        "is_active",
        "country",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "followers_count")
