from django.apps import AppConfig


class FavoritesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.favorites'
    verbose_name = 'Favorites'
    
    def ready(self):
        # Importar señales si las hay
        try:
            import apps.favorites.signals
        except ImportError:
            pass
