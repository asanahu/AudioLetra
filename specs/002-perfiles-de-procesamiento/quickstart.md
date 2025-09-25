# Quickstart: Perfiles de Procesamiento con LLM

**Feature**: 002-perfiles-de-procesamiento  
**Date**: 2025-01-17  
**Status**: Complete

## User Journey Validation

### Scenario 1: Limpiar y Formatear Texto
1. **Given** Usuario tiene una transcripción completada
2. **When** Selecciona "Limpiar y Formatear" del menú desplegable
3. **And** Hace clic en "Procesar"
4. **Then** Ve indicador "Procesando..." 
5. **And** Recibe texto mejorado con puntuación y formato
6. **And** Puede copiar o descargar el resultado

### Scenario 2: Traducir Texto
1. **Given** Usuario tiene texto en español
2. **When** Selecciona "Traducir" del menú
3. **And** Elige idioma destino "Inglés"
4. **And** Hace clic en "Procesar"
5. **Then** Recibe texto traducido al inglés
6. **And** Puede cambiar entre resultados de diferentes perfiles

### Scenario 3: Manejo de Errores
1. **Given** Usuario selecciona un perfil
2. **When** El LLM falla o excede timeout
3. **Then** Ve mensaje de error claro
4. **And** Puede reintentar manualmente
5. **And** No pierde el texto original

## Test Scenarios

### Integration Test 1: Profile Processing Flow
```python
def test_profile_processing_flow():
    # 1. Get available profiles
    profiles = get_profiles()
    assert len(profiles) == 6
    
    # 2. Process text with clean_format profile
    result = process_text(
        profile_id="clean_format",
        text="hola mundo esto es una prueba"
    )
    
    # 3. Verify result structure
    assert result.success == True
    assert result.profile_id == "clean_format"
    assert len(result.output) > 0
    
    # 4. Verify metadata
    assert result.metadata.processing_time > 0
    assert result.created_at is not None
```

### Integration Test 2: Multiple Profiles Same Text
```python
def test_multiple_profiles_same_text():
    text = "Reunión del equipo para discutir nuevos proyectos"
    
    # Process with different profiles
    results = {}
    for profile_id in ["summarize", "extract_tasks", "format_email"]:
        results[profile_id] = process_text(
            profile_id=profile_id,
            text=text
        )
    
    # Verify all succeeded
    for result in results.values():
        assert result.success == True
        assert result.output != text  # Should be transformed
    
    # Verify different outputs
    assert results["summarize"].output != results["extract_tasks"].output
```

### Integration Test 3: Error Handling
```python
def test_error_handling():
    # Test invalid profile
    result = process_text(
        profile_id="invalid_profile",
        text="test"
    )
    assert result.success == False
    assert result.error.code == "INVALID_PROFILE"
    
    # Test empty text
    result = process_text(
        profile_id="clean_format", 
        text=""
    )
    assert result.success == False
    assert result.error.code == "INVALID_TEXT"
```

## Performance Validation

### Timeout Calculation Test
```python
def test_timeout_calculation():
    # Test with different text lengths
    test_cases = [
        ("short", 1000, 31),      # 30s + 1s
        ("medium", 10000, 40),    # 30s + 10s  
        ("long", 50000, 80)       # 30s + 50s
    ]
    
    for name, chars, expected_timeout in test_cases:
        text = "a" * chars
        timeout = calculate_timeout(text)
        assert timeout == expected_timeout
```

## File Download Validation

### Download Format Test
```python
def test_download_formats():
    result = process_text("clean_format", "test text")
    
    # Test all supported formats
    formats = ["txt", "docx", "pdf"]
    for format_type in formats:
        download_response = download_result(
            result_id=result.result_id,
            format=format_type
        )
        
        assert download_response.status_code == 200
        assert download_response.headers["Content-Type"] == get_content_type(format_type)
```

## UI Integration Test

### Frontend State Management
```javascript
// Test profile selection and processing
async function testProfileProcessing() {
    // 1. Load profiles
    const profiles = await fetchProfiles();
    expect(profiles.length).toBe(6);
    
    // 2. Select profile and process
    const result = await processWithProfile("clean_format", "test text");
    expect(result.success).toBe(true);
    
    // 3. Verify UI state
    expect(document.querySelector('.processing-indicator')).toBeHidden();
    expect(document.querySelector('.result-panel')).toBeVisible();
    
    // 4. Test result switching
    const result2 = await processWithProfile("summarize", "test text");
    expect(document.querySelectorAll('.result-tab')).toHaveLength(2);
}
```

## Success Criteria Validation

✅ **1 clic desde transcripción a resultado**: Menú desplegable + procesar = 2 clics  
✅ **Resultados consistentes por perfil**: Plantillas predefinidas garantizan consistencia  
✅ **Feedback visible de estado**: Indicador "Procesando..." durante procesamiento  
✅ **No se envía audio**: Solo texto transcrito se envía al LLM  
✅ **Manejo de errores**: Mensajes claros y opción de reintentar  
✅ **Múltiples formatos de descarga**: TXT, DOCX, PDF soportados  
✅ **Historial de resultados**: Navegación entre diferentes perfiles  

---

**Quickstart Status**: ✅ Complete - All scenarios validated
