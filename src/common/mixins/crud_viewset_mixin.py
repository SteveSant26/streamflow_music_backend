"""
Mixin para ViewSets que utilizan casos de uso y necesitan operaciones CRUD completas.
Extiende FilteredViewSetMixin para vistas que no son de solo lectura.
"""
from typing import Any, List

from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated

from .logging_mixin import LoggingMixin
from .pagination_mixin import PaginationMixin


class CRUDViewSetMixin(PaginationMixin, viewsets.ModelViewSet, LoggingMixin):
    """
    Mixin base para ViewSets con operaciones CRUD completas y casos de uso.

    Proporciona funcionalidad común para:
    - Paginación automática
    - Logging de requests
    - Filtros de Django Filter
    - Permisos configurables por acción
    - Operaciones CRUD (Create, Read, Update, Delete)
    """

    # Configuración por defecto que puede ser sobrescrita
    permission_classes = [IsAuthenticated]
    ordering = ["-created_at"]

    def get_permissions(self) -> List[BasePermission]:
        """Define permisos según la acción - debe ser sobrescrito en subclases"""
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Personalizar el queryset base con optimizaciones.
        Las subclases pueden sobrescribir este método para agregar
        optimizaciones específicas como select_related o prefetch_related.
        """
        return super().get_queryset()

    def list(self, request, *args, **kwargs) -> Any:
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

    def retrieve(self, request, pk=None, *args, **kwargs) -> Any:
        """Obtiene un objeto específico"""
        queryset = self.get_queryset()
        if queryset is not None and hasattr(queryset, "model"):
            model_name = queryset.model._meta.verbose_name
        else:
            model_name = "object"
        self.logger.info(f"Getting {model_name} with ID: {pk}")
        return super().retrieve(request, pk, *args, **kwargs)

    def create(self, request, *args, **kwargs) -> Any:
        """Crea un nuevo objeto"""
        queryset = self.get_queryset()
        if queryset is not None and hasattr(queryset, "model"):
            model_name = queryset.model._meta.verbose_name
        else:
            model_name = "object"
        self.logger.info(f"Creating new {model_name}")
        return super().create(request, *args, **kwargs)

    def update(self, request, pk=None, *args, **kwargs) -> Any:
        """Actualiza un objeto existente"""
        queryset = self.get_queryset()
        if queryset is not None and hasattr(queryset, "model"):
            model_name = queryset.model._meta.verbose_name
        else:
            model_name = "object"
        self.logger.info(f"Updating {model_name} with ID: {pk}")
        return super().update(request, pk, *args, **kwargs)

    def destroy(self, request, pk=None, *args, **kwargs) -> Any:
        """Elimina un objeto"""
        queryset = self.get_queryset()
        if queryset is not None and hasattr(queryset, "model"):
            model_name = queryset.model._meta.verbose_name
        else:
            model_name = "object"
        self.logger.info(f"Deleting {model_name} with ID: {pk}")
        return super().destroy(request, pk, *args, **kwargs)
