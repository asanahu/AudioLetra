# AudioLetra Backend

Backend service for AudioLetra LLM Profile Processing feature.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

## Development

### Code Quality Tools

- **Black** (code formatting): `black .`
- **Flake8** (linting): `flake8`
- **Pytest** (testing): `pytest`

### Project Structure

```
backend/
├── src/
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── api/            # REST endpoints
│   └── utils/          # Utility functions
├── tests/
│   ├── contract/       # API contract tests
│   ├── integration/    # Integration tests
│   └── unit/           # Unit tests
└── app.py              # Flask application
```

## API Endpoints

- `GET /health` - Health check
- `GET /llm/profiles` - Get available profiles
- `POST /llm/process` - Process text with profile
- `GET /llm/results/{id}` - Get processing result
- `POST /llm/download/{id}` - Download result file

## Configuration

See `src/config.py` for configuration options and `env.example` for environment variables.
