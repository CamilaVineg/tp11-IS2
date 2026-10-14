# Changelog

Todas las novedades del proyecto se registran en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el versionado sigue [Semantic Versioning](https://semver.org/lang/es/).

Tipos de cambio:

- **Added**: funcionalidad nueva.
- **Changed**: funcionalidad existente modificada.
- **Fixed**: correccion de errores.
- **Security**: correcciones de seguridad.
- **Docs**: cambios solo de documentacion.
- **Chore**: tareas de mantenimiento que no afectan al codigo.

## [No publicado]

## [1.0.0] - 2026-10-14

### Added

- Herramienta `collatz` en `src/collatz.py` que calcula las iteraciones
  necesarias para alcanzar el 1, con validacion del rango [1, 1999] y manejo
  de entrada cancelada o inexistente.
- Pruebas de la conjetura en `tests/test_collatz.py`.
- Herramienta `json2csv` en `src/json2csv.py` que convierte JSON a CSV
  usando una estrategia de filtro (`normalizar` -> `aplanar` -> `escribir_csv`).
- Interfaz de linea de comandos con las opciones `-i/--input`, `-o/--output`
  y `-d/--delimiter`, con lectura por entrada estandar y escritura por salida
  estandar cuando se omiten.
- Manejo robusto de excepciones: JSON invalido, archivo inexistente y tipos de
  datos no soportados devuelven codigo de salida 1 y mensaje por stderr.
- Constantes `VERSION` y `BUILD` en el modulo y archivo `VERSION` en la raiz.
- Suite de 69 pruebas unitarias con pytest (`tests/`), con cobertura del 94%
  (umbral exigido: 85%).
- Configuracion centralizada en `pyproject.toml` para ruff, black, mypy,
  pytest/coverage y pdoc.
- Configuración `[tool.bandit]` en `pyproject.toml` para la auditoría de
  seguridad del código de producción.
- Plantilla de CookieCutter en `cookiecutter/` para generar esqueletos de
  proyecto con la misma estructura y controles.
- Flujo de trabajo de integracion continua en
  `.github/workflows/ci.yml` con ruff, black, mypy, pyright, pytest, bandit,
  truffleHog, auditoria de dependencias y publicacion de la documentacion
  generada con pdoc.
- Documentacion automatica con pdoc y este `CHANGELOG.md`.
- Registro de los prompts de IA en `CONTEXT.md`.

### Changed

- `README.md` actualizado con la estructura del proyecto, el flujo de trabajo
  de calidad y los comandos de uso.

### Security

- Analisis estatico con bandit (sin hallazgos en `src/`).
- Deteccion de secretos con truffleHog sobre el historial del repositorio.
- Verificacion de vulnerabilidades en dependencias con `pip-audit`.