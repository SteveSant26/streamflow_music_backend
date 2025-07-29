from django.core.management.base import BaseCommand
from apps.user_profile.infrastructure.models.user_profile import UserProfile
import uuid


class Command(BaseCommand):
    help = 'Crear datos de prueba para user profiles'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Creando datos de prueba para user profiles...')
        
        # Datos de prueba para perfiles
        test_profiles = [
            {
                'email': 'user1@streamflow.com',
                'profile_picture': 'https://picsum.photos/200/200?random=1'
            },
            {
                'email': 'user2@streamflow.com',
                'profile_picture': 'https://picsum.photos/200/200?random=2'
            },
            {
                'email': 'user3@streamflow.com', 
                'profile_picture': 'https://picsum.photos/200/200?random=3'
            },
            {
                'email': 'maria.garcia@music.com',
                'profile_picture': 'https://picsum.photos/200/200?random=4'
            },
            {
                'email': 'carlos.lopez@beats.com',
                'profile_picture': 'https://picsum.photos/200/200?random=5'
            }
        ]
        
        created_count = 0
        
        for profile_data in test_profiles:
            # Crear o obtener el perfil de usuario
            profile, created = UserProfile.objects.get_or_create(
                email=profile_data['email'],
                defaults={
                    'id': uuid.uuid4(),
                    'profile_picture': profile_data['profile_picture']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Perfil creado: {profile.email}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Perfil ya existe: {profile.email}')
                )
        
        total_profiles = UserProfile.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Completado! {created_count} nuevos perfiles creados. Total: {total_profiles}'
            )
        )
