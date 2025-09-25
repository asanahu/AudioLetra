# API Contracts: Perfiles de Procesamiento con LLM

**Feature**: 002-perfiles-de-procesamiento  
**Date**: 2025-01-17  
**Status**: Complete

## Endpoints

### POST /llm/process
Procesa texto usando un perfil específico de LLM

**Request**:
```json
{
    "profile_id": "clean_format",
    "text": "Texto a procesar...",
    "parameters": {
        "target_language": "en"
    }
}
```

**Response (Success)**:
```json
{
    "success": true,
    "profile_id": "clean_format",
    "result_id": "550e8400-e29b-41d4-a716-446655440000",
    "output": "Texto procesado y formateado...",
    "metadata": {
        "processing_time": 2.5,
        "tokens_used": 150,
        "model_used": "gpt-3.5-turbo"
    },
    "created_at": "2025-01-17T10:30:00Z"
}
```

**Response (Error)**:
```json
{
    "success": false,
    "error": {
        "code": "TIMEOUT_ERROR",
        "message": "El procesamiento excedió el tiempo límite",
        "details": {
            "timeout_seconds": 45,
            "profile_id": "summarize"
        }
    }
}
```

### GET /llm/profiles
Obtiene lista de perfiles disponibles

**Response**:
```json
{
    "profiles": [
        {
            "id": "clean_format",
            "name": "Limpiar y Formatear",
            "description": "Mejora la puntuación y estructura",
            "parameters": {}
        },
        {
            "id": "translate",
            "name": "Traducir", 
            "description": "Traduce al idioma seleccionado",
            "parameters": {
                "supported_languages": ["es", "en", "fr", "de"]
            }
        }
    ]
}
```

### GET /llm/results/{result_id}
Obtiene un resultado específico

**Response**:
```json
{
    "result_id": "550e8400-e29b-41d4-a716-446655440000",
    "profile_id": "clean_format",
    "output": "Texto procesado...",
    "metadata": {
        "processing_time": 2.5
    },
    "created_at": "2025-01-17T10:30:00Z"
}
```

### POST /llm/download/{result_id}
Descarga resultado en formato específico

**Request**:
```json
{
    "format": "pdf",
    "filename": "resultado.pdf"
}
```

**Response**: Binary file download

## Error Codes

- `INVALID_PROFILE`: Perfil no existe
- `INVALID_TEXT`: Texto vacío o inválido  
- `TIMEOUT_ERROR`: Procesamiento excedió tiempo límite
- `LLM_ERROR`: Error del proveedor LLM
- `RATE_LIMIT`: Límite de requests excedido
- `VALIDATION_ERROR`: Parámetros inválidos

---

**Contracts Status**: ✅ Complete
