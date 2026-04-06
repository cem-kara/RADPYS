# apps/api

FastAPI backend for REPYS Next.

## Quick start

```bash
cd apps/api
python -m venv .venv
. .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Health endpoints

- `GET /health` returns basic service info.
- `GET /ready` returns readiness status.

## Notes

- Environment variables are loaded from your shell. See the root `.env.example`.
