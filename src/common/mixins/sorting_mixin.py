class SortingMixin:
    ordering_fields: list[str] = []
    ordering: list[str] = []

    def get_ordering_fields(self, view):  # NOSONAR
        return getattr(self, "ordering_fields", [])

    def get_ordering(self, request, queryset, view):  # NOSONAR
        return getattr(self, "ordering", [])
