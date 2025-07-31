from rest_framework import serializers

from apps.user_profile.api.dtos import UserProfileResponseDTO
from apps.user_profile.api.mappers import UserProfileMapper
from apps.user_profile.domain.entities import UserProfileEntity
from common.serializers import BaseEntitySerializer


class RetrieveUserProfileSerializer(BaseEntitySerializer):
    """
    Serializer inteligente que hereda funcionalidad automática de conversión.
    Solo necesita definir las clases correspondientes.
    """

    # Configuración para el serializer base
    mapper_class = UserProfileMapper()
    entity_class = UserProfileEntity
    dto_class = UserProfileResponseDTO

    # Definición de campos (opcional, solo para documentación/validación)
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    profile_picture = serializers.CharField(
        read_only=True, required=False, allow_null=True
    )
