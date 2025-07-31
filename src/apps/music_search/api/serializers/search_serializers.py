from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    """Serializer para resultados de búsqueda individuales"""

    result_type = serializers.CharField()
    result_id = serializers.CharField()
    title = serializers.CharField()
    subtitle = serializers.CharField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_null=True)
    relevance_score = serializers.FloatField(default=0.0)


class SearchRequestSerializer(serializers.Serializer):
    """Serializer para solicitudes de búsqueda"""

    query = serializers.CharField(max_length=255, help_text="Texto de búsqueda")
    types = serializers.ListField(
        child=serializers.ChoiceField(choices=["artists", "albums", "songs", "genres"]),
        required=False,
        help_text="Tipos de resultados a buscar. Si no se especifica, busca en todos.",
    )
    limit = serializers.IntegerField(
        min_value=1, max_value=50, default=10, help_text="Límite de resultados por tipo"
    )


class SearchResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de búsqueda"""

    query = serializers.CharField()
    artists = SearchResultSerializer(many=True)
    albums = SearchResultSerializer(many=True)
    songs = SearchResultSerializer(many=True)
    genres = SearchResultSerializer(many=True)
    total_results = serializers.IntegerField()
    search_time_ms = serializers.FloatField(required=False, allow_null=True)


class QuickSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda rápida (solo query)"""

    q = serializers.CharField(max_length=255, help_text="Texto de búsqueda")


class SearchHistorySerializer(serializers.Serializer):
    """Serializer para historial de búsquedas"""

    id = serializers.CharField()
    query_text = serializers.CharField()
    user_id = serializers.CharField(required=False, allow_null=True)
    results_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
