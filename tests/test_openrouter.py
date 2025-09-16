#!/usr/bin/env python3
"""
Script de prueba para OpenRouter LLM.
"""

import sys
from pathlib import Path

# Agregar directorios al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "config"))
sys.path.append(str(project_root / "utils"))


def test_openrouter():
    """Prueba la conexión con OpenRouter"""
    print("🤖 Probando conexión con OpenRouter...")
    
    try:
        from utils.text_processor import TextProcessor
        
        # Solicitar API key si no está configurada
        api_key = input("🔑 Ingresa tu API key de OpenRouter (o presiona Enter para usar la del .env): ").strip()
        
        if not api_key:
            from config.config import config
            api_key = config.openai_api_key
        
        if not api_key:
            print("❌ No se proporcionó API key")
            return False
        
        # Crear procesador de texto
        processor = TextProcessor(
            api_key=api_key,
            model="openai/gpt-4o-mini",
            provider="openrouter"
        )
        
        if not processor.is_available():
            print("❌ No se pudo inicializar OpenRouter")
            return False
        
        # Probar con texto de ejemplo
        test_text = "hola como estas espero que bien gracias por preguntar"
        print(f"\n📝 Texto de prueba: {test_text}")
        
        print("🔄 Procesando con OpenRouter...")
        improved_text = processor.improve_text(test_text, "cleanup")
        
        if improved_text:
            print(f"✅ Resultado: {improved_text}")
            return True
        else:
            print("❌ No se pudo procesar el texto")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def show_openrouter_models():
    """Muestra modelos populares de OpenRouter"""
    print("\n📋 Modelos populares de OpenRouter:")
    print("=" * 50)
    
    models = {
        "OpenAI": [
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "openai/gpt-3.5-turbo"
        ],
        "Anthropic": [
            "anthropic/claude-3-haiku",
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-opus"
        ],
        "Meta": [
            "meta-llama/llama-3.1-8b-instruct",
            "meta-llama/llama-3.1-70b-instruct"
        ],
        "Google": [
            "google/gemini-pro",
            "google/gemini-flash-1.5"
        ],
        "Otros": [
            "mistralai/mistral-7b-instruct",
            "microsoft/phi-3-medium-128k-instruct"
        ]
    }
    
    for provider, model_list in models.items():
        print(f"\n{provider}:")
        for model in model_list:
            print(f"  - {model}")


def main():
    """Función principal"""
    print("🎙️  PRUEBA DE OPENROUTER - DICTADO INTELIGENTE")
    print("=" * 60)
    
    print("\n💡 Instrucciones:")
    print("1. Ve a https://openrouter.ai/keys")
    print("2. Crea una cuenta y obtén tu API key")
    print("3. Configura tu API key en el archivo .env")
    print("4. Ejecuta esta prueba")
    
    show_openrouter_models()
    
    print("\n" + "=" * 60)
    
    if test_openrouter():
        print("\n🎉 ¡OpenRouter funciona correctamente!")
        print("\n💡 Para usar en el dictado:")
        print("   python whisper_dictado.py --llm-enable")
    else:
        print("\n⚠️  Hay problemas con OpenRouter")
        print("💡 Verifica tu API key y conexión a internet")


if __name__ == "__main__":
    main()
