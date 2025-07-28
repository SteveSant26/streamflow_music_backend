from django.contrib import admin

from .infrastructure.models import UserProfile

# Register your models here.
admin.site.register(UserProfile)
