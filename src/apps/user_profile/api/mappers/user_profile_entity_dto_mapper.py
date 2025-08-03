from apps.user_profile.domain.entities import UserProfileEntity
from common.factories.storage_service_factory import StorageServiceFactory
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper
from common.mixins.logging_mixin import LoggingMixin

from ..dtos import UserProfileResponseDTO


class UserProfileEntityDTOMapper(
    AbstractEntityDtoMapper[UserProfileEntity, UserProfileResponseDTO], LoggingMixin
):
    """Mapper para convertir entre entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: UserProfileEntity) -> UserProfileResponseDTO:
        """
        Convierte una entidad del dominio a DTO de respuesta.

        Esta es la ÚNICA responsabilidad del mapper:
        - Convertir entre capas
        - Aplicar transformaciones específicas (como generar URLs)
        """
        self.logger.debug(
            f"Converting entity to DTO for user {entity.id} with profile_picture: {entity.profile_picture}"
        )

        # Si hay una ruta de imagen, generamos la URL pública
        profile_picture_url = None
        if entity.profile_picture:
            self.logger.debug(f"Profile picture path: {entity.profile_picture}")
            profile_picture_service = (
                StorageServiceFactory.create_profile_pictures_service()
            )
            profile_picture_url = profile_picture_service.get_item_url(
                entity.profile_picture
            )
            self.logger.debug(f"Generated profile picture URL: {profile_picture_url}")

        return UserProfileResponseDTO(
            id=entity.id, email=entity.email, profile_picture=profile_picture_url
        )

    def dto_to_entity(self, dto: UserProfileResponseDTO) -> UserProfileEntity:
        """
        Convierte un DTO a entidad del dominio.
        Nota: La URL se convierte de vuelta a ruta interna.
        """
        return UserProfileEntity(
            id=dto.id,
            email=dto.email,
            profile_picture=dto.profile_picture,
        )
