# json2csv

Herramientas de línea de comandos desarrolladas como parte del **TP11** de la
materia **Ingeniería de Software 2** (UADER FCyT).

El proyecto contiene dos ejercicios:

| Módulo | Descripción |
|---|---|
| `src/collatz.py` | Cómputo y verificación de la **Conjetura de Collatz**. |
| `src/json2csv.py` | Conversión de **JSON a CSV** con estrategia de filtro. |

## json2csv: ¿qué hace?

Los datos JSON atraviesan una cadena de filtros antes de serializarse:

1. `normalizar` — valida la entrada y la convierte en una lista de registros.
2. `aplanar` — aplana los objetos anidados con claves compuestas (`dir.ciudad`).
3. `escribir_csv` — arma los encabezados y escribe el CSV.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
```

## Uso

```bash
python src\json2csv.py {-i input.txt} {-o output.txt} {-d delimitador}
```

| Opción | Efecto |
|---|---|
| `-i`, `--input` | Archivo JSON de entrada. Si se omite, lee por **entrada estándar**. |
| `-o`, `--output` | Archivo CSV de salida. Si se omite, escribe por **salida estándar**. |
| `-d`, `--delimiter` | Delimitador. Por defecto es la **coma** (`,`). |

### Ejemplos

```powershell
# 1) Entrada por archivo, salida por pantalla (delimitador coma)
python src\json2csv.py -i examples\datos.json

# 2) Entrada por pipe, delimitador punto y coma
'{"id":3,"nombre":"Zoe"}' | python src\json2csv.py -d ";"

# 3) Entrada y salida por archivo, delimitador barra vertical
python src\json2csv.py -i examples\datos.json -o salida.csv -d "|"
Get-Content salida.csv
```

| Comando | Entrada | Delimitador | Salida esperada |
|---|---|---|---|
| 1 | `examples/datos.json` (Ana, Luis) | coma (por defecto) | `1,Ana,Parana,3100,a b` |
| 2 | pipe: `{"id":3,...Zoe}` | punto y coma (`;`) | `3;Zoe` |
| 3 | `examples/datos.json` (Ana, Luis) | barra (`\|`) | `1\|Ana\|Parana\|3100\|a b` |

### Ejemplo de transformación

Entrada:
```json
[{"id": 1, "nombre": "Ana", "dir": {"ciudad": "Parana", "cp": 3100}, "tags": ["a", "b"]}]
```

Salida:
```
id,nombre,dir.ciudad,dir.cp,tags
1,Ana,Parana,3100,a b
```

## Manejo de errores

| Situación | Comportamiento |
|---|---|
| JSON inválido | `Error: ...` por stderr, código de salida 1 |
| Archivo inexistente | `Error: ...` por stderr, código de salida 1 |
| JSON que no es objeto ni lista | `Error: ...` por stderr, código de salida 1 |

## collatz: ¿qué hace?

Cuenta cuántas iteraciones tarda un número entero positivo en llegar al 1 según
la conjetura de Collatz (si es par, dividir por dos; si es impar, multiplicar
por tres y sumar uno).

```bash
python src\collatz.py
```

| Entrada | Resultado |
|---|---|
| `27` | `El número de iteraciones para 27 es 111` |
| `6` | `El número de iteraciones para 6 es 8` |
| `1` | `El número de iteraciones para 1 es 0` |
| `0` o `abc` | Mensaje de error y código de salida 1 |

El módulo rechaza valores fuera del rango `[1, 1999]`. Esta validación es
necesaria: sin ella, `collatz(0)` entra en un bucle infinito porque cero
siempre es par y `0 // 2` sigue siendo cero.

## Calidad e integridad del código

Todos los controles se ejecutan también en la integración continua:

| Control | Comando |
|---|---|
| Formato y convenciones (PEP8 / PEP257) | `python -m ruff check src tests` |
| Formato consistente | `python -m black --check src tests` |
| Tipado estricto (mypy) | `python -m mypy` |
| Tipado estricto (pyright) | `pyright src` |
| Pruebas unitarias (mínimo 85 %) | `python -m pytest` |
| Seguridad (bandit) | `python -m bandit -r src -c pyproject.toml` |
| Documentación (pdoc) | `python -m pdoc --output-directory docs ./src` |

Estado actual: **69 pruebas, 94 % de cobertura**.

## Integración continua

`.github/workflows/ci.yml` se ejecuta en cada `push` a `main` y en cada Pull
Request, con cuatro trabajos encadenados:

1. **Calidad** — ruff, black, mypy y pyright.
2. **Pruebas** — pytest con cobertura mínima del 85 %.
3. **Seguridad** — bandit, truffleHog (detección de secretos) y `pip-audit`.
4. **Documentación** — genera la documentación con pdoc y la publica.

## Estructura del proyecto

```
json2csv/
├── .github/workflows/ci.yml   Integración continua
├── cookiecutter/              Plantilla para generar proyectos nuevos
├── doc/                       Documentación .docx
├── examples/                  Archivos JSON de ejemplo
├── src/json2csv.py            Conversión JSON -> CSV
├── src/collatz.py             Conjetura de Collatz
├── tests/                     Pruebas unitarias
├── CHANGELOG.md               Registro de cambios
├── CONTEXT.md                 Registro de prompts de IA
├── LICENSE                    MIT
├── VERSION                    Versión semántica
├── pyproject.toml             Configuración de herramientas
├── requirements.txt           Dependencias de ejecución
└── requirements-dev.txt       Dependencias de desarrollo
```

## Registro de versiones

- `VERSION` (raíz y constante del módulo): versión semántica.
- `BUILD` (constante del módulo): número de build incremental.
- Cambios relevantes en `CHANGELOG.md`.

## Licencia

MIT. Ver [LICENSE](LICENSE).