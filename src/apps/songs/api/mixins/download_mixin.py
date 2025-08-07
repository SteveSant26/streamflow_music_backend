from django.http import FileResponse, Http404, HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
import requests
import os
import tempfile
from urllib.parse import urlparse

from apps.songs.infrastructure.models import SongModel
from src.common.mixins import LoggingMixin


class SongDownloadMixin(LoggingMixin):
    """Mixin para agregar funcionalidad de descarga a las vistas de canciones"""

    @extend_schema(
        tags=["Songs"],
        description="Download a song file. This will increment the download count and return the audio file.",
        summary="Download song",
        responses={
            200: {
                "content": {
                    "audio/mpeg": {"schema": {"type": "string", "format": "binary"}},
                    "audio/wav": {"schema": {"type": "string", "format": "binary"}},
                    "audio/mp4": {"schema": {"type": "string", "format": "binary"}},
                },
                "description": "Audio file download"
            },
            404: {"description": "Song not found or no audio file available"},
            500: {"description": "Error downloading file"}
        }
    )
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, id=None):
        """Descarga el archivo de audio de una canción"""
        try:
            # Obtener la canción
            song = self.get_object()
            
            if not song.file_url:
                return Response(
                    {'error': 'No audio file available for this song'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Incrementar contador de descargas
            song.download_count += 1
            song.save(update_fields=['download_count'])
            
            self.logger.info(f"Download requested for song: {song.title} (ID: {song.id})")
            
            # Determinar el tipo de archivo y nombre
            file_url = song.file_url
            parsed_url = urlparse(file_url)
            
            # Extraer extensión del archivo o usar mp3 por defecto
            file_extension = os.path.splitext(parsed_url.path)[1] or '.mp3'
            safe_title = "".join(c for c in song.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            artist_name = song.artist.name if song.artist else "Unknown Artist"
            safe_artist = "".join(c for c in artist_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            filename = f"{safe_artist} - {safe_title}{file_extension}"
            
            # Si es una URL externa, descargar el archivo
            if file_url.startswith(('http://', 'https://')):
                try:
                    response = requests.get(file_url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    # Crear archivo temporal
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
                    
                    # Escribir contenido al archivo temporal
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            temp_file.write(chunk)
                    
                    temp_file.close()
                    
                    # Determinar content type
                    content_type = 'audio/mpeg'
                    if file_extension.lower() == '.wav':
                        content_type = 'audio/wav'
                    elif file_extension.lower() in ['.mp4', '.m4a']:
                        content_type = 'audio/mp4'
                    
                    # Crear response para descarga
                    file_response = FileResponse(
                        open(temp_file.name, 'rb'),
                        content_type=content_type,
                        as_attachment=True,
                        filename=filename
                    )
                    
                    # Limpiar archivo temporal después de enviar
                    def cleanup():
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass
                    
                    # Nota: En producción, deberías usar una tarea asíncrona para limpiar
                    # Por ahora, el archivo se limpiará cuando se cierre la respuesta
                    
                    return file_response
                    
                except requests.RequestException as e:
                    self.logger.error(f"Error downloading file from {file_url}: {str(e)}")
                    return Response(
                        {'error': f'Error accessing audio file: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            # Si es un archivo local (poco probable en producción)
            else:
                if os.path.exists(file_url):
                    return FileResponse(
                        open(file_url, 'rb'),
                        as_attachment=True,
                        filename=filename
                    )
                else:
                    return Response(
                        {'error': 'Audio file not found on server'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                    
        except SongModel.DoesNotExist:
            return Response(
                {'error': 'Song not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            self.logger.error(f"Unexpected error downloading song {id}: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=["Songs"],
        description="Get download statistics for a song",
        summary="Get song download stats",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "song_id": {"type": "string"},
                    "title": {"type": "string"},
                    "download_count": {"type": "integer"},
                    "can_download": {"type": "boolean"},
                    "file_size_mb": {"type": "number", "nullable": True},
                    "audio_quality": {"type": "string"}
                }
            },
            404: {"description": "Song not found"}
        }
    )
    @action(detail=True, methods=['get'], url_path='download/stats')
    def download_stats(self, request, id=None):
        """Obtiene estadísticas de descarga de una canción"""
        try:
            song = self.get_object()
            
            return Response({
                'song_id': str(song.id),
                'title': song.title,
                'artist': song.artist.name if song.artist else 'Unknown Artist',
                'download_count': song.download_count,
                'can_download': bool(song.file_url),
                'audio_quality': song.audio_quality,
                'source_type': song.source_type
            }, status=status.HTTP_200_OK)
            
        except SongModel.DoesNotExist:
            return Response(
                {'error': 'Song not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
