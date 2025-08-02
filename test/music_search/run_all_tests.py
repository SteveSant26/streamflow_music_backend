#!/usr/bin/env python3
"""
Script maestro para ejecutar todos los tests de Music Search (Arquitectura Hexagonal)
"""

import os
import subprocess
import sys
from datetime import datetime

# Configurar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..")


def run_test_file(test_file: str) -> tuple[bool, float]:
    """Ejecutar un archivo de test específico y medir tiempo"""
    test_path = os.path.join(current_dir, test_file)

    if not os.path.exists(test_path):
        print(f"❌ Archivo de test no encontrado: {test_file}")
        return False, 0.0

    print(f"\n🧪 Ejecutando {test_file}...")
    print("=" * 60)

    start_time = datetime.now()

    try:
        # Cambiar al directorio del proyecto para ejecutar
        original_cwd = os.getcwd()
        os.chdir(project_root)

        # Ejecutar el test usando Python con codificación UTF-8
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        result = subprocess.run(
            [sys.executable, os.path.join("test", "music_search", test_file)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )

        # Restaurar directorio
        os.chdir(original_cwd)

        # Calcular tiempo de ejecución
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Mostrar output
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr)

        success = result.returncode == 0

        if success:
            print(f"✅ {test_file} completado exitosamente ({execution_time:.2f}s)")
        else:
            print(f"❌ {test_file} falló (código: {result.returncode})")

        return success, execution_time

    except Exception as e:
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        print(f"❌ Error ejecutando {test_file}: {e}")
        return False, execution_time


def main():
    """Función principal"""
    print("🔍 SUITE DE TESTS MUSIC SEARCH - ARQUITECTURA HEXAGONAL")
    print("=" * 65)
    print(f"📅 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Lista de tests a ejecutar (arquitectura hexagonal)
    test_files = [
        "domain/test_entities.py",  # Tests de entidades del dominio
        "use_cases/test_search_use_cases.py",  # Tests de casos de uso
        "api/test_serializers.py",  # Tests de serializadores API
        "infrastructure/test_search_infrastructure.py",  # Tests de infraestructura
    ]

    results = {}
    execution_times = {}
    total_tests = len(test_files)
    total_start_time = datetime.now()

    for test_file in test_files:
        success, exec_time = run_test_file(test_file)
        results[test_file] = success
        execution_times[test_file] = exec_time

    total_end_time = datetime.now()
    total_execution_time = (total_end_time - total_start_time).total_seconds()

    # Resumen final
    print("\n" + "=" * 65)
    print("📊 RESUMEN FINAL DE TESTS - MUSIC SEARCH")
    print("=" * 65)

    passed = sum(1 for success in results.values() if success)
    failed = total_tests - passed

    for test_file, success in results.items():
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        exec_time = execution_times[test_file]
        print(f"   {test_file:<35} {status} ({exec_time:.2f}s)")

    print("\n" + "-" * 65)
    print(f"📈 ESTADÍSTICAS:")
    print(f"   • Total de archivos de test: {total_tests}")
    print(f"   • Tests que pasaron: {passed}")
    print(f"   • Tests que fallaron: {failed}")
    print(f"   • Porcentaje de éxito: {(passed/total_tests)*100:.1f}%")
    print(f"   • Tiempo total: {total_execution_time:.2f}s")

    if failed == 0:
        print("\n🎉 ¡TODOS LOS TESTS DE MUSIC SEARCH PASARON!")
        print("✨ El módulo Music Search está completamente probado y funcional")
    else:
        print(f"\n⚠️  {failed} archivos de test fallaron")
        print("🔧 Revisa los errores mostrados arriba")

    print(f"\n📅 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
