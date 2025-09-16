"""
Módulo alternativo para detección de actividad de voz (VAD) sin webrtcvad.
Usa análisis de energía de audio para detectar voz.
"""

import numpy as np
from typing import List, Tuple, Optional
import collections
import time


class SimpleVADDetector:
    """Detector de actividad de voz basado en análisis de energía"""
    
    def __init__(self, sample_rate: int = 16000, sensitivity: float = 0.01):
        """
        Inicializa el detector VAD simple
        
        Args:
            sample_rate: Frecuencia de muestreo
            sensitivity: Sensibilidad del detector (umbral de energía)
        """
        self.sample_rate = sample_rate
        self.sensitivity = sensitivity
        
        # Configuración de frames
        self.frame_duration_ms = 30  # Duración de cada frame en ms
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)
        
        # Buffer para almacenar frames
        self.frame_buffer = collections.deque(maxlen=10)
        
        print(f"🎯 VAD Simple inicializado - Sensibilidad: {sensitivity}, Frame size: {self.frame_size}")
    
    def is_speech(self, audio_frame: np.ndarray) -> bool:
        """
        Detecta si un frame de audio contiene voz basado en energía
        
        Args:
            audio_frame: Frame de audio
            
        Returns:
            True si detecta voz, False si es silencio
        """
        if len(audio_frame) == 0:
            return False
        
        # Calcular energía RMS
        energy = np.sqrt(np.mean(audio_frame**2))
        
        # Detectar voz si la energía supera el umbral
        return energy > self.sensitivity
    
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
            Probabilidad de voz basada en energía
        """
        if len(audio_frame) == 0:
            return 0.0
        
        energy = np.sqrt(np.mean(audio_frame**2))
        
        # Normalizar probabilidad (0.0 a 1.0)
        # Usar función sigmoide para suavizar la transición
        probability = 1.0 / (1.0 + np.exp(-(energy - self.sensitivity) * 100))
        
        return float(probability)


class RealTimeSimpleVAD:
    """VAD en tiempo real usando análisis de energía"""
    
    def __init__(self, sample_rate: int = 16000, sensitivity: float = 0.01,
                 min_speech_duration: float = 0.5, min_silence_duration: float = 1.0):
        """
        Inicializa VAD en tiempo real
        
        Args:
            sample_rate: Frecuencia de muestreo
            sensitivity: Sensibilidad del detector
            min_speech_duration: Duración mínima de voz
            min_silence_duration: Duración mínima de silencio
        """
        self.vad = SimpleVADDetector(sample_rate, sensitivity)
        self.min_speech_duration = min_speech_duration
        self.min_silence_duration = min_silence_duration
        
        # Estado del detector
        self.is_speaking = False
        self.speech_start_time = None
        self.silence_start_time = None
        
        # Buffer de audio para análisis
        self.audio_buffer = []
        self.frame_size = self.vad.frame_size
        
        print(f"🔄 VAD Simple en tiempo real iniciado")
    
    def process_frame(self, audio_frame: np.ndarray) -> dict:
        """
        Procesa un frame de audio y retorna estado
        
        Args:
            audio_frame: Frame de audio
            
        Returns:
            Diccionario con estado del VAD
        """
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


# Función para detectar automáticamente qué VAD usar
def create_vad_detector(sample_rate: int = 16000, sensitivity: int = 2, 
                       use_webrtc: bool = True) -> object:
    """
    Crea un detector VAD, intentando usar webrtcvad primero, 
    luego cayendo a la implementación simple
    
    Args:
        sample_rate: Frecuencia de muestreo
        sensitivity: Sensibilidad del detector
        use_webrtc: Intentar usar webrtcvad primero
        
    Returns:
        Instancia del detector VAD
    """
    if use_webrtc:
        try:
            import webrtcvad
            from .vad_detector import VADDetector, RealTimeVAD
            print("✅ Usando webrtcvad (WebRTC VAD)")
            return RealTimeVAD(sample_rate, sensitivity)
        except ImportError:
            print("⚠️  webrtcvad no disponible, usando VAD simple")
    
    # Usar implementación simple
    sensitivity_map = {0: 0.005, 1: 0.01, 2: 0.02, 3: 0.05}
    simple_sensitivity = sensitivity_map.get(sensitivity, 0.02)
    
    return RealTimeSimpleVAD(sample_rate, simple_sensitivity)
