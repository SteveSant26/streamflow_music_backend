from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer


class PaginationMixin:
    def paginate_queryset(self, queryset):
        ...

    def get_serializer(self, *args, **kwargs) -> Serializer:
        ...

    def get_paginated_response(self, data) -> Response:
        ...

    def paginate_and_respond(
        self,
        queryset,
    ):
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
