"""
Mixin para ViewSets con filtros de Django Filter integrados.
Elimina la redundancia de código en las vistas que utilizan filtros.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .logging_mixin import LoggingMixin
from .pagination_mixin import PaginationMixin


class FilteredViewSetMixin(
    PaginationMixin, viewsets.ReadOnlyModelViewSet, LoggingMixin
):
    """
    Mixin base para ViewSets de solo lectura con filtros integrados.

    Proporciona funcionalidad común para:
    - Paginación automática
    - Logging de requests
    - Filtros de Django Filter
    - Permisos configurables
    - Queryset optimizado
    - Búsqueda y ordenamiento
    """

    # Configuración por defecto que puede ser sobrescrita
    permission_classes = [AllowAny]
    ordering = ["-created_at"]

    def get_permissions(self):
        """Define permisos según la acción"""
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Personalizar el queryset base con optimizaciones.
        Las subclases pueden sobrescribir este método para agregar
        optimizaciones específicas como select_related o prefetch_related.
        """
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        """
        Obtiene todos los objetos con filtros aplicados.

        Los filtros disponibles dependen del filterset_class configurado.
        """
        queryset = self.get_queryset()
        if queryset is not None and hasattr(queryset, "model"):
            model_name = queryset.model._meta.verbose_name_plural
        else:
            model_name = "objects"
        self.logger.info(f"Getting {model_name} with filters: {request.query_params}")
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Obtiene un objeto específico"""
        queryset = self.get_queryset()
        if queryset is not None and hasattr(queryset, "model"):
            model_name = queryset.model._meta.verbose_name
        else:
            model_name = "object"
        self.logger.info(f"Getting {model_name} with ID: {pk}")
        return super().retrieve(request, pk, *args, **kwargs)
