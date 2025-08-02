#!/usr/bin/env python
"""
Runner personalizado para tests de Songs
"""
import argparse
import os
import sys
from pathlib import Path

# Configurar paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

# Configurar Django con configuración más simple para tests
# Configurar Django con env de desarrollo que tiene las keys
from dotenv import load_dotenv

load_dotenv(BASE_DIR / "config" / "settings" / ".env.dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
os.environ.setdefault("YOUTUBE_API_KEY", "test-key-for-testing")
os.environ.setdefault("SUPABASE_URL", "http://localhost:8000")
os.environ.setdefault("SUPABASE_KEY", "test-key")

import django

django.setup()

from django.conf import settings
from django.test.utils import get_runner


def run_tests(layer=None, verbosity=2):
    """
    Ejecuta tests de songs con configuración personalizada

    Args:
        layer (str): Capa específica a testear (domain, use_cases, infrastructure, api)
        verbosity (int): Nivel de detalle en la salida
    """

    # Configurar runner de tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity, interactive=True)

    # Definir patrones de tests por capa
    test_patterns = {
        "domain": ["test.songs.domain"],
        "use_cases": ["test.songs.use_cases"],
        "infrastructure": ["test.songs.infrastructure"],
        "api": ["test.songs.api"],
        "all": ["test.songs"],
    }

    # Determinar qué tests ejecutar
    if layer and layer in test_patterns:
        test_labels = test_patterns[layer]
        print(f"🎵 Ejecutando tests de Songs - Capa: {layer}")
    else:
        test_labels = test_patterns["all"]
        print("🎵 Ejecutando todos los tests de Songs")

    print("-" * 50)

    # Ejecutar tests
    failures = test_runner.run_tests(test_labels)

    # Mostrar resumen
    if failures:
        print(f"\n❌ Tests fallidos: {failures}")
        return failures
    else:
        print(f"\n✅ Todos los tests de Songs pasaron correctamente!")
        return 0


def main():
    """Función principal del runner"""
    parser = argparse.ArgumentParser(description="Runner de tests para Songs")
    parser.add_argument(
        "--layer",
        choices=["domain", "use_cases", "infrastructure", "api", "all"],
        help="Capa específica a testear",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=2,
        choices=[0, 1, 2, 3],
        help="Nivel de verbosidad (0-3)",
    )

    args = parser.parse_args()

    # Ejecutar tests
    exit_code = run_tests(layer=args.layer, verbosity=args.verbosity)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
