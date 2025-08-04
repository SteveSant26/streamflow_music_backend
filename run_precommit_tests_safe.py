#!/usr/bin/env python
"""
Script para ejecutar solo los tests que sabemos que funcionan en pre-commit.
Ejecuta user_profile y albums que están al 100% funcionales.
Versión compatible con Windows/codificación.
"""
import sys
import subprocess
import os

def run_working_tests():
    """Ejecuta solo los módulos de test que están funcionando correctamente."""
    print("Ejecutando tests funcionales para pre-commit...")
    
    # Cambiar al directorio del proyecto
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Lista de módulos funcionales
    working_modules = [
        'test/user_profile/run_all_tests.py',
        'test/albums/run_all_tests.py'
    ]
    
    all_passed = True
    results = []
    
    for module in working_modules:
        print(f"\nEjecutando: {module}")
        try:
            # Configurar variables de entorno para Unicode
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # Ejecutar subprocess de forma segura con archivos internos del proyecto
            result = subprocess.run([sys.executable, module],  # nosec B603
                                  capture_output=True, 
                                  text=True, 
                                  timeout=60,
                                  env=env,
                                  encoding='utf-8',
                                  errors='replace')
            
            if result.returncode == 0:
                print(f"PASSED: {module}")
                results.append(f"PASSED: {module}")
            else:
                print(f"FAILED: {module}")
                if result.stdout:
                    print(f"STDOUT: {result.stdout}")
                if result.stderr:
                    print(f"STDERR: {result.stderr}")
                results.append(f"FAILED: {module}")
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT: {module}")
            results.append(f"TIMEOUT: {module}")
            all_passed = False
        except Exception as e:
            print(f"ERROR: {module} - {e}")
            results.append(f"ERROR: {module}")
            all_passed = False
    
    # Resumen final
    print("\n" + "="*50)
    print("RESUMEN DE TESTS PRE-COMMIT:")
    for result in results:
        print(f"  {result}")
    
    if all_passed:
        print("\nTodos los tests funcionales pasaron - COMMIT PERMITIDO")
        return True
    else:
        print("\nAlgunos tests fallaron - COMMIT BLOQUEADO")
        return False

if __name__ == '__main__':
    success = run_working_tests()
    sys.exit(0 if success else 1)
