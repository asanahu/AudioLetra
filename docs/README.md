# Dictado Inteligente con Whisper (local) + post-procesado opcional con LLM

## Qué hace
1. **Escucha tu micro**, detecta automáticamente cuándo hablas (VAD) y corta por frases.
2. **Transcribe localmente** con [faster-whisper] (no envía audio a Internet).
3. **(Opcional) Mejora el texto** con un LLM (p. ej., `gpt-4o-mini`) para:
   - limpiar y puntuar mejor,
   - resumir,
   - sacar bullets/tareas,
   - formatear como email o acta de reunión.

## Instalación (Windows/macOS/Linux)
1. **Instala FFmpeg** (necesario para mejor compatibilidad de audio).
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - Windows: descarga binarios desde la web oficial y añade a PATH.
2. Crea y activa un entorno:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso básico
```bash
python whisper_dictado.py
```

## Configuración avanzada
1. Copia `config_template.env` a `.env` y ajusta parámetros:
   ```bash
   cp config_template.env .env
   ```
2. Edita `.env` para personalizar:
   - Modelo de Whisper (tiny, base, small, medium, large)
   - Idioma (es, en, auto)
   - Configuración de VAD
   - **LLM Provider**: `openrouter` (recomendado) o `openai`
   - **API Key**: De OpenRouter o OpenAI
   - **Modelo LLM**: `openai/gpt-4o-mini`, `anthropic/claude-3-haiku`, etc.

## Características principales

### 🎤 Detección automática de voz (VAD)
- Detecta cuando empiezas y terminas de hablar
- Evita transcribir silencios innecesarios
- Configurable por sensibilidad

### 🧠 Transcripción local con Whisper
- **Sin conexión a Internet** para la transcripción
- Múltiples modelos disponibles (tiny → large)
- Soporte para múltiples idiomas
- Corrección automática de puntuación básica

### ✨ Post-procesado inteligente (opcional)
- Mejora la puntuación y formato
- Extrae tareas y bullets automáticamente
- Formatea como emails o actas de reunión
- Resúmenes inteligentes
- **Soporte para múltiples proveedores de LLM:**
  - **OpenRouter** (recomendado): Acceso a múltiples modelos (GPT-4, Claude, Llama, etc.)
  - **OpenAI**: Modelos oficiales de OpenAI

### 📁 Gestión de archivos
- Guarda automáticamente transcripciones
- Historial de sesiones
- Exportación a múltiples formatos

## Ejemplos de uso

### Dictado básico
```bash
python whisper_dictado.py
```

### Con post-procesado LLM
```bash
python whisper_dictado.py --llm-enable
```

### Configurar OpenRouter (Recomendado)
1. Ve a [OpenRouter](https://openrouter.ai/keys) y crea una cuenta
2. Obtén tu API key
3. Configura en `.env`:
   ```env
   LLM_ENABLED=true
   LLM_PROVIDER=openrouter
   OPENAI_API_KEY=tu_api_key_aqui
   OPENAI_MODEL=openai/gpt-4o-mini
   ```
4. Prueba la conexión:
   ```bash
   python test_openrouter.py
   ```

### Idioma específico
```bash
python whisper_dictado.py --idioma es
```

### Modelo específico
```bash
python whisper_dictado.py --modelo small
```

## Estructura del proyecto
```
whisper_inteligente/
├── whisper_dictado.py      # Script principal
├── config/
│   ├── config_template.env # Plantilla de configuración
│   └── config.py          # Módulo de configuración
├── utils/
│   ├── audio_handler.py   # Manejo de audio
│   ├── vad_detector.py    # Detección de voz
│   └── text_processor.py  # Procesamiento de texto
├── output/                # Transcripciones guardadas
├── requirements.txt       # Dependencias
└── README.md             # Este archivo
```

## Troubleshooting

### Error de audio
- Verifica que tu micrófono esté conectado
- En Windows, ejecuta como administrador si hay problemas de permisos
- Prueba diferentes dispositivos de audio en la configuración

### Error de FFmpeg
- Asegúrate de que FFmpeg esté instalado y en el PATH
- Reinicia la terminal después de instalar FFmpeg

### Problemas de transcripción
- Prueba con un modelo más grande (small, medium, large)
- Verifica que el idioma esté configurado correctamente
- Habla más claro y cerca del micrófono

## Contribuir
¡Las contribuciones son bienvenidas! Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia
MIT License - ver LICENSE para más detalles.
