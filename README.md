# Lucerna

## Development

### Run the app
```bash
uvicorn service_host.api:app --host 0.0.0.0 --port 8000
```

- http://127.0.0.1:8000/docs (Swagger like UI)
- http://127.0.0.1:8000/redoc (cleaner, more doc-focused UI)
- http://127.0.0.1:8000/dashboard (simple dashboard)
  
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

