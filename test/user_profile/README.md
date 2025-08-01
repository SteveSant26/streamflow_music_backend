# Comandos para Testing - User Profile

## Ejecutar todos los tests
```bash
# Desde la raíz del proyecto
python manage.py test test.user_profile

# Usando el runner personalizado
python test/user_profile/run_tests.py
```

## Ejecutar tests por capas

```bash
# Tests del dominio (entidades)
python test/user_profile/run_tests.py --layer domain

# Tests de casos de uso
python test/user_profile/run_tests.py --layer use_cases

# Tests de infraestructura (modelos, repositorios)
python test/user_profile/run_tests.py --layer infrastructure

# Tests de API (views, serializers)
python test/user_profile/run_tests.py --layer api
```

## Ejecutar tests específicos

```bash
# Solo tests de entidades
python manage.py test test.user_profile.domain.test_entities

# Solo tests de casos de uso
python manage.py test test.user_profile.use_cases.test_get_user_profile

# Solo tests de modelos
python manage.py test test.user_profile.infrastructure.test_models

# Solo tests de API
python manage.py test test.user_profile.api.test_views
```

## Coverage (si tienes coverage instalado)

```bash
# Instalar coverage
pip install coverage

# Ejecutar tests con coverage
coverage run --source='src/apps/user_profile' manage.py test test.user_profile
coverage report
coverage html
```

## Tests con pytest (alternativa)

```bash
# Instalar pytest-django
pip install pytest pytest-django

# Ejecutar con pytest
pytest test/user_profile/
pytest test/user_profile/domain/
pytest test/user_profile/api/test_views.py::TestUserProfileAPI::test_get_user_profile_success
```
