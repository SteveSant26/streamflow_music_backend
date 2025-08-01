# from .infrastructure.models import SongModel
# admin.site.register(SongModel)

from django.contrib import admin
from .infrastructure.models import SongModel

admin.site.register(SongModel)
