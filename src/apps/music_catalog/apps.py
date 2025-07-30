from django.apps import AppConfig


class MusicCatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.music_catalog'
    verbose_name = 'Music Catalog'
    
    def ready(self):
        """
        Configuración que se ejecuta cuando la app está lista
        """
        pass
