"""Pruebas unitarias del modulo collatz.

Cubren el conteo de iteraciones, los limites del rango aceptado y las
condiciones de excepcion del punto de entrada.
"""

import io
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
MODULO = RAIZ / "src" / "collatz.py"

sys.path.insert(0, str(MODULO.parent))

import collatz as modulo  # noqa: E402


# --------------------------------------------------------------------------
# collatz
# --------------------------------------------------------------------------
class TestCollatz:
    """Pruebas del conteo de iteraciones."""

    @pytest.mark.parametrize(
        ("numero", "esperado"),
        [
            (1, 0),
            (2, 1),
            (3, 7),
            (6, 8),
            (7, 16),
            (27, 111),
        ],
    )
    def test_iteraciones_conocidas(self, numero: int, esperado: int) -> None:
        assert modulo.collatz(numero) == esperado

    def test_toda_la_secuencia_termina_en_uno(self) -> None:
        for numero in range(1, 300):
            valor = numero
            pasos = 0
            while valor != 1 and pasos < 20000:
                valor = valor // 2 if valor % 2 == 0 else 3 * valor + 1
                pasos += 1
            assert valor == 1, f"la secuencia de {numero} no llega a 1"

    def test_no_modifica_el_argumento(self) -> None:
        numero = 27
        modulo.collatz(numero)
        assert numero == 27

    @pytest.mark.parametrize("numero", [0, -1, -100, modulo.MAXIMO + 1, 10_000])
    def test_valor_fuera_de_rango_lanza_value_error(self, numero: int) -> None:
        with pytest.raises(ValueError, match="rango"):
            modulo.collatz(numero)

    @pytest.mark.parametrize("numero", [modulo.MINIMO, modulo.MAXIMO])
    def test_los_extremos_del_rango_son_validos(self, numero: int) -> None:
        assert modulo.collatz(numero) >= 0


# --------------------------------------------------------------------------
# Constantes de version
# --------------------------------------------------------------------------
def test_version_y_build_definidos() -> None:
    """La version y el build deben estar declarados (requisito h)."""
    assert modulo.VERSION == "1.0.0"
    assert isinstance(modulo.BUILD, int)
    assert modulo.BUILD >= 1


def test_rango_expuesto() -> None:
    """El rango aceptado debe estar definido y ser coherente."""
    assert modulo.MINIMO < modulo.MAXIMO


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
class TestMain:
    """Pruebas del punto de entrada con la entrada simulada."""

    def test_entrada_valida_muestra_el_resultado(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "27")
        modulo.main()
        salida = capsys.readouterr().out
        assert "El número de iteraciones para 27 es 111" in salida

    def test_texto_no_numerico_terminia_con_error(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "abc")
        with pytest.raises(SystemExit) as excinfo:
            modulo.main()
        assert excinfo.value.code == 1
        assert "Error:" in capsys.readouterr().out

    def test_numero_fuera_de_rango_terminia_con_error(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "0")
        with pytest.raises(SystemExit) as excinfo:
            modulo.main()
        assert excinfo.value.code == 1
        assert "rango" in capsys.readouterr().out

    def test_entrada_cancelada_terminia_con_error(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        def lanzar(_: str) -> str:
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", lanzar)
        with pytest.raises(SystemExit) as excinfo:
            modulo.main()
        assert excinfo.value.code == 1
        assert "cancelada" in capsys.readouterr().out

    def test_sin_entrada_terminia_con_error(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        def lanzar(_: str) -> str:
            raise EOFError

        monkeypatch.setattr("builtins.input", lanzar)
        with pytest.raises(SystemExit) as excinfo:
            modulo.main()
        assert excinfo.value.code == 1
        assert "cancelada" in capsys.readouterr().out


# --------------------------------------------------------------------------
# Ejecucion real como script
# --------------------------------------------------------------------------
class TestComoScript:
    """Verifica el comportamiento de la CLI real."""

    def test_ayuda_por_codigo_de_salida(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(MODULO)],
            input="27\n",
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0
        assert "111" in proc.stdout

    def test_entrada_invalida_devuelve_codigo_1(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(MODULO)],
            input="no es un numero\n",
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 1
        assert "Error:" in proc.stdout


# --------------------------------------------------------------------------
# Ejemplo de la documentacion
# --------------------------------------------------------------------------
def test_ejemplo_docstring_modulo() -> None:
    """El ejemplo del docstring del modulo debe seguir siendo valido."""
    salida = io.StringIO()
    assert modulo.collatz(27) == 111
    salida.write("ok")
    assert salida.getvalue() == "ok"
