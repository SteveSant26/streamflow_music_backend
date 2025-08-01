#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from src.apps.user_profile.models import UserProfile

# Check existing users
users = UserProfile.objects.all()
print(f"Total de usuarios existentes: {users.count()}")

for user in users:
    print(f"- Email: {user.email}, Password: {'Sí' if user.password else 'No'}")

if users.count() == 0:
    print("No hay usuarios existentes, la migración debería funcionar sin problemas.")
else:
    print("Hay usuarios existentes sin contraseña. Necesitamos crear una migración personalizada.")
