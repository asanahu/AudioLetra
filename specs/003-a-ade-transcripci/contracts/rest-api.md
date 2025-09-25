# REST API Contract: Transcripción en Streaming

**Feature**: Transcripción en Streaming (Tiempo Real)  
**Date**: 2025-01-27  
**Branch**: `003-a-ade-transcripci`

## Base URL
```
http://localhost:5000/api/streaming
```

## Endpoints

### POST /api/streaming/sessions
Crea una nueva sesión de transcripción en streaming.

**Request**:
```json
{
  "language": "string (optional, default: es)",
  "model_size": "string (optional, default: base)",
  "duration_limit": "integer (optional, default: 3600)"
}
```

**Response** (201 Created):
```json
{
  "session_id": "string (UUID)",
  "status": "string (created)",
  "websocket_url": "string (ws://localhost:5000/socket.io/)",
  "config": {
    "language": "string",
    "model_size": "string",
    "duration_limit": "integer",
    "max_chunk_size": "integer (1048576)",
    "supported_formats": ["audio/webm;codecs=opus"]
  },
  "created_at": "string (ISO 8601)"
}
```

**Error Responses**:
- `400 Bad Request`: Parámetros inválidos
- `429 Too Many Requests`: Límite de sesiones concurrentes excedido
- `500 Internal Server Error`: Error del servidor

### GET /api/streaming/sessions/{session_id}
Obtiene información de una sesión específica.

**Response** (200 OK):
```json
{
  "session_id": "string (UUID)",
  "status": "string",
  "created_at": "string (ISO 8601)",
  "last_activity": "string (ISO 8601)",
  "duration_limit": "integer",
  "audio_chunks_received": "integer",
  "partial_text": "string",
  "confirmed_text": "string",
  "metadata": {
    "language": "string",
    "model_size": "string",
    "total_duration_ms": "integer",
    "average_latency_ms": "number"
  }
}
```

**Error Responses**:
- `404 Not Found`: Sesión no encontrada
- `500 Internal Server Error`: Error del servidor

### DELETE /api/streaming/sessions/{session_id}
Finaliza y elimina una sesión.

**Response** (200 OK):
```json
{
  "session_id": "string (UUID)",
  "status": "string (deleted)",
  "final_text": "string",
  "total_chunks": "integer",
  "total_duration_ms": "integer",
  "average_latency_ms": "number",
  "saved_to_history": "boolean",
  "file_path": "string (optional)"
}
```

**Error Responses**:
- `404 Not Found`: Sesión no encontrada
- `500 Internal Server Error`: Error del servidor

### GET /api/streaming/sessions/{session_id}/metrics
Obtiene métricas de rendimiento de una sesión.

**Response** (200 OK):
```json
{
  "session_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "current_latency_ms": "integer",
  "average_latency_ms": "number",
  "chunks_processed": "integer",
  "chunks_pending": "integer",
  "cpu_usage_percent": "number",
  "memory_usage_mb": "number",
  "gpu_available": "boolean",
  "audio_quality_score": "number",
  "warning_threshold_exceeded": "boolean"
}
```

### POST /api/streaming/sessions/{session_id}/save
Guarda la transcripción final en el historial local.

**Response** (200 OK):
```json
{
  "session_id": "string (UUID)",
  "status": "string (saved)",
  "file_path": "string",
  "file_size": "integer",
  "transcription_length": "integer",
  "saved_at": "string (ISO 8601)"
}
```

**Error Responses**:
- `404 Not Found`: Sesión no encontrada
- `400 Bad Request`: Sesión no finalizada
- `500 Internal Server Error`: Error al guardar

### GET /api/streaming/status
Obtiene el estado general del servicio de streaming.

**Response** (200 OK):
```json
{
  "service_status": "string (running|maintenance|error)",
  "active_sessions": "integer",
  "max_concurrent_sessions": "integer",
  "system_resources": {
    "cpu_usage_percent": "number",
    "memory_usage_mb": "number",
    "memory_available_mb": "number",
    "gpu_available": "boolean"
  },
  "supported_models": ["tiny", "base", "small", "medium", "large"],
  "supported_languages": ["es", "en", "fr", "de", "it"],
  "version": "string",
  "uptime_seconds": "integer"
}
```

## WebSocket Connection

### Connection URL
```
ws://localhost:5000/socket.io/?session_id={session_id}
```

### Connection Parameters
- `session_id`: UUID de la sesión (requerido)
- `transport`: websocket (por defecto)
- `namespace`: / (por defecto)

### Authentication
No se requiere autenticación para sesiones locales.

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)",
    "timestamp": "string (ISO 8601)",
    "request_id": "string (UUID)"
  }
}
```

### Error Codes
- `INVALID_REQUEST`: Solicitud malformada
- `INVALID_SESSION`: Sesión no válida
- `SESSION_NOT_FOUND`: Sesión no encontrada
- `SESSION_EXPIRED`: Sesión expirada
- `RATE_LIMIT_EXCEEDED`: Límite de velocidad excedido
- `RESOURCE_UNAVAILABLE`: Recurso no disponible
- `PROCESSING_ERROR`: Error en procesamiento
- `STORAGE_ERROR`: Error de almacenamiento
- `SYSTEM_ERROR`: Error del sistema

## Rate Limiting

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Limits
- Creación de sesiones: 10 por minuto por IP
- Consultas de sesión: 100 por minuto por IP
- Métricas: 60 por minuto por sesión

## CORS Configuration

### Allowed Origins
```
http://localhost:5000
http://127.0.0.1:5000
```

### Allowed Methods
```
GET, POST, DELETE, OPTIONS
```

### Allowed Headers
```
Content-Type, Authorization, X-Requested-With
```

## Content Types

### Request Content Types
- `application/json`: Para endpoints REST
- `application/octet-stream`: Para uploads de audio (no usado en streaming)

### Response Content Types
- `application/json`: Para todas las respuestas JSON
- `text/plain`: Para respuestas de error simples

## Validation Rules

### Session Creation
- `language`: Debe ser código ISO 639-1 válido
- `model_size`: Debe ser uno de los modelos soportados
- `duration_limit`: Debe estar entre 60 y 3600 segundos

### Session ID
- Debe ser UUID v4 válido
- Debe existir en la base de datos de sesiones
- No debe estar expirado

### Metrics
- Timestamp debe ser ISO 8601 válido
- Valores numéricos deben ser >= 0
- Porcentajes deben estar entre 0.0 y 100.0

## Security Considerations

### Input Validation
- Validar todos los parámetros de entrada
- Sanitizar strings para prevenir inyección
- Validar tamaños de datos
- Verificar formatos de UUID

### Rate Limiting
- Implementar límites por IP
- Implementar límites por sesión
- Implementar backoff exponencial
- Monitorear patrones de abuso

### Data Protection
- No logear contenido sensible
- Encriptar conexiones (HTTPS/WSS en producción)
- Limpiar datos temporales
- Implementar timeouts de sesión

## Testing

### Contract Tests
- Validar esquemas JSON
- Probar códigos de error
- Verificar headers de respuesta
- Validar timeouts

### Integration Tests
- Probar flujo completo de sesión
- Verificar persistencia de datos
- Probar manejo de errores
- Validar métricas en tiempo real
