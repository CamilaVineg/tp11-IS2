# CONTEXT.md

Registro de los prompts de herramientas de IA utilizados durante el
desarrollo. Sirve para trazabilidad de decisiones y auditoria.

## 1. Implementacion inicial de la herramienta JSON a CSV

**Prompt:**
> Implementar el ejercicio de la pagina 4 del PDF en la carpeta TP11, en un
> archivo aparte del que ya existe. El enunciado dice: "Desarrolle una
> herramienta en lenguaje Python para convertir archivos de formato JSON a
> formato CSV. El programa debera implementarse con una estrategia de filtro.
> El formato de ejecucion sera: `python json2csv.py {-i input.txt} {-o
> output.txt} {-d delimitador}`. Si no se informa `-i` el programa podra
> aceptar el archivo de entrada mediante entrada estandar, y si no se informa
> `-o` se emitira el texto resultante mediante salida estandar. Se utilizara
> la coma como delimitador, excepto que se indique uno distinto con `-d`."

**Decisiones tomadas:**
- La "estrategia de filtro" se implemento como un pipeline de funciones
  encadenadas: `normalizar` valida y envuelve la entrada, `aplanar` aplana
  los registros anidados y `aplicar_filtro` los recorre de forma perezosa
  mediante un generador.
- Se uso `argparse` para cumplir el formato `{-i} {-o} {-d}`.
- El delimitador por defecto es `,` y se reemplaza con el valor de `-d`.
- Se leen archivos con `utf-8-sig` para tolerar archivos con BOM de Windows.
- Se eligio el nombre `json2csv.py` porque es el indicado literalmente en el
  enunciado.

## 2. Documentacion de la implementacion

**Prompt:**
> Escribir un pequeno resumen de la implementacion explicando que hace, que
> muestra en cada caso, como cumple lo pedido y como probarlo. Guardarlo en
> un .docx.

**Resultado:**
- Se genero `doc/TP11-json2csv-resumen.docx` con python-docx.
- Se detecto una ambiguedad en el documento (las salidas de ejemplo no
  indicaban a que comando correspondian) y se corrigio agregando una tabla
  de correspondencias.

## 3. Plan de ingenieria de software e integracion continua

**Prompt:**
> Ahora hay que implementar una checklist de ingenieria: entorno virtual,
> esqueleto CookieCutter, documentacion de prompts de IA, README, CHANGELOG,
> requirements.txt, licencia MIT, documentacion automatica con pdoc, registro
> de VERSION y BUILD, ejecucion de ruff, black, PEP8, PEP257, mypy, pyright,
> pruebas unitarias con pytest y cobertura del 85% o mejor, bandit,
> truffleHog, documentacion basica de modulos y un workflow de GitHub que
> integre la fase de CI/CD completa.

**Decisiones tomadas:**
- Alcance limitado a `src/TP11` y `tests`, para no tener que corregir los
  ~90 modulos historicos del repositorio.
- Se eligio `pdoc` sobre Sphinx por simplicidad de configuracion.
- `VERSION` y `BUILD` quedaron expuestos como constantes del modulo y
  ademas en el archivo `VERSION` de la raiz.
- La plantilla de CookieCutter se creo en `cookiecutter/` para no ensuciar la
  raiz del repositorio.

**Correcciones durante la implementacion:**
- `pytest` fallaba al leer la configuracion de `pyproject.toml` por usar
  concatenacion implicita de cadenas; se cambio a un array de cadenas.
- La cobertura inicial daba 0% por referenciar la ruta del archivo en vez
  del nombre del modulo; se cambio `--cov=json2csv`.
- `ruff` (PTH123) exigio reemplazar `open()` por `Path.open()`.
- `ruff` (D301) exigio docstrings con prefijo `r` cuando contienen `\r\n`.
- `mypy` en modo estricto exigio anotaciones en todas las pruebas.
- `bandit` reportaba `assert` en los tests; se configuro la seccion
  `[tool.bandit]` de `pyproject.toml` para excluir esa carpeta del analisis.
- `bandit` no parsea archivos `.bandit` en formato INI; la version instalada
  espera YAML o TOML, por eso la configuracion quedo en `pyproject.toml`.

## 4. Prompts de esta sesion

**Prompt:**
> Corregir el .docx para aclarar que salida corresponde a cada comando.

**Prompt:**
> Implementar la checklist de ingenieria de software e integracion continua
> de GitHub.