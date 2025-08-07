#!/usr/bin/env python3
"""
Script para probar el comando de Django de actualización de letras
"""

import os
import sys
import subprocess

def run_django_command(command_args):
    """Ejecuta un comando de Django"""
    print(f"Ejecutando: python manage.py {' '.join(command_args)}")
    try:
        result = subprocess.run(
            ["python", "manage.py"] + command_args,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Comando excedió el tiempo límite")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def test_lyrics_commands():
    """Prueba los comandos de letras"""
    print("🎵 Prueba de Comandos de Django para Letras 🎵")
    print("=" * 60)
    
    # Cambiar al directorio del backend
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    print(f"Directorio de trabajo: {backend_dir}")
    
    # 1. Probar ayuda del comando
    print("\n1. Probando ayuda del comando...")
    success = run_django_command(["update_lyrics", "--help"])
    if not success:
        print("❌ Error obteniendo ayuda del comando")
        return
    
    # 2. Probar actualización con límite pequeño (dry-run simulado)
    print("\n2. Probando actualización con límite pequeño...")
    success = run_django_command(["update_lyrics", "--limit", "3", "--verbose"])
    if success:
        print("✅ Comando ejecutado correctamente")
    else:
        print("❌ Error en el comando")
    
    # 3. Probar estadísticas de letras
    print("\n3. Probando estadísticas de letras...")
    success = run_django_command(["update_lyrics", "--stats-only"])
    if success:
        print("✅ Estadísticas obtenidas correctamente")
    else:
        print("❌ Error obteniendo estadísticas")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "commands":
        test_lyrics_commands()
    else:
        print("Uso:")
        print("  python test_lyrics_commands.py commands  # Probar comandos de Django")

if __name__ == "__main__":
    main()
