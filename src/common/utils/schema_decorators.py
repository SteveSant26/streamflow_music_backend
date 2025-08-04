from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema


def paginated_endpoint(tags=None, description=None, **kwargs):
    """
    Decorator que automáticamente agrega parámetros de paginación a los endpoints.

    Args:
        tags: Lista de tags para la documentación
        description: Descripción del endpoint
        **kwargs: Otros parámetros para extend_schema

    Usage:
        @paginated_endpoint(tags=["Songs"], description="Get popular songs")
        def get(self, request):
            return self.paginate_and_respond(data, Serializer, request)
    """
    # Parámetros de paginación estándar
    pagination_parameters = [
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination",
            required=False,
            default=1,
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of items per page (max 100)",
            required=False,
            default=10,
        ),
    ]

    # Combinar parámetros existentes con los de paginación
    existing_parameters = kwargs.get("parameters", [])
    kwargs["parameters"] = existing_parameters + pagination_parameters

    # Agregar tags y description si se proporcionan
    if tags:
        kwargs["tags"] = tags
    if description:
        kwargs["description"] = description

    return extend_schema(**kwargs)


def paginated_list_endpoint(serializer_class, tags=None, description=None, **kwargs):
    """
    Decorator específico para endpoints que devuelven listas paginadas.

    Args:
        serializer_class: La clase del serializer para la respuesta
        tags: Lista de tags para la documentación
        description: Descripción del endpoint
        **kwargs: Otros parámetros para extend_schema

    Usage:
        @paginated_list_endpoint(SongListSerializer, tags=["Songs"], description="Get songs")
        def get(self, request):
            return self.paginate_and_respond(data, SongListSerializer, request)
    """
    # Configurar la respuesta automáticamente
    kwargs["responses"] = kwargs.get("responses", {200: serializer_class(many=True)})

    return paginated_endpoint(tags=tags, description=description, **kwargs)
