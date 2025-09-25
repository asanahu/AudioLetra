#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesamiento de texto con y sin LLM, y gestion simple de transcripciones.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import os
import re

try:
    import openai  # type: ignore
except Exception:
    openai = None  # LLM opcional


class TextProcessor:
    """Procesador de texto con capacidades de LLM (opcional)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini",
                 provider: str = "openai", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.provider = (provider or "openai").lower()
        self.base_url = base_url
        self.client = None

        if api_key and openai is not None:
            try:
                if self.provider == "openrouter":
                    base = base_url or "https://openrouter.ai/api/v1"
                    self.client = openai.OpenAI(api_key=api_key, base_url=base)
                else:
                    self.client = openai.OpenAI(api_key=api_key)
                print(f"LLM inicializado ({self.provider}) - Modelo: {model}")
            except Exception as e:
                print(f"Error al inicializar LLM ({self.provider}): {e}")
                self.client = None
        elif api_key and openai is None:
            print("Aviso: 'openai' no disponible; LLM deshabilitado")
        else:
            print("LLM deshabilitado (sin API key)")

    def is_available(self) -> bool:
        return self.client is not None

    def improve_text(self, text: str, prompt_type: str = "cleanup") -> Optional[str]:
        if not self.is_available():
            return None
        if not text or not text.strip():
            return text

        prompt = self._get_prompt(prompt_type, text)
        try:
            extra_headers = {}
            if self.provider == "openrouter":
                extra_headers["HTTP-Referer"] = "http://127.0.0.1:5000"
                extra_headers["X-Title"] = "Whisper Dictation"

            params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Eres un asistente que mejora textos transcritos. Responde solo con el texto mejorado, sin explicaciones."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 2000,
                "temperature": 0.3,
            }
            if extra_headers:
                params["extra_headers"] = extra_headers

            response = self.client.chat.completions.create(**params)  # type: ignore[attr-defined]
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            print(f"Error al procesar texto con LLM ({self.provider}): {e}")
            return None

    def translate_text(self, text: str, target_lang: str = "en") -> Optional[str]:
        if not self.is_available():
            return None
        if not text or not text.strip():
            return text
        
        # Mapeo de códigos de idioma a nombres completos
        lang_names = {
            'en': 'inglés',
            'fr': 'francés', 
            'de': 'alemán',
            'pt': 'portugués',
            'es': 'español',
            'it': 'italiano',
            'nl': 'holandés',
            'ru': 'ruso',
            'zh': 'chino',
            'ja': 'japonés',
            'ko': 'coreano',
            'ar': 'árabe'
        }
        
        target_lang_name = lang_names.get(target_lang.lower(), 'inglés')
        
        try:
            extra_headers = {}
            if self.provider == "openrouter":
                extra_headers["HTTP-Referer"] = "http://127.0.0.1:5000"
                extra_headers["X-Title"] = "Whisper Dictation"

            prompt = (
                f"Traduce fiel y naturalmente al {target_lang_name} el siguiente texto en español. "
                "Mantén el significado, nombres propios y formato básico. "
                "Devuelve solo el texto traducido, sin notas ni explicaciones:\n\n" + text
            )

            params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Eres un traductor experto. Responde solo con la traduccion."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 2000,
                "temperature": 0.2,
            }
            if extra_headers:
                params["extra_headers"] = extra_headers

            resp = self.client.chat.completions.create(**params)  # type: ignore[attr-defined]
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            print(f"Error al traducir texto con LLM ({self.provider}): {e}")
            return None

    def _get_prompt(self, prompt_type: str, text: str) -> str:
        prompts = {
            "cleanup": f"Mejora la puntuacion y formato de este texto transcrito, manteniendo el contenido original:\n\n{text}",
            "summary": f"Crea un resumen conciso de este texto:\n\n{text}",
            "tasks": f"Extrae las tareas y puntos importantes de este texto en formato de lista:\n\n{text}",
            "email": f"Formatea este texto como un email profesional:\n\n{text}",
            "meeting": f"Formatea este texto como un acta de reunion con puntos clave:\n\n{text}",
            "notes": f"Organiza este texto como notas estructuradas:\n\n{text}",
        }
        return prompts.get(prompt_type, prompts["cleanup"])

    def cleanup_text(self, text: str) -> str:
        if not text:
            return text
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"([,.!?;:])\s*([,.!?;:])", r"\1", text)
        sentences = re.split(r"([.!?])", text)
        cleaned: List[str] = []
        for s in sentences:
            if s.strip() and s not in ".!?":
                s = s.strip()
                if s:
                    s = s[0].upper() + s[1:]
                cleaned.append(s)
            elif s in ".!?":
                cleaned.append(s)
        text = "".join(cleaned)
        return text.strip()

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        if not text:
            return []
        clean_text = re.sub(r"[^\w\s]", "", text.lower())
        stop_words = {
            'el','la','de','que','y','a','en','un','es','se','no','te','lo','le','da','su','por','son','con','para','al','del','los','las','una','uno','esta','este','estan','pero','como','mas','muy','todo','todos','toda','todas','bien','mejor','peor','gran','grande','pequeno','nuevo','viejo','bueno','malo'
        }
        words = clean_text.split()
        counts: Dict[str,int] = {}
        for w in words:
            if len(w) > 2 and w not in stop_words:
                counts[w] = counts.get(w, 0) + 1
        return [w for w,_ in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:max_keywords]]

    def format_as_notes(self, text: str) -> str:
        if not text:
            return text
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        return "\n".join([f"- {s}" for s in sentences])

    def add_timestamp(self, text: str) -> str:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{ts}] {text}"

    def save_text(self, text: str, filename: str, format_type: str = "txt") -> bool:
        try:
            if format_type == "md":
                content = f"# Transcripcion\n\n{text}\n\n---\n*Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            elif format_type == "json":
                data = {
                    "text": text,
                    "timestamp": datetime.now().isoformat(),
                    "word_count": len(text.split()),
                    "char_count": len(text),
                }
                content = json.dumps(data, indent=2, ensure_ascii=False)
            else:
                content = text
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Texto guardado: {filename}")
            return True
        except Exception as e:
            print(f"Error al guardar texto: {e}")
            return False


class TranscriptionManager:
    """Manejador de transcripciones con historial (memoria en proceso)."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.transcriptions: List[Dict[str, Any]] = []
        os.makedirs(output_dir, exist_ok=True)

    def add_transcription(self, text: str, audio_file: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        import uuid, time
        tid = str(uuid.uuid4())
        entry: Dict[str, Any] = {
            "id": tid,
            "text": text,
            "timestamp": time.time(),
            "audio_file": audio_file,
            "metadata": metadata or {},
        }
        self.transcriptions.append(entry)
        self._save_transcription(entry)
        return tid

    def _save_transcription(self, transcription: Dict[str, Any]) -> bool:
        try:
            ts = datetime.fromtimestamp(transcription["timestamp"]) 
            filename = f"transcripcion_{ts.strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Transcripcion ID: {transcription['id']}\n")
                f.write(f"Timestamp: {ts.strftime('%Y-%m-%d %H:%M:%S')}\n")
                if transcription.get('audio_file'):
                    f.write(f"Audio: {transcription['audio_file']}\n")
                f.write(f"\n{transcription['text']}\n")
            return True
        except Exception as e:
            print(f"Error al guardar transcripcion: {e}")
            return False

    def get_transcription(self, transcription_id: str) -> Optional[Dict[str, Any]]:
        for t in self.transcriptions:
            if t["id"] == transcription_id:
                return t
        return None

    def get_recent_transcriptions(self, limit: int = 10) -> List[Dict[str, Any]]:
        return sorted(self.transcriptions, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def export_all(self, format_type: str = "json") -> bool:
        try:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.output_dir, f"export_{ts}.{format_type}")
            if format_type == "json":
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.transcriptions, f, indent=2, ensure_ascii=False)
            else:
                with open(filename, 'w', encoding='utf-8') as f:
                    for trans in self.transcriptions:
                        f.write(f"=== {datetime.fromtimestamp(trans['timestamp']).strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                        f.write(f"{trans['text']}\n\n")
            print(f"Exportacion completa: {filename}")
            return True
        except Exception as e:
            print(f"Error al exportar: {e}")
            return False

