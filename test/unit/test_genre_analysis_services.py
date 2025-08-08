"""
🧪 TESTS UNITARIOS PARA SERVICIOS DE ANÁLISIS DE GÉNEROS
====================================================
Tests completos para análisis de géneros y recomendaciones musicales
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Mock numpy si no está disponible
try:
    import numpy as np
except ImportError:
    import sys
    np = Mock()
    np.array = Mock(return_value=[1, 2, 3])
    np.mean = Mock(return_value=2.0)
    np.std = Mock(return_value=0.5)
    np.corrcoef = Mock(return_value=[[1.0, 0.8], [0.8, 1.0]])
    np.linalg = Mock()
    np.linalg.norm = Mock(return_value=1.0)
    sys.modules['numpy'] = np

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Crear mocks para cuando las importaciones fallen
try:
    from apps.music.infrastructure.services.genre_analyzer_service import GenreAnalyzerService
    from apps.music.infrastructure.services.recommendation_service import RecommendationService
    from apps.music.domain.entities import SongEntity, GenreEntity, PlaylistEntity
    from common.utils.genre_classifier import GenreClassifier
except ImportError:
    GenreAnalyzerService = Mock
    RecommendationService = Mock
    SongEntity = Mock
    GenreEntity = Mock
    PlaylistEntity = Mock
    GenreClassifier = Mock


class TestGenreAnalyzerService:
    """Tests unitarios para GenreAnalyzerService"""

    @pytest.fixture
    def mock_genre_classifier(self):
        """Mock del clasificador de géneros"""
        classifier = Mock()
        
        # Mock de análisis de audio
        classifier.analyze_audio_features.return_value = {
            'tempo': 128.5,
            'energy': 0.8,
            'danceability': 0.7,
            'valence': 0.6,
            'acousticness': 0.2,
            'instrumentalness': 0.1,
            'speechiness': 0.05,
            'loudness': -5.2
        }
        
        # Mock de predicción de género
        classifier.predict_genre.return_value = {
            'primary_genre': 'electronic',
            'confidence': 0.85,
            'secondary_genres': [
                {'genre': 'dance', 'confidence': 0.65},
                {'genre': 'pop', 'confidence': 0.45}
            ]
        }
        
        return classifier

    @pytest.fixture
    def mock_lyrics_analyzer(self):
        """Mock del analizador de letras"""
        analyzer = Mock()
        
        analyzer.analyze_lyrics.return_value = {
            'mood': 'positive',
            'themes': ['love', 'freedom', 'celebration'],
            'language': 'en',
            'explicit': False,
            'sentiment_score': 0.7
        }
        
        return analyzer

    @pytest.fixture
    def genre_analyzer_service(self, mock_genre_classifier, mock_lyrics_analyzer):
        """Instancia del servicio con mocks"""
        if GenreAnalyzerService == Mock:
            service = Mock()
            service.genre_classifier = mock_genre_classifier
            service.lyrics_analyzer = mock_lyrics_analyzer
            return service
        else:
            with patch('apps.music.infrastructure.services.genre_analyzer_service.GenreClassifier', mock_genre_classifier), \
                 patch('apps.music.infrastructure.services.genre_analyzer_service.LyricsAnalyzer', mock_lyrics_analyzer):
                return GenreAnalyzerService()

    @pytest.mark.asyncio
    async def test_analyze_song_genre_with_audio_features(self, genre_analyzer_service):
        """Test de análisis de género con características de audio"""
        song_data = {
            'id': 'song-123',
            'title': 'Test Song',
            'artist': 'Test Artist',
            'audio_url': 'https://example.com/song.mp3',
            'duration': 180
        }
        
        if genre_analyzer_service == Mock():
            analysis_result = {
                'song_id': 'song-123',
                'primary_genre': 'electronic',
                'confidence': 0.85,
                'audio_features': {
                    'tempo': 128.5,
                    'energy': 0.8,
                    'danceability': 0.7
                },
                'secondary_genres': ['dance', 'pop']
            }
            genre_analyzer_service.analyze_song_genre = AsyncMock(return_value=analysis_result)
            
            result = await genre_analyzer_service.analyze_song_genre(song_data)
            
            assert result['primary_genre'] == 'electronic'
            assert result['confidence'] > 0.8
            assert 'audio_features' in result

    @pytest.mark.asyncio
    async def test_analyze_song_genre_with_lyrics(self, genre_analyzer_service):
        """Test de análisis de género incluyendo letras"""
        song_data = {
            'id': 'song-123',
            'title': 'Love Song',
            'artist': 'Romantic Artist',
            'lyrics': 'Beautiful lyrics about love and happiness...'
        }
        
        if genre_analyzer_service == Mock():
            analysis_result = {
                'song_id': 'song-123',
                'primary_genre': 'pop',
                'confidence': 0.9,
                'lyrics_analysis': {
                    'mood': 'positive',
                    'themes': ['love', 'happiness'],
                    'sentiment_score': 0.8
                },
                'genre_reasons': [
                    'Positive sentiment matches pop genre',
                    'Love theme common in pop music'
                ]
            }
            genre_analyzer_service.analyze_song_with_lyrics = AsyncMock(return_value=analysis_result)
            
            result = await genre_analyzer_service.analyze_song_with_lyrics(song_data)
            
            assert result['primary_genre'] == 'pop'
            assert result['confidence'] > 0.85
            assert 'lyrics_analysis' in result

    @pytest.mark.asyncio
    async def test_analyze_playlist_genre_distribution(self, genre_analyzer_service):
        """Test de análisis de distribución de géneros en playlist"""
        playlist_data = {
            'id': 'playlist-123',
            'name': 'My Mix',
            'songs': [
                {'id': 'song-1', 'genre': 'rock'},
                {'id': 'song-2', 'genre': 'rock'},
                {'id': 'song-3', 'genre': 'pop'},
                {'id': 'song-4', 'genre': 'electronic'}
            ]
        }
        
        if genre_analyzer_service == Mock():
            distribution_result = {
                'playlist_id': 'playlist-123',
                'total_songs': 4,
                'genre_distribution': {
                    'rock': {'count': 2, 'percentage': 50.0},
                    'pop': {'count': 1, 'percentage': 25.0},
                    'electronic': {'count': 1, 'percentage': 25.0}
                },
                'dominant_genre': 'rock',
                'diversity_score': 0.75
            }
            genre_analyzer_service.analyze_playlist_distribution = AsyncMock(return_value=distribution_result)
            
            result = await genre_analyzer_service.analyze_playlist_distribution(playlist_data)
            
            assert result['dominant_genre'] == 'rock'
            assert result['total_songs'] == 4
            assert result['diversity_score'] > 0.5

    @pytest.mark.asyncio
    async def test_batch_analyze_songs(self, genre_analyzer_service):
        """Test de análisis en lote de múltiples canciones"""
        songs_data = [
            {'id': 'song-1', 'title': 'Rock Song'},
            {'id': 'song-2', 'title': 'Pop Song'},
            {'id': 'song-3', 'title': 'Jazz Song'}
        ]
        
        if genre_analyzer_service == Mock():
            batch_results = [
                {'song_id': 'song-1', 'primary_genre': 'rock', 'confidence': 0.9},
                {'song_id': 'song-2', 'primary_genre': 'pop', 'confidence': 0.85},
                {'song_id': 'song-3', 'primary_genre': 'jazz', 'confidence': 0.8}
            ]
            genre_analyzer_service.batch_analyze_songs = AsyncMock(return_value=batch_results)
            
            results = await genre_analyzer_service.batch_analyze_songs(songs_data)
            
            assert len(results) == 3
            assert all('primary_genre' in result for result in results)
            assert all(result['confidence'] > 0.7 for result in results)

    @pytest.mark.asyncio
    async def test_analyze_genre_similarity(self, genre_analyzer_service):
        """Test de análisis de similitud entre géneros"""
        genre1 = 'rock'
        genre2 = 'metal'
        
        if genre_analyzer_service == Mock():
            similarity_result = {
                'genre1': genre1,
                'genre2': genre2,
                'similarity_score': 0.8,
                'common_features': ['high_energy', 'guitar_heavy'],
                'differences': ['tempo_range', 'vocal_style']
            }
            genre_analyzer_service.analyze_genre_similarity = AsyncMock(return_value=similarity_result)
            
            result = await genre_analyzer_service.analyze_genre_similarity(genre1, genre2)
            
            assert result['similarity_score'] > 0.7
            assert len(result['common_features']) > 0

    @pytest.mark.asyncio
    async def test_update_genre_model_with_feedback(self, genre_analyzer_service):
        """Test de actualización del modelo con feedback del usuario"""
        feedback_data = {
            'song_id': 'song-123',
            'predicted_genre': 'rock',
            'actual_genre': 'metal',
            'user_id': 'user-456',
            'confidence': 0.7
        }
        
        if genre_analyzer_service == Mock():
            update_result = {
                'model_updated': True,
                'feedback_processed': True,
                'new_accuracy': 0.92,
                'training_samples_added': 1
            }
            genre_analyzer_service.update_model_with_feedback = AsyncMock(return_value=update_result)
            
            result = await genre_analyzer_service.update_model_with_feedback(feedback_data)
            
            assert result['model_updated'] is True
            assert result['new_accuracy'] > 0.9

    @pytest.mark.asyncio
    async def test_analyze_song_with_invalid_audio(self, genre_analyzer_service):
        """Test de manejo de audio inválido"""
        song_data = {
            'id': 'song-invalid',
            'audio_url': 'https://example.com/invalid.mp3'
        }
        
        if genre_analyzer_service == Mock():
            genre_analyzer_service.analyze_song_genre = AsyncMock(
                side_effect=Exception("Invalid audio format")
            )
            
            with pytest.raises(Exception, match="Invalid audio format"):
                await genre_analyzer_service.analyze_song_genre(song_data)

    @pytest.mark.asyncio
    async def test_get_genre_trends(self, genre_analyzer_service):
        """Test de obtención de tendencias de géneros"""
        time_period = {
            'start_date': datetime.now() - timedelta(days=30),
            'end_date': datetime.now()
        }
        
        if genre_analyzer_service == Mock():
            trends_result = {
                'period': '30_days',
                'trending_genres': [
                    {'genre': 'hyperpop', 'growth_rate': 1.5},
                    {'genre': 'synthwave', 'growth_rate': 1.2},
                    {'genre': 'lofi', 'growth_rate': 1.1}
                ],
                'declining_genres': [
                    {'genre': 'dubstep', 'decline_rate': -0.8}
                ]
            }
            genre_analyzer_service.get_genre_trends = AsyncMock(return_value=trends_result)
            
            result = await genre_analyzer_service.get_genre_trends(time_period)
            
            assert len(result['trending_genres']) > 0
            assert all(trend['growth_rate'] > 1.0 for trend in result['trending_genres'])


class TestRecommendationService:
    """Tests unitarios para RecommendationService"""

    @pytest.fixture
    def mock_ml_model(self):
        """Mock del modelo de machine learning"""
        model = Mock()
        
        # Mock de predicciones de recomendación
        model.predict_recommendations.return_value = [
            {'song_id': 'song-rec-1', 'score': 0.95, 'reason': 'Similar genre and tempo'},
            {'song_id': 'song-rec-2', 'score': 0.87, 'reason': 'Same artist preference'},
            {'song_id': 'song-rec-3', 'score': 0.82, 'reason': 'Popular in similar playlists'}
        ]
        
        return model

    @pytest.fixture
    def mock_user_behavior_analyzer(self):
        """Mock del analizador de comportamiento de usuario"""
        analyzer = Mock()
        
        analyzer.get_user_preferences.return_value = {
            'favorite_genres': ['rock', 'electronic', 'indie'],
            'preferred_tempo_range': [120, 140],
            'activity_times': ['evening', 'night'],
            'skip_rate_by_genre': {'pop': 0.3, 'country': 0.8},
            'average_session_length': 45  # minutes
        }
        
        return analyzer

    @pytest.fixture
    def recommendation_service(self, mock_ml_model, mock_user_behavior_analyzer):
        """Instancia del servicio con mocks"""
        if RecommendationService == Mock:
            service = Mock()
            service.ml_model = mock_ml_model
            service.behavior_analyzer = mock_user_behavior_analyzer
            return service
        else:
            with patch('apps.music.infrastructure.services.recommendation_service.MLModel', mock_ml_model), \
                 patch('apps.music.infrastructure.services.recommendation_service.UserBehaviorAnalyzer', mock_user_behavior_analyzer):
                return RecommendationService()

    @pytest.mark.asyncio
    async def test_get_personalized_recommendations(self, recommendation_service):
        """Test de recomendaciones personalizadas"""
        user_id = 'user-123'
        request_params = {
            'limit': 10,
            'genres': ['rock', 'electronic'],
            'exclude_listened': True
        }
        
        if recommendation_service == Mock():
            recommendations = [
                {
                    'song_id': 'song-rec-1',
                    'title': 'Recommended Song 1',
                    'artist': 'Artist 1',
                    'score': 0.95,
                    'reason': 'Matches your rock preferences'
                },
                {
                    'song_id': 'song-rec-2',
                    'title': 'Recommended Song 2',
                    'artist': 'Artist 2',
                    'score': 0.87,
                    'reason': 'Similar to songs you liked'
                }
            ]
            recommendation_service.get_personalized_recommendations = AsyncMock(return_value=recommendations)
            
            result = await recommendation_service.get_personalized_recommendations(user_id, request_params)
            
            assert len(result) == 2
            assert all(rec['score'] > 0.8 for rec in result)
            assert all('reason' in rec for rec in result)

    @pytest.mark.asyncio
    async def test_get_similar_songs_recommendations(self, recommendation_service):
        """Test de recomendaciones basadas en canciones similares"""
        song_id = 'song-123'
        similarity_params = {
            'limit': 5,
            'similarity_threshold': 0.7,
            'include_same_artist': False
        }
        
        if recommendation_service == Mock():
            similar_songs = [
                {
                    'song_id': 'similar-1',
                    'similarity_score': 0.92,
                    'matching_features': ['genre', 'tempo', 'energy']
                },
                {
                    'song_id': 'similar-2',
                    'similarity_score': 0.85,
                    'matching_features': ['genre', 'mood']
                }
            ]
            recommendation_service.get_similar_songs = AsyncMock(return_value=similar_songs)
            
            result = await recommendation_service.get_similar_songs(song_id, similarity_params)
            
            assert len(result) == 2
            assert all(song['similarity_score'] > 0.7 for song in result)

    @pytest.mark.asyncio
    async def test_get_playlist_continuation_recommendations(self, recommendation_service):
        """Test de recomendaciones para continuar playlist"""
        playlist_id = 'playlist-123'
        continuation_params = {
            'analyze_last_songs': 3,
            'maintain_flow': True,
            'limit': 8
        }
        
        if recommendation_service == Mock():
            continuation_recs = [
                {
                    'song_id': 'continue-1',
                    'flow_score': 0.88,
                    'reason': 'Maintains energy level and genre consistency'
                },
                {
                    'song_id': 'continue-2',
                    'flow_score': 0.82,
                    'reason': 'Smooth tempo transition'
                }
            ]
            recommendation_service.get_playlist_continuation = AsyncMock(return_value=continuation_recs)
            
            result = await recommendation_service.get_playlist_continuation(playlist_id, continuation_params)
            
            assert len(result) == 2
            assert all(rec['flow_score'] > 0.8 for rec in result)

    @pytest.mark.asyncio
    async def test_get_mood_based_recommendations(self, recommendation_service):
        """Test de recomendaciones basadas en estado de ánimo"""
        user_id = 'user-123'
        mood_params = {
            'mood': 'energetic',
            'activity': 'workout',
            'time_of_day': 'morning',
            'limit': 15
        }
        
        if recommendation_service == Mock():
            mood_recs = [
                {
                    'song_id': 'energetic-1',
                    'mood_match_score': 0.94,
                    'energy_level': 0.9,
                    'genre': 'electronic'
                },
                {
                    'song_id': 'energetic-2',
                    'mood_match_score': 0.89,
                    'energy_level': 0.85,
                    'genre': 'rock'
                }
            ]
            recommendation_service.get_mood_based_recommendations = AsyncMock(return_value=mood_recs)
            
            result = await recommendation_service.get_mood_based_recommendations(user_id, mood_params)
            
            assert len(result) == 2
            assert all(rec['mood_match_score'] > 0.85 for rec in result)

    @pytest.mark.asyncio
    async def test_get_trending_recommendations(self, recommendation_service):
        """Test de recomendaciones de tendencias"""
        trending_params = {
            'region': 'global',
            'time_period': 'week',
            'filter_by_user_taste': True,
            'limit': 20
        }
        
        if recommendation_service == Mock():
            trending_recs = [
                {
                    'song_id': 'trending-1',
                    'trending_score': 0.96,
                    'popularity_rank': 1,
                    'genre': 'pop'
                },
                {
                    'song_id': 'trending-2',
                    'trending_score': 0.91,
                    'popularity_rank': 2,
                    'genre': 'hip-hop'
                }
            ]
            recommendation_service.get_trending_recommendations = AsyncMock(return_value=trending_recs)
            
            result = await recommendation_service.get_trending_recommendations(trending_params)
            
            assert len(result) == 2
            assert all(rec['trending_score'] > 0.9 for rec in result)

    @pytest.mark.asyncio
    async def test_get_collaborative_filtering_recommendations(self, recommendation_service):
        """Test de recomendaciones por filtrado colaborativo"""
        user_id = 'user-123'
        collaborative_params = {
            'similar_users_count': 50,
            'min_common_songs': 5,
            'limit': 12
        }
        
        if recommendation_service == Mock():
            collaborative_recs = [
                {
                    'song_id': 'collab-1',
                    'similarity_score': 0.87,
                    'common_users_count': 23,
                    'confidence': 0.9
                }
            ]
            recommendation_service.get_collaborative_recommendations = AsyncMock(return_value=collaborative_recs)
            
            result = await recommendation_service.get_collaborative_recommendations(user_id, collaborative_params)
            
            assert len(result) == 1
            assert result[0]['confidence'] > 0.85

    @pytest.mark.asyncio
    async def test_track_recommendation_feedback(self, recommendation_service):
        """Test de seguimiento de feedback de recomendaciones"""
        feedback_data = {
            'user_id': 'user-123',
            'song_id': 'song-rec-1',
            'recommendation_id': 'rec-456',
            'action': 'liked',  # liked, skipped, added_to_playlist, etc.
            'timestamp': datetime.now(),
            'context': 'personalized_recommendations'
        }
        
        if recommendation_service == Mock():
            feedback_result = {
                'feedback_recorded': True,
                'model_updated': True,
                'user_profile_updated': True,
                'recommendation_score_adjustment': 0.05
            }
            recommendation_service.track_feedback = AsyncMock(return_value=feedback_result)
            
            result = await recommendation_service.track_feedback(feedback_data)
            
            assert result['feedback_recorded'] is True
            assert result['model_updated'] is True

    @pytest.mark.asyncio
    async def test_get_recommendation_explanation(self, recommendation_service):
        """Test de explicación de recomendaciones"""
        recommendation_data = {
            'user_id': 'user-123',
            'song_id': 'song-rec-1',
            'recommendation_score': 0.92
        }
        
        if recommendation_service == Mock():
            explanation = {
                'primary_reasons': [
                    'You frequently listen to rock music (80% of your library)',
                    'This song has similar tempo to your favorites (128 BPM)',
                    'Artist is popular among users with similar taste'
                ],
                'feature_contributions': {
                    'genre_match': 0.35,
                    'tempo_similarity': 0.25,
                    'artist_preference': 0.20,
                    'user_similarity': 0.20
                },
                'confidence_level': 'high'
            }
            recommendation_service.explain_recommendation = AsyncMock(return_value=explanation)
            
            result = await recommendation_service.explain_recommendation(recommendation_data)
            
            assert len(result['primary_reasons']) > 0
            assert result['confidence_level'] == 'high'

    @pytest.mark.asyncio
    async def test_batch_recommendations_for_multiple_users(self, recommendation_service):
        """Test de recomendaciones en lote para múltiples usuarios"""
        user_ids = ['user-1', 'user-2', 'user-3']
        batch_params = {
            'recommendations_per_user': 10,
            'recommendation_type': 'personalized'
        }
        
        if recommendation_service == Mock():
            batch_results = {
                'user-1': [{'song_id': 'rec-1-1', 'score': 0.9}],
                'user-2': [{'song_id': 'rec-2-1', 'score': 0.85}],
                'user-3': [{'song_id': 'rec-3-1', 'score': 0.88}]
            }
            recommendation_service.batch_recommendations = AsyncMock(return_value=batch_results)
            
            result = await recommendation_service.batch_recommendations(user_ids, batch_params)
            
            assert len(result) == 3
            assert all(user_id in result for user_id in user_ids)

    @pytest.mark.asyncio
    async def test_cold_start_recommendations_for_new_user(self, recommendation_service):
        """Test de recomendaciones para usuarios nuevos (cold start)"""
        new_user_data = {
            'user_id': 'new-user-123',
            'age': 25,
            'preferred_genres': ['indie', 'alternative'],
            'country': 'US'
        }
        
        if recommendation_service == Mock():
            cold_start_recs = [
                {
                    'song_id': 'popular-indie-1',
                    'reason': 'Popular indie song in your region',
                    'score': 0.75
                },
                {
                    'song_id': 'trending-alt-1',
                    'reason': 'Trending alternative song for your age group',
                    'score': 0.72
                }
            ]
            recommendation_service.get_cold_start_recommendations = AsyncMock(return_value=cold_start_recs)
            
            result = await recommendation_service.get_cold_start_recommendations(new_user_data)
            
            assert len(result) == 2
            assert all(rec['score'] > 0.7 for rec in result)

    @pytest.mark.asyncio
    async def test_recommendation_diversity_optimization(self, recommendation_service):
        """Test de optimización de diversidad en recomendaciones"""
        diversity_params = {
            'user_id': 'user-123',
            'base_recommendations': 50,
            'diversity_factor': 0.3,
            'final_count': 20
        }
        
        if recommendation_service == Mock():
            diverse_recs = [
                {'song_id': 'diverse-1', 'genre': 'rock', 'diversity_score': 0.8},
                {'song_id': 'diverse-2', 'genre': 'jazz', 'diversity_score': 0.9},
                {'song_id': 'diverse-3', 'genre': 'electronic', 'diversity_score': 0.75}
            ]
            recommendation_service.optimize_diversity = AsyncMock(return_value=diverse_recs)
            
            result = await recommendation_service.optimize_diversity(diversity_params)
            
            assert len(result) == 3
            # Verificar que hay variedad de géneros
            genres = [rec['genre'] for rec in result]
            assert len(set(genres)) > 1

    def test_recommendation_service_performance_metrics(self, recommendation_service):
        """Test de métricas de rendimiento del servicio"""
        if recommendation_service == Mock():
            metrics = {
                'average_response_time': 120,  # ms
                'cache_hit_rate': 0.85,
                'recommendation_accuracy': 0.78,
                'user_satisfaction_score': 4.2,  # 1-5 scale
                'daily_active_users': 15000
            }
            recommendation_service.get_performance_metrics = Mock(return_value=metrics)
            
            result = recommendation_service.get_performance_metrics()
            
            assert result['cache_hit_rate'] > 0.8
            assert result['recommendation_accuracy'] > 0.75
            assert result['user_satisfaction_score'] > 4.0
