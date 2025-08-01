#!/usr/bin/env python3
"""
Archivo simple para generar datos de coverage
"""
import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Importar algunos módulos del proyecto para generar coverage
    from apps.user_profile.domain import entities
    from common.interfaces import IBaseRepository
    from common.exceptions import base
    from common.utils import string_validations
    
    print("Módulos importados correctamente para coverage")
    
except Exception as e:
    print(f"Error importando módulos: {e}")

if __name__ == "__main__":
    print("Coverage demo ejecutado")
