#!/usr/bin/env python
"""
Script para ejecutar tests funcionales en pre-commit.
Ejecuta solo user_profile y albums que están al 100% funcionales.
"""
import os
import subprocess
import sys


def main():
    """Ejecuta tests funcionales para pre-commit."""
    print("Ejecutando tests funcionales...")

    # Cambiar al directorio test
    original_dir = os.getcwd()
    test_dir = os.path.join(original_dir, "test")
    os.chdir(test_dir)

    # Ejecutar tests de user_profile
    print("Ejecutando tests de user_profile...")
    result1 = subprocess.run(
        [sys.executable, "user_profile/run_all_tests.py"],
        capture_output=True,
        text=True,
    )

    # Ejecutar tests de albums
    print("Ejecutando tests de albums...")
    result2 = subprocess.run(
        [sys.executable, "albums/run_all_tests.py"], capture_output=True, text=True
    )

    # Volver al directorio original
    os.chdir(original_dir)

    # Mostrar resultados
    status1 = "PASSED" if result1.returncode == 0 else "FAILED"
    status2 = "PASSED" if result2.returncode == 0 else "FAILED"

    print(f"Tests user_profile: {status1}")
    print(f"Tests albums: {status2}")

    # Debug info
    if result1.returncode != 0:
        print("Error en user_profile:")
        print("STDOUT:", result1.stdout[-500:])
        print("STDERR:", result1.stderr[-500:])

    if result2.returncode != 0:
        print("Error en albums:")
        print("STDOUT:", result2.stdout[-500:])
        print("STDERR:", result2.stderr[-500:])

    # Salir con código de error si algún test falló
    success = result1.returncode == 0 and result2.returncode == 0

    if success:
        print("Todos los tests funcionales pasaron!")
    else:
        print("Algunos tests fallaron")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
