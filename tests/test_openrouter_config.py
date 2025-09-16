#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de OpenRouter.
"""

import sys
from pathlib import Path

# Agregar directorios al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "config"))
sys.path.append(str(project_root / "utils"))

from config.config import config
from utils.text_processor import TextProcessor


def test_openrouter():
    """Prueba la configuración de OpenRouter"""
    print("🤖 Probando configuración de OpenRouter...")
    print("=" * 50)
    
    # Mostrar configuración actual
    print(f"Proveedor: {config.llm_provider}")
    print(f"Modelo: {config.openai_model}")
    print(f"API Key: {'***' if config.openai_api_key else 'NO CONFIGURADA'}")
    print(f"Base URL: {config.llm_base_url or 'Predeterminada'}")
    print()
    
    if not config.openai_api_key:
        print("❌ No se encontró API key de OpenRouter")
        print("💡 Configura OPENAI_API_KEY en tu archivo .env")
        return False
    
    # Crear procesador de texto
    processor = TextProcessor(
        api_key=config.openai_api_key,
        model=config.openai_model,
        provider=config.llm_provider,
        base_url=config.llm_base_url
    )
    
    if not processor.is_available():
        print("❌ No se pudo inicializar OpenRouter")
        return False
    
    print("✅ OpenRouter inicializado correctamente")
    
    # Probar con texto de ejemplo
    test_text = "hola como estas espero que bien gracias por preguntar"
    print(f"\n📝 Texto de prueba: {test_text}")
    
    print("🔄 Procesando con OpenRouter...")
    try:
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


def main():
    """Función principal"""
    print("🎙️  PRUEBA DE OPENROUTER")
    print("=" * 60)
    
    if test_openrouter():
        print("\n🎉 ¡OpenRouter funciona correctamente!")
        print("\n💡 Ahora puedes usar el frontend web:")
        print("   python start_web.py")
    else:
        print("\n⚠️  Hay problemas con OpenRouter")
        print("💡 Verifica tu configuración en el archivo .env")


if __name__ == "__main__":
    main()
