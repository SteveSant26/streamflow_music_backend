"""
Mixin para vistas APIView que utilizan casos de uso y paginación.
Elimina redundancia en vistas que heredan de PaginatedAPIView.
"""

from rest_framework.permissions import AllowAny

from .paginated_api_view import PaginatedAPIView


class UseCaseAPIViewMixin(PaginatedAPIView):
    """
    Mixin base para APIViews que utilizan casos de uso y necesitan paginación.

    Proporciona funcionalidad común para:
    - Paginación automática
    - Logging de requests
    - Permisos configurables
    - Manejo estándar de casos de uso
    """

    # Configuración por defecto que puede ser sobrescrita
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        """Inicialización base que puede ser extendida en subclases"""
        super().__init__(**kwargs)
        # Las subclases deben inicializar sus repositorios y casos de uso aquí

    def get_permissions(self):
        """Define permisos según la configuración"""
        return [permission() for permission in self.permission_classes]

    def handle_use_case_execution(self, use_case, *args, **kwargs):
        """
        Método helper para ejecutar casos de uso de forma consistente.

        Args:
            use_case: El caso de uso a ejecutar
            *args: Argumentos para el caso de uso
            **kwargs: Argumentos keyword para el caso de uso

        Returns:
            El resultado del caso de uso
        """
        try:
            if hasattr(use_case, "execute"):
                # Para casos de uso async
                from asgiref.sync import async_to_sync

                if hasattr(use_case.execute, "__call__"):
                    return async_to_sync(use_case.execute)(*args, **kwargs)
                else:
                    return use_case.execute(*args, **kwargs)
            else:
                # Para casos de uso síncronos
                return use_case(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error executing use case: {str(e)}")
            raise

    def map_entities_to_dtos(self, entities, mapper):
        """
        Método helper para convertir entidades a DTOs de forma consistente.

        Args:
            entities: Lista de entidades o entidad única
            mapper: El mapper a utilizar para la conversión

        Returns:
            Lista de DTOs o DTO único
        """
        if isinstance(entities, list):
            return [mapper.entity_to_dto(entity) for entity in entities]
        else:
            return mapper.entity_to_dto(entities)

    def log_request_info(self, action_name, additional_info=""):
        """
        Método helper para logging consistente.

        Args:
            action_name: Nombre de la acción siendo ejecutada
            additional_info: Información adicional para el log
        """
        message = f"Executing {action_name}"
        if additional_info:
            message += f" - {additional_info}"
        self.logger.info(message)
