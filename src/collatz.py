"""Modulo para el computo y verificacion de la Conjetura de Collatz.

La conjetura afirma que, aplicando reiteradamente la regla

- si el numero es par, se divide por dos;
- si el numero es impar, se multiplica por tres y se suma uno,

toda secuencia de enteros positivos termina en 1. Este modulo cuenta cuantas
iteraciones se necesitan para alcanzarlo.

Uso:
    python collatz.py

Attributes:
    VERSION: Version del modulo segun Semantic Versioning.
    BUILD: Numero de build incremental, incrementado en cada entrega.
    MINIMO: Menor valor aceptado por :func:`collatz`.
    MAXIMO: Mayor valor aceptado por :func:`collatz`.

Example:
    >>> collatz(27)
    111
"""

import sys

VERSION = "1.0.0"
BUILD = 1
MINIMO = 1
MAXIMO = 1999


def collatz(num: int) -> int:
    """Calcula el numero de iteraciones necesarias para alcanzar el valor 1.

    Args:
        num: Entero positivo de partida.

    Returns:
        Cantidad de pasos aplicados hasta llegar a 1.

    Raises:
        ValueError: Si ``num`` no es un entero positivo dentro del rango
            aceptado. Sin esta validacion la conjetura no esta definida para
            cero ni para negativos y el bucle no terminaria.

    Example:
        >>> collatz(6)
        8
        >>> collatz(1)
        0
    """
    if not MINIMO <= num <= MAXIMO:
        raise ValueError(
            f"El número debe ser un entero en el rango [{MINIMO}, {MAXIMO}]."
        )

    iteraciones = 0
    valor = num
    while valor != 1:
        if valor % 2 == 0:
            valor //= 2
        else:
            valor = 3 * valor + 1
        iteraciones += 1
    return iteraciones


def main() -> None:
    """Punto de entrada: captura, valida y ejecuta el calculo.

    Solicita un numero por entrada estandar y muestra el resultado. Ante
    cualquier entrada invalida imprime un mensaje por salida de error y
    termina con codigo de salida 1.
    """
    try:
        entrada = input(
            f"Ingrese un número entero positivo ({MINIMO} a {MAXIMO}): "
        ).strip()
        num = int(entrada)
    except ValueError:
        print("Error: Debe ingresar un valor numérico entero válido.")
        sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        print("\nError: Entrada cancelada.")
        sys.exit(1)

    try:
        pasos = collatz(num)
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)

    print(f"El número de iteraciones para {num} es {pasos}\n")


if __name__ == "__main__":
    main()
