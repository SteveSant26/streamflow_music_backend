# Songs API - Filtros y Uso

## Descripción

El API de canciones ha sido optimizado para usar filtros de Django directamente, proporcionando una interfaz flexible y potente para filtrar y buscar canciones. Todos los endpoints específicos han sido consolidados en un solo endpoint principal con filtros.

## Endpoints

### GET `/api/songs/`
Obtiene lista de canciones con filtros opcionales.

### GET `/api/songs/{id}/`
Obtiene una canción específica por ID.

## Filtros Disponibles

### Filtros Básicos
- `title`: Búsqueda por título (contiene texto)
- `artist_name`: Búsqueda por nombre del artista (contiene texto)
- `artist_id`: Filtro por ID específico del artista (UUID)
- `album_title`: Búsqueda por título del álbum (contiene texto)
- `album_id`: Filtro por ID específico del álbum (UUID)
- `genre_name`: Búsqueda por género (contiene texto)
- `source_type`: Tipo de fuente (`youtube`, `upload`, `spotify`, `soundcloud`)
- `audio_quality`: Calidad de audio (`standard`, `high`, `lossless`)

### Filtros por Duración
- `min_duration`: Duración mínima en segundos
- `max_duration`: Duración máxima en segundos
- `duration_range`: Rango predefinido:
  - `short`: Menos de 3 minutos (< 180 segundos)
  - `medium`: Entre 3 y 6 minutos (180-360 segundos)
  - `long`: Más de 6 minutos (> 360 segundos)

### Filtros por Métricas
- `min_play_count` / `max_play_count`: Rango de reproducciones
- `min_favorite_count` / `max_favorite_count`: Rango de favoritos
- `min_download_count` / `max_download_count`: Rango de descargas

### Filtros Booleanos
- `has_lyrics`: Solo canciones con letra (`true`/`false`)
- `has_file_url`: Solo canciones con archivo de audio (`true`/`false`)
- `has_thumbnail`: Solo canciones con imagen (`true`/`false`)

### Filtros por Fechas
- `created_after` / `created_before`: Rango de fechas de creación
- `last_played_after` / `last_played_before`: Rango de última reproducción
- `release_after` / `release_before`: Rango de fechas de lanzamiento

### Filtros Especiales
- `popular`: Solo canciones populares con >1000 reproducciones (`true`)
- `recent`: Solo canciones agregadas en los últimos 30 días (`true`)
- `trending`: Solo canciones en tendencia (reproducidas en los últimos 7 días) (`true`)
- `search`: Búsqueda general en título, artista, álbum, letra y géneros

### Ordenamiento
- `ordering`: Ordenar por campos:
  - `title`, `duration_seconds`, `play_count`, `favorite_count`, `download_count`
  - `created_at`, `updated_at`, `last_played_at`, `release_date`
  - `artist__name`, `album__title`, `artist__followers_count`
- Para orden descendente usar `-` antes del campo: `-play_count`

## Ejemplos de Uso

### Canciones populares
```
GET /api/songs/?popular=true&ordering=-play_count
```

### Canciones de un artista específico
```
GET /api/songs/?artist_name=Shakira&ordering=-play_count
```

### Canciones por género
```
GET /api/songs/?genre_name=Rock&ordering=title
```

### Canciones por duración
```
GET /api/songs/?duration_range=short&ordering=-favorite_count
```

### Canciones trending (en tendencia)
```
GET /api/songs/?trending=true&ordering=-last_played_at
```

### Búsqueda general
```
GET /api/songs/?search=bohemian%20rhapsody
```

### Canciones con letra
```
GET /api/songs/?has_lyrics=true&genre_name=Rock
```

### Canciones de un álbum específico
```
GET /api/songs/?album_id=12345678-1234-1234-1234-123456789012
```

### Canciones por rango de reproducciones
```
GET /api/songs/?min_play_count=1000&max_play_count=10000&ordering=-play_count
```

### Canciones recientes de alta calidad
```
GET /api/songs/?recent=true&audio_quality=high&has_file_url=true
```

### Combinando múltiples filtros
```
GET /api/songs/?artist_name=Beatles&duration_range=medium&has_lyrics=true&min_play_count=500&ordering=-favorite_count
```

## Campos de Respuesta

Cada canción incluye la siguiente información:

```json
{
  "id": "uuid",
  "title": "Nombre de la canción",
  "artist_id": "uuid-del-artista",
  "artist_name": "Nombre del artista",
  "album_id": "uuid-del-album",
  "album_title": "Nombre del álbum",
  "genres": [
    {
      "id": "uuid-genero",
      "name": "Rock"
    }
  ],
  "duration_seconds": 240,
  "track_number": 3,
  "file_url": "https://storage.../audio.mp3",
  "thumbnail_url": "https://storage.../thumb.jpg",
  "lyrics": "Letra de la canción...",
  "play_count": 1500,
  "favorite_count": 85,
  "download_count": 120,
  "source_type": "youtube",
  "source_id": "video-id",
  "source_url": "https://youtube.com/watch?v=...",
  "audio_quality": "standard",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "last_played_at": "2023-12-01T10:30:00Z",
  "release_date": "2023-01-01T00:00:00Z"
}
```

## Casos de Uso Comunes

### Discover/Explorar
```
# Canciones populares recientes
GET /api/songs/?recent=true&popular=true&ordering=-play_count&page_size=20

# Mix de géneros
GET /api/songs/?genre_name=Pop&ordering=-favorite_count&page_size=10
```

### Playlist Building
```
# Canciones de duración similar
GET /api/songs/?duration_range=medium&min_play_count=100

# Canciones del mismo artista
GET /api/songs/?artist_id=12345&has_file_url=true&ordering=album__title,track_number
```

### Search & Discovery
```
# Búsqueda por letra
GET /api/songs/?search=love&has_lyrics=true

# Canciones sin escuchar mucho
GET /api/songs/?max_play_count=10&ordering=-created_at
```

## Paginación

La paginación está habilitada automáticamente:
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (configurado en settings)

Ejemplo:
```
GET /api/songs/?page=3&page_size=50&popular=true
```

## Performance Tips

1. **Usar filtros específicos**: En lugar de `search=`, usar filtros específicos como `artist_name=` o `genre_name=` cuando sea posible
2. **Ordenamiento eficiente**: Los campos con índices (`play_count`, `created_at`, `artist__name`) son más rápidos para ordenar
3. **Límitar resultados**: Usar `page_size` apropiado para tu uso

## Migración desde Endpoints Anteriores

### Antes (endpoints específicos):
- `/api/songs/popular/` → `/api/songs/?popular=true`
- `/api/songs/random/` → `/api/songs/?ordering=?` (usar random en frontend)
- `/api/songs/search/?q=text` → `/api/songs/?search=text`
- `/api/songs/by-artist/{id}/` → `/api/songs/?artist_id={id}`
- `/api/songs/by-genre/{name}/` → `/api/songs/?genre_name={name}`

### Ventajas del nuevo enfoque:
1. **Flexibilidad total**: Combinar cualquier filtro
2. **Performance mejorada**: Filtros aplicados en la base de datos
3. **Menos endpoints**: Una sola URL para todas las necesidades
4. **Búsqueda avanzada**: Múltiples criterios en una consulta
5. **Escalabilidad**: Fácil agregar nuevos filtros sin nuevos endpoints
