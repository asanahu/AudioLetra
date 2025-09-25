"""
Integration guide for AudioLetra Profile Processing
Instructions for integrating the new LLM profile processing feature
"""

# Integration Steps for AudioLetra

## 1. Backend Integration

### Add to existing web_server.py or main Flask app:

`python
# Import the LLM Blueprint
from backend.src.api.llm_routes import llm_bp

# Register the blueprint
app.register_blueprint(llm_bp, url_prefix='/llm')

# Add audio cleanup integration
from backend.src.services.audio_cleanup import cleanup_after_transcription

# In your existing transcription completion handler:
def on_transcription_complete(audio_file_path, transcription_text):
    # Your existing transcription logic...
    
    # Schedule audio cleanup after 5 seconds
    cleanup_after_transcription(audio_file_path, delay=5)
    
    # Continue with existing logic...
`

## 2. Frontend Integration

### Add to existing HTML template (e.g., index.html):

`html
<!-- Add after the transcription section -->
<div id="profile-processing-section">
    <!-- Include the profile integration template -->
    {% include 'profiles/profile-integration.html' %}
</div>
`

### Add CSS and JavaScript includes:

`html
<!-- Add to <head> section -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/profiles.css') }}">

<!-- Add before closing </body> tag -->
<script src="{{ url_for('static', filename='js/profiles/profile-manager.js') }}"></script>
`

### Modify existing transcription textarea:

`html
<!-- Update your existing transcription textarea -->
<textarea id="transcription-text" name="transcription" rows="10" cols="50">
    <!-- Your existing transcription content -->
</textarea>
`

## 3. Environment Configuration

### Create .env file with LLM configuration:

`env
# LLM Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1

# Or for OpenRouter:
# OPENAI_API_KEY=sk-or-your-openrouter-api-key-here
# OPENAI_MODEL=anthropic/claude-3-haiku
# LLM_PROVIDER=openrouter
# LLM_BASE_URL=https://openrouter.ai/api/v1

# Other settings
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=temp
`

## 4. Dependencies

### Install required packages:

`ash
pip install python-docx reportlab
`

### Update requirements.txt:

`
python-docx>=0.8.11
reportlab>=4.0.0
`

## 5. Testing Integration

### Test the integration:

`python
# Test script
from backend.app import create_app

app = create_app()
client = app.test_client()

# Test profiles endpoint
response = client.get('/llm/profiles')
print(f"Profiles status: {response.status_code}")
print(f"Profiles data: {response.get_json()}")

# Test processing endpoint (requires API key)
# response = client.post('/llm/process', json={
#     'profile_id': 'clean_format',
#     'text': 'test text',
#     'parameters': {}
# })
`

## 6. User Experience Flow

1. **User transcribes audio** → Gets text in textarea
2. **User selects profile** → Dropdown shows 6 options
3. **User clicks "Procesar"** → Text is sent to LLM
4. **User sees result** → Processed text appears in result panel
5. **User can download** → TXT, DOCX, or PDF formats
6. **User can try other profiles** → Multiple results stored
7. **Audio is cleaned up** → Automatically deleted after 5 seconds

## 7. Privacy Compliance

✅ **Audio stays local** - Only text is sent to LLM  
✅ **No audio storage** - Files are automatically deleted  
✅ **No sensitive data in logs** - Logging is sanitized  
✅ **User control** - User explicitly chooses to process text  

## 8. Error Handling

- **API key missing** → Clear error message with setup instructions
- **LLM timeout** → Retry option with adjusted timeout
- **Network error** → Graceful fallback with retry button
- **Invalid profile** → Validation error with suggestions

## 9. Performance Considerations

- **Timeout calculation** → Dynamic based on text length
- **File cleanup** → Automatic background cleanup
- **Memory usage** → Minimal, only text processing
- **Response time** → <2s for basic operations

## 10. Monitoring

- **Request logging** → All API calls logged
- **Error tracking** → Failed requests logged with details
- **Usage statistics** → Profile usage tracked
- **Performance metrics** → Processing times recorded
