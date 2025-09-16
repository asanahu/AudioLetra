#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo para manejo de audio y grabacion.
Incluye funciones para capturar audio del microfono y guardar archivos.
"""

from typing import Optional, Callable
import time
import wave

import numpy as np
import sounddevice as sd


class AudioHandler:
    """Manejador de audio para grabacion y procesamiento"""

    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024,
                 channels: int = 1, input_device: Optional[int] = None):
        """
        Inicializa el manejador de audio.

        Args:
            sample_rate: Frecuencia de muestreo
            chunk_size: Tamano del chunk de audio
            channels: Numero de canales
            input_device: Indice del dispositivo de entrada (None para predeterminado)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.input_device = input_device

        self.audio_buffer = []
        self.is_recording = False
        self.stream = None
        self.audio_callback: Optional[Callable] = None

        self._check_devices()

    def _check_devices(self):
        """Verifica los dispositivos de audio disponibles."""
        try:
            devices = sd.query_devices()
            print("Dispositivos de audio disponibles:")
            for i, device in enumerate(devices):
                if device.get('max_input_channels', 0) > 0:
                    status = " (SELECCIONADO)" if (self.input_device is not None and i == self.input_device) else ""
                    print(f"   {i}: {device['name']}{status}")

            if self.input_device is None:
                default_device = sd.default.device[0]
                print(f"Usando dispositivo predeterminado: {default_device}")
                self.input_device = default_device
        except Exception as e:
            print(f"Error al verificar dispositivos: {e}")

    def start_recording(self, callback: Optional[Callable] = None):
        """Inicia la grabacion de audio."""
        if self.is_recording:
            print("Aviso: ya se esta grabando audio")
            return

        self.audio_callback = callback
        self.audio_buffer = []
        self.is_recording = True

        try:
            self.stream = sd.InputStream(
                device=self.input_device,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                dtype=np.float32,
            )
            self.stream.start()
            print("Grabacion iniciada")
        except Exception as e:
            print(f"Error al iniciar grabacion: {e}")
            self.is_recording = False

    def stop_recording(self) -> np.ndarray:
        """Detiene la grabacion y retorna el audio capturado."""
        if not self.is_recording:
            print("Aviso: no se esta grabando audio")
            return np.array([])

        self.is_recording = False

        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            finally:
                self.stream = None

        print("Grabacion detenida")

        if self.audio_buffer:
            return np.concatenate(self.audio_buffer)
        return np.array([])

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"Error de audio: {status}")
        self.audio_buffer.append(indata.copy())
        if self.audio_callback:
            try:
                self.audio_callback(indata, frames, time_info, status)
            except Exception as e:
                print(f"Error en callback de audio: {e}")

    def get_audio_level(self, audio_data: np.ndarray) -> float:
        """Calcula el nivel RMS del audio."""
        if len(audio_data) == 0:
            return 0.0
        return float(np.sqrt(np.mean(audio_data ** 2)))

    def save_audio(self, audio_data: np.ndarray, filename: str) -> bool:
        """Guarda audio en formato WAV."""
        try:
            audio_int16 = (audio_data * 32767).astype(np.int16)
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            print(f"Audio guardado: {filename}")
            return True
        except Exception as e:
            print(f"Error al guardar audio: {e}")
            return False

    def load_audio(self, filename: str) -> Optional[np.ndarray]:
        """Carga audio desde archivo WAV."""
        try:
            with wave.open(filename, 'rb') as wav_file:
                frames = wav_file.readframes(-1)
                audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0
                return audio_data
        except Exception as e:
            print(f"Error al cargar audio: {e}")
            return None

    def trim_silence(self, audio_data: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """Elimina silencios del inicio y final del audio."""
        if len(audio_data) == 0:
            return audio_data
        start_idx = 0
        for i, sample in enumerate(audio_data):
            if abs(sample) > threshold:
                start_idx = i
                break
        end_idx = len(audio_data)
        for i in range(len(audio_data) - 1, -1, -1):
            if abs(audio_data[i]) > threshold:
                end_idx = i + 1
                break
        return audio_data[start_idx:end_idx]

    def get_duration(self, audio_data: np.ndarray) -> float:
        """Calcula la duracion del audio en segundos."""
        return len(audio_data) / self.sample_rate

    def cleanup(self):
        """Limpia recursos de audio."""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            finally:
                self.stream = None
        self.is_recording = False
        self.audio_buffer = []


class AudioRecorder:
    """Clase simplificada para grabacion de audio con VAD."""

    def __init__(self, audio_handler: AudioHandler):
        self.audio_handler = audio_handler
        self.recording_thread = None
        self.is_recording = False

    def record_until_silence(self, silence_threshold: float = 0.01,
                              max_duration: float = 30.0) -> np.ndarray:
        """Graba audio hasta detectar silencio o tiempo maximo."""
        audio_data_parts = []
        start_time = time.time()

        def audio_cb(indata, frames, t, status):
            audio_data_parts.append(indata.copy())

        self.audio_handler.start_recording(audio_cb)
        try:
            while time.time() - start_time < max_duration:
                if audio_data_parts:
                    current_level = self.audio_handler.get_audio_level(audio_data_parts[-1])
                    if current_level < silence_threshold:
                        time.sleep(0.5)
                        if self.audio_handler.get_audio_level(audio_data_parts[-1]) < silence_threshold:
                            break
                time.sleep(0.1)
        finally:
            self.audio_handler.stop_recording()

        if audio_data_parts:
            return np.concatenate(audio_data_parts)
        return np.array([])

