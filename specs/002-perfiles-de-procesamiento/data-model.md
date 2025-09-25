# Data Model: Perfiles de Procesamiento con LLM

**Feature**: 002-perfiles-de-procesamiento  
**Date**: 2025-01-17  
**Status**: Complete

## Core Entities

### Profile (Perfil de Procesamiento)
**Purpose**: Representa una configuración específica de procesamiento de texto con plantilla y parámetros definidos

**Fields**:
- id: str (Identificador único)
- name: str (Nombre para mostrar)
- description: str (Descripción del perfil)
- prompt_template: str (Plantilla Jinja2)
- parameters: Dict[str, Any] (Parámetros específicos)
- timeout_multiplier: float (Multiplicador timeout)

### ProcessingResult (Resultado Procesado)
**Purpose**: Contiene el texto transformado según el perfil aplicado

**Fields**:
- id: str (UUID único)
- profile_id: str (ID del perfil usado)
- input_text: str (Texto original)
- output_text: str (Texto procesado)
- metadata: Dict[str, Any] (Metadatos)
- processing_time: float (Tiempo en segundos)
- created_at: datetime (Timestamp)

### ResultHistory (Historial de Resultados)
**Purpose**: Colección de resultados para una transcripción específica

**Fields**:
- transcription_id: str (ID de transcripción)
- results: Dict[str, ProcessingResult] (Mapeo profile_id -> result)
- created_at: datetime (Primer resultado)
- updated_at: datetime (Último resultado)

## Profile Definitions (6 Predefined)

1. **clean_format**: Limpiar y Formatear
2. **summarize**: Resumir  
3. **extract_tasks**: Extraer Lista de Tareas
4. **format_email**: Formatear como Email
5. **meeting_minutes**: Crear Acta de Reunión
6. **translate**: Traducir (español, inglés, francés, alemán)

## API Payloads

### Process Request
```json
{
    "profile_id": "clean_format",
    "text": "Texto a procesar...",
    "parameters": {"target_language": "en"}
}
```

### Process Response  
```json
{
    "success": true,
    "profile_id": "clean_format",
    "result_id": "uuid-here", 
    "output": "Texto procesado...",
    "metadata": {"processing_time": 2.5},
    "created_at": "2025-01-17T10:30:00Z"
}
```

---

**Data Model Status**: ✅ Complete
