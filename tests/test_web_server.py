#!/usr/bin/env python3
"""
Script de prueba simple para el servidor web de AudioLetra.
"""

import requests
import time
import json

def test_server():
    """Prueba el servidor web"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Probando servidor web...")
    
    try:
        # Probar estado
        print("1. Probando /api/status...")
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Estado: Whisper={data['whisper_available']}, LLM={data['llm_available']}")
        else:
            print(f"❌ Error en status: {response.status_code}")
            return False
        
        # Probar inicio de grabación
        print("2. Probando inicio de grabación...")
        response = requests.post(f"{base_url}/api/start_recording", 
                               json={"use_llm": False})
        if response.status_code == 200:
            print("✅ Grabación iniciada")
        else:
            print(f"❌ Error al iniciar: {response.status_code}")
            return False
        
        # Esperar un poco
        print("3. Esperando 3 segundos...")
        time.sleep(3)
        
        # Probar detener grabación
        print("4. Probando detener grabación...")
        response = requests.post(f"{base_url}/api/stop_recording")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print("✅ Grabación detenida correctamente")
                if 'result' in data and 'success' in data['result']:
                    print(f"📝 Transcripción: {data['result'].get('text', 'Sin texto')}")
            else:
                print(f"⚠️  Respuesta: {data}")
        else:
            print(f"❌ Error al detener: {response.status_code}")
            return False
        
        # Probar dictados
        print("5. Probando obtener dictados...")
        response = requests.get(f"{base_url}/api/dictations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dictados obtenidos: {len(data['dictations'])}")
        else:
            print(f"❌ Error en dictados: {response.status_code}")
            return False
        
        print("\n🎉 ¡Todas las pruebas pasaron!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose:")
        print("   python start_web.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎙️  PRUEBA DEL SERVIDOR WEB - AUDIOLETRA")
    print("=" * 40)
    
    # Esperar un poco para que el servidor se inicie
    print("⏳ Esperando que el servidor se inicie...")
    time.sleep(5)
    
    if test_server():
        print("\n✅ El servidor web funciona correctamente")
        print("🌐 Abre tu navegador en: http://127.0.0.1:5000")
    else:
        print("\n❌ Hay problemas con el servidor web")
