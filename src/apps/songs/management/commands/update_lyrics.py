import asyncio
from django.core.management.base import BaseCommand, CommandError
from apps.songs.use_cases.lyrics_use_cases import BulkUpdateLyricsUseCase


class Command(BaseCommand):
    help = 'Update lyrics for songs that don\'t have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of songs to process (default: 50)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update lyrics even for songs that already have them'
        )
        parser.add_argument(
            '--concurrent',
            type=int,
            default=3,
            help='Maximum number of concurrent requests (default: 3)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress information'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        force_update = options['force']
        max_concurrent = options['concurrent']
        verbose = options['verbose']

        if verbose:
            self.stdout.write(
                self.style.SUCCESS(f'Starting lyrics update process...')
            )
            self.stdout.write(f'- Limit: {limit} songs')
            self.stdout.write(f'- Force update: {force_update}')
            self.stdout.write(f'- Max concurrent: {max_concurrent}')

        try:
            # Crear el use case
            use_case = BulkUpdateLyricsUseCase()
            
            # Ejecutar la actualización masiva
            if verbose:
                self.stdout.write('Executing bulk lyrics update...')
                
            stats = asyncio.run(use_case.execute(
                limit=limit,
                only_without_lyrics=not force_update,
                max_concurrent=max_concurrent
            ))

            # Mostrar resultados
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Lyrics update completed!'
                )
            )
            self.stdout.write(f'📊 Statistics:')
            self.stdout.write(f'   - Total processed: {stats["total_processed"]}')
            self.stdout.write(f'   - Updated: {stats["updated"]}')
            self.stdout.write(f'   - Skipped: {stats["skipped"]}')
            self.stdout.write(f'   - Errors: {stats["errors"]}')
            
            if stats.get('error_message'):
                self.stdout.write(
                    self.style.ERROR(f'❌ Error: {stats["error_message"]}')
                )

            # Calcular tasa de éxito
            if stats["total_processed"] > 0:
                success_rate = (stats["updated"] / stats["total_processed"]) * 100
                self.stdout.write(f'   - Success rate: {success_rate:.1f}%')

        except Exception as e:
            raise CommandError(f'Error during lyrics update: {str(e)}')
