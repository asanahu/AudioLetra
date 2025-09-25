# Research: Transcripción en Streaming (Tiempo Real)

**Feature**: Transcripción en Streaming (Tiempo Real)  
**Date**: 2025-01-27  
**Branch**: `003-a-ade-transcripci`

## Research Tasks & Findings

### 1. WebSockets vs Server-Sent Events (SSE)

**Task**: Evaluar tecnologías para comunicación en tiempo real entre cliente y servidor

**Decision**: WebSockets con Flask-SocketIO

**Rationale**:
- WebSockets proporcionan comunicación bidireccional necesaria para enviar audio del cliente al servidor
- SSE es unidireccional (solo servidor → cliente), no permite envío de audio
- Flask-SocketIO integra perfectamente con la arquitectura Flask existente
- Soporte nativo para reconexión automática y manejo de eventos

**Alternatives considered**:
- Server-Sent Events: Rechazado por ser unidireccional
- HTTP Polling: Rechazado por latencia e ineficiencia
- WebRTC: Rechazado por complejidad innecesaria para este caso de uso

### 2. Captura de Audio en Cliente

**Task**: Investigar APIs para captura de audio en navegadores web

**Decision**: MediaRecorder API con intervalos de 200-500ms

**Rationale**:
- MediaRecorder API es estándar web y ampliamente soportado
- Permite captura en chunks pequeños para baja latencia
- Formato webm/opus es eficiente y soportado por faster-whisper
- Intervalos de 200-500ms balancean latencia vs overhead de red

**Alternatives considered**:
- Web Audio API: Más complejo, innecesario para este caso de uso
- getUserMedia directo: Requiere más procesamiento manual
- Chunks más pequeños (<200ms): Rechazado por overhead de red excesivo

### 3. Procesamiento Incremental en Servidor

**Task**: Diseñar estrategia para procesamiento de audio en chunks con faster-whisper

**Decision**: Cola asíncrona por sesión con procesamiento incremental

**Rationale**:
- Cola asíncrona permite manejar múltiples sesiones concurrentes
- Procesamiento incremental mantiene contexto entre chunks
- Decodificación a PCM permite alimentar faster-whisper eficientemente
- Ventana deslizante para estabilizar resultados parciales vs finales

**Alternatives considered**:
- Procesamiento síncrono: Rechazado por bloqueo de otras sesiones
- Procesamiento por lotes: Rechazado por aumento de latencia
- Sin contexto entre chunks: Rechazado por pérdida de calidad

### 4. Estrategia de Reconexión

**Task**: Diseñar sistema robusto de reconexión ante fallos de red

**Decision**: Reconexión automática con backoff exponencial

**Rationale**:
- Backoff exponencial evita saturar el servidor en reconexiones masivas
- Reconexión automática mejora experiencia de usuario
- Manejo de estado de sesión permite recuperación sin pérdida de datos
- Timeouts razonables evitan conexiones colgadas

**Alternatives considered**:
- Reconexión inmediata: Rechazado por posible saturación
- Reconexión manual: Rechazado por degradación de UX
- Sin reconexión: Rechazado por fragilidad del sistema

### 5. Medición de Latencia

**Task**: Implementar sistema de medición de latencia en tiempo real

**Decision**: Timestamp en envío de chunk y medición hasta primer parcial

**Rationale**:
- Medición end-to-end captura latencia real del sistema completo
- Timestamp permite calcular latencia precisa
- Medición hasta primer parcial refleja experiencia del usuario
- Contador visible ayuda al usuario a entender rendimiento

**Alternatives considered**:
- Medición solo de red: Incompleta, no incluye procesamiento
- Medición solo de procesamiento: Incompleta, no incluye red
- Sin medición: Rechazado por falta de visibilidad del rendimiento

### 6. Manejo de Recursos y Memoria

**Task**: Diseñar estrategia para manejo eficiente de memoria y recursos

**Decision**: Buffers en memoria con purga automática al finalizar sesión

