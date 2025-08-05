from unittest.mock import Mock

import pytest

from common.adapters.media.media_file_service import MediaFileService


class TestMediaFileService:
    """Tests para MediaFileService"""

    def setup_method(self):
        """Setup antes de cada test"""
        self.mock_storage = Mock()
        self.service = MediaFileService(self.mock_storage)

    def test_generate_audio_filename(self):
        """Test generación de nombre de archivo de audio"""
        filename = self.service.generate_audio_filename("video123")

        assert filename.startswith("audio/video123_")
        assert filename.endswith(".mp3")

    def test_generate_thumbnail_filename(self):
        """Test generación de nombre de archivo de thumbnail"""
        image_bytes = b"\xff\xd8\xff"  # JPG header
        filename = self.service.generate_thumbnail_filename("video123", image_bytes)

        assert filename.startswith("thumbnails/video123_")
        assert filename.endswith(".jpg")

    def test_get_image_extension_jpg(self):
        """Test detección de extensión JPG"""
        jpg_bytes = b"\xff\xd8\xff"
        ext = self.service.get_image_extension(jpg_bytes)
        assert ext == "jpg"

    def test_get_image_extension_png(self):
        """Test detección de extensión PNG"""
        png_bytes = b"\x89PNG\r\n\x1a\n"
        ext = self.service.get_image_extension(png_bytes)
        assert ext == "png"

    def test_get_image_extension_webp(self):
        """Test detección de extensión WEBP"""
        webp_bytes = b"RIFFxxxxWEBP"
        ext = self.service.get_image_extension(webp_bytes)
        assert ext == "webp"

    def test_get_image_extension_gif(self):
        """Test detección de extensión GIF"""
        gif_bytes = b"GIF87a"
        ext = self.service.get_image_extension(gif_bytes)
        assert ext == "gif"

    def test_get_image_extension_unknown(self):
        """Test detección de extensión desconocida (default a jpg)"""
        unknown_bytes = b"unknown_format"
        ext = self.service.get_image_extension(unknown_bytes)
        assert ext == "jpg"

    @pytest.mark.asyncio
    async def test_upload_media_files_success(self):
        """Test subida exitosa de archivos multimedia"""
        self.mock_storage.upload_item.return_value = True
        self.mock_storage.get_item_url.return_value = "http://example.com/file.jpg"

        audio_bytes = b"fake_audio"
        thumbnail_bytes = b"\xff\xd8\xff"  # JPG

        audio_name, thumb_name, thumb_url = await self.service.upload_media_files(
            audio_bytes, thumbnail_bytes, "video123"
        )

        assert audio_name is not None
        assert audio_name.startswith("audio/video123_")
        assert thumb_name is not None
        assert thumb_name.startswith("thumbnails/video123_")
        assert thumb_url == "http://example.com/file.jpg"

    @pytest.mark.asyncio
    async def test_upload_media_files_no_files(self):
        """Test cuando no hay archivos para subir"""
        audio_name, thumb_name, thumb_url = await self.service.upload_media_files(
            None, None, "video123"
        )

        assert audio_name is None
        assert thumb_name is None
        assert thumb_url is None

    @pytest.mark.asyncio
    async def test_upload_audio_file_failure(self):
        """Test fallo en subida de archivo de audio"""
        self.mock_storage.upload_item.return_value = False

        result = await self.service._upload_audio_file(b"fake_audio", "video123")

        assert result is None
