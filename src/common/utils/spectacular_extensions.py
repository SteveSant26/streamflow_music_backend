"""
Extensiones personalizadas para DRF Spectacular para mejorar
la documentación automática de filtros.
"""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.extensions import OpenApiFilterExtension
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter


class DjangoFilterExtension(OpenApiFilterExtension):
    """
    Extensión para generar automáticamente parámetros de consulta
    a partir de django-filter FilterSet classes.
    """

    target_class = DjangoFilterBackend

    def get_schema_operation_parameters(self, auto_schema, *args, **kwargs):
        """
        Genera parámetros OpenAPI basados en el filterset_class del viewset.
        """
        parameters = []

        if not hasattr(auto_schema.view, "filterset_class"):
            return parameters

        filterset_class = auto_schema.view.filterset_class
        if not filterset_class:
            return parameters

        # Obtener todos los filtros del FilterSet
        for filter_name, filter_field in filterset_class.base_filters.items():
            param_type = self._get_parameter_type(filter_field)
            param_description = self._get_parameter_description(
                filter_field, filter_name
            )

            parameter = OpenApiParameter(
                name=filter_name,
                type=param_type,
                location=OpenApiParameter.QUERY,
                description=param_description,
                required=False,
            )
            parameters.append(parameter)

        return parameters

    def _get_parameter_type(self, filter_field):
        """
        Determina el tipo OpenAPI basado en el tipo de filtro.
        """
        filter_class_name = filter_field.__class__.__name__

        type_mapping = {
            "CharFilter": OpenApiTypes.STR,
            "UUIDFilter": OpenApiTypes.UUID,
            "NumberFilter": OpenApiTypes.NUMBER,
            "IntegerFilter": OpenApiTypes.INT,
            "DecimalFilter": OpenApiTypes.DECIMAL,
            "BooleanFilter": OpenApiTypes.BOOL,
            "DateFilter": OpenApiTypes.DATE,
            "DateTimeFilter": OpenApiTypes.DATETIME,
            "TimeFilter": OpenApiTypes.TIME,
            "ChoiceFilter": OpenApiTypes.STR,
            "ModelChoiceFilter": OpenApiTypes.STR,
            "ModelMultipleChoiceFilter": OpenApiTypes.STR,
        }

        return type_mapping.get(filter_class_name, OpenApiTypes.STR)

    def _get_parameter_description(self, filter_field, filter_name):
        """
        Genera una descripción para el parámetro basado en el filtro.
        """
        # Si el filtro tiene help_text, usarlo
        if hasattr(filter_field, "help_text") and filter_field.help_text:
            return filter_field.help_text

        # Si tiene choices, incluirlas en la descripción
        if hasattr(filter_field, "choices") and filter_field.choices:
            choices = [choice[0] for choice in filter_field.choices]
            return f"Filter by {filter_name}. Available choices: {', '.join(choices)}"

        # Descripción por defecto basada en el lookup_expr
        lookup_expr = getattr(filter_field, "lookup_expr", "exact")

        lookup_descriptions = {
            "exact": f"Filter by exact {filter_name}",
            "icontains": f"Search in {filter_name} (case insensitive)",
            "contains": f"Search in {filter_name} (case sensitive)",
            "gte": f"Filter by {filter_name} greater than or equal",
            "lte": f"Filter by {filter_name} less than or equal",
            "gt": f"Filter by {filter_name} greater than",
            "lt": f"Filter by {filter_name} less than",
            "isnull": f"Filter by {filter_name} is null/empty",
            "in": f"Filter by {filter_name} in list of values",
        }

        return lookup_descriptions.get(lookup_expr, f"Filter by {filter_name}")
