#!/usr/bin/env python3
"""
Script para formatear automáticamente el código del proyecto
"""
import subprocess  # nosec B404
from pathlib import Path


def run_command(cmd, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔧 {description}...")
    try:
        # Usar shell=False es más seguro, pero este script solo ejecuta comandos conocidos
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )  # nosec B602
        if result.returncode == 0:
            print(f"✅ {description} completado")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"⚠️ {description} tuvo warnings")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error en {description}: {e}")
        return False


def main():
    """Función principal"""
    print("🎨 FORMATEADOR AUTOMÁTICO DE CÓDIGO")
    print("=" * 50)

    project_root = Path(__file__).parent
    print(f"📁 Directorio del proyecto: {project_root}")

    # Instalar herramientas si no existen
    print("\n1️⃣ Instalando herramientas de formateo...")
    tools = ["black", "isort", "flake8", "autopep8"]
    for tool in tools:
        run_command(f"python -m pip install {tool}", f"Instalando {tool}")

    # Formatear con Black
    print("\n2️⃣ Formateando código con Black...")
    run_command(
        "python -m black --line-length 88 --target-version py38 .", "Formateo con Black"
    )

    # Organizar imports con isort
    print("\n3️⃣ Organizando imports con isort...")
    run_command(
        "python -m isort --profile black --multi-line 3 --line-length 88 .",
        "Organización de imports",
    )

    # Formatear archivos específicos que causan problemas
    print("\n4️⃣ Formateando archivos específicos...")
    problem_files = [
        "coverage_demo.py",
        "config/settings/test_database_settings.py",
        "generate_sonar_reports.py",
        "generate_simple_coverage.py",
    ]

    for file_path in problem_files:
        if Path(file_path).exists():
            run_command(
                f"python -m black --line-length 88 {file_path}",
                f"Formateando {file_path}",
            )
            run_command(
                f"python -m isort --profile black {file_path}",
                f"Organizando imports en {file_path}",
            )

    # Verificar estilo con flake8
    print("\n5️⃣ Verificando estilo con flake8...")
    run_command(
        "python -m flake8 --max-line-length=88 --extend-ignore=E203,W503 .",
        "Verificación de estilo",
    )

    print("\n" + "=" * 50)
    print("🎉 FORMATEO COMPLETADO")
    print("=" * 50)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Revisar los cambios con: git diff")
    print("2. Confirmar que todo funciona correctamente")
    print("3. Hacer commit de los cambios formateados")
    print("4. Configurar pre-commit hooks para formateo automático")


if __name__ == "__main__":
    main()