**Rationale**:
- Buffers en memoria proporcionan acceso rápido
- Purga automática previene acumulación de memoria
- Límite de 60 minutos evita sesiones excesivamente largas
- Validación de 8GB RAM mínimo asegura recursos suficientes

**Alternatives considered**:
- Persistencia en disco: Rechazado por latencia y complejidad
- Sin límites de tiempo: Rechazado por riesgo de agotamiento de memoria
- Buffers fijos: Rechazado por inflexibilidad

### 7. Protocolo de Eventos

**Task**: Diseñar protocolo de comunicación entre cliente y servidor

**Decision**: Eventos JSON estructurados con tipos específicos

**Rationale**:
- JSON es estándar y fácil de procesar
- Eventos tipados permiten manejo específico por tipo
- Secuencia de eventos permite orden y confirmación
- Metadata permite trazabilidad y debugging

**Alternatives considered**:
- Protocolo binario: Rechazado por complejidad
- Eventos sin estructura: Rechazado por falta de tipado
- HTTP REST: Rechazado por no ser tiempo real

### 8. Integración con UI Existente

**Task**: Diseñar integración con la UI actual de AudioLetra

**Decision**: Nueva plantilla stream.html con estilos consistentes

**Rationale**:
- Nueva plantilla permite funcionalidad específica sin afectar existente
- Estilos consistentes mantienen coherencia visual
- JavaScript modular permite reutilización
- Navegación integrada mantiene flujo de usuario natural

**Alternatives considered**:
- Modificar plantilla existente: Rechazado por complejidad
- Framework nuevo: Rechazado por violar principios constitucionales
- UI completamente separada: Rechazado por fragmentar experiencia

## Technical Decisions Summary

| Componente | Decisión | Justificación Principal |
|------------|----------|------------------------|
| Comunicación | WebSockets + Flask-SocketIO | Bidireccional, integración Flask |
| Captura Audio | MediaRecorder API | Estándar web, chunks pequeños |
| Procesamiento | Cola asíncrona + faster-whisper | Concurrente, incremental |
| Reconexión | Backoff exponencial | Robusto, no saturación |
| Latencia | Timestamp end-to-end | Medición completa |
| Memoria | Buffers + purga automática | Eficiente, sin acumulación |
| Protocolo | Eventos JSON tipados | Estructurado, trazable |
| UI | Nueva plantilla integrada | Coherente, modular |

## Dependencies Research

### Flask-SocketIO
- **Versión**: 5.x (compatible con Python 3.11+)
- **Características**: Reconexión automática, eventos tipados, soporte WebSocket/HTTP
- **Integración**: Compatible con Flask existente, no requiere cambios arquitectónicos

### MediaRecorder API
- **Soporte**: Chrome 47+, Edge 79+, Firefox 25+
- **Formatos**: webm/opus (recomendado), mp4/aac
- **Limitaciones**: Requiere HTTPS en producción, permisos de micrófono

### faster-whisper
- **Versión**: Última estable compatible con Python 3.11+
- **Modelos**: tiny, base, small, medium, large
- **GPU**: Soporte automático CUDA/ROCm
- **Streaming**: Soporte para procesamiento incremental

## Risk Assessment

### Riesgos Técnicos Identificados
1. **Latencia alta**: Mitigado con chunks pequeños y procesamiento optimizado
2. **Memoria insuficiente**: Mitigado con límite de 8GB RAM y purga automática
3. **Compatibilidad navegador**: Mitigado con validación de APIs disponibles
4. **Reconexión fallida**: Mitigado con fallback a modo por bloques

### Riesgos de Implementación
1. **Complejidad de sincronización**: Eventos ordenados y secuenciales
2. **Manejo de estado**: Estado consistente entre cliente y servidor
3. **Rendimiento**: Optimización de colas y procesamiento asíncrono

## Next Steps
- Phase 1: Diseño detallado de contratos y data model
- Validación de decisiones técnicas con implementación de prueba
- Definición de métricas de rendimiento específicas
