#!/bin/bash
# Script para instalar dependencias y ejecutar tests con coverage

echo "🔧 Instalando dependencias de testing y coverage..."

# Instalar pytest y pytest-cov
pip install pytest pytest-cov coverage

echo "📦 Dependencias instaladas:"
pip show pytest pytest-cov coverage

echo ""
echo "🧪 Ejecutando tests con coverage..."

# Ejecutar tests con coverage completo
pytest \
  --cov=src \
  --cov-report=xml:coverage.xml \
  --cov-report=xml:test-reports/coverage.xml \
  --cov-report=html:htmlcov \
  --cov-report=term-missing \
  --junitxml=test-reports/pytest-results.xml \
  -v \
  test/

echo ""
echo "📊 Verificando archivos generados:"

# Verificar que se generaron los archivos
if [ -f "coverage.xml" ]; then
    echo "✅ coverage.xml generado ($(wc -c < coverage.xml) bytes)"
else
    echo "❌ coverage.xml no encontrado"
fi

if [ -f "test-reports/coverage.xml" ]; then
    echo "✅ test-reports/coverage.xml generado ($(wc -c < test-reports/coverage.xml) bytes)"
else
    echo "❌ test-reports/coverage.xml no encontrado"
fi

if [ -f "test-reports/pytest-results.xml" ]; then
    echo "✅ test-reports/pytest-results.xml generado ($(wc -c < test-reports/pytest-results.xml) bytes)"
else
    echo "❌ test-reports/pytest-results.xml no encontrado"
fi

echo ""
echo "🎯 Para SonarQube/SonarCloud:"
echo "   - Asegúrate de que coverage.xml esté en la raíz del proyecto"
echo "   - Configura sonar.python.coverage.reportPaths=coverage.xml"
echo "   - El archivo debe tener rutas relativas desde la raíz del proyecto"

echo ""
echo "📋 Contenido del directorio actual:"
ls -la *.xml test-reports/ 2>/dev/null || echo "No se encontraron archivos XML"
