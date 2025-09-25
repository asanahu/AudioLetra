# Feature Specification: Transcripción en Streaming (Tiempo Real)

**Feature Branch**: `003-a-ade-transcripci`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "Añade transcripción en streaming (tiempo real) a AudioLetra"

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## Clarifications

### Session 2025-01-27
- Q: ¿Cuál debe ser el límite máximo de duración para una sesión de transcripción en streaming antes de forzar un guardado automático? → A: 60 minutos máximo
- Q: ¿Cómo debe comportarse el sistema cuando el usuario tiene AudioLetra abierto en múltiples pestañas o ventanas simultáneamente? → A: Solo una pestaña puede hacer streaming activo, las demás se desactivan
- Q: ¿Cuál debe ser el umbral máximo de latencia aceptable antes de mostrar una advertencia al usuario? → A: 3 segundos máximo
- Q: ¿En qué formato debe guardarse la transcripción final en el historial local? → A: Mismo formato que transcripciones existentes
- Q: ¿Cuáles deben ser los requisitos mínimos de hardware para soportar transcripción en streaming? → A: 8GB RAM mínimo

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
Como usuario de AudioLetra, quiero ver mi transcripción aparecer casi en tiempo real mientras hablo, para tener una experiencia más fluida y natural que me permita verificar inmediatamente si mis palabras están siendo capturadas correctamente.

### Acceptance Scenarios
1. **Given** que el usuario accede a la vista "Streaming", **When** inicia la grabación, **Then** debe ver un indicador "Conectado/Escuchando" y comenzar a aparecer texto en menos de 2 segundos
2. **Given** que el usuario está hablando durante la transcripción en streaming, **When** el sistema procesa el audio, **Then** debe mostrar texto parcial en gris que se refina progresivamente y texto confirmado en negro
3. **Given** que hay una interrupción de red temporal, **When** se pierde la conexión, **Then** debe mostrar "Reconectando..." y recuperar la conexión automáticamente
4. **Given** que el usuario finaliza la grabación, **When** presiona "Guardar resultado", **Then** debe consolidar la transcripción final en el historial local de AudioLetra
5. **Given** que el sistema de streaming falla o no está disponible, **When** el usuario intenta usar la funcionalidad, **Then** debe caer automáticamente al flujo existente por bloques con una notificación al usuario

### Edge Cases
- ¿Qué pasa cuando el usuario habla durante más de 10 minutos continuos?
- ¿Cómo maneja el sistema cuando el micrófono se desconecta durante la grabación?
- ¿Qué ocurre si la conexión de red es muy inestable con múltiples desconexiones?
- ¿Cómo se comporta el sistema con audio de muy baja calidad o ruido excesivo?
- ¿Qué pasa si el usuario cambia de pestaña o minimiza la ventana del navegador?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Sistema DEBE proporcionar una nueva vista "Streaming" accesible desde la navegación principal
- **FR-002**: Sistema DEBE mostrar texto de transcripción en menos de 2 segundos después de que el usuario comience a hablar
- **FR-003**: Sistema DEBE distinguir visualmente entre texto parcial (gris) y texto confirmado (negro)
- **FR-004**: Sistema DEBE mostrar indicadores de estado claros: "Conectado/Escuchando", "Reconectando...", "Pausado"
- **FR-005**: Sistema DEBE incluir un contador de latencia en milisegundos visible para el usuario
- **FR-006**: Sistema DEBE permitir pausar y reanudar la transcripción en streaming
- **FR-007**: Sistema DEBE manejar reconexiones automáticas cuando se pierde la conexión temporalmente
- **FR-008**: Sistema DEBE consolidar la transcripción final en el historial local al finalizar
- **FR-013**: Sistema DEBE forzar guardado automático cuando una sesión alcance 60 minutos de duración
- **FR-014**: Sistema DEBE permitir solo una sesión de streaming activa por navegador, desactivando automáticamente otras pestañas/ventanas
- **FR-015**: Sistema DEBE mostrar advertencia de latencia alta cuando el contador supere 3 segundos
- **FR-016**: Sistema DEBE guardar las transcripciones en streaming usando el mismo formato que las transcripciones existentes del sistema
- **FR-017**: Sistema DEBE requerir mínimo 8GB de RAM para funcionar correctamente en modo streaming

