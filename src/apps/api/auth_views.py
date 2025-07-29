from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from apps.user_profile.infrastructure.models.user_profile import UserProfile
from django.db import IntegrityError
import re
import uuid
import secrets
import hashlib


def generate_simple_token(user_id):
    """Generar un token simple (no JWT) para el usuario"""
    random_string = secrets.token_urlsafe(32)
    token_data = f"{user_id}:{random_string}"
    return hashlib.sha256(token_data.encode()).hexdigest()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Endpoint para registrar un nuevo usuario
    """
    try:
        data = request.data
        
        # Validar datos requeridos
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        username = data.get('username', '').strip()
        
        if not email or not password:
            return Response({
                'error': True,
                'message': 'Email y contraseña son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar formato de email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return Response({
                'error': True,
                'message': 'Formato de email inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar contraseña
        if len(password) < 6:
            return Response({
                'error': True,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar username si no se proporciona
        if not username:
            username = email.split('@')[0]
        
        # Verificar si el usuario ya existe
        if UserProfile.objects.filter(email=email).exists():
            return Response({
                'error': True,
                'message': 'Ya existe un usuario con este email'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el usuario con UUID
        user_id = uuid.uuid4()
        user = UserProfile.objects.create(
            id=user_id,
            email=email,
            password=make_password(password)  # Hashear la contraseña
        )
        
        # Generar token simple
        token = generate_simple_token(str(user.id))
        
        return Response({
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': username,
                'profileImage': user.profile_picture,
                'createdAt': '',
                'updatedAt': ''
            },
            'token': token,
            'refreshToken': token,  # Por simplicidad, usar el mismo token
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)
        
    except IntegrityError:
        return Response({
            'error': True,
            'message': 'Error al crear el usuario. El email puede estar en uso.'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': True,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Endpoint para iniciar sesión
    """
    try:
        data = request.data
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return Response({
                'error': True,
                'message': 'Email y contraseña son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar usuario por email
        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            return Response({
                'error': True,
                'message': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar contraseña
        if not check_password(password, user.password):
            return Response({
                'error': True,
                'message': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generar token
        token = generate_simple_token(str(user.id))
        
        return Response({
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': user.email.split('@')[0],
                'profileImage': user.profile_picture,
                'createdAt': '',
                'updatedAt': ''
            },
            'token': token,
            'refreshToken': token,
            'message': 'Inicio de sesión exitoso'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': True,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir logout sin autenticación
def logout_view(request):
    """
    Endpoint para cerrar sesión (invalidar token)
    """
    try:
        return Response({
            'message': 'Sesión cerrada exitosamente'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': True,
            'message': 'Error al cerrar sesión'
        }, status=status.HTTP_400_BAD_REQUEST)
