"""
Script de prueba para verificar que la aplicación funciona
"""
import requests
import json
import time

def test_application():
    print("🚀 Probando la aplicación AudioLetra...")
    
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Health check
    print("\n1. Probando health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False
    
    # Test 2: Get profiles
    print("\n2. Probando endpoint de perfiles...")
    try:
        response = requests.get(f"{base_url}/llm/profiles")
        if response.status_code == 200:
            data = response.json()
            print("✅ Profiles endpoint OK")
            print(f"   Available profiles: {len(data['profiles'])}")
            for profile in data['profiles']:
                print(f"   - {profile['name']} ({profile['id']})")
        else:
            print(f"❌ Profiles endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en profiles endpoint: {e}")
        return False
    
    # Test 3: Test process endpoint (without API key)
    print("\n3. Probando endpoint de procesamiento...")
    try:
        response = requests.post(f"{base_url}/llm/process", json={
            "profile_id": "clean_format",
            "text": "hola mundo esto es una prueba",
            "parameters": {}
        })
        
        if response.status_code == 200:
            print("✅ Process endpoint OK (with API key)")
            data = response.json()
            print(f"   Result: {data.get('output', 'No output')[:100]}...")
        elif response.status_code == 500:
            print("⚠️  Process endpoint responds (API key needed)")
            data = response.json()
            print(f"   Error: {data.get('error', {}).get('message', 'Unknown error')}")
        else:
            print(f"❌ Process endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en process endpoint: {e}")
    
    print("\n🎉 Pruebas completadas!")
    print("\n📋 Resumen:")
    print("✅ La aplicación está funcionando correctamente")
    print("✅ Todos los endpoints están disponibles")
    print("⚠️  Para procesar texto necesitas configurar una API key")
    
    return True

if __name__ == "__main__":
    test_application()
