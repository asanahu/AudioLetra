#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor web Flask para AudioLetra: Captura tus ideas, la IA las escribe.
Incluye UI web, grabacion de audio y postprocesado opcional con LLM.
"""

from __future__ import annotations

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Rutas de proyecto
BASE_DIR = Path(__file__).parent.resolve()
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "config"))
sys.path.append(str(BASE_DIR / "utils"))

from config.config import config  # type: ignore
from utils.audio_handler import AudioHandler  # type: ignore
from utils.simple_vad import create_vad_detector  # type: ignore
from utils.text_processor import TextProcessor, TranscriptionManager  # type: ignore

# Whisper (opcional, pero recomendado)
try:
    from faster_whisper import WhisperModel  # type: ignore
    WHISPER_AVAILABLE = True
except Exception:
    print("Aviso: faster-whisper no esta instalado. La transcripcion no estara disponible.")
    WhisperModel = None  # type: ignore
    WHISPER_AVAILABLE = False

import numpy as np


class WebDictationServer:
    def __init__(self) -> None:
        # Plantillas y estaticos con rutas absolutas
        templates_path = str(BASE_DIR / 'web' / 'templates')
        static_path = str(BASE_DIR / 'web' / 'static')
        self.app = Flask(
            __name__,
            template_folder=templates_path,
            static_folder=static_path,
            static_url_path='/static'
        )
        
        # Configurar headers para archivos estáticos
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            from flask import send_from_directory
            return send_from_directory(static_path, filename)
        CORS(self.app)

        # Componentes
        self.whisper_model: Optional[WhisperModel] = None  # type: ignore
        self.audio_handler: Optional[AudioHandler] = None
        self.vad_detector = None
        self.text_processor: Optional[TextProcessor] = None
        self.transcription_manager: Optional[TranscriptionManager] = None

        # Estado
        self.is_recording: bool = False
        self.audio_buffer: List[float] = []
        self._current_use_llm: bool = False

        self._setup_routes()
        self._initialize_components()
        print("Servidor web inicializado")

    def _setup_routes(self) -> None:
        @self.app.after_request
        def _add_charset(response):
            try:
                if request.path.startswith('/static/'):
                    return response
                text_types = {
                    'text/html', 'text/css', 'text/plain',
                    'application/javascript', 'text/javascript', 'application/json'
                }
                if response.mimetype in text_types:
                    ct = response.headers.get('Content-Type', '')
                    if 'charset=' not in ct:
                        response.headers['Content-Type'] = f"{response.mimetype}; charset=utf-8"
            except Exception:
                pass
            return response

        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/simple')
        def simple():
            return render_template('index-simple.html')

        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'whisper_available': WHISPER_AVAILABLE,
                'llm_available': self.text_processor.is_available() if self.text_processor else False,
                'is_recording': self.is_recording,
                'config': {
                    'whisper_model': config.whisper_model,
                    'whisper_language': config.whisper_language,
                    'llm_enabled': config.llm_enabled,
                    'llm_provider': config.llm_provider,
                }
            })

        @self.app.route('/api/start_recording', methods=['POST'])
        def start_recording():
            if self.is_recording:
                return jsonify({'error': 'Ya se esta grabando'}), 400

            data = request.get_json(silent=True) or {}
            self._current_use_llm = bool(data.get('use_llm', False))
            try:
                self._start_recording(self._current_use_llm)
                return jsonify({'status': 'success', 'message': 'Grabacion iniciada'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/stop_recording', methods=['POST'])
        def stop_recording():
            if not self.is_recording:
                return jsonify({'error': 'No se esta grabando'}), 400
            try:
                result = self._stop_recording(self._current_use_llm)
                return jsonify({'status': 'success', 'result': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/dictations')
        def get_dictations():
            try:
                dictations = self._get_recent_dictations()
                return jsonify({'status': 'success', 'dictations': dictations})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/dictations/<dictation_id>')
        def get_dictation(dictation_id):
            try:
                dictation = self._get_dictation_by_id(dictation_id)
                if dictation:
                    return jsonify({'status': 'success', 'dictation': dictation})
                return jsonify({'error': 'Dictado no encontrado'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/dictations/<dictation_id>', methods=['DELETE'])
        def delete_dictation(dictation_id):
            try:
                ok = self._delete_dictation(dictation_id)
                if ok:
                    return jsonify({'status': 'success', 'message': 'Dictado eliminado'})
                return jsonify({'error': 'Dictado no encontrado'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/postprocess', methods=['POST'])
        def postprocess():
            try:
                data = request.get_json(silent=True) or {}
                text = (data.get('text') or '').strip()
                do_summary = bool(data.get('do_summary', True))
                do_translate_en = bool(data.get('do_translate_en', False))
                if not text:
                    return jsonify({'status': 'success', 'result': {'summary': None, 'translation_en': None}})

                summary = None
                translation_en = None
                if self.text_processor and self.text_processor.is_available():
                    if do_summary:
                        try:
                            summary = self.text_processor.improve_text(text, 'summary')
                        except Exception as e:
                            print(f"Error en resumen: {e}")
                    if do_translate_en:
                        try:
                            translation_en = self.text_processor.translate_text(text, 'en')
                        except Exception as e:
                            print(f"Error en traduccion: {e}")
                else:
                    print('LLM no disponible para post-procesado')

                return jsonify({'status': 'success', 'result': {
                    'summary': summary,
                    'translation_en': translation_en
                }})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        # Nuevos endpoints para perfiles de LLM
        @self.app.route('/llm/profiles')
        def get_llm_profiles():
            """Obtener perfiles de procesamiento disponibles"""
            profiles = [
                {
                    "id": "clean_format",
                    "name": "Limpiar y Formatear",
                    "description": "Mejora la puntuación, estructura y legibilidad del texto",
                    "parameters": {},
                    "timeout_multiplier": 1.0
                },
                {
                    "id": "summarize",
                    "name": "Resumir",
                    "description": "Crea un resumen conciso y estructurado del texto",
                    "parameters": {},
                    "timeout_multiplier": 1.2
                },
                {
                    "id": "extract_tasks",
                    "name": "Extraer Lista de Tareas",
                    "description": "Identifica tareas accionables con verbos en infinitivo",
                    "parameters": {},
                    "timeout_multiplier": 1.1
                },
                {
                    "id": "format_email",
                    "name": "Formatear como Email",
                    "description": "Estructura el texto como un email profesional",
                    "parameters": {},
                    "timeout_multiplier": 1.3
                },
                {
                    "id": "meeting_minutes",
                    "name": "Crear Acta de Reunión",
                    "description": "Organiza el texto como acta de reunión",
                    "parameters": {},
                    "timeout_multiplier": 1.4
                },
                {
                    "id": "translate",
                    "name": "Traducir",
                    "description": "Traduce el texto al idioma seleccionado",
                    "parameters": {"target_language": "English"},
                    "timeout_multiplier": 2.0
                }
            ]
            return jsonify({"profiles": profiles})

        @self.app.route('/llm/process', methods=['POST'])
        def process_with_profile():
            """Procesar texto con un perfil específico"""
            try:
                data = request.get_json(silent=True) or {}
                profile_id = data.get('profile_id')
                text = (data.get('text') or '').strip()
                parameters = data.get('parameters', {})
                
                if not profile_id:
                    return jsonify({'error': {'code': 'INVALID_PROFILE', 'message': 'Profile ID is required'}}), 400
                
                if not text:
                    return jsonify({'error': {'code': 'INVALID_TEXT', 'message': 'Text is required'}}), 400
                
                if not self.text_processor or not self.text_processor.is_available():
                    return jsonify({'error': {'code': 'LLM_ERROR', 'message': 'LLM service not available'}}), 500
                
                # Mapear perfiles a funciones del text_processor
                profile_mapping = {
                    'clean_format': 'cleanup',
                    'summarize': 'summary',
                    'extract_tasks': 'tasks',
                    'format_email': 'email',
                    'meeting_minutes': 'meeting',
                    'translate': 'translate'
                }
                
                if profile_id not in profile_mapping:
                    return jsonify({'error': {'code': 'INVALID_PROFILE', 'message': f'Profile {profile_id} not found'}}), 400
                
                # Procesar según el perfil
                try:
                    if profile_id == 'translate':
                        target_language = parameters.get('target_language', 'English')
                        # Mapeo completo de idiomas
                        lang_mapping = {
                            'English': 'en',
                            'French': 'fr', 
                            'German': 'de',
                            'Portuguese': 'pt',
                            'Spanish': 'es',
                            'Italian': 'it',
                            'Dutch': 'nl',
                            'Russian': 'ru',
                            'Chinese': 'zh',
                            'Japanese': 'ja',
                            'Korean': 'ko',
                            'Arabic': 'ar'
                        }
                        lang_code = lang_mapping.get(target_language, 'en')
                        print(f"Traduciendo a: {target_language} (código: {lang_code})")
                        result = self.text_processor.translate_text(text, lang_code)
                        print(f"Resultado traducción: {result[:100] if result else 'None'}...")
                    else:
                        result = self.text_processor.improve_text(text, profile_mapping[profile_id])
                except Exception as e:
                    print(f"Error procesando texto: {e}")
                    return jsonify({'error': {'code': 'PROCESSING_ERROR', 'message': str(e)}}), 500
                
                if not result:
                    error_msg = f'No se pudo procesar el texto con el perfil {profile_id}'
                    if profile_id == 'translate':
                        error_msg += f' al idioma {target_language}'
                    return jsonify({'error': {'code': 'LLM_ERROR', 'message': error_msg}}), 500
                
                return jsonify({
                    'success': True,
                    'profile_id': profile_id,
                    'output': result,
                    'result_id': f"result_{int(datetime.now().timestamp())}",
                    'metadata': {
                        'processing_time': 0.0,
                        'tokens_used': 0
                    }
                })
                
            except Exception as e:
                print(f"Error processing with profile: {e}")
                return jsonify({'error': {'code': 'LLM_ERROR', 'message': str(e)}}), 500

    def _initialize_components(self) -> None:
        try:
            if WHISPER_AVAILABLE and WhisperModel is not None:  # type: ignore
                print("Cargando modelo Whisper...")
                self.whisper_model = WhisperModel(
                    config.whisper_model,
                    device='cpu',
                    compute_type='int8'
                )
                print(f"Modelo Whisper cargado: {config.whisper_model}")
            else:
                print("Whisper no disponible; la transcripcion estara deshabilitada")

            print("Configurando audio...")
            audio_config = config.get_audio_config()
            self.audio_handler = AudioHandler(**audio_config)

            print("Configurando deteccion de voz...")
            vad_config = config.get_vad_config()
            self.vad_detector = create_vad_detector(
                sample_rate=config.sample_rate,
                sensitivity=vad_config.get('sensitivity', 2),
                use_webrtc=True
            )

            print("Configurando procesamiento de texto...")
            self.text_processor = TextProcessor(
                api_key=config.openai_api_key,
                model=config.openai_model,
                provider=config.llm_provider,
                base_url=config.llm_base_url,
            )

            self.transcription_manager = TranscriptionManager(config.output_dir)
            print("Componentes inicializados correctamente")
        except Exception as e:
            print(f"Error al inicializar componentes: {e}")
            # No relanzar para permitir que la UI cargue y se puedan ver estados

    def _start_recording(self, use_llm: bool = False) -> None:
        self.audio_buffer = []
        self._current_use_llm = use_llm

        def cb(indata, frames, t, status):
            if not self.is_recording:
                return
            try:
                self.audio_buffer.extend(indata.flatten().tolist())
                # Limitar buffer a ~60s
                max_buffer_size = config.sample_rate * 300
                if len(self.audio_buffer) > max_buffer_size:
                    self.audio_buffer = self.audio_buffer[-max_buffer_size:]
            except Exception as e:
                print(f"Error procesando audio: {e}")

        if not self.audio_handler:
            raise RuntimeError('Audio no disponible')
        self.audio_handler.start_recording(cb)
        self.is_recording = True
        print("Grabacion iniciada")

    def _stop_recording(self, use_llm: bool = False) -> Dict:
        if not self.is_recording:
            return {'error': 'No se esta grabando'}

        self.is_recording = False
        try:
            if self.audio_handler:
                self.audio_handler.stop_recording()
        except Exception:
            pass

        if len(self.audio_buffer) == 0:
            return {'error': 'No se capturo audio'}

        try:
            # numpy array
            audio_data = np.array(self.audio_buffer, dtype=np.float32)
            if self.audio_handler:
                audio_data = self.audio_handler.trim_silence(audio_data)
            if len(audio_data) == 0:
                return {'error': 'Audio vacio despues de limpiar silencios'}

            # Guardar WAV temporal
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                fname = tmp.name
            try:
                audio_int16 = (audio_data * 32767).astype(np.int16)
                import wave
                with wave.open(fname, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(config.sample_rate)
                    wf.writeframes(audio_int16.tobytes())

                if not self.whisper_model:
                    return {'error': 'Whisper no disponible'}

                segments, info = self.whisper_model.transcribe(
                    fname,
                    language=(config.whisper_language if config.whisper_language != 'auto' else None),
                    beam_size=5,
                    best_of=5,
                )
            finally:
                try:
                    os.unlink(fname)
                except Exception:
                    pass

            text = " ".join(s.text for s in segments).strip()
            if not text:
                return {'error': 'No se detecto texto en el audio'}

            processed = self._process_text(text, use_llm)
            dictation_id = self._save_dictation(processed, audio_data)
            self._cleanup_old_dictations()

            return {
                'success': True,
                'text': processed,
                'original_text': text,
                'dictation_id': dictation_id,
                'duration': float(len(audio_data)) / float(config.sample_rate),
            }
        except Exception as e:
            print(f"Error al procesar audio: {e}")
            return {'error': str(e)}

    def _process_text(self, text: str, use_llm: bool = False) -> str:
        try:
            cleaned = self.text_processor.cleanup_text(text) if self.text_processor else text
            if use_llm and getattr(config, 'llm_enabled', False) and self.text_processor and self.text_processor.is_available():
                print("Mejorando texto con IA.")
                improved = self.text_processor.improve_text(cleaned, 'cleanup')
                if improved:
                    cleaned = improved
            return cleaned
        except Exception as e:
            print(f"Error en _process_text: {e}")
            return text

    def _save_dictation(self, text: str, audio_data: np.ndarray) -> str:
        try:
            ts = datetime.now()
            filename_base = f"dictado_{ts.strftime('%Y%m%d_%H%M%S')}"
            out_path = Path(config.output_dir)
            out_path.mkdir(parents=True, exist_ok=True)
            text_filename = str(out_path / f"{filename_base}.txt")
            if self.text_processor:
                self.text_processor.save_text(text, text_filename, 'txt')
            else:
                with open(text_filename, 'w', encoding='utf-8') as f:
                    f.write(text)

            duration = float(len(audio_data)) / float(config.sample_rate) if audio_data is not None else None
            dictation_id = self.transcription_manager.add_transcription(
                text=text,
                audio_file=None,
                metadata={
                    'duration': duration,
                    'model': getattr(config, 'whisper_model', ''),
                    'language': getattr(config, 'whisper_language', ''),
                    'timestamp': ts.isoformat(),
                },
            )
            return dictation_id
        except Exception as e:
            print(f"Error guardando transcripcion: {e}")
            return f"error-{int(datetime.now().timestamp())}"

    def _get_recent_dictations(self, limit: int = 3) -> List[Dict]:
        dictations = self.transcription_manager.get_recent_transcriptions(limit)
        result: List[Dict] = []
        for trans in dictations:
            result.append({
                'id': trans['id'],
                'text': trans['text'],
                'timestamp': trans['timestamp'],
                'metadata': trans.get('metadata', {}),
            })
        return result

    def _get_dictation_by_id(self, dictation_id: str) -> Optional[Dict]:
        d = self.transcription_manager.get_transcription(dictation_id)
        if d:
            return {
                'id': d['id'],
                'text': d['text'],
                'timestamp': d['timestamp'],
                'metadata': d.get('metadata', {}),
            }
        return None

    def _delete_dictation(self, dictation_id: str) -> bool:
        try:
            d = self.transcription_manager.get_transcription(dictation_id)
            if not d:
                return False
            ts = datetime.fromtimestamp(d['timestamp'])
            filename = f"dictado_{ts.strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = Path(config.output_dir) / filename
            if filepath.exists():
                filepath.unlink()
                print(f"Archivo eliminado: {filename}")
            self.transcription_manager.transcriptions = [t for t in self.transcription_manager.transcriptions if t['id'] != dictation_id]
            return True
        except Exception as e:
            print(f"Error al eliminar dictado {dictation_id}: {e}")
            return False

    def _cleanup_old_dictations(self):
        dictations = self.transcription_manager.get_recent_transcriptions(10)
        if len(dictations) > 3:
            for trans in dictations[3:]:
                try:
                    ts = datetime.fromtimestamp(trans['timestamp'])
                    filename = f"dictado_{ts.strftime('%Y%m%d_%H%M%S')}.txt"
                    filepath = Path(config.output_dir) / filename
                    if filepath.exists():
                        filepath.unlink()
                        print(f"Archivo eliminado: {filename}")
                    self.transcription_manager.transcriptions = [t for t in self.transcription_manager.transcriptions if t['id'] != trans['id']]
                except Exception as e:
                    print(f"Error al eliminar dictado {trans['id']}: {e}")

    def run(self, host='127.0.0.1', port=5000, debug=False):
        print(f"Iniciando servidor web en http://{host}:{port}")
        print("Abre tu navegador y ve a la URL mostrada arriba")
        self.app.run(host=host, port=port, debug=debug, threaded=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Servidor web para AudioLetra")
    parser.add_argument("--host", default="127.0.0.1", help="Host del servidor")
    parser.add_argument("--port", type=int, default=5000, help="Puerto del servidor")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    args = parser.parse_args()
    try:
        server = WebDictationServer()
        server.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nServidor detenido")
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

