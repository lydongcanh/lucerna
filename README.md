# Lucerna

## Development

### API
```bash
# Start the REST Api server
poetry run uvicorn service_host.api:app --reload --app-dir=src
```

- http://127.0.0.1:8000/docs (Swagger like UI)
- http://127.0.0.1:8000/redoc (cleaner, more doc-focused UI)
  
### UI
```bash
# Start the dashboard
poetry run python src/service_host/ui.py
```

- http://127.0.0.1:8050
  
### Others

```bash
# Configure poetry to use venv inside project
poetry config virtualenvs.in-project true
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

