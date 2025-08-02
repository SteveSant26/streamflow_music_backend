"""
Comando de gestión para poblar la base de datos con géneros musicales predefinidos.
"""

import uuid

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.genres.infrastructure.models import GenreModel


class Command(BaseCommand):
    help = "Pobla la base de datos con géneros musicales predefinidos"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Elimina todos los géneros existentes antes de crear nuevos",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Actualiza géneros existentes si ya existen",
        )
        parser.add_argument(
            "--show-stats",
            action="store_true",
            help="Muestra estadísticas después de poblar",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Eliminando géneros existentes...")
            deleted_count = GenreModel.objects.all().count()
            GenreModel.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f"{deleted_count} géneros eliminados exitosamente.")
            )

        genres_config = getattr(settings, "YOUTUBE_MUSIC_GENRES", {})

        if not genres_config:
            self.stdout.write(
                self.style.ERROR("No se encontró configuración de géneros en settings.")
            )
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for genre_key, genre_data in genres_config.items():
            # Verificar que genre_data es un diccionario
            if not isinstance(genre_data, dict):
                self.stdout.write(
                    self.style.WARNING(
                        f"Género {genre_key} no tiene formato válido. Saltando..."
                    )
                )
                skipped_count += 1
                continue

            name = genre_data.get("name")
            category = genre_data.get("category", "General")
            keywords = genre_data.get("keywords", [])

            if not name:
                self.stdout.write(
                    self.style.WARNING(
                        f"Género {genre_key} no tiene nombre. Saltando..."
                    )
                )
                skipped_count += 1
                continue

            # Verificar si el género ya existe
            existing_genre = GenreModel.objects.filter(name=name).first()

            if existing_genre:
                if options["update"]:
                    existing_genre.description = self._build_description(
                        category, keywords
                    )
                    # Mantener la popularidad existente
                    existing_genre.save()
                    self.stdout.write(f"✅ Actualizado: {name}")
                    updated_count += 1
                else:
                    self.stdout.write(f"⏭️  Ya existe: {name} (saltando)")
                    skipped_count += 1
                continue

            # Crear nuevo género
            _ = GenreModel.objects.create(
                id=uuid.uuid4(),
                name=name,
                description=self._build_description(category, keywords),
                popularity_score=0,
                is_active=True,
            )

            self.stdout.write(f"✅ Creado: {name}")
            created_count += 1

        # Mostrar resumen
        self.stdout.write(
            self.style.SUCCESS(
                f"\n--- RESUMEN ---\n"
                f"✅ Géneros creados: {created_count}\n"
                f"🔄 Géneros actualizados: {updated_count}\n"
                f"⏭️  Géneros saltados: {skipped_count}\n"
                f"📊 Total procesados: {len(genres_config)}"
            )
        )

        # Mostrar estadísticas si se solicita
        if options["show_stats"]:
            self._show_statistics()

    def _build_description(self, category, keywords):
        """Construye una descripción basada en la categoría y palabras clave"""
        if not category:
            category = "General"

        description = f"Género musical de la categoría {category}."
        if keywords and isinstance(keywords, list):
            keywords_str = ", ".join(keywords[:5])  # Limitar a 5 palabras clave
            description += f" Palabras clave: {keywords_str}."
        return description

    def _show_statistics(self):
        """Muestra estadísticas de los géneros en la base de datos"""
        self.stdout.write("\n--- ESTADÍSTICAS DE GÉNEROS ---")

        total_genres = GenreModel.objects.count()
        active_genres = GenreModel.objects.filter(is_active=True).count()

        self.stdout.write(f"📊 Total de géneros: {total_genres}")
        self.stdout.write(f"✅ Géneros activos: {active_genres}")

        # Géneros por categoría (basado en descripción)
        categories = {}
        for genre in GenreModel.objects.all():
            if genre.description:
                # Extraer categoría
                words = genre.description.split()
                if "categoría" in words:
                    try:
                        cat_index = words.index("categoría") + 1
                        if cat_index < len(words):
                            category = words[cat_index].replace(".", "")
                            categories[category] = categories.get(category, 0) + 1
                    except (ValueError, IndexError):
                        # Ignore lines that don't contain category information
                        continue

        if categories:
            self.stdout.write("\n📂 Géneros por categoría:")
            for category, count in sorted(categories.items()):
                self.stdout.write(f"   {category}: {count} géneros")

        # Top 5 géneros más populares
        popular_genres = GenreModel.objects.filter(is_active=True).order_by(
            "-popularity_score", "name"
        )[:5]

        if popular_genres:
            self.stdout.write("\n🔥 Top 5 géneros más populares:")
            for i, genre in enumerate(popular_genres, 1):
                self.stdout.write(
                    f"   {i}. {genre.name} (Popularidad: {genre.popularity_score})"
                )

        self.stdout.write("\n💡 Comandos útiles:")
        self.stdout.write(
            "   python manage.py populate_genres --update  # Actualizar existentes"
        )
        self.stdout.write(
            "   python manage.py populate_genres --clear   # Limpiar y recrear"
        )
        self.stdout.write(
            "   python demo_genre_system.py                # Probar el sistema"
        )
