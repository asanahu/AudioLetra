#!/usr/bin/env python3
"""
Script principal para AudioLetra: Captura tus ideas, la IA las escribe.
Combina detección de voz (VAD), transcripción local y post-procesado opcional con LLM.
"""

import argparse
import sys
import os
import time
import signal
import numpy as np
from pathlib import Path
from typing import Optional

# Agregar directorios al path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "config"))
sys.path.append(str(Path(__file__).parent / "utils"))

# Importar módulos locales
from config.config import config
from utils.audio_handler import AudioHandler, AudioRecorder
from utils.simple_vad import create_vad_detector
from utils.text_processor import TextProcessor, TranscriptionManager

# Importar Whisper
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    print("❌ Error: faster-whisper no está instalado")
    print("💡 Instala con: pip install faster-whisper")
    WHISPER_AVAILABLE = False
    sys.exit(1)


class WhisperDictation:
    """Clase principal para dictado inteligente"""
    
    def __init__(self):
        """Inicializa el sistema de dictado"""
        self.whisper_model = None
        self.audio_handler = None
        self.vad_detector = None
        self.text_processor = None
        self.transcription_manager = None
        self.is_running = False
        self.audio_buffer = []  # Buffer de audio como atributo de clase
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("🎙️  Inicializando sistema de dictado inteligente...")
        self._initialize_components()
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de interrupción"""
        print("\n🛑 Deteniendo sistema...")
        self.stop()
        sys.exit(0)
    
    def _initialize_components(self):
        """Inicializa todos los componentes del sistema"""
        try:
            # Inicializar Whisper
            print("🧠 Cargando modelo Whisper...")
            
            # Determinar dispositivo y tipo de computación
            if config.whisper_use_gpu:
                try:
                    # Intentar usar GPU
                    self.whisper_model = WhisperModel(
                        config.whisper_model,
                        device="cuda",
                        compute_type="float16"
                    )
                    print(f"✅ Modelo Whisper cargado en GPU: {config.whisper_model}")
                except Exception as e:
                    print(f"⚠️  Error al cargar en GPU: {e}")
                    print("🔄 Cambiando a CPU...")
                    self.whisper_model = WhisperModel(
                        config.whisper_model,
                        device="cpu",
                        compute_type="int8"
                    )
                    print(f"✅ Modelo Whisper cargado en CPU: {config.whisper_model}")
            else:
                # Usar CPU directamente
                self.whisper_model = WhisperModel(
                    config.whisper_model,
                    device="cpu",
                    compute_type="int8"
                )
                print(f"✅ Modelo Whisper cargado en CPU: {config.whisper_model}")
            
            # Inicializar manejador de audio
            print("🎤 Configurando audio...")
            audio_config = config.get_audio_config()
            self.audio_handler = AudioHandler(**audio_config)
            
            # Inicializar detector VAD
            print("🎯 Configurando detección de voz...")
            vad_config = config.get_vad_config()
            self.vad_detector = create_vad_detector(
                sample_rate=config.sample_rate,
                sensitivity=vad_config["sensitivity"],
                use_webrtc=True  # Intentar usar webrtcvad primero
            )
            
            # Inicializar procesador de texto
            print("📝 Configurando procesamiento de texto...")
            self.text_processor = TextProcessor(
                api_key=config.openai_api_key,
                model=config.openai_model,
                provider=config.llm_provider,
                base_url=config.llm_base_url
            )
            
            # Inicializar manejador de transcripciones
            self.transcription_manager = TranscriptionManager(config.output_dir)
            
            print("✅ Sistema inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error al inicializar componentes: {e}")
            sys.exit(1)
    
    def start_dictation(self):
        """Inicia el proceso de dictado"""
        if not WHISPER_AVAILABLE:
            print("❌ Whisper no está disponible")
            return
        
        print("\n🎙️  === DICTADO INTELIGENTE INICIADO ===")
        print("💡 Habla normalmente - el sistema detectará automáticamente tu voz")
        print("💡 Presiona Ctrl+C para detener")
        print("=" * 50)
        
        self.is_running = True
        self.audio_buffer = []  # Reiniciar buffer
        
        def audio_callback(indata, frames, time, status):
            """Callback para procesar audio en tiempo real"""
            if not self.is_running:
                return
            
            # Manejar errores de audio
            if status:
                if "overflow" in str(status):
                    print(f"\n⚠️  Overflow de audio - reduciendo buffer")
                    # Limpiar buffer parcialmente para evitar overflow
                    if len(self.audio_buffer) > config.sample_rate * 10:  # Más de 10 segundos
                        self.audio_buffer = self.audio_buffer[-config.sample_rate * 5:]  # Mantener solo últimos 5 segundos
                else:
                    print(f"\n⚠️  Error de audio: {status}")
            
            # Agregar al buffer (limitar tamaño)
            new_data = indata.flatten()
            self.audio_buffer.extend(new_data)
            
            # Limitar tamaño del buffer para evitar problemas de memoria
            max_buffer_size = config.sample_rate * 30  # Máximo 30 segundos
            if len(self.audio_buffer) > max_buffer_size:
                self.audio_buffer = self.audio_buffer[-max_buffer_size:]
            
            # Procesar con VAD
            vad_result = self.vad_detector.process_frame(new_data)
            
            # Mostrar estado en tiempo real
            if config.realtime_display:
                status_icon = "🎤" if vad_result['is_speaking'] else "🔇"
                buffer_sec = len(self.audio_buffer) / config.sample_rate
                print(f"\r{status_icon} {'Hablando...' if vad_result['is_speaking'] else 'Escuchando...'} ({buffer_sec:.1f}s)", end="", flush=True)
            
            # Si terminó de hablar, procesar audio
            if vad_result.get('speech_ended'):
                if len(self.audio_buffer) > config.sample_rate * 0.5:  # Al menos 0.5 segundos
                    self._process_audio_segment(self.audio_buffer.copy())
                    self.audio_buffer.clear()
        
        # Iniciar grabación
        self.audio_handler.start_recording(audio_callback)
        
        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Interrumpido por usuario")
        finally:
            self.stop()
    
    def _process_audio_segment(self, audio_data):
        """Procesa un segmento de audio"""
        if len(audio_data) == 0:
            return
        
        print(f"\n🔄 Procesando audio ({len(audio_data)/config.sample_rate:.1f}s)...")
        
        try:
            # Convertir lista a array de numpy si es necesario
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data)
            
            # Limpiar audio
            audio_data = self.audio_handler.trim_silence(audio_data)
            
            if len(audio_data) == 0:
                print("⚠️  Audio vacío después de limpiar silencios")
                return
            
            # Transcribir con Whisper
            print("🧠 Transcribiendo...")
            
            # Convertir audio a formato compatible con Whisper
            import tempfile
            import wave
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
                
                # Guardar audio en formato WAV
                audio_int16 = (audio_data * 32767).astype(np.int16)
                with wave.open(temp_filename, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)  # 16 bits
                    wav_file.setframerate(config.sample_rate)
                    wav_file.writeframes(audio_int16.tobytes())
            
            try:
                # Transcribir desde archivo
                segments, info = self.whisper_model.transcribe(
                    temp_filename,
                    language=config.whisper_language if config.whisper_language != "auto" else None,
                    beam_size=5,
                    best_of=5
                )
            finally:
                # Limpiar archivo temporal
                import os
                try:
                    os.unlink(temp_filename)
                except:
                    pass
            
            # Combinar segmentos
            text = ""
            for segment in segments:
                text += segment.text + " "
            
            text = text.strip()
            
            if not text:
                print("⚠️  No se detectó texto en el audio")
                return
            
            print(f"📝 Transcripción: {text}")
            
            # Procesar texto
            processed_text = self._process_text(text)
            
            # Guardar transcripción
            self._save_transcription(processed_text, audio_data)
            
        except Exception as e:
            print(f"❌ Error al procesar audio: {e}")
    
    def _process_text(self, text: str) -> str:
        """Procesa el texto transcrito"""
        # Limpieza básica
        cleaned_text = self.text_processor.cleanup_text(text)
        
        # Post-procesado con LLM si está habilitado
        if config.llm_enabled and self.text_processor.is_available():
            print("🤖 Mejorando texto con LLM...")
            improved_text = self.text_processor.improve_text(cleaned_text, "cleanup")
            if improved_text:
                cleaned_text = improved_text
        
        return cleaned_text
    
    def _save_transcription(self, text: str, audio_data):
        """Guarda la transcripción"""
        try:
            # Crear nombre de archivo
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            if config.include_timestamp:
                filename_base = f"dictado_{timestamp}"
            else:
                filename_base = "dictado_latest"
            
            # Guardar audio si es necesario
            audio_filename = None
            if config.debug_mode:
                audio_filename = f"{config.output_dir}/{filename_base}.wav"
                self.audio_handler.save_audio(audio_data, audio_filename)
            
            # Guardar transcripción
            text_filename = f"{config.output_dir}/{filename_base}.{config.output_format}"
            self.text_processor.save_text(text, text_filename, config.output_format)
            
            # Añadir al historial
            self.transcription_manager.add_transcription(
                text=text,
                audio_file=audio_filename,
                metadata={
                    "duration": len(audio_data) / config.sample_rate,
                    "model": config.whisper_model,
                    "language": config.whisper_language
                }
            )
            
            print(f"✅ Transcripción guardada: {text_filename}")
            
        except Exception as e:
            print(f"❌ Error al guardar transcripción: {e}")
    
    def stop(self):
        """Detiene el sistema"""
        self.is_running = False
        
        if self.audio_handler:
            self.audio_handler.stop_recording()
            self.audio_handler.cleanup()
        
        print("🛑 Sistema detenido")
    
    def test_audio(self):
        """Prueba la configuración de audio"""
        print("🎤 Probando configuración de audio...")
        
        def test_callback(indata, frames, time, status):
            level = self.audio_handler.get_audio_level(indata)
            print(f"\rNivel de audio: {level:.3f}", end="", flush=True)
        
        self.audio_handler.start_recording(test_callback)
        
        try:
            print("\n💡 Habla en el micrófono para probar...")
            time.sleep(5)
        except KeyboardInterrupt:
            pass
        finally:
            self.audio_handler.stop_recording()
            print("\n✅ Prueba de audio completada")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Dictado inteligente con Whisper")
    parser.add_argument("--test-audio", action="store_true", help="Probar configuración de audio")
    parser.add_argument("--modelo", default=None, help="Modelo de Whisper a usar")
    parser.add_argument("--idioma", default=None, help="Idioma para transcripción")
    parser.add_argument("--llm-enable", action="store_true", help="Habilitar post-procesado con LLM")
    parser.add_argument("--config", help="Archivo de configuración personalizado")
    
    args = parser.parse_args()
    
    # Mostrar configuración
    print("🔧 Configuración:")
    config.print_config()
    
    # Crear instancia del sistema
    dictation = WhisperDictation()
    
    # Probar audio si se solicita
    if args.test_audio:
        dictation.test_audio()
        return
    
    # Iniciar dictado
    try:
        dictation.start_dictation()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
