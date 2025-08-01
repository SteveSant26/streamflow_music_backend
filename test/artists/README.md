# Tests para la App Artists

Este directorio contiene todos los tests para la aplicación **Artists** siguiendo la arquitectura hexagonal.

## 📁 Estructura de Tests

```
test/artists/
├── README.md                      # Este archivo
├── conftest.py                   # Configuraciones compartidas
├── run_tests.py                  # Runner personalizado
├── run_all_direct_tests.py       # Runner para tests directos
├── api/
│   ├── __init__.py
│   ├── test_serializers.py      # Tests de serializers
│   └── test_views.py             # Tests de vistas API
├── domain/
│   ├── __init__.py
│   └── test_entities.py          # Tests de entidades
├── infrastructure/
│   ├── __init__.py
│   ├── test_models.py            # Tests de modelos Django
│   └── test_repository.py        # Tests de repositorio
├── use_cases/
│   ├── __init__.py
│   ├── test_get_artist.py        # Test obtener artista por ID
│   ├── test_get_all_artists.py   # Test obtener todos los artistas
│   ├── test_search_artists.py    # Test buscar artistas por nombre
│   ├── test_artists_by_country.py # Test artistas por país
│   ├── test_popular_artists.py   # Test artistas populares
│   └── test_verified_artists.py  # Test artistas verificados
├── test_direct.py                # Tests directos de entidades
├── test_use_cases_direct.py      # Tests directos de casos de uso
├── test_models_direct.py         # Tests directos de modelos
└── test_serializers_direct.py    # Tests directos de serializers
```

## 🧪 Casos de Uso Cubiertos

### Domain Layer
- ✅ `ArtistEntity` - Entidad del dominio
- ✅ Validaciones de campos requeridos
- ✅ Campos opcionales y por defecto

### Use Cases Layer
- ✅ `GetArtistUseCase` - Obtener artista por ID
- ✅ `GetAllArtistsUseCase` - Obtener todos los artistas
- ✅ `SearchArtistsByNameUseCase` - Buscar por nombre
- ✅ `GetArtistsByCountryUseCase` - Obtener por país
- ✅ `GetPopularArtistsUseCase` - Artistas populares
- ✅ `GetVerifiedArtistsUseCase` - Artistas verificados

### Infrastructure Layer
- ✅ `ArtistModel` - Modelo Django
- ✅ `ArtistRepository` - Repositorio con implementación completa
- ✅ Consultas y filtros avanzados

### API Layer
- ✅ `ArtistResponseSerializer` - Serializer de respuesta
- ✅ `CreateArtistSerializer` - Serializer de creación
- ✅ `UpdateArtistSerializer` - Serializer de actualización
- ✅ Validaciones de entrada y salida

## 🚀 Comandos para Ejecutar Tests

```bash
# Tests directos (recomendado)
python test/artists/run_all_direct_tests.py

# Tests individuales
python test/artists/test_direct.py
python test/artists/test_use_cases_direct.py
python test/artists/test_models_direct.py
python test/artists/test_serializers_direct.py

# Test runner personalizado
python test/artists/run_tests.py

# Ejecutar con Django test runner
python manage.py test test.artists
```

## 🔧 Configuración

Los tests están configurados para:
- ✅ Usar SQLite en memoria para isolation
- ✅ Cargar variables de entorno desde `.env.dev`
- ✅ Bypassing auth requirements para testing
- ✅ Logging detallado para debugging

## 📊 Coverage Esperado

- **Domain**: 100% - Entidades puras
- **Use Cases**: 95%+ - Lógica de negocio
- **Infrastructure**: 90%+ - Models y Repository
- **API**: 85%+ - Serializers y Views
