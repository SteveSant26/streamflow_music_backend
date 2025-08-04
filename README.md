# streamflow_music_backend

Este proyecto es un backend construido con Django y Django REST Framework para gestionar funcionalidades relacionadas con perfiles de usuario, música, playlists y más.

## Requisitos

- Python 3.10+
- pip
- Entorno virtual recomendado

## Instalación

1. Clona el repositorio y entra a la carpeta principal del proyecto.
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   # o
   source venv/bin/activate  # En Linux/Mac
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Migraciones y base de datos

Ejecuta las migraciones para preparar la base de datos:
```bash
python manage.py migrate
```

### Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```

### Ejecutar los tests
```bash
python manage.py test
```

### Poblacion de los generos de música en la base de datos
```bash
python manage.py populate_genres --show-stats
```




## Estructura del proyecto

- `manage.py`: Utilidad principal para comandos Django.
- `requirements.txt`: Lista de dependencias del proyecto.
- `src/`: Código fuente principal.
- `config/`: Configuración de Django.
- `test/`: Pruebas automatizadas.

## Notas
- Asegúrate de configurar correctamente las variables de entorno si usas bases de datos externas o servicios adicionales.
- Puedes personalizar la configuración en `config/settings/`.

---

¡Contribuciones y sugerencias son bienvenidas!
