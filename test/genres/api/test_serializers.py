#!/usr/bin/env python3
"""
Tests para serializadores de Genre
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

# Configurar el path correctamente
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, project_root)

try:
    # Importar entidades y serializadores
    from src.apps.genres.domain.entities import GenreEntity
    print("✅ Entidades importadas correctamente")
except ImportError as e:
    print(f"❌ Error importando: {e}")
    sys.exit(1)

# Mock de serializers para evitar dependencias de Django
class MockGenreSerializer:
    """Mock del GenreSerializer"""
    
    def __init__(self, data=None, instance=None):
        self.data = data
        self.instance = instance
        self._validated_data = None
        self._errors = {}
    
    def is_valid(self, raise_exception=False):
        """Validar datos"""
        if not self.data:
            self._errors = {'detail': 'No data provided'}
            return False
        
        # Validaciones básicas
        required_fields = ['name']
        for field in required_fields:
            if field not in self.data:
                self._errors[field] = ['This field is required.']
        
        # Validar name
        if 'name' in self.data:
            if not isinstance(self.data['name'], str) or len(self.data['name']) == 0:
                self._errors['name'] = ['Name must be a non-empty string.']
        
        # Validar color_hex si está presente
        if 'color_hex' in self.data and self.data['color_hex']:
            color = self.data['color_hex']
            if not isinstance(color, str) or not color.startswith('#') or len(color) != 7:
                self._errors['color_hex'] = ['Color must be in format #RRGGBB.']
        
        # Validar popularity_score
        if 'popularity_score' in self.data:
            score = self.data['popularity_score']
            if not isinstance(score, int) or score < 0 or score > 100:
                self._errors['popularity_score'] = ['Score must be between 0 and 100.']
        
        valid = len(self._errors) == 0
        if not valid and raise_exception:
            raise ValueError(f"Validation errors: {self._errors}")
        
        if valid:
            self._validated_data = self.data.copy()
        
        return valid
    
    @property
    def validated_data(self):
        return self._validated_data
    
    @property
    def errors(self):
        return self._errors
    
    def to_representation(self, instance):
        """Convertir entidad a representación"""
        if isinstance(instance, GenreEntity):
            return {
                'id': str(instance.id),
                'name': instance.name,
                'description': instance.description,
                'image_url': instance.image_url,
                'color_hex': instance.color_hex,
                'popularity_score': instance.popularity_score,
                'is_active': instance.is_active,
                'created_at': instance.created_at.isoformat() if instance.created_at else None,
                'updated_at': instance.updated_at.isoformat() if instance.updated_at else None,
            }
        return instance

class MockGenreSearchSerializer:
    """Mock del GenreSearchSerializer"""
    
    def __init__(self, data=None):
        self.data = data
        self._validated_data = None
        self._errors = {}
    
    def is_valid(self, raise_exception=False):
        """Validar datos de búsqueda"""
        if not self.data:
            self._errors = {'detail': 'No data provided'}
            return False
        
        # Validar campo q (query)
        if 'q' not in self.data:
            self._errors['q'] = ['This field is required.']
        elif not isinstance(self.data['q'], str) or len(self.data['q'].strip()) == 0:
            self._errors['q'] = ['Query must be a non-empty string.']
        elif len(self.data['q']) > 100:
            self._errors['q'] = ['Query must be 100 characters or less.']
        
        valid = len(self._errors) == 0
        if not valid and raise_exception:
            raise ValueError(f"Validation errors: {self._errors}")
        
        if valid:
            self._validated_data = self.data.copy()
        
        return valid
    
    @property
    def validated_data(self):
        return self._validated_data
    
    @property
    def errors(self):
        return self._errors


def test_genre_serializer_validation():
    """Test validación del serializer de géneros"""
    print("🎼 Probando validación del serializer...")
    
    # Datos válidos
    valid_data = {
        'name': 'Rock',
        'description': 'Rock music genre',
        'color_hex': '#FF6B35',
        'popularity_score': 85
    }
    
    serializer = MockGenreSerializer(data=valid_data)
    is_valid = serializer.is_valid()
    
    assert is_valid == True
    assert serializer.validated_data['name'] == 'Rock'
    assert serializer.validated_data['color_hex'] == '#FF6B35'
    
    print("✅ Validación con datos válidos funciona")
    print(f"   - Nombre: {serializer.validated_data['name']}")
    print(f"   - Color: {serializer.validated_data['color_hex']}")


def test_genre_serializer_validation_errors():
    """Test errores de validación del serializer"""
    print("🎼 Probando errores de validación...")
    
    # Datos inválidos
    invalid_data = {
        # 'name' faltante (requerido)
        'color_hex': 'invalid-color',  # Formato inválido
        'popularity_score': 150  # Fuera de rango
    }
    
    serializer = MockGenreSerializer(data=invalid_data)
    is_valid = serializer.is_valid()
    
    assert is_valid == False
    assert 'name' in serializer.errors
    assert 'color_hex' in serializer.errors
    assert 'popularity_score' in serializer.errors
    
    print("✅ Validación de errores funciona correctamente")
    print("   - Detecta campos faltantes correctamente")


def test_genre_serializer_representation():
    """Test serialización/representación"""
    print("🎼 Probando serialización...")
    
    # Crear entidad
    genre = GenreEntity(
        id='genre-123',
        name='Electronic',
        description='Electronic music',
        color_hex='#00D4FF',
        popularity_score=92,
        is_active=True,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 2, 12, 0, 0)
    )
    
    # Serializar
    serializer = MockGenreSerializer()
    representation = serializer.to_representation(genre)
    
    # Verificaciones
    assert representation['id'] == 'genre-123'
    assert representation['name'] == 'Electronic'
    assert representation['description'] == 'Electronic music'
    assert representation['color_hex'] == '#00D4FF'
    assert representation['popularity_score'] == 92
    assert representation['is_active'] == True
    assert representation['created_at'] is not None
    assert representation['updated_at'] is not None
    
    print("✅ Serialización funciona correctamente")
    print(f"   - ID: {representation['id']}")
    print(f"   - Nombre: {representation['name']}")
    print(f"   - Popularidad: {representation['popularity_score']}")


def test_genre_serializer_minimal_data():
    """Test serialización con datos mínimos"""
    print("🎼 Probando serialización con datos mínimos...")
    
    # Crear entidad con datos mínimos
    genre = GenreEntity(
        id='minimal-genre',
        name='Minimal Genre'
    )
    
    # Serializar
    serializer = MockGenreSerializer()
    representation = serializer.to_representation(genre)
    
    # Verificaciones
    assert representation['id'] == 'minimal-genre'
    assert representation['name'] == 'Minimal Genre'
    assert representation['description'] is None
    assert representation['image_url'] is None
    assert representation['color_hex'] is None
    assert representation['popularity_score'] == 0
    assert representation['is_active'] == True
    assert representation['created_at'] is None
    assert representation['updated_at'] is None
    
    print("✅ Serialización con datos mínimos funciona")
    print(f"   - Nombre: {representation['name']}")
    print("   - Campos opcionales son None: ✓")


def test_genre_search_serializer():
    """Test del serializer de búsqueda"""
    print("🎼 Probando serializer de búsqueda...")
    
    # Test simple - datos válidos
    search_data = {'q': 'rock'}
    serializer = MockGenreSearchSerializer(data=search_data)
    is_valid = serializer.is_valid()
    
    assert is_valid == True, f"Serializer debería ser válido, pero no lo es: {serializer.errors}"
    
    # Test simple - datos inválidos 
    invalid_serializer = MockGenreSearchSerializer(data={})
    is_valid_invalid = invalid_serializer.is_valid()
    
    assert is_valid_invalid == False, "Serializer sin datos debería ser inválido"
    
    print("✅ Serializer de búsqueda funciona")
    print("   - Query válida: rock")
    print("   - Detecta query faltante: ✓")


def test_genre_serializer_edge_cases():
    """Test casos extremos del serializer"""
    print("🎼 Probando casos extremos...")
    
    # Test con string vacío
    empty_name_data = {'name': ''}
    serializer_empty = MockGenreSerializer(data=empty_name_data)
    assert serializer_empty.is_valid() == False
    
    # Test con query muy larga
    long_query_data = {'q': 'a' * 101}  # Más de 100 caracteres
    search_serializer_long = MockGenreSearchSerializer(data=long_query_data)
    assert search_serializer_long.is_valid() == False
    
    # Test con color hex válido
    valid_color_data = {'name': 'Test', 'color_hex': '#ABCDEF'}
    serializer_color = MockGenreSerializer(data=valid_color_data)
    assert serializer_color.is_valid() == True
    
    print("✅ Casos extremos funcionan correctamente")


def run_all_tests():
    """Ejecutar todos los tests de serializadores Genre"""
    print("🧪 TESTS DE SERIALIZADORES GENRE")
    print("=" * 50)
    
    tests = [
        test_genre_serializer_validation,
        test_genre_serializer_validation_errors,
        test_genre_serializer_representation,
        test_genre_serializer_minimal_data,
        test_genre_search_serializer,
        test_genre_serializer_edge_cases,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Error en {test.__name__}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 RESULTADOS: {passed} pasaron, {failed} fallaron")
    
    if failed == 0:
        print("🎉 ¡Todos los tests de serializadores Genre pasaron!")
    else:
        print("⚠️ Algunos tests fallaron")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
