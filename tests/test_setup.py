#!/usr/bin/env python3
"""
Script de prueba rápida para AudioLetra: Captura tus ideas, la IA las escribe.
"""

import sys
from pathlib import Path

# Agregar directorios al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "config"))
sys.path.append(str(project_root / "utils"))


def test_imports():
    """Prueba las importaciones"""
    print("🧪 Probando importaciones...")
    
    try:
        from config.config import config
        print("✅ Config - OK")
        
        from utils.audio_handler import AudioHandler
        print("✅ AudioHandler - OK")
        
        from utils.vad_detector import VADDetector
        print("✅ VADDetector - OK")
        
        from utils.text_processor import TextProcessor
        print("✅ TextProcessor - OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False


def test_whisper():
    """Prueba la importación de Whisper"""
    print("\n🧠 Probando Whisper...")
    
    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper - OK")
        return True
    except ImportError:
        print("❌ faster-whisper no instalado")
        return False


def test_audio_dependencies():
    """Prueba las dependencias de audio"""
    print("\n🎤 Probando dependencias de audio...")
    
    try:
        import sounddevice as sd
        print("✅ sounddevice - OK")
        
        import webrtcvad
        print("✅ webrtcvad - OK")
        
        import numpy as np
        print("✅ numpy - OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de dependencias de audio: {e}")
        return False


def test_openai():
    """Prueba OpenAI (opcional)"""
    print("\n🤖 Probando OpenAI...")
    
    try:
        import openai
        print("✅ openai - OK")
        return True
    except ImportError:
        print("⚠️  openai no instalado (opcional)")
        return False


def test_configuration():
    """Prueba la configuración"""
    print("\n⚙️  Probando configuración...")
    
    try:
        from config.config import config
        
        print(f"   Modelo Whisper: {config.whisper_model}")
        print(f"   Idioma: {config.whisper_language}")
        print(f"   Sensibilidad VAD: {config.vad_sensitivity}")
        print(f"   LLM habilitado: {config.llm_enabled}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error de configuración: {e}")
        return False


def main():
    """Función principal de prueba"""
    print("🎙️  PRUEBA RÁPIDA - AUDIOLETRA")
    print("   Captura tus ideas, la IA las escribe")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_whisper,
        test_audio_dependencies,
        test_openai,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error en prueba: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
        print("\n💡 Para iniciar el dictado:")
        print("   python whisper_dictado.py")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("\n💡 Para instalar dependencias faltantes:")
        print("   pip install -r requirements.txt")


if __name__ == "__main__":
    main()
