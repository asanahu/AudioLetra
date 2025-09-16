#!/usr/bin/env python3
"""
Script para configurar automáticamente OpenRouter en el archivo .env
"""

import os
from pathlib import Path


def configure_openrouter():
    """Configura el archivo .env para usar OpenRouter"""
    
    print("🔧 Configurando OpenRouter...")
    
    # Leer el archivo de ejemplo
    example_file = Path("openrouter_example.env")
    if not example_file.exists():
        print("❌ Archivo openrouter_example.env no encontrado")
        return False
    
    # Leer contenido
    with open(example_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Modificar configuración
    content = content.replace("LLM_ENABLED=false", "LLM_ENABLED=true")
    content = content.replace("OPENAI_API_KEY=tu_api_key_de_openrouter_aqui", "OPENAI_API_KEY=")
    
    # Escribir archivo .env
    env_file = Path(".env")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo .env configurado para OpenRouter")
    print("💡 Ahora necesitas:")
    print("   1. Obtener tu API key de https://openrouter.ai/keys")
    print("   2. Editar .env y agregar tu API key")
    print("   3. Ejecutar: python whisper_dictado.py --llm-enable")
    
    return True


def show_current_config():
    """Muestra la configuración actual"""
    print("\n📋 Configuración actual:")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return
    
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    important_vars = [
        "LLM_ENABLED",
        "LLM_PROVIDER", 
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "WHISPER_MODEL",
        "WHISPER_LANGUAGE"
    ]
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key = line.split('=')[0]
            if key in important_vars:
                if key == "OPENAI_API_KEY":
                    value = "***" if line.split('=', 1)[1] else "NO CONFIGURADA"
                else:
                    value = line.split('=', 1)[1]
                print(f"   {key}: {value}")


def main():
    """Función principal"""
    print("🎙️  CONFIGURADOR DE OPENROUTER")
    print("=" * 40)
    
    if configure_openrouter():
        show_current_config()
        
        print("\n🚀 Próximos pasos:")
        print("1. Ve a https://openrouter.ai/keys")
        print("2. Crea una cuenta y obtén tu API key")
        print("3. Edita el archivo .env y agrega tu API key")
        print("4. Prueba: python test_openrouter.py")
        print("5. Usa: python whisper_dictado.py --llm-enable")


if __name__ == "__main__":
    main()
