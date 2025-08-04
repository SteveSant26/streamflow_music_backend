#!/usr/bin/env python3
"""
🚀 STREAMFLOW MUSIC BACKEND - MASTER TEST RUNNER
=================================================
Ejecuta todos los tests de todos los módulos del proyecto
(Arquitectura Hexagonal - 6 Módulos Completos)
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, Tuple

# Configurar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(
    current_dir
)  # Subir un nivel desde test/ para llegar a la raíz


class Colors:
    """Códigos de color ANSI para terminal"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_banner():
    """Print test suite banner (Windows-compatible)."""
    print("🎵 STREAMFLOW MUSIC BACKEND - MASTER TEST SUITE 🎵")
    print("=" * 80)


def run_module_tests(module_name: str) -> Tuple[bool, float, Dict]:
    """Ejecuta los tests de un módulo específico"""
    test_runner_path = os.path.join(
        project_root, "test", module_name, "run_all_tests.py"
    )

    print(f"   🔍 Buscando runner en: {test_runner_path}")

    if not os.path.exists(test_runner_path):
        print(
            f"{Colors.WARNING}⚠️  Test runner no encontrado para {module_name}{Colors.ENDC}"
        )
        print(f"   📁 Path: {test_runner_path}")
        return False, 0.0, {}

    print(f"\n{Colors.OKBLUE}🔍 EJECUTANDO TESTS DE {module_name.upper()}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'=' * 60}{Colors.ENDC}")

    start_time = time.time()

    try:
        # Ejecutar el test runner del módulo
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        # Usar el Python del entorno virtual
        python_exe = r"C:/Users/Marcwos/Documents/Ing Software/5to Semestre/streamflow_music_backend/venv/Scripts/python.exe"

        result = subprocess.run(
            [python_exe, test_runner_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            cwd=project_root,
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Mostrar output
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(f"{Colors.WARNING}STDERR: {result.stderr}{Colors.ENDC}")

        success = result.returncode == 0

        # Parsear estadísticas del output (intentar extraer métricas)
        stats = parse_module_stats(result.stdout)

        if success:
            print(
                f"{Colors.OKGREEN}✅ {module_name.upper()} completado exitosamente ({execution_time:.2f}s){Colors.ENDC}"
            )
        else:
            print(
                f"{Colors.FAIL}❌ {module_name.upper()} falló (código: {result.returncode}){Colors.ENDC}"
            )

        return success, execution_time, stats

    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{Colors.FAIL}❌ Error ejecutando {module_name}: {e}{Colors.ENDC}")
        return False, execution_time, {}


def parse_module_stats(output: str) -> Dict:
    """Intenta parsear estadísticas del output del módulo"""
    stats = {
        "tests_passed": 0,
        "tests_failed": 0,
        "total_tests": 0,
        "success_rate": 0.0,
    }

    try:
        lines = output.split("\n")
        for line in lines:
            if "pasaron" in line and "fallaron" in line:
                # Formato: "📊 RESULTADOS: X pasaron, Y fallaron"
                parts = line.split(":")
                if len(parts) > 1:
                    results_part = parts[1]
                    if "pasaron" in results_part:
                        passed_part = results_part.split("pasaron")[0].strip()
                        stats["tests_passed"] = int(passed_part.split()[-1])
                    if "fallaron" in results_part:
                        failed_part = (
                            results_part.split("fallaron")[0]
                            .split("pasaron")[1]
                            .strip()
                        )
                        stats["tests_failed"] = int(
                            failed_part.replace(",", "").strip().split()[0]
                        )
            elif "Tests que pasaron:" in line:
                stats["tests_passed"] = int(line.split(":")[1].strip())
            elif "Tests que fallaron:" in line:
                stats["tests_failed"] = int(line.split(":")[1].strip())

        stats["total_tests"] = stats["tests_passed"] + stats["tests_failed"]
        if stats["total_tests"] > 0:
            stats["success_rate"] = (stats["tests_passed"] / stats["total_tests"]) * 100

    except Exception:
        # Si no se puede parsear, usar valores por defecto
        pass

    return stats


def print_final_summary(results: Dict[str, Tuple[bool, float, Dict]]):
    """Imprime el resumen final del proyecto"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}")
    print("🏆 RESUMEN FINAL - STREAMFLOW MUSIC BACKEND")
    print(f"{'=' * 80}{Colors.ENDC}")

    total_modules = len(results)
    successful_modules = sum(1 for success, _, _ in results.values() if success)
    failed_modules = total_modules - successful_modules
    total_execution_time = sum(exec_time for _, exec_time, _ in results.values())

    # Estadísticas por módulo
    total_tests_passed = 0
    total_tests_failed = 0
    total_tests = 0

    print(f"\n{Colors.OKBLUE}📊 RESULTADOS POR MÓDULO:{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-' * 80}{Colors.ENDC}")

    for module_name, (success, exec_time, stats) in results.items():
        status_color = Colors.OKGREEN if success else Colors.FAIL
        status_icon = "✅" if success else "❌"
        status_text = "PASÓ" if success else "FALLÓ"

        tests_info = ""
        if stats.get("total_tests", 0) > 0:
            tests_info = f" ({stats['tests_passed']}/{stats['total_tests']} tests - {stats['success_rate']:.1f}%)"

        print(
            f"   {status_color}{status_icon} {module_name.ljust(15)} {status_text.ljust(8)} ({exec_time:.2f}s){tests_info}{Colors.ENDC}"
        )

        total_tests_passed += stats.get("tests_passed", 0)
        total_tests_failed += stats.get("tests_failed", 0)
        total_tests += stats.get("total_tests", 0)

    # Resumen general
    print(f"\n{Colors.OKBLUE}📈 ESTADÍSTICAS GENERALES:{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-' * 80}{Colors.ENDC}")
    print(f"   🏗️  Módulos totales: {total_modules}")
    print(f"   ✅ Módulos exitosos: {successful_modules}")
    print(f"   ❌ Módulos fallidos: {failed_modules}")
    print(f"   📊 Porcentaje de éxito: {(successful_modules/total_modules)*100:.1f}%")
    print(f"   ⏱️  Tiempo total: {total_execution_time:.2f}s")

    if total_tests > 0:
        print(f"   🧪 Tests ejecutados: {total_tests}")
        print(f"   ✅ Tests pasados: {total_tests_passed}")
        print(f"   ❌ Tests fallidos: {total_tests_failed}")
        print(f"   📊 Éxito en tests: {(total_tests_passed/total_tests)*100:.1f}%")

    # Mensaje final
    print(f"\n{Colors.HEADER}{'-' * 80}{Colors.ENDC}")

    if failed_modules == 0:
        print(
            f"{Colors.OKGREEN}{Colors.BOLD}🎉 ¡TODOS LOS MÓDULOS PASARON EXITOSAMENTE!{Colors.ENDC}"
        )
        print(
            f"{Colors.OKGREEN}✨ StreamFlow Music Backend está completamente probado y funcional{Colors.ENDC}"
        )
        print(
            f"{Colors.OKGREEN}🚀 El proyecto está listo para producción desde la perspectiva de testing{Colors.ENDC}"
        )

        # Lista de módulos completados
        print(
            f"\n{Colors.OKCYAN}📋 MÓDULOS COMPLETADOS CON TESTING EXHAUSTIVO:{Colors.ENDC}"
        )
        for module_name in results.keys():
            print(f"   ✅ {module_name.upper()} - Arquitectura Hexagonal Completa")

    else:
        print(
            f"{Colors.WARNING}⚠️  {failed_modules} módulo(s) tuvieron problemas{Colors.ENDC}"
        )
        print(f"{Colors.WARNING}🔧 Revisa los errores mostrados arriba{Colors.ENDC}")

    print(
        f"\n{Colors.OKCYAN}📅 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}"
    )
    print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}")


def main():
    """Función principal"""
    print_banner()

    # Lista de módulos a probar (en orden lógico)
    modules = [
        "user_profile",  # Base - Usuarios
        "songs",  # Core - Canciones
        "artists",  # Core - Artistas
        "albums",  # Core - Álbumes
        "genres",  # Core - Géneros
        "music_search",  # Integración - Búsqueda
    ]

    results = {}
    total_start_time = time.time()

    print(
        f"\n{Colors.OKBLUE}🚀 Iniciando ejecución de {len(modules)} módulos...{Colors.ENDC}"
    )

    for i, module in enumerate(modules, 1):
        print(
            f"\n{Colors.OKCYAN}[{i}/{len(modules)}] Procesando {module}...{Colors.ENDC}"
        )

        success, exec_time, stats = run_module_tests(module)
        results[module] = (success, exec_time, stats)

        # Pausa corta entre módulos para clarity
        time.sleep(0.5)

    total_end_time = time.time()
    total_time = total_end_time - total_start_time

    # Agregar tiempo total a los resultados
    print(
        f"\n{Colors.OKCYAN}⏱️  Tiempo total de ejecución: {total_time:.2f}s{Colors.ENDC}"
    )

    # Mostrar resumen final
    print_final_summary(results)

    # Código de salida
    failed_count = sum(1 for success, _, _ in results.values() if not success)
    return failed_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
