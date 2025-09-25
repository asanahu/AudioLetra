# Streaming Lifecycle: Transcripción en Tiempo Real

**Feature**: Transcripción en Streaming (Tiempo Real)  
**Date**: 2025-01-27  
**Branch**: `003-a-ade-transcripci`

## Diagrama de Estados

```mermaid
stateDiagram-v2
    [*] --> Connecting
    Connecting --> Connected : WebSocket establecido
    Connecting --> Error : Fallo de conexión
    
    Connected --> Recording : Usuario inicia grabación
    Connected --> Error : Fallo de autenticación
    
    Recording --> Paused : Usuario pausa
    Recording --> Reconnecting : Pérdida de conexión
    Recording --> Finalizing : Usuario detiene
    Recording --> Error : Error de procesamiento
    
    Paused --> Recording : Usuario reanuda
    Paused --> Reconnecting : Pérdida de conexión
    Paused --> Finalizing : Usuario detiene
    Paused --> Error : Error de sistema
    
    Reconnecting --> Recording : Reconexión exitosa
    Reconnecting --> Error : Fallo de reconexión
    
    Finalizing --> Completed : Guardado exitoso
    Finalizing --> Error : Error de guardado
    
    Completed --> [*]
    Error --> [*]
```

## Secuencia de Eventos

### 1. Inicio de Sesión

```mermaid
sequenceDiagram
    participant C as Cliente
    participant S as Servidor
    participant W as WebSocket
    participant Q as Cola Procesamiento
    
    C->>S: POST /api/streaming/sessions
    S->>S: Crear StreamingSession
    S->>C: 201 Created + session_id
    
    C->>W: Conectar WebSocket
    W->>S: Connection establecida
    S->>Q: Inicializar cola de sesión
    S->>C: server:session_created
    C->>C: Estado: "Conectado"
```

### 2. Grabación de Audio

```mermaid
sequenceDiagram
    participant C as Cliente
    participant S as Servidor
    participant Q as Cola Procesamiento
    participant W as faster-whisper
    
    C->>C: MediaRecorder captura audio
    C->>C: Chunk 200-500ms
    C->>S: client:audio_chunk
    S->>S: Validar chunk
    S->>Q: Agregar a cola
    S->>C: server:ack
    
    Q->>W: Procesar chunk
    W->>Q: Resultado parcial
    Q->>S: Emitir resultado
    S->>C: server:transcription_partial
    
    W->>Q: Resultado final
    Q->>S: Emitir resultado
    S->>C: server:transcription_final
```

### 3. Reconexión Automática

```mermaid
sequenceDiagram
    participant C as Cliente
    participant S as Servidor
    participant N as Red
    
    N->>C: Pérdida de conexión
    C->>C: Detectar desconexión
    C->>C: Estado: "Reconectando"
    
    loop Backoff exponencial
        C->>S: Intentar reconexión
        alt Conexión exitosa
            S->>C: server:status (connected)
            C->>C: Estado: "Conectado"
        else Fallo
            C->>C: Esperar (1s, 2s, 4s, 8s, 16s)
        end
    end
    
    alt Reconexión exitosa
        C->>C: Estado: "Conectado"
        S->>C: Sincronizar estado
    else Fallo total
        C->>C: Estado: "Error"
        C->>C: Fallback a modo por bloques
    end
```

### 4. Finalización de Sesión

```mermaid
sequenceDiagram
    participant C as Cliente
    participant S as Servidor
    participant Q as Cola Procesamiento
    participant F as Sistema Archivos
    
    C->>S: client:control (stop)
    S->>Q: Finalizar procesamiento
    Q->>Q: Procesar chunks pendientes
    Q->>S: Resultados finales
    S->>C: server:status (finalizing)
    
    S->>F: Consolidar texto final
    F->>S: Archivo guardado
    S->>S: Limpiar recursos
    S->>C: server:session_completed
    C->>C: Estado: "Completado"
    
    S->>S: Eliminar sesión
    S->>S: Purga de memoria
```

