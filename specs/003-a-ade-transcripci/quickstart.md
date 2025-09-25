# Quickstart: Transcripción en Streaming

**Feature**: Transcripción en Streaming (Tiempo Real)  
**Date**: 2025-01-27  
**Branch**: `003-a-ade-transcripci`

## Prerrequisitos

### Sistema
- Python 3.11+
- 8GB RAM mínimo
- Navegador Chrome/Edge actualizado
- Micrófono disponible

### Dependencias
```bash
pip install flask-socketio faster-whisper
```

## Configuración Inicial

### 1. Verificar Instalación
```bash
# Verificar Python
python --version  # Debe ser 3.11+

# Verificar dependencias
python -c "import flask_socketio, faster_whisper; print('Dependencias OK')"
```

### 2. Configurar AudioLetra
```bash
# Navegar al directorio del proyecto
cd E:\Variedades\AudioLetra

# Verificar estructura existente
ls web/templates/  # Debe existir index.html
ls web/static/js/  # Debe existir app.js
```

## Ejecución Local

### 1. Iniciar Servidor
```bash
# Desde el directorio raíz del proyecto
python web_server.py

# El servidor debe iniciar en http://localhost:5000
```

### 2. Acceder a la Vista Streaming
1. Abrir navegador en `http://localhost:5000`
2. Navegar a la nueva sección "Streaming" en el menú principal
3. Verificar que aparece la vista de transcripción en streaming

## Demo Paso a Paso

### Verificación de Latencia (< 2 segundos)
1. **Iniciar grabación**:
   - Hacer clic en "Iniciar Grabación"
   - Verificar que aparece estado "Conectado/Escuchando"
   - Observar contador de latencia en esquina superior derecha

2. **Probar transcripción**:
   - Hablar claramente por 5 segundos
   - Cronometrar tiempo hasta primera aparición de texto
   - **Objetivo**: Texto debe aparecer en < 2 segundos

3. **Verificar tipos de texto**:
   - Texto parcial debe aparecer en gris
   - Texto confirmado debe aparecer en negro
   - El texto confirmado debe ser más estable

### Verificación de Reconexión
1. **Simular pérdida de conexión**:
   - Desconectar WiFi brevemente (5 segundos)
   - Observar que aparece "Reconectando..."
   - Reconectar WiFi

2. **Verificar recuperación**:
   - Confirmar que la transcripción continúa sin pérdida
   - Verificar que no hay duplicación de texto
   - Estado debe volver a "Conectado/Escuchando"

### Verificación de Pausa/Reanudar
1. **Pausar grabación**:
   - Hacer clic en "Pausar"
   - Verificar que estado cambia a "Pausado"
   - Confirmar que no se procesa audio durante pausa

2. **Reanudar grabación**:
   - Hacer clic en "Reanudar"
   - Verificar que estado vuelve a "Conectado/Escuchando"
   - Confirmar que la transcripción continúa

### Verificación de Guardado
1. **Completar transcripción**:
   - Grabar al menos 1 minuto de audio
   - Observar acumulación de texto confirmado

2. **Guardar resultado**:
   - Hacer clic en "Guardar resultado"
   - Verificar que aparece confirmación de guardado
   - Navegar al historial de transcripciones
   - Confirmar que la transcripción aparece en la lista

### Verificación de Límites
1. **Probar límite de tiempo**:
   - Grabar por más de 60 minutos (o simular)
   - Verificar que aparece advertencia de límite
   - Confirmar guardado automático

2. **Probar límite de latencia**:
   - Si latencia supera 3 segundos, verificar advertencia
   - Observar cambio de color en contador de latencia

## Script de Prueba Manual

