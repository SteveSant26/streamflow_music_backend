from django.db import models


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    email = models.EmailField(editable=False, unique=True)

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.email
