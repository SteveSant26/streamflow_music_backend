CUSTOM_MIDDLEWARE = [
    # Se agrega esto para el manejo de errores
    "common.middlewares.error_handler_middleware.ErrorHandlerMiddleware",
    # Se agrega esto para el manejo de logs
    "common.middlewares.logging_middleware.LoggingMiddleware",
]

DJANGO_MIDDLEWARE = [
    # Se agrega esto para el acople con django
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

MIDDLEWARE = DJANGO_MIDDLEWARE + CUSTOM_MIDDLEWARE