### Test de 60 Segundos
```bash
# Ejecutar este test para verificación completa
echo "Iniciando test de 60 segundos..."

# 1. Iniciar grabación
echo "1. Iniciar grabación - verificar estado 'Conectado'"

# 2. Hablar por 10 segundos
echo "2. Hablar por 10 segundos - verificar texto en < 2s"

# 3. Pausar por 5 segundos
echo "3. Pausar - verificar estado 'Pausado'"

# 4. Reanudar por 10 segundos
echo "4. Reanudar - verificar continuación de texto"

# 5. Simular desconexión (desconectar WiFi 5s)
echo "5. Simular desconexión - verificar 'Reconectando...'"

# 6. Continuar por 10 segundos
echo "6. Continuar - verificar recuperación"

# 7. Detener y guardar
echo "7. Detener y guardar - verificar en historial"

echo "Test completado - verificar todos los puntos"
```

## Verificación de Estados de UI

### Estados Requeridos
- ✅ **Conectado**: Indicador verde, botón "Pausar" habilitado
- ✅ **Escuchando**: Indicador azul parpadeante, contador de latencia activo
- ✅ **Reconectando**: Indicador amarillo, mensaje "Reconectando..."
- ✅ **Pausado**: Indicador gris, botón "Reanudar" habilitado
- ✅ **Finalizado**: Indicador verde sólido, botón "Guardar resultado"

### Botones Requeridos
- ✅ **Iniciar Grabación**: Inicia nueva sesión
- ✅ **Pausar/Reanudar**: Control de grabación
- ✅ **Detener**: Finaliza sesión
- ✅ **Guardar Resultado**: Guarda transcripción final

## Verificación de Fallback

### Simular Fallo de Streaming
1. **Detener servicio de streaming**:
   - Comentar código de streaming en servidor
   - Reiniciar servidor
   - Intentar acceder a vista Streaming

2. **Verificar fallback**:
   - Debe aparecer notificación de fallback
   - Debe redirigir automáticamente al modo por bloques
   - Usuario debe poder continuar con funcionalidad existente

## Métricas de Rendimiento

### Latencia Esperada
- **Primera transcripción**: < 2 segundos
- **Transcripciones posteriores**: < 1 segundo
- **Umbral de advertencia**: 3 segundos

### Recursos del Sistema
- **RAM utilizada**: < 2GB por sesión activa
- **CPU**: < 50% durante transcripción
- **Red**: < 1MB/minuto de audio

### Calidad de Audio
- **Formato**: webm/opus
- **Calidad**: 16kHz, mono
- **Tamaño de chunk**: 200-500ms

## Troubleshooting

### Problemas Comunes

#### No aparece texto en 2 segundos
- Verificar que el micrófono funciona
- Comprobar permisos de micrófono en navegador
- Verificar que faster-whisper está instalado correctamente

#### Error de reconexión
- Verificar conexión de red
- Comprobar logs del servidor
- Reiniciar navegador si persiste

#### Latencia alta (>3s)
- Verificar recursos del sistema (RAM/CPU)
- Comprobar carga del servidor
- Considerar usar modelo más pequeño (tiny/base)

#### No se guarda transcripción
- Verificar permisos de escritura en directorio output/
- Comprobar que la sesión se completó correctamente
- Verificar logs de error del servidor

### Logs de Debug
```bash
# Ver logs del servidor
tail -f logs/audiLetra.log

# Ver logs del navegador (F12 → Console)
# Buscar errores relacionados con WebSocket o MediaRecorder
```

## Validación Final

### Checklist de Completitud
- [ ] Vista "Streaming" accesible desde navegación
- [ ] Estados de UI funcionan correctamente
- [ ] Latencia < 2s para primera transcripción
- [ ] Reconexión automática funciona
- [ ] Pausa/reanudar funciona
- [ ] Guardado en historial funciona
- [ ] Fallback a modo por bloques funciona
- [ ] Contador de latencia visible y preciso
- [ ] Texto parcial (gris) y confirmado (negro) diferenciados
- [ ] Límites de tiempo y recursos respetados

### Criterios de Éxito
- ✅ Funcionalidad completamente operativa sin mocks
- ✅ Experiencia de usuario fluida y responsiva
- ✅ Manejo robusto de errores y reconexiones
- ✅ Integración perfecta con sistema existente
- ✅ Cumplimiento de todos los requisitos de especificación
