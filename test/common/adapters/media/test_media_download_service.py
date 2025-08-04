import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from common.adapters.media.media_download_service import MediaDownloadService


class TestMediaDownloadService:
    """Tests para MediaDownloadService"""

    def setup_method(self):
        """Setup antes de cada test"""
        self.mock_music_service = Mock()
        self.service = MediaDownloadService(self.mock_music_service)

    @pytest.mark.asyncio
    async def test_download_thumbnail_success(self):
        """Test descarga exitosa de thumbnail"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = b"fake_image_data"

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await self.service.download_thumbnail(
                "http://example.com/image.jpg"
            )

        assert result == b"fake_image_data"

    @pytest.mark.asyncio
    async def test_download_thumbnail_http_error(self):
        """Test manejo de error HTTP en descarga de thumbnail"""
        mock_response = AsyncMock()
        mock_response.status = 404

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await self.service.download_thumbnail(
                "http://example.com/image.jpg"
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_download_audio_success(self):
        """Test descarga exitosa de audio"""
        self.mock_music_service.download_audio_from_video = AsyncMock(
            return_value=b"fake_audio_data"
        )

        result = await self.service.download_audio("video123")

        assert result == b"fake_audio_data"
        self.mock_music_service.download_audio_from_video.assert_called_once_with(
            "video123"
        )

    @pytest.mark.asyncio
    async def test_download_audio_no_service(self):
        """Test descarga de audio sin servicio de música"""
        service_without_music = MediaDownloadService(None)

        result = await service_without_music.download_audio("video123")

        assert result is None

    @pytest.mark.asyncio
    async def test_download_audio_exception(self):
        """Test manejo de excepción en descarga de audio"""
        self.mock_music_service.download_audio_from_video = AsyncMock(
            side_effect=Exception("Download failed")
        )

        result = await self.service.download_audio("video123")

        assert result is None