### Non-Functional Requirements
- **NFR-001**: Sistema DEBE funcionar con mínimo 8GB RAM para transcripción en streaming
- **NFR-002**: Sistema DEBE mostrar advertencia cuando latencia supere 3 segundos
- **NFR-003**: Sistema DEBE limitar sesiones a máximo 60 minutos con guardado automático
- **FR-009**: Sistema DEBE caer automáticamente al flujo por bloques si el streaming falla, notificando al usuario
- **FR-010**: Sistema DEBE mantener la privacidad sin enviar audio a servicios externos
- **FR-011**: Sistema DEBE ser compatible con navegadores Chrome y Edge actuales
- **FR-012**: Sistema DEBE funcionar sin mocks, con UI completamente funcional y estados reales

### Key Entities
- **Transcripción en Streaming**: Representa una sesión activa de transcripción en tiempo real con estado, texto parcial, texto confirmado y métricas de latencia
- **Resultado de Transcripción**: Representa la transcripción final consolidada que se guarda en el historial local
- **Estado de Conexión**: Representa el estado actual de la conexión (conectado, reconectando, pausado, error)

---

## Riesgos y Casos Límite

### Riesgos Técnicos
- **Latencia alta**: Si el procesamiento local supera 3 segundos, se debe mostrar advertencia al usuario y la experiencia se degrada significativamente
- **Memoria insuficiente**: Sistemas con menos de 8GB RAM pueden no soportar transcripción en streaming adecuadamente
- **Compatibilidad de navegador**: APIs de audio pueden no estar disponibles o tener limitaciones
- **Calidad de audio**: Micrófonos de baja calidad pueden afectar la precisión de la transcripción

### Casos Límite
- **Sesiones muy largas**: Más de 60 minutos de grabación continua requieren guardado automático para evitar problemas de rendimiento
- **Red inestable**: Múltiples desconexiones consecutivas pueden causar pérdida de datos
- **Audio simultáneo**: Múltiples fuentes de audio pueden confundir el sistema de transcripción
- **Cambio de contexto**: Usuario cambia de pestaña o aplicación durante la grabación
- **Recursos limitados**: Sistema con poca RAM o CPU puede no soportar el procesamiento en tiempo real

### Plan de Mitigación
- Implementar límites de tiempo de sesión con guardado automático
- Desarrollar sistema de reconexión robusto con reintentos exponenciales
- Proporcionar indicadores claros de estado y opciones de recuperación
- Fallback automático al sistema por bloques si hay problemas técnicos

---

## Lista de Revisión para Demo

### Verificación de Latencia
1. Iniciar grabación y cronometrar tiempo hasta primera aparición de texto
2. Verificar que el contador de latencia muestra valores realistas (< 2000ms)
3. Probar con diferentes duraciones de audio (5s, 30s, 2min)

### Verificación de Reconexión
1. Simular pérdida de conexión (desconectar wifi brevemente)
2. Verificar que aparece "Reconectando..." durante la desconexión
3. Confirmar que la transcripción continúa sin pérdida de datos al reconectar

### Verificación de Guardado
1. Completar una transcripción de al menos 1 minuto
2. Presionar "Guardar resultado"
3. Verificar que aparece en el historial local con timestamp correcto
4. Comparar texto final con segmentos confirmados mostrados durante la grabación

### Verificación de Estados de UI
1. Verificar todos los estados: "Conectado", "Reconectando", "Pausado", "Finalizado"
2. Confirmar que botones responden correctamente en cada estado
3. Verificar que texto parcial aparece en gris y confirmado en negro
4. Probar pausar/reanudar múltiples veces durante una sesión

### Verificación de Fallback
1. Simular fallo del sistema de streaming (desactivar servicio)
2. Verificar que aparece notificación de fallback al modo por bloques
3. Confirmar que el usuario puede continuar con el flujo existente

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous  
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed