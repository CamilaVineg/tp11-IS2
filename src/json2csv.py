r"""Convierte datos en formato JSON a formato CSV.

La conversion se implementa con una estrategia de filtro: los datos crudos
se normalizan y luego atraviesan una cadena de filtros que transforma cada
registro antes de serializarlo en CSV.

Formato de ejecucion:
    python json2csv.py {-i input.txt} {-o output.txt} {-d delimitador}

Si no se informa ``-i`` la entrada se lee por entrada estandar; si no se
informa ``-o`` el resultado se emite por salida estandar. El delimitador por
defecto es la coma (``,``), salvo que se indique otro con ``-d``.

Attributes:
    VERSION: Version del modulo segun Semantic Versioning.
    BUILD: Numero de build incremental, incremented en cada entrega.

Example:
    >>> import io, json
    >>> salida = io.StringIO()
    >>> datos = json.loads('[{"id": 1, "nombre": "Ana"}]')
    >>> registros = aplicar_filtro(normalizar(datos), aplanar)
    >>> escribir_csv(registros, salida, ",")
    >>> salida.getvalue()
    'id,nombre\\r\\n1,Ana\\r\\n'
"""

import argparse
import csv
import json
import sys
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Any, TextIO

VERSION = "1.0.0"
BUILD = 1

Registro = dict[str, Any]


def normalizar(datos: Any) -> list[Registro]:
    """Filtro 1: normaliza la entrada a una lista de registros.

    Acepta tanto un objeto JSON suelto como una lista de objetos. Los
    elementos de la lista que no son objetos se descartan.

    Args:
        datos: Estructura previamente cargada con :func:`json.load`.

    Returns:
        Una lista de diccionarios, vacia si la entrada no contenia objetos.

    Raises:
        ValueError: Si la entrada es un escalar que no representa registros.

    Example:
        >>> normalizar({"id": 1})
        [{'id': 1}]
        >>> normalizar([{"id": 1}, 5])
        [{'id': 1}]
    """
    if isinstance(datos, dict):
        return [datos]
    if isinstance(datos, list):
        return [registro for registro in datos if isinstance(registro, dict)]
    raise ValueError("El JSON debe contener un objeto o una lista de objetos.")


def aplanar(registro: Registro, prefijo: str = "") -> Registro:
    """Filtro 2: aplana los registros anidados usando claves compuestas.

    Los diccionarios anidados se convierten en claves con notacion de punto
    (``dir.ciudad``) y las listas se unen en una unica celda separada por
    espacios.

    Args:
        registro: Diccionario de un solo registro a aplanar.
        prefijo: Prefijo acumulado al descender en la estructura anidada.

    Returns:
        Un diccionario de un solo nivel con todas las claves aplanadas.

    Example:
        >>> aplanar({"dir": {"ciudad": "Parana"}, "tags": ["a", "b"]})
        {'dir.ciudad': 'Parana', 'tags': 'a b'}
    """
    plano: Registro = {}
    for clave, valor in registro.items():
        nombre = f"{prefijo}{clave}"
        if isinstance(valor, dict):
            plano.update(aplanar(valor, f"{nombre}."))
        elif isinstance(valor, list):
            plano[nombre] = " ".join(str(item) for item in valor)
        else:
            plano[nombre] = valor
    return plano


def aplicar_filtro(
    registros: Iterable[Registro], filtro: Callable[[Registro], Registro]
) -> Iterator[Registro]:
    """Aplica un filtro a cada registro de forma perezosa.

    Args:
        registros: Coleccion de registros de entrada.
        filtro: Funcion a aplicar a cada registro.

    Returns:
        Un iterador perezoso con los registros ya transformados.

    Example:
        >>> list(aplicar_filtro([{"a": 1}], lambda r: r))
        [{'a': 1}]
    """
    return (filtro(registro) for registro in registros)


