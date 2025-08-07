#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de letras
Prueba las APIs de letras del backend
"""

import requests
import json
import sys
import time

# Configuración
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/songs"

def test_song_lyrics(song_id):
    """Prueba obtener letras de una canción"""
    print(f"\n=== Probando letras para canción ID: {song_id} ===")
    
    # 1. Obtener letras (GET)
    print("\n1. Obteniendo letras...")
    try:
        response = requests.get(f"{API_URL}/{song_id}/lyrics/", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Título: {data.get('title', 'N/A')}")
            print(f"Artista: {data.get('artist', 'N/A')}")
            print(f"Tiene letras: {data.get('has_lyrics', False)}")
            
            lyrics = data.get('lyrics')
            if lyrics:
                print(f"Letras (primeros 200 chars): {lyrics[:200]}...")
            else:
                print("Sin letras disponibles")
            
            source = data.get('source')
            if source:
                print(f"Fuente: {source}")
                
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return False
    
    # 2. Forzar actualización de letras (POST)
    print("\n2. Forzando actualización de letras...")
    try:
        response = requests.post(f"{API_URL}/{song_id}/lyrics/update/", 
                               json={"force": True}, 
                               timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Actualizado: {data.get('updated', False)}")
            print(f"Mensaje: {data.get('message', 'N/A')}")
            
            lyrics = data.get('lyrics')
            if lyrics:
                print(f"Nuevas letras (primeros 200 chars): {lyrics[:200]}...")
            else:
                print("Sin letras obtenidas")
                
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return False
    
    return True

def test_multiple_songs():
    """Prueba con múltiples canciones"""
    # IDs de canciones de prueba - estos deberían existir en tu DB
    test_song_ids = ["1", "2", "3"]
    
    for song_id in test_song_ids:
        success = test_song_lyrics(song_id)
        if not success:
            print(f"❌ Falló la prueba para canción {song_id}")
        else:
            print(f"✅ Prueba exitosa para canción {song_id}")
        
        time.sleep(2)  # Pausa entre pruebas para evitar rate limiting

def test_health():
    """Prueba que el servidor esté funcionando"""
    print("=== Verificando estado del servidor ===")
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=10)
        if response.status_code == 200:
            print("✅ Servidor funcionando")
            return True
        else:
            print(f"❌ Servidor responde con error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return False

def main():
    """Función principal"""
    print("🎵 Prueba de Funcionalidad de Letras 🎵")
    print("=" * 50)
    
    # Verificar servidor
    if not test_health():
        print("\n❌ El servidor no está disponible. Asegúrate de que Django esté ejecutándose.")
        return
    
    # Obtener ID de canción del usuario
    if len(sys.argv) > 1:
        song_id = sys.argv[1]
        test_song_lyrics(song_id)
    else:
        print("\nProbando con canciones por defecto...")
        test_multiple_songs()
    
    print("\n🏁 Pruebas completadas")

if __name__ == "__main__":
    main()
