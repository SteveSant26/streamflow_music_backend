from django.db import models


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    email = models.EmailField(editable=False, unique=True)
    password = models.CharField(max_length=255)  # Campo para la contraseña
    profile_picture = models.CharField(
        max_length=255,
        blank=True,
        null=True,  # NOSONAR
    )

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.email