def obtener_campos(registros: Iterable[Registro]) -> list[str]:
    """Obtiene todas las claves presentes, preservando el orden de aparicion.

    Args:
        registros: Registros de los que se extraen las claves.

    Returns:
        Lista de nombres de campo sin repetir y en orden de primera
        aparicion, util para heterogeneity entre registros.

    Example:
        >>> obtener_campos([{"a": 1}, {"b": 2}])
        ['a', 'b']
    """
    campos: list[str] = []
    for registro in registros:
        for clave in registro:
            if clave not in campos:
                campos.append(clave)
    return campos


def escribir_csv(
    registros: Iterable[Registro], salida: TextIO, delimitador: str
) -> None:
    r"""Serializa los registros (ya filtrados) en formato CSV.

    Args:
        registros: Registros aplanados a escribir.
        salida: Flujo de texto abierto para escritura (archivo o stdout).
        delimitador: Caracter separador de columnas.

    Example:
        >>> import io
        >>> flujo = io.StringIO()
        >>> escribir_csv([{"a": 1, "b": 2}], flujo, ";")
        >>> flujo.getvalue()
        'a;b\\r\\n1;2\\r\\n'
    """
    registros = list(registros)
    if not registros:
        return
    campos = obtener_campos(registros)
    escritor = csv.DictWriter(
        salida, fieldnames=campos, delimiter=delimitador, extrasaction="ignore"
    )
    escritor.writeheader()
    escritor.writerows(registros)


def construir_parser() -> argparse.ArgumentParser:
    """Define los argumentos de linea de comandos.

    Returns:
        El parser con las opciones ``-i``, ``-o`` y ``-d``.

    Example:
        >>> args = construir_parser().parse_args(["-i", "a.json", "-d", ";"])
        >>> args.delimiter
        ';'
    """
    parser = argparse.ArgumentParser(
        description="Convierte datos en formato JSON a formato CSV."
    )
    parser.add_argument("-i", "--input", help="Archivo JSON de entrada.")
    parser.add_argument("-o", "--output", help="Archivo CSV de salida.")
    parser.add_argument(
        "-d",
        "--delimiter",
        default=",",
        help="Delimitador a utilizar (por defecto ',').",
    )
    return parser


def leer_datos(origen: str | None) -> Any:
    """Carga el JSON desde un archivo o, si es ``None``, desde stdin.

    Args:
        origen: Ruta del archivo JSON, o ``None`` para usar entrada estandar.

    Returns:
        La estructura de datos leida, todavia sin normalizar.

    Raises:
        OSError: Si el archivo no existe o no se puede leer.
        json.JSONDecodeError: Si el contenido no es JSON valido.

    Example:
        >>> import io, json, sys
        >>> sys.stdin = io.StringIO('{"id": 1}')
        >>> leer_datos(None)
        {'id': 1}
    """
    if origen:
        with Path(origen).open(encoding="utf-8-sig") as archivo:
            return json.load(archivo)
    return json.load(sys.stdin)


def ejecutar(args: argparse.Namespace, entrada: TextIO, salida: TextIO) -> int:
    """Ejecuta la conversion sobre los flujos indicados.

    Args:
        args: Namespace con ``input``, ``output`` y ``delimiter``.
        entrada: Flujo del JSON de entrada (para simular stdin en tests).
        salida: Flujo donde se emite el CSV (para simular stdout en tests).

    Returns:
        Codigo de salida: 0 si todo ok, 1 ante cualquier error controlado.

    Example:
        >>> import io
        >>> import sys
        >>> argumentos = construir_parser().parse_args([])
        >>> ejecutar(argumentos, io.StringIO('[{"a": 1}]'), io.StringIO())
        0
    """
    try:
        datos = json.load(entrada) if not args.input else leer_datos(args.input)
        registros = aplicar_filtro(normalizar(datos), aplanar)

        if args.output:
            with Path(args.output).open("w", encoding="utf-8", newline="") as archivo:
                escribir_csv(registros, archivo, args.delimiter)
        else:
            escribir_csv(registros, salida, args.delimiter)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    """Punto de entrada: parsea argumentos y lanza la conversion."""
    args = construir_parser().parse_args()
    sys.exit(ejecutar(args, sys.stdin, sys.stdout))


if __name__ == "__main__":
    main()
