# Imagen base
FROM python:3.11-slim

# Evita prompts en instalaciones
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del código del proyecto
COPY . .

# Variables de entorno
ENV DJANGO_SETTINGS_MODULE=config.settings.base
ENV ENV_FILE_PATH=/app/.env.dev

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput || true

# Exponer el puerto del servidor de desarrollo
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
