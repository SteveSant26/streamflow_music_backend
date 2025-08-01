# Comandos para Testing - Songs

## Ejecutar todos los tests
```bash
# Desde la raíz del proyecto
python manage.py test test.songs

# Usando el runner personalizado
python test/songs/run_tests.py
```

## Ejecutar tests por capas

```bash
# Tests del dominio (entidades)
python test/songs/run_tests.py --layer domain

# Tests de casos de uso
python test/songs/run_tests.py --layer use_cases

# Tests de infraestructura (modelos, repositorios)
python test/songs/run_tests.py --layer infrastructure

# Tests de API (views, serializers)
python test/songs/run_tests.py --layer api
```

## Ejecutar tests específicos

```bash
# Solo tests de entidades
python manage.py test test.songs.domain.test_entities

# Tests de casos de uso específicos
python manage.py test test.songs.use_cases.test_get_song
python manage.py test test.songs.use_cases.test_search_songs
python manage.py test test.songs.use_cases.test_get_popular_songs

# Tests de modelos
python manage.py test test.songs.infrastructure.test_models

# Tests de repositorios
python manage.py test test.songs.infrastructure.test_repository

# Tests de API
python manage.py test test.songs.api.test_views
python manage.py test test.songs.api.test_serializers
```

## Coverage (si tienes coverage instalado)

```bash
# Instalar coverage
pip install coverage

# Ejecutar tests con coverage para songs
coverage run --source='src/apps/songs' manage.py test test.songs
coverage report
coverage html
```

## Estructura de Tests

```
test/songs/
├── __init__.py
├── conftest.py                 # Configuración y datos de prueba
├── README.md                   # Este archivo
├── run_tests.py               # Runner personalizado
├── domain/
│   └── test_entities.py       # Tests de SongEntity y excepciones
├── use_cases/
│   ├── test_get_song.py       # Tests para obtener canción
│   ├── test_search_songs.py   # Tests para búsqueda
│   └── test_get_popular_songs.py # Tests para canciones populares
├── infrastructure/
│   ├── test_models.py         # Tests de modelos Django
│   └── test_repository.py     # Tests de repositorios
└── api/
    ├── test_views.py          # Tests de vistas/endpoints
    └── test_serializers.py    # Tests de serializers
```

## Tipos de Tests

### Domain Layer
- Validación de entidades
- Lógica de negocio
- Excepciones del dominio

### Use Cases Layer
- Casos de uso individuales
- Interacción entre capas
- Validación de flujos

### Infrastructure Layer
- Modelos Django
- Repositorios
- Acceso a datos

### API Layer
- Endpoints REST
- Serialización
- Validación de entrada/salida

## Convenciones

- Usar `Test` como sufijo para clases de test
- Usar `setUp` y `tearDown` para preparación/limpieza
- Usar nombres descriptivos para métodos de test
- Agrupar tests relacionados en la misma clase
- Usar mocks para dependencias externas
