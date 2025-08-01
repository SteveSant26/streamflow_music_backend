# Tests para el módulo Genres

Este directorio contiene todos los tests para el módulo **Genres** siguiendo la arquitectura hexagonal.

## Estructura

```
test/genres/
├── domain/
│   ├── __init__.py
│   └── test_entities.py         # Tests de entidades del dominio
├── use_cases/
│   ├── __init__.py
│   └── test_genre_use_cases.py  # Tests de casos de uso
├── api/
│   ├── __init__.py
│   └── test_serializers.py      # Tests de API/serializers
├── infrastructure/
│   ├── __init__.py
│   └── test_models.py           # Tests de modelos/infrastructure
└── run_all_tests.py             # Ejecutor principal
```

## Ejecución

Para ejecutar todos los tests:

```bash
cd test/genres
python run_all_tests.py
```

## Cobertura de Tests

- ✅ **Domain**: Entidades GenreEntity
- ✅ **Use Cases**: GetGenre, GetAllGenres, GetPopularGenres, SearchByName
- ✅ **API**: Serializers de genres y búsqueda
- ✅ **Infrastructure**: Modelos Django (mocked)

## Tests Incluidos

### Domain Layer
- Creación de entidades con datos completos y mínimos
- Validación de propiedades
- Representación string y igualdad

### Use Cases Layer
- Obtener género por ID
- Obtener todos los géneros
- Obtener géneros populares
- Buscar géneros por nombre
- Manejo de excepciones

### API Layer
- Validación de serializers
- Serialización de entidades
- Búsqueda de géneros
- Manejo de errores de validación

### Infrastructure Layer
- Creación y consulta de modelos
- Conversión modelo-entidad
- Operaciones CRUD básicas
