from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .services import StatisticsService
from .serializers import (
    UserStatisticsSerializer,
    UserTopContentSerializer,
    GlobalStatisticsSerializer,
    TopArtistSerializer,
    TopSongSerializer
)


class UserStatisticsView(APIView):
    """Vista para obtener estadísticas del usuario autenticado"""
    # permission_classes = [IsAuthenticated]  # Comentado temporalmente para testing
    
    @extend_schema(
        summary="Obtener estadísticas del usuario",
        description="Retorna las estadísticas personales del usuario autenticado",
        responses={200: UserStatisticsSerializer}
    )
    def get(self, request):
        # Para testing usamos un user_id fijo
        user_id = "7449a6c2-11af-4166-9e73-87619b3418cf"  # str(request.user.id)
        stats = StatisticsService.get_user_statistics(user_id)
        serializer = UserStatisticsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTopContentView(APIView):
    """Vista para obtener el contenido más escuchado por el usuario"""
    # permission_classes = [IsAuthenticated]  # Comentado temporalmente para testing
    
    @extend_schema(
        summary="Obtener contenido top del usuario",
        description="Retorna los artistas y canciones más escuchados por el usuario",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Número de elementos a retornar (default: 10)',
                default=10
            )
        ],
        responses={200: UserTopContentSerializer}
    )
    def get(self, request):
        user_id = "7449a6c2-11af-4166-9e73-87619b3418cf"  # str(request.user.id) - Usando ID fijo para testing
        limit = int(request.query_params.get('limit', 10))
        
        top_content = StatisticsService.get_user_top_content(user_id, limit)
        serializer = UserTopContentSerializer(top_content)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GlobalStatisticsView(APIView):
    """Vista para obtener estadísticas globales de la aplicación"""
    
    @extend_schema(
        summary="Obtener estadísticas globales",
        description="Retorna las estadísticas generales de toda la aplicación",
        responses={200: GlobalStatisticsSerializer}
    )
    def get(self, request):
        stats = StatisticsService.get_global_statistics()
        serializer = GlobalStatisticsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrendingContentView(APIView):
    """Vista para obtener contenido en tendencia"""
    
    @extend_schema(
        summary="Obtener contenido en tendencia",
        description="Retorna el contenido más popular de los últimos 7 días",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Número de elementos a retornar (default: 10)',
                default=10
            )
        ],
        responses={200: UserTopContentSerializer}
    )
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        trending = StatisticsService.get_trending_content(limit)
        serializer = UserTopContentSerializer(trending)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TopArtistsView(APIView):
    """Vista para obtener los artistas más populares"""
    
    @extend_schema(
        summary="Obtener artistas más populares",
        description="Retorna los artistas con más reproducciones",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Número de artistas a retornar (default: 10)',
                default=10
            )
        ],
        responses={200: TopArtistSerializer(many=True)}
    )
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        top_content = StatisticsService._get_global_top_content(limit)
        return Response(top_content["top_artists"], status=status.HTTP_200_OK)


class TopSongsView(APIView):
    """Vista para obtener las canciones más populares"""
    
    @extend_schema(
        summary="Obtener canciones más populares",
        description="Retorna las canciones con más reproducciones",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Número de canciones a retornar (default: 10)',
                default=10
            )
        ],
        responses={200: TopSongSerializer(many=True)}
    )
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        top_content = StatisticsService._get_global_top_content(limit)
        return Response(top_content["top_songs"], status=status.HTTP_200_OK)


class RecordPlayView(APIView):
    """Vista para registrar una reproducción"""
    # permission_classes = [IsAuthenticated]  # Comentado temporalmente para testing
    
    @extend_schema(
        summary="Registrar reproducción",
        description="Registra una reproducción de canción en el historial del usuario",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'song_id': {'type': 'string', 'format': 'uuid'},
                    'duration_played': {'type': 'integer', 'description': 'Segundos reproducidos'},
                    'completed': {'type': 'boolean', 'default': False},
                    'source': {
                        'type': 'string', 
                        'enum': ['playlist', 'album', 'search', 'recommendation', 'shuffle', 'direct'],
                        'default': 'direct'
                    },
                    'device_type': {
                        'type': 'string',
                        'enum': ['web', 'mobile', 'desktop', 'tablet'],
                        'default': 'web'
                    }
                },
                'required': ['song_id', 'duration_played']
            }
        },
        responses={201: {'description': 'Reproducción registrada'}}
    )
    def post(self, request):
        user_id = "7449a6c2-11af-4166-9e73-87619b3418cf"  # str(request.user.id) - Para testing
        song_id = request.data.get('song_id')
        duration_played = request.data.get('duration_played')
        completed = request.data.get('completed', False)
        source = request.data.get('source', 'direct')
        device_type = request.data.get('device_type', 'web')
        
        if not song_id or not duration_played:
            return Response(
                {'error': 'song_id y duration_played son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            play_record = StatisticsService.record_play(
                user_id, song_id, duration_played, completed, source, device_type
            )
            return Response(
                {'message': 'Reproducción registrada', 'id': str(play_record.id)},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ToggleFavoriteArtistView(APIView):
    """Vista para agregar/quitar artistas de favoritos"""
    # permission_classes = [IsAuthenticated]  # Comentado temporalmente para testing
    
    @extend_schema(
        summary="Toggle artista favorito",
        description="Agrega o quita un artista de la lista de favoritos del usuario",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'artist_id': {'type': 'string', 'format': 'uuid'}
                },
                'required': ['artist_id']
            }
        },
        responses={200: {'description': 'Estado de favorito actualizado'}}
    )
    def post(self, request):
        user_id = "7449a6c2-11af-4166-9e73-87619b3418cf"  # UUID hardcodeado para testing
        artist_id = request.data.get('artist_id')
        
        if not artist_id:
            return Response(
                {'error': 'artist_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = StatisticsService.toggle_favorite_artist(user_id, artist_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ToggleFavoriteSongView(APIView):
    """Vista para agregar/quitar canciones de favoritos"""
    # permission_classes = [IsAuthenticated]  # Comentado temporalmente para testing
    
    @extend_schema(
        summary="Toggle canción favorita",
        description="Agrega o quita una canción de la lista de favoritos del usuario",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'song_id': {'type': 'string', 'format': 'uuid'}
                },
                'required': ['song_id']
            }
        },
        responses={200: {'description': 'Estado de favorito actualizado'}}
    )
    def post(self, request):
        user_id = "7449a6c2-11af-4166-9e73-87619b3418cf"  # UUID hardcodeado para testing
        song_id = request.data.get('song_id')
        
        if not song_id:
            return Response(
                {'error': 'song_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = StatisticsService.toggle_favorite_song(user_id, song_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
