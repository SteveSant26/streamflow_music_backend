from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import check_password
from apps.user_profile.infrastructure.models.user_profile import UserProfile
import uuid
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def get_user_from_token(request):
    """
    Extraer usuario del token (implementación simple)
    En una implementación real, validarías el token JWT
    """
    auth_header = request.headers.get('Authorization', '')
    print(f"Authorization header recibido: {auth_header[:50]}...")
    
    if not auth_header.startswith('Bearer '):
        print("No se encontró Bearer token")
        return None
        
    token = auth_header.split(' ')[1]
    print(f"Token extraído: {token[:20]}...")
    
    # Por ahora, simplemente devolvemos el primer usuario con este token
    # En una implementación real, decodificarías el token para obtener el user_id
    try:
        # Buscar usuario por token (simple implementación para pruebas)
        user = UserProfile.objects.first()  # Temporal para pruebas
        if user:
            print(f"Usuario encontrado: {user.email}")
        else:
            print("No se encontró ningún usuario")
        return user
    except UserProfile.DoesNotExist:
        print("Error: Usuario no existe")
        return None
    except Exception as e:
        print(f"Error al buscar usuario: {str(e)}")
        return None


@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile_view(request):
    """
    Obtener el perfil del usuario autenticado
    """
    try:
        user = get_user_from_token(request)
        if not user:
            return Response({
                'error': True,
                'message': 'Token inválido o usuario no encontrado'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': user.email.split('@')[0],
                'profileImage': user.profile_picture,
                'createdAt': '',
                'updatedAt': ''
            },
            'message': 'Perfil obtenido exitosamente'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': True,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_profile_view(request):
    """
    Actualizar el perfil del usuario autenticado
    """
    try:
        user = get_user_from_token(request)
        if not user:
            return Response({
                'error': True,
                'message': 'Token inválido o usuario no encontrado'
            }, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        print(f"Datos recibidos para actualizar perfil: {data}")
        
        # Actualizar campos si se proporcionan
        updated = False
        
        if 'username' in data and data['username']:
            # Para este ejemplo, guardamos el username en el email si es diferente
            new_email_parts = data['username'] + '@streamflow.com'
            if user.email != new_email_parts:
                user.email = new_email_parts
                updated = True
                
        if 'email' in data and data['email']:
            if user.email != data['email']:
                user.email = data['email']
                updated = True
                
        # El profile_picture se maneja en el endpoint de upload separado
        
        if updated:
            user.save()
            print(f"Usuario actualizado: {user.email}")
        
        return Response({
            'id': str(user.id),
            'email': user.email,
            'username': user.email.split('@')[0],
            'profileImage': user.profile_picture,
            'createdAt': '',
            'updatedAt': ''
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error al actualizar perfil: {str(e)}")
        return Response({
            'error': True,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_profile_image_view(request):
    """
    Subir imagen de perfil del usuario autenticado
    """
    try:
        print(f"Upload de imagen iniciado. Files: {request.FILES.keys()}")
        
        user = get_user_from_token(request)
        if not user:
            return Response({
                'error': True,
                'message': 'Token inválido o usuario no encontrado'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if 'file' not in request.FILES:
            print(f"No se encontró 'file' en request.FILES. Disponibles: {list(request.FILES.keys())}")
            return Response({
                'error': True,
                'message': 'No se proporcionó ningún archivo'
            }, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        print(f"Archivo recibido: {file.name}, tipo: {file.content_type}, tamaño: {file.size}")
        
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return Response({
                'error': True,
                'message': 'Tipo de archivo no permitido. Solo se permiten imágenes JPEG, PNG, GIF, WebP'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar tamaño (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size > max_size:
            return Response({
                'error': True,
                'message': 'El archivo es demasiado grande. El tamaño máximo es 5MB'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generar nombre único para el archivo
        file_extension = os.path.splitext(file.name)[1]
        unique_filename = f"profile_{user.id}_{uuid.uuid4()}{file_extension}"
        print(f"Nombre único generado: {unique_filename}")
        
        # Crear directorio si no existe
        upload_path = 'profile_images/'
        
        # Guardar archivo
        file_path = default_storage.save(
            upload_path + unique_filename,
            ContentFile(file.read())
        )
        print(f"Archivo guardado en: {file_path}")
        
        # Actualizar usuario con la nueva URL de imagen
        # Por simplicidad, guardamos solo el nombre del archivo
        user.profile_picture = unique_filename
        user.save()
        print(f"Usuario actualizado con nueva imagen: {unique_filename}")

        return Response({
            'id': str(user.id),
            'email': user.email,
            'username': user.email.split('@')[0],
            'profileImage': user.profile_picture,
            'createdAt': '',
            'updatedAt': ''
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error en upload de imagen: {str(e)}")
        return Response({
            'error': True,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)