# from .infrastructure.models import ArtistModel
# admin.site.register(ArtistModel)

from django.contrib import admin

from .infrastructure.models import ArtistModel

admin.site.register(ArtistModel)