## Flujo de Datos

### Captura de Audio (Cliente)

```
Micrófono → MediaRecorder → Chunk (200-500ms) → WebSocket → Servidor
```

**Detalles**:
- Formato: webm/opus
- Frecuencia: 16kHz
- Canales: Mono
- Tamaño: < 1MB por chunk

### Procesamiento (Servidor)

```
WebSocket → Validación → Cola Asíncrona → faster-whisper → Resultado → WebSocket
```

**Detalles**:
- Cola por sesión
- Procesamiento incremental
- Contexto mantenido entre chunks
- Resultados parciales y finales

### Almacenamiento

```
Resultado Final → Consolidación → Archivo Local → Historial
```

**Detalles**:
- Formato: Mismo que transcripciones existentes
- Ubicación: output/transcripcion_timestamp.txt
- Metadatos: Timestamp, duración, latencia promedio

## Manejo de Errores

### Tipos de Error

#### Error de Conexión
- **Causa**: Pérdida de red, servidor inaccesible
- **Acción**: Reconexión automática con backoff
- **Fallback**: Modo por bloques si falla

#### Error de Procesamiento
- **Causa**: faster-whisper falla, audio corrupto
- **Acción**: Reintentar chunk, saltar si persiste
- **Recuperación**: Continuar con siguiente chunk

#### Error de Memoria
- **Causa**: RAM insuficiente, sesión muy larga
- **Acción**: Guardado forzado, limpieza de recursos
- **Prevención**: Límite de 60 minutos, monitoreo de RAM

#### Error de Validación
- **Causa**: Chunk malformado, secuencia incorrecta
- **Acción**: Rechazar chunk, solicitar reenvío
- **Recuperación**: Sincronización de secuencia

### Estrategias de Recuperación

#### Recuperación Automática
- Reconexión con backoff exponencial
- Reintento de chunks fallidos
- Limpieza automática de recursos
- Guardado forzado en límites

#### Recuperación Manual
- Botón de reconexión manual
- Opción de reiniciar sesión
- Fallback a modo por bloques
- Exportación manual de transcripción

## Métricas y Monitoreo

### Métricas en Tiempo Real

#### Latencia
- Medición: Timestamp de envío → Recepción de parcial
- Objetivo: < 2 segundos
- Advertencia: > 3 segundos

#### Rendimiento
- CPU: Uso porcentual
- RAM: Uso en MB
- GPU: Disponibilidad y uso
- Red: Chunks por segundo

#### Calidad
- Confianza de transcripción
- Calidad de audio
- Pérdida de chunks
- Errores de procesamiento

### Alertas Automáticas

#### Latencia Alta
- Trigger: > 3 segundos
- Acción: Advertencia visual, optimización automática

#### Memoria Baja
- Trigger: < 1GB disponible
- Acción: Limpieza de recursos, advertencia

#### Conexión Inestable
- Trigger: Múltiples reconexiones
- Acción: Sugerir modo por bloques

## Optimizaciones

### Optimización de Latencia

#### Cliente
- Chunks pequeños (200-500ms)
- Compresión eficiente (opus)
- Envío asíncrono
- Cache de resultados

#### Servidor
- Procesamiento asíncrono
- Cola optimizada
- Modelo apropiado (base/small)
- GPU cuando disponible

### Optimización de Recursos

#### Memoria
- Buffers limitados
- Purga automática
- Límites de sesión
- Monitoreo continuo

#### CPU
- Procesamiento incremental
- Modelos eficientes
- Paralelización cuando posible
- Throttling inteligente

## Consideraciones de Seguridad

### Validación de Entrada
- UUID de sesión válido
- Tamaño de chunk limitado
- Formato de audio válido
- Secuencia numérica correcta

### Protección de Datos
- No persistencia de audio
- Limpieza automática
- Logs sin contenido sensible
- Conexiones encriptadas (WSS)

### Rate Limiting
- Chunks por segundo
- Sesiones concurrentes
- Reconexiones por sesión
- Límites por IP
