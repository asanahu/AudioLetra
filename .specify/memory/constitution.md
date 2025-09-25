<!--
Sync Impact Report:
Version change: N/A → 1.0.0 (initial creation)
Modified principles: N/A (new constitution)
Added sections: Principios No Negociables, Tecnología, Seguridad y Calidad, Gobernanza
Removed sections: N/A
Templates requiring updates: ⚠ pending - .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md
Follow-up TODOs: Create template directory structure
-->

# Constitución del Proyecto AudioLetra

**Versión:** 1.0.0  
**Fecha de Ratificación:** 2025-01-17  
**Última Modificación:** 2025-01-17  

## Principios No Negociables

### Privacidad
El audio se procesa SIEMPRE en local; solo el texto puede enviarse a un LLM de forma opcional.

**Reglas:**
- El procesamiento de audio con Whisper debe ejecutarse completamente en el dispositivo local
- Los archivos de audio deben eliminarse inmediatamente después de la transcripción
- Solo el texto transcrito puede enviarse a servicios externos de LLM, y únicamente cuando el usuario lo autorice explícitamente
- No se almacenan grabaciones de audio en servicios externos

**Justificación:** Garantizar la privacidad del usuario y cumplir con regulaciones de protección de datos.

### Simplicidad
Interfaz clara, acciones rápidas y accesibles.

**Reglas:**
- La interfaz debe ser intuitiva y requerir máximo 3 clics para cualquier acción principal
- Las funciones críticas deben estar disponibles sin configuración previa
- El diseño debe seguir principios de accesibilidad web (WCAG 2.1 AA)
- Los tiempos de respuesta deben ser menores a 2 segundos para acciones básicas

**Justificación:** Maximizar la adopción y usabilidad del producto.

## Tecnología

### Backend
Python 3.11+ con Flask (REST y tiempo real).

**Reglas:**
- Usar Python 3.11 o superior como versión mínima
- Flask como framework web principal
- Implementar endpoints REST para funcionalidades básicas
- WebSockets para comunicación en tiempo real cuando sea necesario
- Seguir patrones de arquitectura limpia y separación de responsabilidades

### ASR (Reconocimiento Automático de Voz)
faster-whisper local (usa GPU si está disponible).

**Reglas:**
- Usar faster-whisper como motor de transcripción principal
- Detectar y utilizar GPU automáticamente cuando esté disponible
- Implementar fallback a CPU si GPU no está disponible
- Soporte para múltiples modelos de Whisper (tiny, base, small, medium, large)
- Configuración de idioma por defecto en español con soporte para otros idiomas

### Frontend
HTML/JS ligero integrado en Flask.

**Reglas:**
- HTML5 semántico y CSS3 moderno
- JavaScript vanilla (sin frameworks pesados)
- Diseño responsivo que funcione en móviles y escritorio
- Integración directa con Flask usando templates Jinja2
- Optimización de recursos (CSS/JS minificado en producción)

### LLM
OpenAI u OpenRouter configurados por variables de entorno.

**Reglas:**
- Soporte para OpenAI y OpenRouter como proveedores principales
- Configuración mediante variables de entorno
- Implementar sistema de fallback entre proveedores
- Validación de API keys antes de permitir uso
- Rate limiting y manejo de errores robusto

## Seguridad y Calidad

### Eliminación de Audio
Eliminar audio tras la transcripción.

**Reglas:**
- Los archivos de audio temporales deben eliminarse inmediatamente después de la transcripción
- Implementar limpieza automática de archivos temporales al cerrar la aplicación
- No mantener logs de audio o metadatos de grabación
- Verificar eliminación exitosa de archivos sensibles

### Validación de Archivos
Validar tamaño y formato de archivos.

**Reglas:**
- Validar formato de archivo antes del procesamiento (WAV, MP3, M4A)
- Limitar tamaño máximo de archivos de audio (configurable, por defecto 100MB)
- Sanitizar nombres de archivo para prevenir ataques de path traversal
- Implementar checksums para verificar integridad de archivos

### Logs y Código
Logs sin datos sensibles y código estilo PEP8.

**Reglas:**
- Los logs NO deben contener contenido de audio, transcripciones o API keys
- Implementar niveles de log apropiados (DEBUG, INFO, WARNING, ERROR)
- Seguir estándares PEP8 para estilo de código Python
- Implementar linting automático en el pipeline de CI/CD
- Documentación de código obligatoria para funciones públicas

## Gobernanza

### Procedimiento de Enmiendas
Las modificaciones a esta constitución requieren:

1. **Propuesta:** Documentar la propuesta de cambio con justificación técnica
2. **Revisión:** Evaluación de impacto en principios existentes
3. **Aprobación:** Consenso del equipo de desarrollo principal
4. **Implementación:** Actualización de código y documentación
5. **Comunicación:** Notificación a todos los contribuidores

### Política de Versionado
- **MAJOR (X.0.0):** Cambios incompatibles en principios fundamentales
- **MINOR (X.Y.0):** Nuevos principios o expansiones significativas
- **PATCH (X.Y.Z):** Clarificaciones, correcciones de redacción, mejoras menores

### Revisión de Cumplimiento
- Revisión trimestral del cumplimiento de principios
- Auditoría anual de seguridad y privacidad
- Evaluación continua de métricas de simplicidad y usabilidad
- Documentación de desviaciones y planes de corrección

---

*Esta constitución es un documento vivo que guía el desarrollo y evolución del proyecto AudioLetra, asegurando que los principios fundamentales se mantengan a lo largo del tiempo.*