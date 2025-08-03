# Refactorización del Sistema de Mappers

## Resumen

Se ha refactorizado el sistema de conversión entre entidades de dominio y modelos de Django siguiendo el principio de responsabilidad única (SRP). En lugar de definir `model_to_entity()` y `entity_to_model()` dentro de cada repositorio, estas funciones se han movido a módulos de mapeo dedicados.

## Estructura Creada

### Mappers Base
- **BaseInfrastructureMapper**: Clase base abstracta que extiende AbstractMapper con métodos específicos para infraestructura:
  - `entity_to_model()`: Convierte entidad a diccionario de datos del modelo
  - `entity_to_model_instance()`: Convierte entidad a instancia del modelo Django
  - `model_to_entity()`: Convierte modelo Django a entidad (heredado)

### Mappers por Entidad

#### 1. ArtistMapper (`common/infrastructure/mappers/artist_mapper.py`)
```python
class ArtistMapper(BaseInfrastructureMapper[ArtistModel, ArtistEntity])
```

#### 2. AlbumMapper (`common/infrastructure/mappers/album_mapper.py`)
```python
class AlbumMapper(BaseInfrastructureMapper[AlbumModel, AlbumEntity])
```

#### 3. GenreMapper (`common/infrastructure/mappers/genre_mapper.py`)
```python
class GenreMapper(BaseInfrastructureMapper[GenreModel, GenreEntity])
```

#### 4. SongMapper (`common/infrastructure/mappers/song_mapper.py`)
```python
class SongMapper(BaseInfrastructureMapper[SongModel, SongEntity])
```
- Incluye método especial `set_entity_genres_to_model()` para manejar relaciones many-to-many

#### 5. UserMapper (`common/infrastructure/mappers/user_mapper.py`)
```python
class UserMapper(BaseInfrastructureMapper[UserProfileModel, UserProfileEntity])
```

## Cambios en Repositorios

Todos los repositorios han sido refactorizados para usar los mappers correspondientes:

### Ejemplo - GenreRepository
```python
class GenreRepository(BaseDjangoRepository[GenreEntity, GenreModel], IGenreRepository):
    def __init__(self):
        super().__init__(GenreModel)
        self.mapper = GenreMapper()

    def _model_to_entity(self, model: GenreModel) -> GenreEntity:
        return self.mapper.model_to_entity(model)

    def _entity_to_model(self, entity: GenreEntity) -> dict[str, Any]:
        return self.mapper.entity_to_model(entity)
```

## Mappers de API

Los mappers existentes de la capa API han sido actualizados para heredar de los mappers base:

### Ejemplo - GenreMapper API
```python
class GenreMapper(BaseGenreMapper):
    # Hereda model_to_entity y entity_to_model del BaseGenreMapper
    # Solo implementa entity_to_response_dto y dto_to_entity
```

## Correcciones en Interfaces Base

Se corrigieron inconsistencias en las interfaces base:
- `IWriteOnlyRepository._entity_to_model()` ahora retorna `Dict[str, Any]` consistentemente
- Eliminadas definiciones duplicadas y conflictivas

## Beneficios

1. **Separación de Responsabilidades**: El mapeo está centralizado y desacoplado de los repositorios
2. **Reutilización**: Los mappers pueden ser utilizados desde diferentes capas
3. **Mantenibilidad**: Cambios en el mapeo solo requieren modificar un archivo
4. **Testabilidad**: Los mappers pueden ser probados de forma independiente
5. **Arquitectura Limpia**: Eliminación de duplicación de código

## Uso con Dataclasses

Para casos simples donde se necesite crear un modelo a partir de un dict, se puede utilizar:

```python
from dataclasses import asdict

artist_entity = ArtistEntity(...)
ArtistModel.objects.create(**asdict(artist_entity))
```

Sin embargo, se recomienda usar los mappers para mayor control y consistencia.

## Archivos Modificados

### Nuevos Archivos
- `src/common/infrastructure/mappers/__init__.py`
- `src/common/infrastructure/mappers/base_infrastructure_mapper.py`
- `src/common/infrastructure/mappers/artist_mapper.py`
- `src/common/infrastructure/mappers/album_mapper.py`
- `src/common/infrastructure/mappers/genre_mapper.py`
- `src/common/infrastructure/mappers/song_mapper.py`
- `src/common/infrastructure/mappers/user_mapper.py`

### Archivos Modificados
- `src/common/interfaces/ibase_repository.py`
- `src/common/core/repositories/base_write_only_repository.py`
- `src/apps/*/infrastructure/repository/*_repository.py` (todos los repositorios)
- `src/apps/genres/api/mappers/genre_mapper.py`

## Próximos Pasos

1. Crear mappers API similares para otras entidades si es necesario
2. Considerar crear tests unitarios específicos para cada mapper
3. Documentar patrones de uso para nuevos desarrolladores
