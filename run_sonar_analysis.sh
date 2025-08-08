#!/bin/bash
# 🎯 SCRIPT PARA EJECUTAR TESTS Y SONARQUBE
# =========================================
# Ejecuta desde la raíz del proyecto: c:\Users\Marcwos\Documents\Ing Software\5to Semestre\streamflow_music_backend

echo "🎵 STREAMFLOW MUSIC BACKEND - ANÁLISIS SONARQUBE"
echo "================================================="

echo "📍 Ubicación actual:"
pwd

echo ""
echo "🧪 Paso 1: Ejecutando tests y generando reportes..."
pytest

echo ""
echo "📊 Verificando reportes generados..."
if [ -f "test-reports/pytest-results.xml" ]; then
    echo "✅ test-reports/pytest-results.xml generado"
else
    echo "❌ Error: No se generó pytest-results.xml"
    exit 1
fi

echo ""
echo "🔍 Paso 2: Ejecutando SonarQube Scanner..."
sonar-scanner

echo ""
echo "✅ ¡Análisis completado!"
echo "📈 Revisa los resultados en SonarCloud dashboard"
