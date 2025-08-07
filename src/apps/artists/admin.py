<<<<<<< HEAD
# from .infrastructure.models import ArtistModel
# admin.site.register(ArtistModel)

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
from django.contrib import admin

from .infrastructure.models import ArtistModel

<<<<<<< HEAD
admin.site.register(ArtistModel)
=======

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
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
