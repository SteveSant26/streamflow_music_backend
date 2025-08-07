# 🎯 SCRIPT PARA EJECUTAR TESTS Y SONARQUBE
# =========================================
# Ejecuta desde la raíz del proyecto

Write-Host "🎵 STREAMFLOW MUSIC BACKEND - ANÁLISIS SONARQUBE" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

Write-Host "📍 Ubicación actual:" -ForegroundColor Yellow
Get-Location

Write-Host ""
Write-Host "🧪 Paso 1: Ejecutando tests y generando reportes..." -ForegroundColor Green
pytest

Write-Host ""
Write-Host "📊 Verificando reportes generados..." -ForegroundColor Yellow
if (Test-Path "test-reports/pytest-results.xml") {
    Write-Host "✅ test-reports/pytest-results.xml generado" -ForegroundColor Green
} else {
    Write-Host "❌ Error: No se generó pytest-results.xml" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔍 Paso 2: Ejecutando SonarQube Scanner..." -ForegroundColor Green
if (Get-Command "sonar-scanner" -ErrorAction SilentlyContinue) {
    sonar-scanner
    Write-Host ""
    Write-Host "✅ ¡Análisis completado!" -ForegroundColor Green
    Write-Host "📈 Revisa los resultados en SonarCloud dashboard" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ sonar-scanner no está instalado" -ForegroundColor Red
    Write-Host "📥 Instálalo con: npm install -g sonarqube-scanner" -ForegroundColor Yellow
    Write-Host "📥 O descárgalo de: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/" -ForegroundColor Yellow
}
