"""
Módulo para detección de actividad de voz (VAD).
Utiliza webrtcvad para detectar cuando el usuario está hablando.
"""

import webrtcvad
import numpy as np
from typing import List, Tuple, Optional
import collections


class VADDetector:
    """Detector de actividad de voz usando WebRTC VAD"""
    
    def __init__(self, sample_rate: int = 16000, sensitivity: int = 2):
        """
        Inicializa el detector VAD
        
        Args:
            sample_rate: Frecuencia de muestreo (debe ser 8000, 16000, 32000 o 48000)
            sensitivity: Sensibilidad del detector (0-3, donde 3 es más sensible)
        """
        self.sample_rate = sample_rate
        self.sensitivity = sensitivity
        
        # Validar frecuencia de muestreo
        valid_rates = [8000, 16000, 32000, 48000]
        if sample_rate not in valid_rates:
            raise ValueError(f"Frecuencia de muestreo debe ser una de: {valid_rates}")
        
        # Crear detector VAD
        self.vad = webrtcvad.Vad(sensitivity)
        
        # Configuración de frames
        self.frame_duration_ms = 30  # Duración de cada frame en ms
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)
        
        # Buffer para almacenar frames
        self.frame_buffer = collections.deque(maxlen=10)
        
        print(f"🎯 VAD inicializado - Sensibilidad: {sensitivity}, Frame size: {self.frame_size}")
    
    def is_speech(self, audio_frame: np.ndarray) -> bool:
        """
        Detecta si un frame de audio contiene voz
        
        Args:
            audio_frame: Frame de audio (debe ser exactamente frame_size samples)
            
        Returns:
            True si detecta voz, False si es silencio
        """
        if len(audio_frame) != self.frame_size:
            # Redimensionar si es necesario
            if len(audio_frame) > self.frame_size:
                audio_frame = audio_frame[:self.frame_size]
            else:
                # Rellenar con ceros si es muy corto
                audio_frame = np.pad(audio_frame, (0, self.frame_size - len(audio_frame)))
        
        # Convertir a formato requerido por webrtcvad (int16)
        audio_int16 = (audio_frame * 32767).astype(np.int16)
        
        try:
            return self.vad.is_speech(audio_int16.tobytes(), self.sample_rate)
        except Exception as e:
            print(f"⚠️  Error en detección VAD: {e}")
            return False
    
    def detect_speech_segments(self, audio_data: np.ndarray, 
                             min_speech_duration: float = 0.5,
                             min_silence_duration: float = 1.0) -> List[Tuple[int, int]]:
        """
        Detecta segmentos de voz en audio largo
        
        Args:
            audio_data: Datos de audio completos
            min_speech_duration: Duración mínima de voz para considerar válida
            min_silence_duration: Duración mínima de silencio para separar segmentos
            
        Returns:
            Lista de tuplas (inicio, fin) en samples
        """
        speech_segments = []
        in_speech = False
        speech_start = 0
        
        min_speech_samples = int(min_speech_duration * self.sample_rate)
        min_silence_samples = int(min_silence_duration * self.sample_rate)
        
        # Procesar audio frame por frame
        for i in range(0, len(audio_data) - self.frame_size, self.frame_size):
            frame = audio_data[i:i + self.frame_size]
            is_speech_frame = self.is_speech(frame)
            
            if is_speech_frame and not in_speech:
                # Inicio de voz
                in_speech = True
                speech_start = i
                
            elif not is_speech_frame and in_speech:
                # Fin de voz
                speech_end = i + self.frame_size
                speech_duration = speech_end - speech_start
                
                if speech_duration >= min_speech_samples:
                    speech_segments.append((speech_start, speech_end))
                
                in_speech = False
        
        # Manejar caso donde el audio termina en voz
        if in_speech:
            speech_end = len(audio_data)
            speech_duration = speech_end - speech_start
            if speech_duration >= min_speech_samples:
                speech_segments.append((speech_start, speech_end))
        
        # Fusionar segmentos muy cercanos
        merged_segments = self._merge_close_segments(speech_segments, min_silence_samples)
        
        return merged_segments
    
    def _merge_close_segments(self, segments: List[Tuple[int, int]], 
                             min_gap: int) -> List[Tuple[int, int]]:
        """
        Fusiona segmentos de voz que están muy cerca
        
        Args:
            segments: Lista de segmentos
            min_gap: Gap mínimo entre segmentos
            
        Returns:
            Lista de segmentos fusionados
        """
        if not segments:
            return []
        
        merged = [segments[0]]
        
        for current_start, current_end in segments[1:]:
            last_start, last_end = merged[-1]
            
            # Si el gap es menor que min_gap, fusionar
            if current_start - last_end < min_gap:
                merged[-1] = (last_start, current_end)
            else:
                merged.append((current_start, current_end))
        
        return merged
    
    def get_speech_probability(self, audio_frame: np.ndarray) -> float:
        """
        Obtiene una probabilidad de voz (0.0 a 1.0)
        
        Args:
            audio_frame: Frame de audio
            
        Returns:
            Probabilidad de voz
        """
        # Usar múltiples sensibilidades para obtener probabilidad
        probabilities = []
        
        for sensitivity in range(4):
            vad_temp = webrtcvad.Vad(sensitivity)
            try:
                audio_int16 = (audio_frame * 32767).astype(np.int16)
                if len(audio_int16) != self.frame_size:
                    if len(audio_int16) > self.frame_size:
                        audio_int16 = audio_int16[:self.frame_size]
                    else:
                        audio_int16 = np.pad(audio_int16, (0, self.frame_size - len(audio_int16)))
                
                is_speech = vad_temp.is_speech(audio_int16.tobytes(), self.sample_rate)
                probabilities.append(1.0 if is_speech else 0.0)
            except:
                probabilities.append(0.0)
        
        # Promedio de probabilidades
        return sum(probabilities) / len(probabilities)


