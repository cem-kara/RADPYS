# REPYS 2.0

REPYS 2.0 is a desktop management system for radiology departments.
It is built with Python 3.12, PySide6, and SQLite.

## Features

- Personnel records and identity details
- Leave and shift planning workflows
- Device, maintenance, and failure tracking modules
- Dosimeter and health follow-up support
- Modular page loading via menu registry

## Tech Stack

- Python 3.12
- PySide6
- SQLite (WAL)
- pytest

## Project Structure

- `main.py`: application entry point
- `app/`: domain logic, services, database, validators
- `ui/`: PySide6 widgets, shared components, pages
- `modules/`: legacy/module pages
- `tests/`: automated tests
- `docs/`: design and usage documentation

## Quick Start

### 1. Create and activate virtual environment

```powershell
uv python install 3.12
uv venv .venv --python 3.12
.\.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Run the app

```powershell
python main.py
```

## Running Tests

```powershell
python -m pytest -q
```

## Contributing

See `CONTRIBUTING.md` for contribution workflow and standards.

## Security

See `SECURITY.md` for reporting vulnerabilities.

## License

This project is licensed under the MIT License. See `LICENSE`.
