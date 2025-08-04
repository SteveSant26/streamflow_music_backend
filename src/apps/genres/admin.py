# from .infrastructure.models import GenreModel
# admin.site.register(GenreModel)

from django.contrib import admin

from .infrastructure.models import GenreModel

admin.site.register(GenreModel)
