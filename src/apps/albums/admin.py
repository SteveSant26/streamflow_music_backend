# Register your models here.
# from .infrastructure.models import AlbumModel
# admin.site.register(AlbumModel)
from django.contrib import admin
from .infrastructure.models import AlbumModel  # Ajusta el nombre según tu modelo

admin.site.register(AlbumModel)