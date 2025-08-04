#!/usr/bin/env python3
"""
🚀 SCRIPT PARA HACER COMMITS CON PRE-COMMIT
==========================================
Ayuda a hacer commits siguiendo las mejores prácticas
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, check=True):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=check
        )
        if result.returncode == 0:
            print(f"✅ {description} completado")
            if result.stdout and result.stdout.strip():
                print(f"   📄 Output: {result.stdout.strip()}")
        else:
            print(f"⚠️ {description} tuvo issues")
            if result.stderr and result.stderr.strip():
                print(f"   ❌ Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error en {description}: {e}")
        return False


def check_git_status():
    """Verificar el estado de git"""
    print("\n📋 VERIFICANDO ESTADO DE GIT:")
    run_command(
        "git status --porcelain", "Verificando archivos modificados", check=False
    )
    return True


def run_pre_commit():
    """Ejecutar pre-commit en archivos staged"""
    print("\n🧪 EJECUTANDO PRE-COMMIT:")
    success = run_command(
        "pre-commit run", "Pre-commit en archivos staged", check=False
    )
    if not success:
        print(
            "\n⚠️ Pre-commit encontró problemas. Los archivos han sido corregidos automáticamente."
        )
        print("💡 Revisa los cambios y vuelve a hacer git add si estás de acuerdo.")
        return False
    return True


def main():
    """Función principal"""
    print("🚀 ASISTENTE PARA COMMITS CON PRE-COMMIT")
    print("=" * 50)

    # Verificar que estamos en un repo git
    if not Path(".git").exists():
        print("❌ No estás en un repositorio git")
        return False

    # Verificar estado de git
    check_git_status()

    # Preguntar si quiere stagear archivos
    print("\n📦 PREPARANDO ARCHIVOS PARA COMMIT:")
    stage_all = input(
        "¿Quieres stagear todos los archivos modificados? (y/N): "
    ).lower()

    if stage_all in ["y", "yes", "sí", "s"]:
        run_command("git add .", "Stageando todos los archivos")
    else:
        print("💡 Usa 'git add <archivo>' para stagear archivos específicos")

    # Ejecutar pre-commit
    if not run_pre_commit():
        print("\n🔄 SIGUIENTES PASOS:")
        print("1. Revisa los cambios hechos por pre-commit")
        print("2. Si estás de acuerdo, ejecuta: git add .")
        print("3. Vuelve a ejecutar este script")
        return False

    # Si llegamos aquí, pre-commit pasó
    print("\n✅ PRE-COMMIT PASÓ EXITOSAMENTE")

    # Preguntar por el mensaje de commit
    print("\n💬 CREANDO COMMIT:")
    commit_message = input("Ingresa el mensaje de commit: ").strip()

    if not commit_message:
        print("❌ Mensaje de commit vacío. Cancelando...")
        return False

    # Hacer el commit
    commit_cmd = f'git commit -m "{commit_message}"'
    if run_command(commit_cmd, "Creando commit"):
        print("\n🎉 ¡COMMIT EXITOSO!")
        print("\n🚀 PRÓXIMOS PASOS:")
        print("- git push origin <branch>  # Para subir cambios")
        print("- git log --oneline -5      # Para ver últimos commits")
        return True
    else:
        print("\n❌ Error al crear commit")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
