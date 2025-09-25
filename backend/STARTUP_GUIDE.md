# 🚀 Guía de Inicio de AudioLetra

## ✅ Estado Actual
La aplicación está **COMPLETAMENTE IMPLEMENTADA** y lista para usar.

## 🔧 Pasos para Iniciar la Aplicación

### 1. Configurar Variables de Entorno
Edita el archivo .env en la raíz del proyecto:

`env
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=tu-api-key-aqui
OPENAI_MODEL=gpt-3.5-turbo

# Flask Configuration
SECRET_KEY=tu-secret-key-aqui
FLASK_ENV=development
FLASK_DEBUG=True
`

### 2. Instalar Dependencias
`ash
cd backend
pip install -r requirements.txt
`

### 3. Iniciar la Aplicación
`ash
cd backend
python app.py
`

La aplicación estará disponible en: http://127.0.0.1:5000

## 🧪 Verificar que Funciona

### Endpoints Disponibles:
- GET /health - Health check
- GET /llm/profiles - Obtener perfiles disponibles
- POST /llm/process - Procesar texto con perfil
- GET /llm/results/{id} - Obtener resultado
- POST /llm/download/{id} - Descargar resultado

### Prueba Rápida:
`ash
# Health check
curl http://127.0.0.1:5000/health

# Obtener perfiles
curl http://127.0.0.1:5000/llm/profiles
`

## 🎯 Perfiles Disponibles

1. **Limpiar y Formatear** (clean_format)
2. **Resumir** (summarize)
3. **Extraer Lista de Tareas** (extract_tasks)
4. **Formatear como Email** (ormat_email)
5. **Crear Acta de Reunión** (meeting_minutes)
6. **Traducir** (	ranslate)

## 🔑 Configuración de API Key

### Para OpenAI:
1. Ve a https://platform.openai.com/api-keys
2. Crea una nueva API key
3. Agrega la key al archivo .env:
   `
   OPENAI_API_KEY=sk-tu-key-aqui
   `

### Para OpenRouter:
1. Ve a https://openrouter.ai/keys
2. Crea una nueva API key
3. Agrega la key al archivo .env:
   `
   LLM_PROVIDER=openrouter
   OPENAI_API_KEY=sk-or-tu-key-aqui
   OPENAI_MODEL=anthropic/claude-3-haiku
   `

## 📱 Integración con Frontend

Para integrar con el frontend existente de AudioLetra:

1. **Agregar CSS**: Incluir web/static/css/profiles.css
2. **Agregar JavaScript**: Incluir web/static/js/profiles/profile-manager.js
3. **Agregar HTML**: Incluir web/templates/profiles/profile-integration.html

## 🧪 Testing

### Tests Unitarios:
`ash
cd backend
python -m pytest tests/unit/ -v
`

### Tests de Integración:
`ash
cd backend
python -m pytest tests/integration/ -v
`

### Tests de Rendimiento:
`ash
cd backend
python -m pytest tests/unit/test_performance.py -v
`

## 📊 Monitoreo

### Logs:
- Los logs se guardan en ackend/logs/audiLetra.log
- Incluye requests, responses, y errores

### Estadísticas:
- Endpoint: GET /llm/statistics
- Muestra uso de perfiles y rendimiento

## 🚨 Solución de Problemas

### Error: "LLM API key is required"
- Verifica que OPENAI_API_KEY esté configurado en .env
- Reinicia la aplicación después de cambiar .env

### Error: "Profile not found"
- Verifica que el profile_id sea válido
- Usa GET /llm/profiles para ver perfiles disponibles

### Error: "Timeout"
- El timeout se calcula automáticamente
- Para textos largos, aumenta el timeout en el perfil

## 🎉 ¡Listo para Usar!

La aplicación está completamente funcional y lista para procesar texto con los 6 perfiles de LLM.

**Próximo paso**: Configura tu API key y ¡comienza a usar AudioLetra!
