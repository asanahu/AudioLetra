# Data Model: Transcripción en Streaming

**Feature**: Transcripción en Streaming (Tiempo Real)  
**Date**: 2025-01-27  
**Branch**: `003-a-ade-transcripci`

## Entities

### StreamingSession
Representa una sesión activa de transcripción en streaming.

**Fields**:
- `session_id` (string, UUID): Identificador único de la sesión
- `user_id` (string, optional): Identificador del usuario (si hay autenticación)
- `status` (enum): Estado actual de la sesión
  - `connecting`: Estableciendo conexión
  - `connected`: Conectado y listo
  - `recording`: Grabando audio
  - `paused`: Pausado por usuario
  - `reconnecting`: Reconectando tras fallo
  - `finalizing`: Finalizando sesión
  - `completed`: Sesión completada
  - `error`: Error en la sesión
- `start_time` (datetime): Timestamp de inicio de sesión
- `last_activity` (datetime): Última actividad en la sesión
- `duration_limit` (integer): Límite de duración en segundos (3600 = 60min)
- `audio_chunks_received` (integer): Contador de chunks de audio recibidos
- `partial_text` (string): Texto parcial actual (no confirmado)
- `confirmed_text` (string): Texto confirmado acumulado
- `metadata` (object): Metadatos adicionales de la sesión

**Validation Rules**:
- `session_id` debe ser UUID válido
- `status` debe ser uno de los valores del enum
- `start_time` debe ser timestamp válido
- `duration_limit` debe ser >= 60 y <= 3600 segundos
- `audio_chunks_received` debe ser >= 0

**State Transitions**:
```
connecting → connected → recording → paused → recording → finalizing → completed
     ↓           ↓           ↓         ↓         ↓           ↓
   error      error      error    error    error      error
     ↓           ↓           ↓         ↓         ↓           ↓
reconnecting ← reconnecting ← reconnecting ← reconnecting ← reconnecting
```

### AudioChunk
Representa un fragmento de audio recibido del cliente.

**Fields**:
- `chunk_id` (string): Identificador único del chunk
- `session_id` (string): Referencia a la sesión
- `sequence_number` (integer): Número de secuencia del chunk
- `timestamp` (datetime): Timestamp de captura en cliente
- `mime_type` (string): Tipo MIME del audio (audio/webm;codecs=opus)
- `audio_data` (bytes): Datos de audio en base64
- `size_bytes` (integer): Tamaño del chunk en bytes
- `received_at` (datetime): Timestamp de recepción en servidor

**Validation Rules**:
- `chunk_id` debe ser string no vacío
- `sequence_number` debe ser >= 1
- `mime_type` debe ser tipo MIME válido de audio
- `size_bytes` debe ser > 0 y <= 1MB (límite de chunk)
- `audio_data` debe ser base64 válido

**Relationships**:
- Pertenece a una `StreamingSession` (many-to-one)

### TranscriptionResult
Representa un resultado de transcripción (parcial o final).

**Fields**:
- `result_id` (string): Identificador único del resultado
- `session_id` (string): Referencia a la sesión
- `sequence_number` (integer): Número de secuencia del chunk procesado
- `result_type` (enum): Tipo de resultado
  - `partial`: Resultado parcial (puede cambiar)
  - `final`: Resultado final (confirmado)
- `text_content` (string): Texto transcrito
- `confidence` (float): Nivel de confianza (0.0-1.0)
- `start_time` (float): Tiempo de inicio en audio (segundos)
- `end_time` (float): Tiempo de fin en audio (segundos)
- `language` (string): Idioma detectado
- `processing_time_ms` (integer): Tiempo de procesamiento en milisegundos
- `created_at` (datetime): Timestamp de creación

**Validation Rules**:
- `result_id` debe ser string no vacío
- `result_type` debe ser 'partial' o 'final'
- `text_content` debe ser string (puede estar vacío)
- `confidence` debe estar entre 0.0 y 1.0
- `start_time` y `end_time` deben ser >= 0
- `processing_time_ms` debe ser >= 0

**Relationships**:
- Pertenece a una `StreamingSession` (many-to-one)
- Relacionado con un `AudioChunk` por sequence_number

### SessionMetrics
Representa métricas de rendimiento de una sesión.

**Fields**:
- `metrics_id` (string): Identificador único de las métricas
- `session_id` (string): Referencia a la sesión
- `timestamp` (datetime): Timestamp de la medición
- `latency_ms` (integer): Latencia actual en milisegundos
- `chunks_processed` (integer): Chunks procesados hasta el momento
- `chunks_pending` (integer): Chunks pendientes en cola
- `cpu_usage_percent` (float): Uso de CPU actual
- `memory_usage_mb` (float): Uso de memoria en MB
- `gpu_available` (boolean): GPU disponible para procesamiento
- `audio_quality_score` (float): Puntuación de calidad de audio (0.0-1.0)

**Validation Rules**:
- `metrics_id` debe ser string no vacío
- `latency_ms` debe ser >= 0
- `chunks_processed` y `chunks_pending` deben ser >= 0
- `cpu_usage_percent` debe estar entre 0.0 y 100.0
- `memory_usage_mb` debe ser >= 0
- `audio_quality_score` debe estar entre 0.0 y 1.0

**Relationships**:
- Pertenece a una `StreamingSession` (many-to-one)

## Data Flow

### 1. Inicio de Sesión
```
Cliente → WebSocket connect → Servidor crea StreamingSession
Servidor → WebSocket emit('session_created') → Cliente
```

### 2. Envío de Audio
```
Cliente captura audio → MediaRecorder → AudioChunk
Cliente → WebSocket emit('audio_chunk') → Servidor
Servidor → Cola asíncrona → faster-whisper → TranscriptionResult
Servidor → WebSocket emit('transcription_partial') → Cliente
```

### 3. Finalización de Sesión
```
Cliente → WebSocket emit('stop_recording') → Servidor
Servidor → Procesar chunks pendientes → Consolidar resultados
Servidor → Guardar transcripción final → Historial local
Servidor → WebSocket emit('session_completed') → Cliente
```

## Constraints

### Límites de Sesión
- Duración máxima: 60 minutos (3600 segundos)
- Chunks máximos por sesión: 180,000 (1 chunk/segundo × 60min × 60seg)
- Tamaño máximo por chunk: 1MB

### Límites de Recursos
- RAM mínima requerida: 8GB
- CPU: Procesamiento asíncrono sin bloqueo
- Almacenamiento: Solo texto final, no audio persistente

### Límites de Red
- Timeout de conexión: 30 segundos
- Reintentos de reconexión: 5 máximo
- Backoff exponencial: 1s, 2s, 4s, 8s, 16s

## State Management

### Cliente
- Estado de conexión WebSocket
- Estado de grabación (idle, recording, paused)
- Buffer de chunks pendientes de envío
- Cache de resultados parciales

### Servidor
- Pool de sesiones activas
- Cola de procesamiento por sesión
- Cache de modelos faster-whisper
- Métricas de rendimiento en tiempo real

## Data Persistence

### Transitorio (Memoria)
- `StreamingSession` activas
- `AudioChunk` en cola de procesamiento
- `TranscriptionResult` parciales
- `SessionMetrics` en tiempo real

### Persistente (Archivos)
- Transcripción final consolidada (formato existente)
- Logs de sesión (sin contenido sensible)
- Métricas agregadas de rendimiento

### Eliminación Automática
- Audio chunks eliminados inmediatamente tras procesamiento
- Sesiones eliminadas tras completarse
- Métricas antiguas purgadas periódicamente
- Archivos temporales limpiados al cerrar aplicación
