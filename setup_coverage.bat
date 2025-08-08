@echo off
REM Script para Windows - Instalar dependencias y ejecutar tests con coverage

echo 🔧 Instalando dependencias de testing y coverage...

REM Instalar pytest y pytest-cov
pip install pytest pytest-cov coverage

echo.
echo 📦 Verificando instalación:
pip show pytest pytest-cov coverage

echo.
echo 🧪 Ejecutando tests con coverage...

REM Crear directorio de reportes si no existe
if not exist "test-reports" mkdir test-reports

REM Ejecutar tests con coverage completo
python -m pytest ^
  --cov=src ^
  --cov-report=xml:coverage.xml ^
  --cov-report=xml:test-reports/coverage.xml ^
  --cov-report=html:htmlcov ^
  --cov-report=term-missing ^
  --junitxml=test-reports/pytest-results.xml ^
  -v ^
  test/

echo.
echo 📊 Verificando archivos generados:

REM Verificar que se generaron los archivos
if exist "coverage.xml" (
    for %%A in (coverage.xml) do echo ✅ coverage.xml generado ^(%%~zA bytes^)
) else (
    echo ❌ coverage.xml no encontrado
)

if exist "test-reports\coverage.xml" (
    for %%A in (test-reports\coverage.xml) do echo ✅ test-reports/coverage.xml generado ^(%%~zA bytes^)
) else (
    echo ❌ test-reports/coverage.xml no encontrado
)

if exist "test-reports\pytest-results.xml" (
    for %%A in (test-reports\pytest-results.xml) do echo ✅ test-reports/pytest-results.xml generado ^(%%~zA bytes^)
) else (
    echo ❌ test-reports/pytest-results.xml no encontrado
)

echo.
echo 🎯 Para SonarQube/SonarCloud:
echo    - Asegúrate de que coverage.xml esté en la raíz del proyecto
echo    - Configura sonar.python.coverage.reportPaths=coverage.xml
echo    - El archivo debe tener rutas relativas desde la raíz del proyecto

echo.
echo 📋 Archivos XML encontrados:
dir *.xml 2>nul
dir test-reports\*.xml 2>nul

pause
