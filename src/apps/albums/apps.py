from django.apps import AppConfig


class AlbumsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.apps.albums"
    verbose_name = "Albums Management"
