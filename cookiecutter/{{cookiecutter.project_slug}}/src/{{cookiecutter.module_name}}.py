"""Modulo de ejemplo generado por CookieCutter.

Reemplace este contenido por la logica del proyecto. Todas las funciones
publicas deben tener docstring en formato PEP 257 porque ruff lo exige.

Attributes:
    VERSION: Version del modulo segun Semantic Versioning.
    BUILD: Numero de build incremental, incremented en cada entrega.
"""

VERSION = "{{cookiecutter.version}}"
BUILD = 1


def sumar(primero: int, segundo: int) -> int:
    """Suma dos numeros enteros.

    Args:
        primero: Primer sumando.
        segundo: Segundo sumando.

    Returns:
        La suma de ambos valores.

    Example:
        >>> sumar(2, 3)
        5
    """
    return primero + segundo
