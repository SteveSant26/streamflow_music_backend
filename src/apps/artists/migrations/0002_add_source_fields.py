# Generated migration for artist model changes

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("artists", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="artistmodel",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Activo"),
        ),
        migrations.AddField(
            model_name="artistmodel",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("manual", "Manual"),
                    ("youtube", "YouTube"),
                    ("spotify", "Spotify"),
                    ("soundcloud", "SoundCloud"),
                ],
                default="manual",
                max_length=20,
                verbose_name="Tipo de fuente",
            ),
        ),
        migrations.AddField(
            model_name="artistmodel",
            name="source_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=100,
                null=True,
                verbose_name="ID de fuente externa",
            ),
        ),
        migrations.AddField(
            model_name="artistmodel",
            name="source_url",
            field=models.URLField(
                blank=True, null=True, verbose_name="URL de fuente externa"
            ),
        ),
        migrations.AddIndex(
            model_name="artistmodel",
            index=models.Index(
                fields=["source_type", "source_id"],
                name="artists_artistmodel_source_type_source_id_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="artistmodel",
            constraint=models.UniqueConstraint(
                condition=models.Q(source_id__isnull=False),
                fields=("source_type", "source_id"),
                name="unique_artist_source_per_type",
            ),
        ),
    ]
