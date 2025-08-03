# Imagen base de Python
FROM python:3.11-slim

# Evitar prompts durante instalaciones
ENV DEBIAN_FRONTEND=noninteractive

# Variables comunes en entornos Django
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Recoger archivos estáticos (opcional)
RUN python manage.py collectstatic --noinput || true

# Exponer el puerto de desarrollo de Django
EXPOSE 8000

# Comando por defecto para levantar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
