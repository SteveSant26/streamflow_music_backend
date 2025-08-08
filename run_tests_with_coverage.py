#!/usr/bin/env python3
"""
Script para ejecutar tests con coverage y generar reportes para SonarQube/SonarCloud.
Este script asegura que los archivos de coverage se generen correctamente.
"""
import os
import subprocess  # nosec B404
import sys
from pathlib import Path


def main():
    """Ejecuta tests con coverage y genera reportes XML."""

    # Configuración de directorios
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    test_dir = project_root / "test"
    test_reports_dir = project_root / "test-reports"

    print("🚀 Iniciando ejecución de tests con coverage...")
    print(f"📁 Directorio del proyecto: {project_root}")
    print(f"📂 Directorio de código fuente: {src_dir}")
    print(f"🧪 Directorio de tests: {test_dir}")

    # Verificar que existen los directorios necesarios
    if not src_dir.exists():
        print(f"❌ Error: No se encontró el directorio src/ en {src_dir}")
        sys.exit(1)

    if not test_dir.exists():
        print(f"❌ Error: No se encontró el directorio test/ en {test_dir}")
        sys.exit(1)

    # Crear directorio de reportes si no existe
    test_reports_dir.mkdir(exist_ok=True)
    print(f"📊 Directorio de reportes: {test_reports_dir}")

    # Cambiar al directorio del proyecto
    os.chdir(project_root)

    # Comando para ejecutar pytest con coverage
    cmd = [
        "python",
        "-m",
        "pytest",
        # Configuración de coverage
        "--cov=src",  # Medir coverage en directorio src/
        "--cov-report=xml:coverage.xml",  # Generar XML en raíz
        "--cov-report=xml:test-reports/coverage.xml",  # Generar XML en test-reports/
        "--cov-report=html:htmlcov",  # Generar reporte HTML
        "--cov-report=term-missing",  # Mostrar líneas faltantes en terminal
        # Configuración de tests
        "--junitxml=test-reports/pytest-results.xml",  # Generar reporte JUnit XML
        "-v",  # Verbose output
        # Directorio de tests
        "test/",
    ]

    print("🏃‍♂️ Ejecutando comando:")
    print(f"   {' '.join(cmd)}")
    print()

    try:
        # Ejecutar pytest con coverage
        result = subprocess.run(cmd, check=False, capture_output=False)  # nosec B603

        # Verificar que se generaron los archivos esperados
        files_to_check = [
            "coverage.xml",
            "test-reports/coverage.xml",
            "test-reports/pytest-results.xml",
        ]

        print("\n📋 Verificando archivos generados:")
        all_files_exist = True

        for file_path in files_to_check:
            full_path = project_root / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                print(f"   ✅ {file_path} ({size:,} bytes)")
            else:
                print(f"   ❌ {file_path} (no encontrado)")
                all_files_exist = False

        if all_files_exist:
            print("\n🎉 ¡Todos los archivos de coverage se generaron correctamente!")
            print("\n📌 Para SonarQube/SonarCloud:")
            print("   - coverage.xml: Reporte principal de coverage")
            print("   - test-reports/pytest-results.xml: Reporte de tests unitarios")
            print("   - htmlcov/: Reporte HTML para revisión local")
        else:
            print("\n⚠️  Algunos archivos no se generaron correctamente.")

        return result.returncode

    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando pytest: {e}")
        return e.returncode
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
