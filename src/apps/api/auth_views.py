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
        print(f"Datos de registro recibidos: {data}")
        
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
        
        # Verificar si el email ya existe
        if UserProfile.objects.filter(email=email).exists():
            return Response({
                'error': True,
                'message': 'El email ya está registrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear usuario
        user = UserProfile.objects.create(
            id=uuid.uuid4(),
            email=email,
            password=make_password(password)
        )
        
        # Generar token
        token = generate_simple_token(str(user.id))
        
        print(f"Usuario registrado exitosamente: {email}")
        
        return Response({
            'message': 'Registro exitoso',
            'token': token,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': user.email.split('@')[0],
                'profileImage': user.profile_picture,
                'createdAt': '',
                'updatedAt': ''
            }
        }, status=status.HTTP_201_CREATED)
        
    except IntegrityError:
        return Response({
            'error': True,
            'message': 'El email ya está registrado'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error en registro: {str(e)}")
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
        print(f"Datos de login recibidos: {data}")
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return Response({
                'error': True,
                'message': 'Email y contraseña son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar usuario
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
        
        print(f"Login exitoso para: {email}")
        
        return Response({
            'message': 'Login exitoso',
            'token': token,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': user.email.split('@')[0],
                'profileImage': user.profile_picture,
                'createdAt': '',
                'updatedAt': ''
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return Response({
            'error': True,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # No requerir autenticación para logout
def logout_view(request):
    """
    Endpoint para cerrar sesión
    """
    try:
        print("Logout solicitado")
        return Response({
            'message': 'Logout exitoso'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error en logout: {str(e)}")
        return Response({
            'error': True,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)