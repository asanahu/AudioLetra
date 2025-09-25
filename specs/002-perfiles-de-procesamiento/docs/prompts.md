# LLM Prompt Templates

**Feature**: 002-perfiles-de-procesamiento  
**Date**: 2025-01-17  
**Status**: Complete

## Template System

The prompt system uses Jinja2 templates for dynamic prompt generation. Each profile has a base template that can be customized with parameters.

## Profile Templates

### 1. Clean & Format (clean_format)

**Purpose**: Improve punctuation, grammar, and text structure  
**Template**:
`
Por favor, mejora el siguiente texto corrigiendo la puntuación, gramática y estructura:

{{ text }}

Instrucciones:
- Corrige errores de puntuación y gramática
- Mejora la estructura y legibilidad
- Mantén el contenido original
- Usa un tono profesional pero natural
`

**Parameters**: None  
**Timeout Multiplier**: 1.0

### 2. Summarize (summarize)

**Purpose**: Create concise and structured summaries  
**Template**:
`
Por favor, crea un resumen conciso y estructurado del siguiente texto:

{{ text }}

Instrucciones:
- Identifica los puntos principales
- Crea un resumen claro y organizado
- Mantén la información esencial
- Usa un formato estructurado con puntos clave
`

**Parameters**: None  
**Timeout Multiplier**: 1.2

### 3. Extract Tasks (extract_tasks)

**Purpose**: Identify actionable tasks with infinitive verbs  
**Template**:
`
Por favor, extrae las tareas accionables del siguiente texto y preséntalas como una lista de acciones:

{{ text }}

Instrucciones:
- Identifica todas las tareas mencionadas
- Usa verbos en infinitivo (hacer, revisar, enviar, etc.)
- Organiza las tareas por prioridad
- Incluye detalles específicos cuando sea necesario
- Formato: lista de viñetas con verbos en infinitivo
`

**Parameters**: None  
**Timeout Multiplier**: 1.1

### 4. Format as Email (format_email)

**Purpose**: Structure text as professional email  
**Template**:
`
Por favor, formatea el siguiente texto como un email profesional:

{{ text }}

Instrucciones:
- Crea un asunto apropiado
- Estructura el cuerpo del email profesionalmente
- Usa un tono formal pero accesible
- Incluye saludo y despedida apropiados
- Organiza la información de manera clara

Formato:
Asunto: [asunto del email]

Estimado/a [destinatario],

[cuerpo del email]

Saludos cordiales,
[remitente]
`

**Parameters**: None  
**Timeout Multiplier**: 1.3

### 5. Meeting Minutes (meeting_minutes)

**Purpose**: Organize text as meeting minutes  
**Template**:
`
Por favor, organiza el siguiente texto como acta de reunión:

{{ text }}

Instrucciones:
- Identifica los asistentes mencionados
- Extrae los acuerdos y decisiones tomadas
- Identifica los próximos pasos y responsabilidades
- Organiza la información en secciones claras

Formato:
ACTA DE REUNIÓN

Asistentes:
- [lista de asistentes]

Acuerdos:
- [lista de acuerdos]

Próximos pasos:
- [lista de próximos pasos con responsables]
`

**Parameters**: None  
**Timeout Multiplier**: 1.4

### 6. Translate (translate)

**Purpose**: Translate text to target language  
**Template**:
`
Por favor, traduce el siguiente texto al {{ target_language }}:

{{ text }}

Instrucciones:
- Traduce manteniendo el significado original
- Preserva el tono y estilo del texto
- Asegúrate de que la traducción sea natural y fluida
- Mantén la estructura y formato original
- Si hay términos técnicos, usa la traducción más apropiada
`

**Parameters**: 
- 	arget_language: Target language for translation (e.g., "English", "French", "German")

**Timeout Multiplier**: 2.0

## Template Usage

### Basic Usage
`python
from src.services.prompt_service import PromptService

service = PromptService(config)
prompt = service.render_prompt("clean_format", "texto a procesar", {})
`

### With Parameters
`python
# For translate profile
prompt = service.render_prompt(
    "translate", 
    "texto a traducir", 
    {"target_language": "English"}
)
`

### Error Handling
`python
try:
    prompt = service.render_prompt("invalid_profile", "text", {})
except ValueError as e:
    print(f"Error: {e}")
`

## Template Customization

### Adding New Profiles
1. Create new profile in ProfileManager
2. Add template to PromptService
3. Update profile validation
4. Test with various inputs

### Modifying Existing Templates
1. Update template in PromptService
2. Test with sample inputs
3. Verify output quality
4. Update documentation

## Quality Guidelines

### Template Design Principles
- **Clarity**: Instructions should be clear and specific
- **Consistency**: Similar tasks should have similar formats
- **Flexibility**: Templates should work with various input types
- **Efficiency**: Avoid unnecessary complexity

### Testing Templates
- Test with short text (< 1000 chars)
- Test with medium text (1000-10000 chars)
- Test with long text (> 10000 chars)
- Test with special characters and formatting
- Test with different languages (for translate)

## Performance Considerations

### Timeout Calculation
- Base timeout: 30 seconds
- Additional time: 1 second per 1000 characters
- Profile multiplier applied to total

### Template Complexity
- Keep templates concise but clear
- Avoid overly complex instructions
- Balance detail with efficiency

## Security Considerations

### Input Sanitization
- Templates use Jinja2 auto-escaping
- No user input is executed as code
- Parameters are validated before use

### Content Filtering
- No sensitive data in templates
- No external API calls in templates
- Templates are static and validated

## Maintenance

### Regular Updates
- Review template effectiveness monthly
- Update based on user feedback
- Monitor LLM response quality
- Adjust timeout multipliers as needed

### Version Control
- All template changes are versioned
- Test changes before deployment
- Maintain backward compatibility
- Document all modifications

---

**Template Status**: ✅ Complete - All 6 profiles implemented and tested
