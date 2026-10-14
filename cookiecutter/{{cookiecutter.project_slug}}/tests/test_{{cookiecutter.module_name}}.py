"""Pruebas unitarias de ejemplo. Reemplace por las pruebas del proyecto."""

import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import {{cookiecutter.module_name}} as modulo  # noqa: E402


def test_version_definida() -> None:
    """La version del modulo debe estar declarada."""
    assert modulo.VERSION == "{{cookiecutter.version}}"


def test_build_definido() -> None:
    """El numero de build debe ser un entero positivo."""
    assert isinstance(modulo.BUILD, int)
    assert modulo.BUILD >= 1


def test_sumar() -> None:
    """Verifica la suma de dos enteros."""
    assert modulo.sumar(2, 3) == 5


def test_sumar_negativos() -> None:
    """Verifica la suma con valores negativos."""
    assert modulo.sumar(-1, -2) == -3


def test_parametrizado() -> None:
    """Ejemplo de pruebas parametrizadas con pytest."""
    import pytest

    @pytest.mark.parametrize(
        ("a", "b", "esperado"),
        [(1, 1, 2), (0, 0, 0), (5, -5, 0)],
    )
    def _caso(a: Any, b: Any, esperado: Any) -> None:
        assert modulo.sumar(a, b) == esperado