# WebSocket Events Contract: Transcripción en Streaming

**Feature**: Transcripción en Streaming (Tiempo Real)  
**Date**: 2025-01-27  
**Branch**: `003-a-ade-transcripci`

## Event Types

### Cliente → Servidor

#### `client:audio_chunk`
Envía un fragmento de audio para transcripción.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "sequence_number": "integer (>=1)",
  "timestamp": "string (ISO 8601)",
  "mime_type": "string (audio/webm;codecs=opus)",
  "audio_data": "string (base64)",
  "size_bytes": "integer (>0, <=1MB)"
}
```

**Validation**:
- `session_id` debe ser UUID válido
- `sequence_number` debe incrementar secuencialmente
- `timestamp` debe ser ISO 8601 válido
- `mime_type` debe ser tipo MIME de audio soportado
- `audio_data` debe ser base64 válido
- `size_bytes` debe coincidir con tamaño real del audio

**Response**: `server:ack` con `sequence_number`

#### `client:control`
Envía comandos de control de la sesión.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "action": "string (pause|resume|stop)",
  "timestamp": "string (ISO 8601)"
}
```

**Validation**:
- `session_id` debe ser UUID válido
- `action` debe ser uno de: pause, resume, stop
- `timestamp` debe ser ISO 8601 válido

**Response**: `server:control_ack` con `action` confirmado

#### `client:ping`
Mantiene la conexión activa y mide latencia.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "client_time": "integer (milliseconds)"
}
```

**Response**: `server:pong` con timestamps para cálculo de latencia

### Servidor → Cliente

#### `server:session_created`
Confirma la creación de una nueva sesión.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "status": "string (connected)",
  "server_time": "string (ISO 8601)",
  "duration_limit": "integer (3600)",
  "config": {
    "max_chunk_size": "integer (1048576)",
    "supported_formats": ["audio/webm;codecs=opus"],
    "reconnection_enabled": "boolean (true)"
  }
}
```

#### `server:ack`
Confirma recepción de un chunk de audio.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "sequence_number": "integer",
  "received_at": "string (ISO 8601)",
  "queue_size": "integer (>=0)"
}
```

#### `server:transcription_partial`
Envía resultado de transcripción parcial.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "sequence_number": "integer",
  "result_type": "string (partial)",
  "text": "string",
  "confidence": "number (0.0-1.0)",
  "start_time": "number (seconds)",
  "end_time": "number (seconds)",
  "language": "string",
  "processing_time_ms": "integer"
}
```

#### `server:transcription_final`
Envía resultado de transcripción final confirmado.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "sequence_number": "integer",
  "result_type": "string (final)",
  "text": "string",
  "confidence": "number (0.0-1.0)",
  "start_time": "number (seconds)",
  "end_time": "number (seconds)",
  "language": "string",
  "processing_time_ms": "integer"
}
```

#### `server:status`
Informa cambios de estado de la sesión.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "status": "string (connected|recording|paused|reconnecting|finalizing|completed|error)",
  "timestamp": "string (ISO 8601)",
  "message": "string (optional)",
  "can_reconnect": "boolean"
}
```

#### `server:metrics`
Envía métricas de rendimiento en tiempo real.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "latency_ms": "integer",
  "chunks_processed": "integer",
  "chunks_pending": "integer",
  "cpu_usage_percent": "number (0.0-100.0)",
  "memory_usage_mb": "number (>=0)",
  "gpu_available": "boolean",
  "audio_quality_score": "number (0.0-1.0)",
  "warning_threshold_exceeded": "boolean"
}
```

#### `server:control_ack`
Confirma recepción de comando de control.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "action": "string (pause|resume|stop)",
  "status": "string",
  "timestamp": "string (ISO 8601)"
}
```

#### `server:pong`
Responde a ping para medición de latencia.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "client_time": "integer (milliseconds)",
  "server_time": "integer (milliseconds)",
  "round_trip_ms": "integer"
}
```

#### `server:error`
Reporta errores en la sesión.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "error_code": "string",
  "error_message": "string",
  "timestamp": "string (ISO 8601)",
  "recoverable": "boolean",
  "suggested_action": "string (optional)"
}
```

#### `server:session_completed`
Informa finalización exitosa de la sesión.

**Payload**:
```json
{
  "session_id": "string (UUID)",
  "status": "string (completed)",
  "final_text": "string",
  "total_chunks": "integer",
  "total_duration_ms": "integer",
  "average_latency_ms": "number",
  "saved_to_history": "boolean",
  "file_path": "string (optional)"
}
```

## Error Codes

### Códigos de Error del Servidor
- `INVALID_SESSION`: Sesión no válida o expirada
- `CHUNK_TOO_LARGE`: Chunk de audio excede tamaño máximo
- `INVALID_FORMAT`: Formato de audio no soportado
- `SEQUENCE_MISMATCH`: Número de secuencia incorrecto
- `SESSION_EXPIRED`: Sesión expirada por límite de tiempo
- `MEMORY_LIMIT`: Límite de memoria alcanzado
- `PROCESSING_ERROR`: Error en procesamiento de audio
- `CONNECTION_LOST`: Pérdida de conexión
- `RATE_LIMIT`: Límite de velocidad excedido
- `HARDWARE_ERROR`: Error de hardware (GPU/CPU)

## Rate Limiting

### Límites por Sesión
- Chunks por segundo: 10 máximo
- Tamaño por chunk: 1MB máximo
- Tamaño total por sesión: 100MB máximo
- Duración máxima: 60 minutos

### Límites Globales
- Sesiones concurrentes: 10 máximo
- Conexiones por IP: 5 máximo
- Reconexiones por sesión: 5 máximo

## Timeouts

### Cliente
- Timeout de conexión: 30 segundos
- Timeout de respuesta: 10 segundos
- Intervalo de ping: 30 segundos
- Timeout de reconexión: 60 segundos

### Servidor
- Timeout de sesión inactiva: 5 minutos
- Timeout de procesamiento: 30 segundos
- Timeout de cola: 2 segundos
- Timeout de limpieza: 1 hora

## Reconnection Strategy

### Cliente
1. Detectar pérdida de conexión
2. Esperar 1 segundo
3. Intentar reconexión
4. Si falla, esperar 2s, 4s, 8s, 16s (backoff exponencial)
5. Máximo 5 intentos
6. Si todos fallan, mostrar error y fallback a modo por bloques

### Servidor
1. Detectar cliente desconectado
2. Mantener sesión activa por 5 minutos
3. Pausar procesamiento de chunks
4. Al reconectar, sincronizar estado
5. Reanudar procesamiento desde último chunk confirmado

## Message Ordering

### Garantías
- `server:ack` siempre se envía después de `client:audio_chunk`
- `server:transcription_partial` puede enviarse múltiples veces para el mismo chunk
- `server:transcription_final` se envía una vez por chunk
- `server:status` se envía antes de cambios de estado
- `server:metrics` se envía periódicamente (cada 5 segundos)

### Secuencia Típica
```
client:audio_chunk → server:ack → server:transcription_partial → server:transcription_final
```

## Security Considerations

### Validación
- Validar UUID de sesión en cada mensaje
- Verificar secuencia numérica para prevenir ataques
- Validar tamaño y formato de chunks
- Rate limiting por IP y sesión

### Privacidad
- No logear contenido de audio o texto
- Eliminar chunks inmediatamente tras procesamiento
- No persistir metadatos sensibles
- Encriptar conexión WebSocket (WSS en producción)
