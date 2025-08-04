from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework.views import APIView

from .logging_mixin import LoggingMixin
from .pagination_mixin import PaginationMixin


class PaginatedAPIView(APIView, PaginationMixin, LoggingMixin):
    """
    Base class for APIViews that need pagination.
    Combines APIView with PaginationMixin and LoggingMixin.

    Automatically includes pagination parameters in OpenAPI schema:
    - page: Page number
    - page_size: Number of items per page

    Inherits all pagination functionality from PaginationMixin:
    - paginate_queryset()
    - get_paginated_response()
    - paginate_and_respond()

    Usage:
        @extend_schema_view(
            get=extend_schema(
                tags=["YourTag"],
                description="Your endpoint description",
                # pagination parameters are automatically included
            )
        )
        class MyView(PaginatedAPIView):
            def get(self, request):
                data = [...]  # your data
                return self.paginate_and_respond(data, SomeSerializer, request)
    """

    @classmethod
    def get_pagination_parameters(cls):
        """
        Returns the standard pagination parameters for OpenAPI documentation.
        Can be overridden in subclasses to customize pagination parameters.
        """
        return [
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

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to automatically add pagination parameters to the schema.
        """
        # Get the view method (get, post, put, etc.)
        method = request.method.lower()
        view_method = getattr(self, method, None)

        if view_method and hasattr(view_method, "_spectacular_annotation"):
            # If the method already has schema annotation, add pagination parameters
            annotation = view_method._spectacular_annotation
            if "parameters" not in annotation:
                annotation["parameters"] = []

            # Add pagination parameters if not already present
            existing_param_names = {
                p.name for p in annotation["parameters"] if hasattr(p, "name")
            }
            pagination_params = [
                p
                for p in self.get_pagination_parameters()
                if p.name not in existing_param_names
            ]
            annotation["parameters"].extend(pagination_params)

        return super().dispatch(request, *args, **kwargs)
