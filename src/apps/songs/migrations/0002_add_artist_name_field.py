# Generated migration for song model changes

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("songs", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="songmodel",
            name="artist_name",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Nombre del artista desnormalizado para rendimiento",
                max_length=200,
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name="songmodel",
            index=models.Index(fields=["artist_name"], name="songs_artist_name_idx"),
        ),
    ]
