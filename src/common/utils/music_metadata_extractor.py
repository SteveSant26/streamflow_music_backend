import re
from typing import Dict, List, Optional

from ..mixins.logging_mixin import LoggingMixin
from ..types.media_types import (
    ExtractedAlbumInfo,
    ExtractedArtistInfo,
    YouTubeVideoInfo,
)


class MusicMetadataExtractor(LoggingMixin):
    """Extrae información de artistas y álbumes desde metadatos de YouTube"""

    def __init__(self):
        super().__init__()
        self._init_patterns()

    def _init_patterns(self):
        """Inicializa patrones de extracción comunes"""

        # Patrones para separadores de artista-título
        self.artist_title_patterns = [
            r"^(.+?)\s*[-–—]\s*(.+)$",  # Artist - Title
            r"^(.+?)\s*[:|]\s*(.+)$",  # Artist : Title o Artist | Title
            r'^(.+?)\s*["""]\s*(.+?)\s*["""]$',  # Artist "Title"
            r"^(.+?)\s*['']\s*(.+?)\s*['']\s*$",  # Artist 'Title'
            r"^(.+?)\s*by\s+(.+)$",  # Title by Artist
            r"^(.+?)\s*ft\.?\s+(.+)$",  # Artist ft. Guest
            r"^(.+?)\s*feat\.?\s+(.+)$",  # Artist feat. Guest
        ]

        # Patrones para álbumes
        self.album_patterns = [
            r'(?:from|off|album)\s+["""' '](.*?)["""' "]",  # from "Album"
            r"(?:álbum|album):\s*(.+?)(?:\s*[-|]|$)",  # Álbum: Name
            r"\[(.+?)\]",  # [Album Name]
            r"\((.+?)\)",  # (Album Name) - menos específico
        ]

        # Patrones para años
        self.year_patterns = [
            r"\b(19[0-9][0-9]|20[0-2][0-9])\b",  # Años 1900-2029
        ]

        # Palabras clave que indican que NO es un álbum
        self.album_exclusions = {
            "official",
            "video",
            "music",
            "audio",
            "lyric",
            "lyrics",
            "live",
            "remix",
            "cover",
            "acoustic",
            "instrumental",
            "karaoke",
            "demo",
            "single",
            "ep",
            "compilation",
            "greatest hits",
            "best of",
        }

        # Palabras clave que indican colaboraciones
        self.collaboration_keywords = [
            "ft",
            "feat",
            "featuring",
            "with",
            "vs",
            "versus",
            "&",
            "and",
            "y",
            "e",
        ]

    def extract_music_metadata(self, video_info: YouTubeVideoInfo) -> YouTubeVideoInfo:
        """
        Extrae metadatos musicales completos del video info

        Args:
            video_info: Información del video de YouTube

        Returns:
            YouTubeVideoInfo con metadatos extraídos
        """
        try:
            # Extraer artistas
            artists = self._extract_artists(video_info)

            # Extraer álbumes
            albums = self._extract_albums(video_info, artists)

            # Asignar resultados
            video_info.extracted_artists = artists
            video_info.extracted_albums = albums

            self.logger.debug(
                f"Extracted {len(artists)} artists and {len(albums)} albums from video {video_info.video_id}"
            )

            return video_info

        except Exception as e:
            self.logger.error(f"Error extracting music metadata: {str(e)}")
            video_info.extracted_artists = []
            video_info.extracted_albums = []
            return video_info

    def _extract_artists(
        self, video_info: YouTubeVideoInfo
    ) -> List[ExtractedArtistInfo]:
        """Extrae información de artistas"""
        artists = []

        # 1. Extraer del canal (más confiable)
        channel_artist = self._extract_artist_from_channel(video_info)
        if channel_artist:
            artists.append(channel_artist)

        # 2. Extraer del título
        title_artists = self._extract_artists_from_title(video_info.title)
        artists.extend(title_artists)

        # 3. Extraer de la descripción
        description_artists = self._extract_artists_from_description(
            video_info.description
        )
        artists.extend(description_artists)

        # 4. Extraer de tags
        tag_artists = self._extract_artists_from_tags(video_info.tags)
        artists.extend(tag_artists)

        # Deduplicar y rankear por confianza
        return self._deduplicate_and_rank_artists(artists)

    def _extract_artist_from_channel(
        self, video_info: YouTubeVideoInfo
    ) -> Optional[ExtractedArtistInfo]:
        """Extrae artista del nombre del canal"""
        channel_name = video_info.channel_title.strip()

        # Limpiar el nombre del canal
        cleaned_name = self._clean_artist_name(channel_name)

        if self._is_likely_artist_channel(cleaned_name):
            return ExtractedArtistInfo(
                name=cleaned_name,
                channel_id=video_info.channel_id,
                extracted_from="channel",
                confidence_score=0.8,
                additional_info={"original_channel_name": channel_name},
            )

        return None

    def _extract_artists_from_title(self, title: str) -> List[ExtractedArtistInfo]:
        """Extrae artistas del título del video"""
        artists = []

        for pattern in self.artist_title_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                # Determinar cuál grupo es el artista
                potential_artists = [match.group(1).strip(), match.group(2).strip()]

                for i, potential_artist in enumerate(potential_artists):
                    cleaned = self._clean_artist_name(potential_artist)
                    if cleaned and self._is_likely_artist_name(cleaned):
                        # Mayor confianza al primer grupo en patrones Artist - Title
                        confidence = 0.7 if i == 0 else 0.6

                        artists.append(
                            ExtractedArtistInfo(
                                name=cleaned,
                                extracted_from="title",
                                confidence_score=confidence,
                                additional_info={
                                    "pattern_matched": pattern,
                                    "original_text": potential_artist,
                                },
                            )
                        )
                break

        # Buscar colaboraciones
        collaboration_artists = self._extract_collaborations_from_title(title)
        artists.extend(collaboration_artists)

        return artists

    def _extract_collaborations_from_title(
        self, title: str
    ) -> List[ExtractedArtistInfo]:
        """Extrae artistas colaboradores del título"""
        artists = []

        for keyword in self.collaboration_keywords:
            pattern = rf"\b{re.escape(keyword)}\b\s+(.+?)(?:\s*[-|]|$)"
            matches = re.finditer(pattern, title, re.IGNORECASE)

            for match in matches:
                potential_artist = match.group(1).strip()
                cleaned = self._clean_artist_name(potential_artist)

                if cleaned and self._is_likely_artist_name(cleaned):
                    artists.append(
                        ExtractedArtistInfo(
                            name=cleaned,
                            extracted_from="title",
                            confidence_score=0.6,
                            additional_info={
                                "collaboration_type": keyword,
                                "original_text": potential_artist,
                            },
                        )
                    )

        return artists

    def _extract_artists_from_description(
        self, description: str
    ) -> List[ExtractedArtistInfo]:
        """Extrae artistas de la descripción"""
        if not description:
            return []

        artists = []

        # Buscar patrones como "Artist:", "Performed by:", etc.
        artist_patterns = [
            r"(?:artist|artista|performed by|cantante|singer):\s*(.+?)(?:\n|$)",
            r"(?:música|music)\s+by\s+(.+?)(?:\n|$)",
        ]

        for pattern in artist_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE | re.MULTILINE)

            for match in matches:
                potential_artist = match.group(1).strip()
                cleaned = self._clean_artist_name(potential_artist)

                if cleaned and self._is_likely_artist_name(cleaned):
                    artists.append(
                        ExtractedArtistInfo(
                            name=cleaned,
                            extracted_from="description",
                            confidence_score=0.5,
                            additional_info={"original_text": potential_artist},
                        )
                    )

        return artists

    def _extract_artists_from_tags(self, tags: List[str]) -> List[ExtractedArtistInfo]:
        """Extrae artistas de los tags"""
        if not tags:
            return []

        artists = []

        for tag in tags:
            cleaned = self._clean_artist_name(tag)
            if cleaned and self._is_likely_artist_name(cleaned) and len(cleaned) > 2:
                artists.append(
                    ExtractedArtistInfo(
                        name=cleaned,
                        extracted_from="tags",
                        confidence_score=0.3,
                        additional_info={"original_tag": tag},
                    )
                )

        return artists

    def _extract_albums(
        self, video_info: YouTubeVideoInfo, artists: List[ExtractedArtistInfo]
    ) -> List[ExtractedAlbumInfo]:
        """Extrae información de álbumes"""
        albums = []

        # Extraer del título
        title_albums = self._extract_albums_from_title(video_info.title, artists)
        albums.extend(title_albums)

        # Extraer de la descripción
        description_albums = self._extract_albums_from_description(
            video_info.description, artists
        )
        albums.extend(description_albums)

        # Extraer de tags
        tag_albums = self._extract_albums_from_tags(video_info.tags, artists)
        albums.extend(tag_albums)

        return self._deduplicate_albums(albums)

    def _extract_albums_from_title(
        self, title: str, artists: List[ExtractedArtistInfo]
    ) -> List[ExtractedAlbumInfo]:
        """Extrae álbumes del título"""
        albums = []

        for pattern in self.album_patterns:
            matches = re.finditer(pattern, title, re.IGNORECASE)

            for match in matches:
                potential_album = match.group(1).strip()

                if self._is_likely_album_name(potential_album):
                    # Extraer año si está presente
                    year = self._extract_year_from_text(potential_album)

                    # Determinar artista principal
                    main_artist = artists[0].name if artists else None

                    albums.append(
                        ExtractedAlbumInfo(
                            title=potential_album,
                            artist_name=main_artist,
                            extracted_from="title",
                            confidence_score=0.6,
                            release_year=year,
                            additional_info={"original_text": potential_album},
                        )
                    )

        return albums

    def _extract_albums_from_description(
        self, description: str, artists: List[ExtractedArtistInfo]
    ) -> List[ExtractedAlbumInfo]:
        """Extrae álbumes de la descripción"""
        if not description:
            return []

        albums = []

        # Patrones específicos para descripción
        description_patterns = [
            r"(?:album|álbum):\s*(.+?)(?:\n|$)",
            r'(?:from the album|del álbum)\s*["""' '](.*?)["""' "]",
            r"(?:taken from|extraído de)\s*(.+?)(?:\n|$)",
        ]

        for pattern in description_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE | re.MULTILINE)

            for match in matches:
                potential_album = match.group(1).strip()

                if self._is_likely_album_name(potential_album):
                    year = self._extract_year_from_text(potential_album)
                    main_artist = artists[0].name if artists else None

                    albums.append(
                        ExtractedAlbumInfo(
                            title=potential_album,
                            artist_name=main_artist,
                            extracted_from="description",
                            confidence_score=0.5,
                            release_year=year,
                            additional_info={"original_text": potential_album},
                        )
                    )

        return albums

    def _extract_albums_from_tags(
        self, tags: List[str], artists: List[ExtractedArtistInfo]
    ) -> List[ExtractedAlbumInfo]:
        """Extrae álbumes de los tags"""
        if not tags:
            return []

        albums = []

        for tag in tags:
            if self._is_likely_album_name(tag) and len(tag) > 3:
                main_artist = artists[0].name if artists else None

                albums.append(
                    ExtractedAlbumInfo(
                        title=tag,
                        artist_name=main_artist,
                        extracted_from="tags",
                        confidence_score=0.3,
                        additional_info={"original_tag": tag},
                    )
                )

        return albums

    def _clean_artist_name(self, name: str) -> str:
        """Limpia el nombre del artista"""
        if not name:
            return ""

        # Remover sufijos comunes de canales
        suffixes_to_remove = [
            r"\s*-?\s*official\s*$",
            r"\s*-?\s*music\s*$",
            r"\s*-?\s*vevo\s*$",
            r"\s*-?\s*records\s*$",
            r"\s*-?\s*label\s*$",
            r"\s*-?\s*entertainment\s*$",
        ]

        cleaned = name.strip()

        for suffix in suffixes_to_remove:
            cleaned = re.sub(suffix, "", cleaned, flags=re.IGNORECASE)

        return cleaned.strip()

    def _is_likely_artist_channel(self, channel_name: str) -> bool:
        """Determina si un canal es probablemente de un artista"""
        if not channel_name or len(channel_name) < 2:
            return False

        # Excluir canales obviamente no artistas
        excluded_keywords = [
            "youtube",
            "music",
            "records",
            "entertainment",
            "media",
            "network",
            "channel",
            "tv",
            "radio",
            "podcast",
            "news",
            "compilation",
            "playlist",
            "mix",
            "various",
            "varios",
            "different",
            "unknown",
        ]

        for keyword in excluded_keywords:
            if keyword in channel_name.lower():
                return False

        return True

    def _is_likely_artist_name(self, name: str) -> bool:
        """Determina si un texto es probablemente un nombre de artista"""
        if not name or len(name) < 2:
            return False

        # Excluir palabras comunes que no son artistas
        excluded_words = [
            "official",
            "video",
            "music",
            "audio",
            "song",
            "track",
            "single",
            "album",
            "ep",
            "live",
            "remix",
            "cover",
            "acoustic",
            "instrumental",
            "lyric",
            "lyrics",
            "karaoke",
            "demo",
            "version",
            "edit",
        ]

        name_lower = name.lower()
        for word in excluded_words:
            if word == name_lower:
                return False

        return True

    def _is_likely_album_name(self, name: str) -> bool:
        """Determina si un texto es probablemente un nombre de álbum"""
        if not name or len(name) < 2:
            return False

        name_lower = name.lower().strip()

        # Verificar palabras de exclusión
        for exclusion in self.album_exclusions:
            if exclusion in name_lower:
                return False

        return True

    def _extract_year_from_text(self, text: str) -> Optional[int]:
        """Extrae año de un texto"""
        matches = re.findall(self.year_patterns[0], text)
        if matches:
            return int(matches[0])
        return None

    def _deduplicate_and_rank_artists(
        self, artists: List[ExtractedArtistInfo]
    ) -> List[ExtractedArtistInfo]:
        """Deduplica y rankea artistas por confianza"""
        if not artists:
            return []

        # Agrupar por nombre (ignorando case)
        artist_groups: Dict[str, List[ExtractedArtistInfo]] = {}
        for artist in artists:
            key = artist.name.lower().strip()
            if key not in artist_groups:
                artist_groups[key] = []
            artist_groups[key].append(artist)

        # Seleccionar el mejor de cada grupo
        deduplicated = []
        for group in artist_groups.values():
            # Ordenar por confianza y tomar el mejor
            best_artist = max(group, key=lambda x: x.confidence_score)
            deduplicated.append(best_artist)

        # Ordenar por confianza descendente
        return sorted(deduplicated, key=lambda x: x.confidence_score, reverse=True)

    def _deduplicate_albums(
        self, albums: List[ExtractedAlbumInfo]
    ) -> List[ExtractedAlbumInfo]:
        """Deduplica álbumes"""
        if not albums:
            return []

        # Agrupar por título (ignorando case)
        album_groups: Dict[str, List[ExtractedAlbumInfo]] = {}
        for album in albums:
            key = album.title.lower().strip()
            if key not in album_groups:
                album_groups[key] = []
            album_groups[key].append(album)

        # Seleccionar el mejor de cada grupo
        deduplicated = []
        for group in album_groups.values():
            best_album = max(group, key=lambda x: x.confidence_score)
            deduplicated.append(best_album)

        # Ordenar por confianza descendente
        return sorted(deduplicated, key=lambda x: x.confidence_score, reverse=True)
