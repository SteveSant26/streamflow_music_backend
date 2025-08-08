#!/usr/bin/env python3
"""
Analiza el impacto de cobertura para priorizar tests
"""

# Top archivos con 0% cobertura y mayor número de líneas (mayor impacto)
high_impact_files = [
    ("src/common/adapters/media/youtube_service.py", 238),
    ("src/common/utils/music_metadata_extractor.py", 208),
    ("src/common/adapters/media/audio_download_service.py", 200),
    ("src/common/adapters/media/unified_music_service.py", 193),
    ("src/common/adapters/lyrics/lyrics_service.py", 188),
    ("src/apps/songs/use_cases/music_track_artist_album_extractor_use_case.py", 115),
    ("src/apps/playlists/infrastructure/repository/playlist_repository.py", 118),
    ("src/apps/songs/infrastructure/repository/song_repository.py", 114),
    ("src/common/utils/validators.py", 99),
    ("src/apps/genres/services/music_genre_analyzer.py", 99),
    ("src/apps/payments/api/dtos/payment_dtos.py", 95),
    ("src/apps/payments/infrastructure/services/stripe_service.py", 93),
]

print("TOP 12 ARCHIVOS CON MAYOR IMPACTO (0% cobertura):")
print("=" * 80)
for i, (file, lines) in enumerate(high_impact_files):
    print(f"{i+1:2d}. {file:<80} ({lines:3d} líneas)")

print("\n" + "=" * 80)
print(f"TOTAL LÍNEAS POTENCIALES: {sum(lines for _, lines in high_impact_files):,}")
print(
    "ESTRATEGIA: Crear tests para estos archivos aumentará significativamente la cobertura"
)
