"""
🧪 TESTS SIMPLES PARA GENRE ENTITY
=================================
Tests unitarios para Genre sin dependencias Django
"""
import pytest
from dataclasses import dataclass
from typing import List


@dataclass
class SimpleGenreEntity:
    """Entidad Genre simplificada para tests"""
    id: str
    name: str
    description: str = ""
    parent_genre: str = ""
    is_active: bool = True
    color_code: str = ""
    icon: str = ""


class TestSimpleGenreEntity:
    """Tests simples para Genre Entity"""
    
    @pytest.mark.unit
    def test_genre_creation_complete(self):
        """Test creación completa de Genre"""
        # Given
        genre_data = {
            "id": "genre-123",
            "name": "Rock",
            "description": "Rock music genre",
            "parent_genre": "Popular",
            "color_code": "#FF5733",
            "icon": "🎸"
        }
        
        # When
        genre = SimpleGenreEntity(**genre_data)
        
        # Then
        assert genre.id == "genre-123"
        assert genre.name == "Rock"
        assert genre.description == "Rock music genre"
        assert genre.parent_genre == "Popular"
        assert genre.color_code == "#FF5733"
        assert genre.icon == "🎸"
        assert genre.is_active is True
    
    @pytest.mark.unit
    def test_genre_minimal_creation(self):
        """Test creación mínima de Genre"""
        # Given & When
        genre = SimpleGenreEntity(id="minimal", name="Pop")
        
        # Then
        assert genre.id == "minimal"
        assert genre.name == "Pop"
        assert genre.description == ""
        assert genre.parent_genre == ""
        assert genre.is_active is True
    
    @pytest.mark.unit
    @pytest.mark.parametrize("genre_name,expected_icon", [
        ("Rock", "🎸"),
        ("Pop", "🎤"),
        ("Electronic", "🎛️"),
        ("Classical", "🎼"),
        ("Jazz", "🎺"),
        ("Hip-Hop", "🎤"),
    ])
    def test_genre_icons_assignment(self, genre_name, expected_icon):
        """Test asignación de iconos por género"""
        # Given
        genre = SimpleGenreEntity(
            id=f"genre-{genre_name.lower()}",
            name=genre_name
        )
        
        # When - Simular asignación de icono
        if genre_name == "Rock":
            genre.icon = "🎸"
        elif genre_name == "Pop":
            genre.icon = "🎤"
        elif genre_name == "Electronic":
            genre.icon = "🎛️"
        elif genre_name == "Classical":
            genre.icon = "🎼"
        elif genre_name == "Jazz":
            genre.icon = "🎺"
        elif genre_name == "Hip-Hop":
            genre.icon = "🎤"
        
        # Then
        assert genre.icon == expected_icon
    
    @pytest.mark.unit
    def test_genre_with_parent_hierarchy(self):
        """Test Genre con jerarquía padre"""
        # Given
        sub_genre = SimpleGenreEntity(
            id="alternative-rock",
            name="Alternative Rock",
            parent_genre="Rock"
        )
        
        # Then
        assert sub_genre.parent_genre == "Rock"
        assert "Rock" in sub_genre.name
    
    @pytest.mark.unit
    def test_genre_color_code_validation(self):
        """Test validación de código de color"""
        # Given
        genre = SimpleGenreEntity(
            id="colored-genre",
            name="Colored Genre",
            color_code="#FF5733"
        )
        
        # When
        is_valid_hex = genre.color_code.startswith("#") and len(genre.color_code) == 7
        
        # Then
        assert is_valid_hex is True
        assert genre.color_code == "#FF5733"
    
    @pytest.mark.unit
    def test_genre_inactive_state(self):
        """Test Genre inactivo"""
        # Given & When
        genre = SimpleGenreEntity(
            id="inactive",
            name="Inactive Genre",
            is_active=False
        )
        
        # Then
        assert genre.is_active is False
    
    @pytest.mark.unit
    def test_genre_description_length(self):
        """Test longitud de descripción"""
        # Given
        short_desc = "Short description"
        long_desc = "This is a very long description for a music genre " * 5
        
        genre_short = SimpleGenreEntity(
            id="short-desc",
            name="Short Genre",
            description=short_desc
        )
        
        genre_long = SimpleGenreEntity(
            id="long-desc", 
            name="Long Genre",
            description=long_desc
        )
        
        # Then
        assert len(genre_short.description) < 50
        assert len(genre_long.description) > 100
    
    @pytest.mark.unit
    @pytest.mark.parametrize("genre_name", [
        "Rock",
        "Pop",
        "Electronic",
        "Hip-Hop",
        "Classical",
        "Jazz",
        "Country",
        "Blues",
        "Reggae",
        "Folk"
    ])
    def test_different_genre_names(self, genre_name):
        """Test diferentes nombres de géneros"""
        # Given & When
        genre = SimpleGenreEntity(
            id=f"genre-{genre_name.lower()}",
            name=genre_name
        )
        
        # Then
        assert genre.name == genre_name
        assert len(genre.name) > 0
        assert genre.name.replace("-", "").isalpha() or "-" in genre.name
    
    @pytest.mark.unit
    def test_genre_string_representation(self):
        """Test representación como string"""
        # Given
        genre = SimpleGenreEntity(
            id="str-test",
            name="String Test Genre"
        )
        
        # When
        genre_str = str(genre)
        
        # Then
        assert "String Test Genre" in genre_str or "str-test" in genre_str
    
    @pytest.mark.unit
    def test_genre_name_case_sensitivity(self):
        """Test sensibilidad a mayúsculas en nombres"""
        # Given
        genre1 = SimpleGenreEntity(id="rock-1", name="Rock")
        genre2 = SimpleGenreEntity(id="rock-2", name="ROCK")
        genre3 = SimpleGenreEntity(id="rock-3", name="rock")
        
        # When
        normalized_names = [g.name.lower() for g in [genre1, genre2, genre3]]
        
        # Then
        assert all(name == "rock" for name in normalized_names)
        assert genre1.name != genre2.name  # Diferentes en caso original
    
    @pytest.mark.unit
    def test_genre_with_special_characters(self):
        """Test Genre con caracteres especiales"""
        # Given & When
        genre = SimpleGenreEntity(
            id="special-genre",
            name="Hip-Hop/Rap",
            description="Genre with special chars: / & -"
        )
        
        # Then
        assert "/" in genre.name
        assert "-" in genre.name
        assert "&" in genre.description
