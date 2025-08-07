"""
Test simple para verificar que los nuevos endpoints de playlists funcionan correctamente
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.playlists.infrastructure.models import PlaylistModel

User = get_user_model()


class TestPlaylistEndpoints(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@test.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@test.com", password="testpass123"
        )
        
        # Crear playlists de prueba
        self.public_playlist_user1 = PlaylistModel.objects.create(
            name="Public Playlist 1",
            description="A public playlist",
            user_id=str(self.user1.id),
            is_public=True
        )
        
        self.private_playlist_user1 = PlaylistModel.objects.create(
            name="Private Playlist 1",
            description="A private playlist",
            user_id=str(self.user1.id),
            is_public=False
        )
        
        self.public_playlist_user2 = PlaylistModel.objects.create(
            name="Public Playlist 2",
            description="Another public playlist",
            user_id=str(self.user2.id),
            is_public=True
        )

    def test_list_playlists_anonymous(self):
        """Test que usuarios anónimos solo ven playlists públicas"""
        response = self.client.get("/api/playlists/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Debe devolver solo playlists públicas
        data = response.json()
        playlist_names = [p["name"] for p in data]
        
        self.assertIn("Public Playlist 1", playlist_names)
        self.assertIn("Public Playlist 2", playlist_names)
        self.assertNotIn("Private Playlist 1", playlist_names)

    def test_list_playlists_authenticated(self):
        """Test que usuarios autenticados ven playlists públicas + sus propias playlists"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/playlists/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        playlist_names = [p["name"] for p in data]
        
        # Debe incluir playlists públicas de otros usuarios
        self.assertIn("Public Playlist 2", playlist_names)
        # Debe incluir sus propias playlists (públicas y privadas)
        self.assertIn("Public Playlist 1", playlist_names)
        self.assertIn("Private Playlist 1", playlist_names)

    def test_user_playlists_endpoint(self):
        """Test del endpoint para obtener playlists de un usuario específico"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/user/profile/{self.user1.id}/playlists/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        playlist_names = [p["name"] for p in data]
        
        # Solo debe incluir playlists del usuario específico
        self.assertIn("Public Playlist 1", playlist_names)
        self.assertIn("Private Playlist 1", playlist_names)
        self.assertNotIn("Public Playlist 2", playlist_names)

    def test_user_playlists_endpoint_forbidden(self):
        """Test que usuarios no pueden ver playlists de otros usuarios"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/user/profile/{self.user2.id}/playlists/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_playlist_requires_auth(self):
        """Test que crear playlist requiere autenticación"""
        response = self.client.post("/api/playlists/", {
            "name": "New Playlist",
            "description": "Test playlist"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_playlist_authenticated(self):
        """Test que usuarios autenticados pueden crear playlists"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post("/api/playlists/", {
            "name": "New Playlist",
            "description": "Test playlist",
            "is_public": True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
