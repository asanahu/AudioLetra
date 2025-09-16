# 🎙️ AudioLetra - Captura tus ideas, la IA las escribe

Una aplicación web moderna para transcripción de audio usando Whisper y procesamiento inteligente con LLM.

## ✨ Características

- 🎤 **Grabación de audio en tiempo real** con detección de voz
- 🧠 **Transcripción con Whisper** (modelo local)
- 🤖 **Procesamiento inteligente** con LLM (OpenAI/OpenRouter)
- 🌙 **Modo oscuro/claro** con transiciones suaves
- 📱 **Diseño responsivo** optimizado para móviles
- 🎨 **Interfaz moderna** con animaciones elegantes
- 📊 **Gestión de dictados** con historial
- 🌐 **Traducción automática** al inglés
- 📝 **Resúmenes inteligentes** del contenido

## 🚀 Inicio Rápido

### Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd AudioLetra

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configuración inicial
python install.py
```

### Configuración

1. **Configurar variables de entorno**:
   ```bash
   cp config/config_template.env .env
   # Editar .env con tus configuraciones
   ```

2. **Configurar LLM (opcional)**:
   ```bash
   python configure_openrouter.py
   ```

### Uso

#### Interfaz Web (Recomendado)
```bash
python web_server.py --host 127.0.0.1 --port 5000
```
Abre tu navegador en `http://127.0.0.1:5000`

#### Línea de Comandos
```bash
python whisper_dictado.py [--llm-enable]
```

## 📁 Estructura del Proyecto

```
AudioLetra/
├── 📁 config/           # Configuraciones
│   ├── config_template.env
│   └── config.py
├── 📁 data/             # Datos del proyecto
│   ├── audio/           # Archivos de audio
│   ├── transcriptions/  # Transcripciones
│   └── models/          # Modelos de IA
├── 📁 docs/             # Documentación
│   ├── README.md
│   ├── WEB_README.md
│   └── AGENTS.md
├── 📁 scripts/          # Scripts auxiliares
├── 📁 tests/            # Pruebas
├── 📁 utils/            # Utilidades
│   ├── audio_handler.py
│   ├── text_processor.py
│   └── vad_detector.py
├── 📁 web/              # Interfaz web
│   ├── static/          # CSS, JS, imágenes
│   └── templates/       # Plantillas HTML
├── 📄 web_server.py     # Servidor web principal
├── 📄 whisper_dictado.py # CLI principal
└── 📄 install.py        # Instalador
```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `config/config_template.env`:

```env
# Whisper
WHISPER_MODEL=base
WHISPER_LANGUAGE=es

# LLM (OpenAI/OpenRouter)
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-3.5-turbo
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1

# Audio
SAMPLE_RATE=16000
CHUNK_SIZE=1024

# Rutas
OUTPUT_DIR=output
```

### Modelos Whisper Disponibles

- `tiny` - Más rápido, menos preciso
- `base` - Equilibrio velocidad/precisión (recomendado)
- `small` - Mejor precisión
- `medium` - Alta precisión
- `large` - Máxima precisión (requiere más recursos)

## 🧪 Pruebas

```bash
# Prueba de configuración
python tests/test_setup.py

# Prueba del servidor web
python tests/test_web_server.py

# Prueba de configuración LLM
python tests/test_openrouter.py
```

## 🛠️ Desarrollo

### Estructura de Desarrollo

- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Backend**: Python Flask
- **IA**: Whisper (OpenAI), LLM (OpenAI/OpenRouter)
- **Audio**: PyAudio, NumPy

### Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📋 Requisitos

- Python 3.8+
- Micrófono funcional
- Conexión a internet (para LLM)
- 4GB RAM mínimo (8GB recomendado para modelos grandes)

## 🔒 Seguridad

- ⚠️ **Nunca commits archivos `.env`** con API keys
- 🔐 Las API keys se almacenan localmente
- 🌐 El audio se procesa localmente (Whisper)
- ☁️ Solo el texto se envía al LLM (opcional)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🤝 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación en `docs/`
2. Ejecuta las pruebas para diagnosticar problemas
3. Abre un issue en GitHub
4. Contacta al desarrollador

## 🎯 Roadmap

- [ ] Soporte para más idiomas
- [ ] Integración con más proveedores LLM
- [ ] Exportación a diferentes formatos
- [ ] API REST para integración
- [ ] Modo offline completo
- [ ] Reconocimiento de voz en tiempo real

---

**Desarrollado con ❤️ por Alberto Sanahuja**
