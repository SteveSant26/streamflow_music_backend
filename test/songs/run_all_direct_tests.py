#!/usr/bin/env python
"""
Ejecutar todos los tests directos de Songs
"""
import subprocess
import sys
from pathlib import Path


def run_test_file(test_file):
    """Ejecutar un archivo de test específico"""
    print(f"\n{'='*60}")
    print(f"🚀 Ejecutando: {test_file}")
    print(f"{'='*60}")

    result = subprocess.run(
        [sys.executable, test_file],
        capture_output=False,
        cwd=Path(__file__).parent.parent.parent,
    )

    if result.returncode == 0:
        print(f"✅ {test_file} - PASSED")
        return True
    else:
        print(f"❌ {test_file} - FAILED")
        return False


def main():
    """Ejecutar todos los tests directos"""
    print("🎵 STREAMFLOW MUSIC - Tests Directos de Songs")
    print("=" * 60)

    # Lista de archivos de test
    test_files = [
        "test/songs/test_direct.py",  # Entities
        "test/songs/test_use_cases_direct.py",  # Use Cases
        "test/songs/test_models_direct.py",  # Models
        "test/songs/test_serializers_direct.py",  # Serializers
    ]

    passed = 0
    failed = 0

    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"🎯 RESUMEN DE TESTS DE SONGS")
    print(f"{'='*60}")
    print(f"✅ Pasaron: {passed}")
    print(f"❌ Fallaron: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print(f"\n🎉 ¡TODOS LOS TESTS DE SONGS PASARON!")
        print(f"✨ La app Songs está lista para producción")
        return True
    else:
        print(f"\n⚠️  Algunos tests fallaron")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
