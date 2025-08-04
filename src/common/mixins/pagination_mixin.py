from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from ..core.pagination import CustomPagination


class PaginationMixin:
    """
    Mixin that provides pagination functionality for APIViews.
    Automatically initializes CustomPagination.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, "paginator"):
            self.paginator = CustomPagination()

    def paginate_queryset(self, queryset, request=None):
        """Paginate a queryset using the custom paginator"""
        if not hasattr(self, "paginator"):
            self.paginator = CustomPagination()

        request = request or getattr(self, "request", None)
        return self.paginator.paginate_queryset(queryset, request, view=self)

    def get_paginated_response(self, data) -> Response:
        """Get paginated response using the custom paginator"""
        if not hasattr(self, "paginator"):
            self.paginator = CustomPagination()
        return self.paginator.get_paginated_response(data)

    def get_serializer_class(
        self,
    ) -> type[Serializer]:
        """Override this method in your view to specify the serializer class"""
        raise NotImplementedError("You must implement get_serializer_class method")

    def paginate_and_respond(self, queryset, request=None):
        """
        Utility method to paginate data and return response.

        Args:
            queryset: List of objects to paginate
            serializer_class: Serializer class to use
            request: HTTP request object (optional, will try to get from self.request)

        Returns:
            Response: Paginated response
        """
        request = request or getattr(self, "request", None)
        page = self.paginate_queryset(queryset, request)
        serializer_class = self.get_serializer_class()

        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