class RealTimeVAD:
    """VAD en tiempo real para streaming de audio"""
    
    def __init__(self, sample_rate: int = 16000, sensitivity: int = 2,
                 min_speech_duration: float = 0.5, min_silence_duration: float = 1.0):
        """
        Inicializa VAD en tiempo real
        
        Args:
            sample_rate: Frecuencia de muestreo
            sensitivity: Sensibilidad del detector
            min_speech_duration: Duración mínima de voz
            min_silence_duration: Duración mínima de silencio
        """
        self.vad = VADDetector(sample_rate, sensitivity)
        self.min_speech_duration = min_speech_duration
        self.min_silence_duration = min_silence_duration
        
        # Estado del detector
        self.is_speaking = False
        self.speech_start_time = None
        self.silence_start_time = None
        
        # Buffer de audio para análisis
        self.audio_buffer = []
        self.frame_size = self.vad.frame_size
        
        print(f"🔄 VAD en tiempo real iniciado")
    
    def process_frame(self, audio_frame: np.ndarray) -> dict:
        """
        Procesa un frame de audio y retorna estado
        
        Args:
            audio_frame: Frame de audio
            
        Returns:
            Diccionario con estado del VAD
        """
        import time
        current_time = time.time()
        
        # Agregar frame al buffer
        self.audio_buffer.extend(audio_frame)
        
        # Procesar solo si tenemos suficientes samples
        if len(self.audio_buffer) >= self.frame_size:
            frame = np.array(self.audio_buffer[:self.frame_size])
            self.audio_buffer = self.audio_buffer[self.frame_size:]
            
            is_speech = self.vad.is_speech(frame)
            
            if is_speech and not self.is_speaking:
                # Inicio de voz
                self.is_speaking = True
                self.speech_start_time = current_time
                self.silence_start_time = None
                
            elif not is_speech and self.is_speaking:
                # Posible fin de voz
                if self.silence_start_time is None:
                    self.silence_start_time = current_time
                
                # Verificar si el silencio es suficientemente largo
                silence_duration = current_time - self.silence_start_time
                if silence_duration >= self.min_silence_duration:
                    # Fin de voz confirmado
                    speech_duration = self.silence_start_time - self.speech_start_time
                    
                    if speech_duration >= self.min_speech_duration:
                        self.is_speaking = False
                        return {
                            'is_speaking': False,
                            'speech_ended': True,
                            'speech_duration': speech_duration
                        }
            
            elif is_speech and self.is_speaking:
                # Continuando hablando
                self.silence_start_time = None
        
        return {
            'is_speaking': self.is_speaking,
            'speech_ended': False,
            'speech_duration': None
        }
    
    def reset(self):
        """Reinicia el estado del detector"""
        self.is_speaking = False
        self.speech_start_time = None
        self.silence_start_time = None
        self.audio_buffer = []
