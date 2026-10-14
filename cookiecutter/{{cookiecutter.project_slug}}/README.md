# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Requisitos

- Python {{cookiecutter.python_version}} o superior.
- Licencia {{cookiecutter.license}}.

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
```

## Uso

```bash
python src/{{cookiecutter.module_name}}.py
```

## Calidad

```bash
python -m ruff check .
python -m black --check .
python -m mypy
python -m pytest
python -m bandit -r src -c pyproject.toml
```

## Documentacion

```bash
python -m pdoc ./src/{{cookiecutter.module_name}}.py
```

## Version

- VERSION: `{{cookiecutter.version}}`
- BUILD: `1`
