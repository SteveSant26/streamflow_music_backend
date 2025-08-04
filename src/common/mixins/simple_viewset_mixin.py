"""
Mixin para ViewSets simples que no requieren paginación automática.
Proporciona funcionalidad básica de logging y permisos.
"""
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet

from .logging_mixin import LoggingMixin


class SimpleViewSetMixin(ViewSet, LoggingMixin):
    """
    Mixin base para ViewSets simples sin paginación automática.

    Proporciona funcionalidad común para:
    - Logging de requests
    - Permisos configurables por acción
    - Métodos helper para serializers
    """

    # Configuración por defecto que puede ser sobrescrita
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Define permisos según la acción - puede ser sobrescrito en subclases"""
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        """
        Selecciona el serializer según la acción.
        Debe ser sobrescrito en subclases que usen múltiples serializers.
        """
        return getattr(self, "serializer_class", None)

    def log_action(self, action_name, additional_info=""):
        """
        Método helper para logging consistente de acciones.

        Args:
            action_name: Nombre de la acción siendo ejecutada
            additional_info: Información adicional para el log
        """
        message = f"Executing {action_name}"
        if additional_info:
            message += f" - {additional_info}"
        self.logger.info(message)
