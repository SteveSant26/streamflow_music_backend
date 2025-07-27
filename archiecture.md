my_project/
│
├── manage.py
├── requirements.txt
├── config/                  # Configuración de Django (settings, urls, wsgi, etc.)
│   └── settings.py
│
├── src/                     # Código fuente
│   ├── domain/              # Lógica de negocio pura
│   │   └── user/
│   │       ├── entities.py  # Clases de dominio (User, etc.)
│   │       └── interfaces/  # Interfaces (protocolos) que deben implementar los adaptadores
│   │           └── repositories.py
│   │
│   ├── application/         # Casos de uso (servicios)
│   │   └── user/
│   │       └── use_cases.py
│   │
│   ├── infrastructure/      # Detalles externos (ORM, serializers, DRF, etc.)
│   │   └── user/
│   │       ├── models.py    # Modelos Django
│   │       ├── serializers.py
│   │       └── repositories.py  # Implementaciones de interfaces
│   │
│   ├── api/                 # Controladores y rutas DRF
│   │   └── user/
│   │       ├── views.py
│   │       └── urls.py
│   │
│   └── shared/              # Utilidades comunes (exceptions, utils, etc.)
│       └── exceptions.py
