#!/usr/bin/env python3
"""
Script de instalación y configuración para AudioLetra: Captura tus ideas, la IA las escribe.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_banner():
    """Imprime el banner de bienvenida"""
    print("=" * 60)
    print("🎙️  AUDIOLETRA - INSTALACIÓN")
    print("   Captura tus ideas, la IA las escribe")
    print("=" * 60)
    print()


def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True


def check_ffmpeg():
    """Verifica si FFmpeg está instalado"""
    print("\n🎬 Verificando FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg encontrado - OK")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  FFmpeg no encontrado")
    print("💡 Instrucciones de instalación:")
    
    system = platform.system().lower()
    if system == "windows":
        print("   Windows: Descarga desde https://ffmpeg.org/download.html")
        print("   Añade ffmpeg.exe al PATH del sistema")
    elif system == "darwin":
        print("   macOS: brew install ffmpeg")
    elif system == "linux":
        print("   Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("   CentOS/RHEL: sudo yum install ffmpeg")
    
    return False


def install_dependencies():
    """Instala las dependencias de Python"""
    print("\n📦 Instalando dependencias...")
    
    # Primero intentar instalar webrtcvad-wheels
    print("🔧 Intentando instalar webrtcvad-wheels (versión precompilada)...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'webrtcvad-wheels'], 
                      check=True, capture_output=True)
        print("✅ webrtcvad-wheels instalado correctamente")
    except subprocess.CalledProcessError:
        print("⚠️  webrtcvad-wheels no disponible, usando VAD simple")
    
    # Instalar el resto de dependencias
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        print("\n💡 Soluciones alternativas:")
        print("   1. Instalar Microsoft Visual C++ Build Tools")
        print("   2. Usar: pip install webrtcvad-wheels")
        print("   3. El sistema funcionará con VAD simple si webrtcvad falla")
        return False


def setup_configuration():
    """Configura el archivo de configuración"""
    print("\n⚙️  Configurando archivo de configuración...")
    
    env_file = Path(".env")
    template_file = Path("config/config_template.env")
    
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return True
    
    if template_file.exists():
        # Copiar plantilla
        with open(template_file, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(env_file, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print("✅ Archivo .env creado desde plantilla")
        print("💡 Edita .env para personalizar la configuración")
        return True
    else:
        print("⚠️  Plantilla de configuración no encontrada")
        return False


def create_directories():
    """Crea los directorios necesarios"""
    print("\n📁 Creando directorios...")
    
    directories = ["output", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directorio {directory}/ creado")
    
    return True


def test_installation():
    """Prueba la instalación"""
    print("\n🧪 Probando instalación...")
    
    try:
        # Importar módulos principales
        from config.config import config
        print("✅ Módulo de configuración - OK")
        
        from utils.audio_handler import AudioHandler
        print("✅ Módulo de audio - OK")
        
        from utils.vad_detector import VADDetector
        print("✅ Módulo VAD - OK")
        
        from utils.text_processor import TextProcessor
        print("✅ Módulo de procesamiento de texto - OK")
        
        print("✅ Todos los módulos cargados correctamente")
        return True
        
    except ImportError as e:
        print(f"❌ Error al importar módulos: {e}")
        return False


def show_next_steps():
    """Muestra los siguientes pasos"""
    print("\n" + "=" * 60)
    print("🎉 ¡INSTALACIÓN COMPLETADA!")
    print("=" * 60)
    print()
    print("📋 Próximos pasos:")
    print()
    print("1. 🔧 Configurar el sistema:")
    print("   - Edita el archivo .env para personalizar la configuración")
    print("   - Ajusta la sensibilidad VAD si es necesario")
    print("   - Configura tu API key de OpenAI si quieres usar LLM")
    print()
    print("2. 🎤 Probar el audio:")
    print("   python whisper_dictado.py --test-audio")
    print()
    print("3. 🎙️  Iniciar dictado:")
    print("   python whisper_dictado.py")
    print()
    print("4. 📚 Opciones avanzadas:")
    print("   python whisper_dictado.py --help")
    print()
    print("💡 Para más información, consulta README.md")
    print()


def main():
    """Función principal del instalador"""
    print_banner()
    
    # Verificaciones
    if not check_python_version():
        sys.exit(1)
    
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        print("\n⚠️  Continuando sin FFmpeg (algunas funciones pueden no funcionar)")
    
    # Instalación
    if not install_dependencies():
        sys.exit(1)
    
    if not setup_configuration():
        print("⚠️  Continuando sin configuración personalizada")
    
    if not create_directories():
        print("⚠️  Error al crear directorios")
    
    # Pruebas
    if not test_installation():
        print("⚠️  Algunos módulos pueden no funcionar correctamente")
    
    # Finalización
    show_next_steps()


if __name__ == "__main__":
    main()
