# Lucerna

## Development steps:

### Core
```bash
# Start this service
poetry run uvicorn service_host.main:app --reload --app-dir=src
```

Access the application at:
- :8000/docs (Swagger like UI)
- :8000/redoc (cleaner, more doc-focused UI)
  
### Others
```bash
# Configure poetry to use venv inside project
poetry config virtualenvs.in-project true
```

```bash 
# Install dependencies & venv  
poetry install
```

```bash
# Active shell
poetry shell
```

```bash
# Run code / CLI
poetry run python src/main.py
```

```bash
# Format & lint
poetry run black src tests
poetry run ruff check src tests
```

```bash
#  Run tests
poetry run pytest -v --cov=src
```

