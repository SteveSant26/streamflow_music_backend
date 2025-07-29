backend/
├── archiecture.md                # Documento de arquitectura
├── commandsDjango.md             # Comandos útiles de Django
├── manage.py                     # Script principal de Django
├── README.md                     # Documentación principal
├── requirements.txt              # Dependencias del proyecto
├── sonar-project.properties      # Configuración de SonarQube
├── config/                       # Configuración global del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── urls.py
│   ├── wsgi.py
│   └── settings/                 # Configuraciones separadas por contexto
│       ├── __init__.py
│       ├── apps_settings.py
│       ├── auth_settings.py
│       ├── base.py
│       ├── database_settings.py
│       ├── jazzmin_settings.py
│       ├── middleware_settings.py
│       ├── rest_framework_settings.py
│       ├── supabase_settings.py
│       ├── templates_settings.py
│       └── utils/
│           └── env.py
├── logs/                         # Archivos de log
│   ├── dev_errors.log
│   └── dev.log
├── src/                          # Código fuente principal
│   ├── apps/                     # Aplicaciones internas
│   │   ├── api/
│   │   │   └── urls.py
│   │   └── user_profile/         # Perfil de usuario
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── tests.py
│   │       ├── api/
│   │       ├── domain/
│   │       ├── infrastructure/
│   │       ├── migrations/
│   │       └── use_cases/
│   ├── common/                   # Utilidades y componentes comunes
│   │   ├── core/
│   │   │   ├── authentication_backend.py
│   │   │   ├── authentication.py
│   │   │   └── pagination.py
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   └── base.py
│   │   ├── interfaces/
│   │   │   ├── IBaseRepository.py
│   │   │   └── types.py
│   │   ├── middlewares/
│   │   ├── mixins/
│   │   └── utils/
│   └── docs/                     # Documentación OpenAPI/Swagger
│       ├── __init__.py
│       ├── schema.py
│       └── urls.py
└── tests/                        # Pruebas unitarias y de integración
    └── apps/
        └── user_profile/
