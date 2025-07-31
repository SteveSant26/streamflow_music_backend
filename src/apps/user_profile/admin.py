from django.contrib import admin

from .infrastructure.models import UserProfileModel

# Register your models here.
admin.site.register(UserProfileModel)
