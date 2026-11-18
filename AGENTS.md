# Repository Guidelines

## Project Structure & Module Organization

Kellytix currently focuses on football match data preparation and a local SQLite database. `database/` contains SQLAlchemy models and connection setup; `scripts/` contains dataset creation, cleaning, verification, and loading utilities. Product code is intended for `src/mobile/` and `src/backend/`, while `tests/unit/`, `tests/integration/`, and `tests/e2e/` are reserved for their respective test levels. `docs/` holds project, architecture, and data documentation. Raw and processed datasets and `kellytix.db` are local artifacts, not source files.

## Build, Test, and Development Commands

Use a virtual environment and install the pinned/project dependencies:

```bash
python -m venv venv
source venv/bin/activate             # Windows: venv\Scripts\activate
python -m pip install -r requirements.txt
```

The documented data workflow is `python scripts/crear_dataset.py`, `python scripts/clean_data.py`, then `python scripts/verificar_dataset.py`. Initialize the local database with `python database/connection.py`, then load cleaned records using `python scripts/load_db.py`. Use `--help` on a script for supported options; `load_db.py --replace` replaces historical match rows and can invalidate prediction references.

## Coding Style & Naming Conventions

Write Python with four-space indentation and follow these naming conventions:

- **Files and directories:** `kebab-case` (e.g., `data-loader.py`, `unit-tests/`).
- **Modules, functions, and variables:** `snake_case` (e.g., `load_dataset`, `match_data`).
- **SQLAlchemy model classes:** `PascalCase` (e.g., `FootballMatch`).

Keep scripts runnable from the repository root and resolve input/output paths consistently with existing scripts. No formatter or linter configuration is currently present; keep changes readable and avoid adding tooling without project need.

## Testing Guidelines

The test directories are currently placeholders and no test framework or coverage threshold is configured. When adding tests, place them under the matching `tests/unit/`, `tests/integration/`, or `tests/e2e/` directory and use descriptive `test_*.py` names. For data-pipeline changes, include a small reproducible fixture and verify expected output rows and schema; do not depend on locally downloaded full datasets.

## Commit & Pull Request Guidelines

Follow the [`commit-conventions`](.agents/skills/commit-conventions/SKILL.md) skill for all commit-related tasks, including creating, suggesting, reviewing, and correcting commit messages.

Do not duplicate or override the conventions defined in the skill. It is the single source of truth for commit messages.

Pull requests should explain the change and its motivation, list relevant validation commands and outcomes, link related issues when available, and include screenshots for UI changes or sample output/schema details for data changes.

## Data and Configuration

Follow `GUIA_INICIALIZACION_BASE_DATOS.md` for local dataset setup. Keep downloaded CSV files, generated datasets, virtual environments, credentials, and the SQLite database out of commits. Never commit secrets; use local configuration for machine-specific settings.
