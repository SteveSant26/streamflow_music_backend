"""
Test runner principal para user_profile
Ejecuta todos los tests de la aplicación user_profile
"""
<<<<<<< HEAD

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
import os
import sys
import unittest

# Agregar el directorio src al PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django

django.setup()


def run_all_tests():
    """Ejecuta todos los tests de user_profile"""
    # Descubrir todos los tests en el directorio user_profile
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Ejecutar los tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_specific_layer(layer):
    """Ejecuta tests de una capa específica"""
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), layer)

    if not os.path.exists(start_dir):
        print(f"Directorio {layer} no existe")
        return False

    suite = loader.discover(start_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ejecutar tests de user_profile")
    parser.add_argument(
        "--layer",
        choices=["domain", "infrastructure", "api", "use_cases"],
        help="Ejecutar tests de una capa específica",
    )

    args = parser.parse_args()

    if args.layer:
        print(f"\n🧪 Ejecutando tests de la capa: {args.layer}")
        success = run_specific_layer(args.layer)
    else:
        print("\n🧪 Ejecutando todos los tests de user_profile")
        success = run_all_tests()

    if success:
        print("\n✅ Todos los tests pasaron exitosamente!")
        sys.exit(0)
    else:
        print("\n❌ Algunos tests fallaron")
        sys.exit(1)
