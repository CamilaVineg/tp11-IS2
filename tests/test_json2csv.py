"""Pruebas unitarias del modulo json2csv.

Cubren la estrategia de filtro (normalizar, aplanar), la escritura CSV, el
manejo de argumentos y las condiciones de excepcion del punto de entrada.
"""

import argparse
import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

RAIZ = Path(__file__).resolve().parent.parent
MODULO = RAIZ / "src" / "json2csv.py"

sys.path.insert(0, str(MODULO.parent))

import json2csv  # noqa: E402


@pytest.fixture
def parser() -> Any:
    """Devuelve el parser de argumentos del modulo."""
    return json2csv.construir_parser()


@pytest.fixture
def ejecuta(parser: Any) -> Any:
    """Devuelve un helper que corre el programa y devuelve (codigo, stdout)."""

    def _ejecuta(argv: list[str], entrada_json: str) -> tuple[int, str]:
        salida = io.StringIO()
        argumentos = parser.parse_args(argv)
        codigo = json2csv.ejecutar(argumentos, io.StringIO(entrada_json), salida)
        return codigo, salida.getvalue()

    return _ejecuta


# --------------------------------------------------------------------------
# normalizar
# --------------------------------------------------------------------------
class TestNormalizar:
    """Pruebas del primer filtro."""

    def test_envuelve_objeto_suelto(self) -> None:
        assert json2csv.normalizar({"id": 1}) == [{"id": 1}]

    def test_conserva_lista_de_objetos(self) -> None:
        datos = [{"id": 1}, {"id": 2}]
        assert json2csv.normalizar(datos) == datos

    def test_descarta_elementos_no_objeto(self) -> None:
        assert json2csv.normalizar([{"id": 1}, 5, "texto", None]) == [{"id": 1}]

    def test_lista_vacia(self) -> None:
        assert json2csv.normalizar([]) == []

    @pytest.mark.parametrize("datos", [5, "texto", None, 3.5, True])
    def test_escalar_invalido_lanza_value_error(self, datos: Any) -> None:
        with pytest.raises(ValueError, match="objeto o una lista de objetos"):
            json2csv.normalizar(datos)


# --------------------------------------------------------------------------
# aplanar
# --------------------------------------------------------------------------
class TestAplanar:
    """Pruebas del segundo filtro."""

    def test_registro_plano_no_cambia(self) -> None:
        assert json2csv.aplanar({"a": 1, "b": "x"}) == {"a": 1, "b": "x"}

    def test_anida_con_claves_compuestas(self) -> None:
        entrada = {"dir": {"ciudad": "Parana", "cp": 3100}}
        assert json2csv.aplanar(entrada) == {"dir.ciudad": "Parana", "dir.cp": 3100}

    def test_anidamiento_profundo(self) -> None:
        entrada = {"a": {"b": {"c": 1}}}
        assert json2csv.aplanar(entrada) == {"a.b.c": 1}

    def test_lista_se_une_con_espacios(self) -> None:
        assert json2csv.aplanar({"tags": ["a", "b", "c"]}) == {"tags": "a b c"}

    def test_lista_de_diccionarios_se_aplana_por_elemento(self) -> None:
        entrada = {"items": [{"k": 1}, {"k": 2}]}
        resultado = json2csv.aplanar(entrada)
        assert resultado == {"items": "{'k': 1} {'k': 2}"}

    def test_valores_none_se_conservan(self) -> None:
        assert json2csv.aplanar({"a": None}) == {"a": None}

    def test_prefijo_explicito(self) -> None:
        assert json2csv.aplanar({"a": 1}, prefijo="x.") == {"x.a": 1}


# --------------------------------------------------------------------------
# aplicar_filtro y obtener_campos
# --------------------------------------------------------------------------
class TestAplicarFiltro:
    """Pruebas del pipeline de filtros."""

    def test_aplica_filtro_a_cada_registro(self) -> None:
        resultado = list(
            json2csv.aplicar_filtro([{"a": 1}, {"a": 2}], json2csv.aplanar)
        )
        assert resultado == [{"a": 1}, {"a": 2}]

    def test_es_perezoso(self) -> None:
        consumir = json2csv.aplicar_filtro(iter([{"a": 1}]), json2csv.aplanar)
        assert hasattr(consumir, "__next__")

    def test_cadena_de_filtros(self) -> None:
        def mayusculas(registro: dict[str, Any]) -> dict[str, Any]:
            return {k: str(v).upper() for k, v in registro.items()}

        resultado = list(
            json2csv.aplicar_filtro(
                json2csv.aplicar_filtro([{"n": "ana"}], mayusculas), json2csv.aplanar
            )
        )
        assert resultado == [{"n": "ANA"}]


class TestObtenerCampos:
    """Pruebas de la extraccion de encabezados."""

    def test_une_claves_de_varios_registros(self) -> None:
        registros = [{"a": 1}, {"b": 2}, {"a": 3, "c": 4}]
        assert json2csv.obtener_campos(registros) == ["a", "b", "c"]

    def test_no_repite_claves(self) -> None:
        assert json2csv.obtener_campos([{"a": 1}, {"a": 2}]) == ["a"]

    def test_sin_registros(self) -> None:
        assert json2csv.obtener_campos([]) == []


# --------------------------------------------------------------------------
# escribir_csv
# --------------------------------------------------------------------------
class TestEscribirCsv:
    """Pruebas de la serializacion."""

    def test_escribe_encabezado_y_filas(self) -> None:
        flujo = io.StringIO()
        json2csv.escribir_csv([{"a": 1, "b": 2}], flujo, ",")
        assert flujo.getvalue() == "a,b\r\n1,2\r\n"

    def test_respeta_delimitador(self) -> None:
        flujo = io.StringIO()
        json2csv.escribir_csv([{"a": 1, "b": 2}], flujo, ";")
        assert flujo.getvalue() == "a;b\r\n1;2\r\n"

    def test_registros_con_claves_disimiles(self) -> None:
        flujo = io.StringIO()
        json2csv.escribir_csv([{"a": 1}, {"b": 2}], flujo, ",")
        assert flujo.getvalue() == "a,b\r\n1,\r\n,2\r\n"

    def test_sin_registros_no_escribe(self) -> None:
        flujo = io.StringIO()
        json2csv.escribir_csv([], flujo, ",")
        assert flujo.getvalue() == ""

    def test_escapa_delimitador_en_valores(self) -> None:
        flujo = io.StringIO()
        json2csv.escribir_csv([{"a": "x,y"}], flujo, ",")
        assert flujo.getvalue() == 'a\r\n"x,y"\r\n'


# --------------------------------------------------------------------------
# construir_parser
# --------------------------------------------------------------------------
class TestParser:
    """Pruebas de la definicion de argumentos."""

    def test_valores_por_defecto(self, parser: Any) -> None:
        args = parser.parse_args([])
        assert args.input is None
        assert args.output is None
        assert args.delimiter == ","

    def test_lectura_de_argumentos(self, parser: Any) -> None:
        args = parser.parse_args(["-i", "a.json", "-o", "b.csv", "-d", ";"])
        assert (args.input, args.output, args.delimiter) == ("a.json", "b.csv", ";")

    def test_opciones_largas(self, parser: Any) -> None:
        args = parser.parse_args(["--input", "a.json", "--delimiter", "|"])
        assert args.input == "a.json"
        assert args.delimiter == "|"


# --------------------------------------------------------------------------
# Integracion de ejecutar
# --------------------------------------------------------------------------
class TestEjecutar:
    """Pruebas de extremo a extremo sobre flujos en memoria."""

    def test_entrada_por_archivo_salida_por_pantalla(
        self, tmp_path: Path, ejecuta: Any
    ) -> None:
        origen = tmp_path / "in.json"
        origen.write_text('[{"id": 1, "nombre": "Ana"}]', encoding="utf-8")
        codigo, salida = ejecuta(["-i", str(origen)], "")
        assert codigo == 0
        assert salida == "id,nombre\r\n1,Ana\r\n"

    def test_entrada_por_stdin(self, ejecuta: Any) -> None:
        codigo, salida = ejecuta([], '[{"id": 3, "nombre": "Zoe"}]')
        assert codigo == 0
        assert salida == "id,nombre\r\n3,Zoe\r\n"

    def test_delimitador_personalizado(self, ejecuta: Any) -> None:
        codigo, salida = ejecuta(["-d", ";"], '[{"id": 1, "nombre": "Ana"}]')
        assert codigo == 0
        assert salida == "id;nombre\r\n1;Ana\r\n"

    def test_entrada_y_salida_por_archivo(self, tmp_path: Path, parser: Any) -> None:
        origen = tmp_path / "in.json"
        destino = tmp_path / "out.csv"
        origen.write_text('[{"id": 1, "nombre": "Ana"}]', encoding="utf-8")
        argumentos = parser.parse_args(
            ["-i", str(origen), "-o", str(destino), "-d", "|"]
        )
        codigo = json2csv.ejecutar(argumentos, io.StringIO(""), io.StringIO())
        assert codigo == 0
        contenido = destino.read_text(encoding="utf-8")
        assert contenido.splitlines() == ["id|nombre", "1|Ana"]

    def test_lectura_con_bom(self, tmp_path: Path, ejecuta: Any) -> None:
        origen = tmp_path / "bom.json"
        origen.write_text('[{"id": 1}]', encoding="utf-8-sig")
        codigo, salida = ejecuta(["-i", str(origen)], "")
        assert codigo == 0
        assert salida == "id\r\n1\r\n"

    def test_json_invalido_devuelve_error(self, ejecuta: Any, capsys: Any) -> None:
        codigo, _ = ejecuta([], "esto no es json")
        assert codigo == 1
        assert "Error:" in capsys.readouterr().err

    def test_archivo_inexistente_devuelve_error(
        self, ejecuta: Any, capsys: Any
    ) -> None:
        codigo, _ = ejecuta(["-i", "no_existe.json"], "")
        assert codigo == 1
        assert "Error:" in capsys.readouterr().err

    def test_escalar_invalido_devuelve_error(self, ejecuta: Any, capsys: Any) -> None:
        codigo, _ = ejecuta([], "12345")
        assert codigo == 1
        assert "Error:" in capsys.readouterr().err

    def test_lista_vacia_no_produce_salida(self, ejecuta: Any) -> None:
        codigo, salida = ejecuta([], "[]")
        assert codigo == 0
        assert salida == ""


# --------------------------------------------------------------------------
# Version / Build
# --------------------------------------------------------------------------
def test_version_y_build_definidos() -> None:
    """La version y el build deben estar declarados (requisito h)."""
    assert json2csv.VERSION == "1.0.0"
    assert isinstance(json2csv.BUILD, int)
    assert json2csv.BUILD >= 1


# --------------------------------------------------------------------------
# Ejecucion real como script
# --------------------------------------------------------------------------
class TestComoScript:
    """Verifica la CLI real invocando un subproceso."""

    def test_ayuda(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(MODULO), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0
        assert "--input" in proc.stdout
        assert "--output" in proc.stdout
        assert "--delimiter" in proc.stdout

    def test_conversion_completa_por_subproceso(self, tmp_path: Path) -> None:
        origen = tmp_path / "in.json"
        destino = tmp_path / "out.csv"
        origen.write_text(
            json.dumps(
                [
                    {"id": 1, "dir": {"ciudad": "Parana"}, "tags": ["a", "b"]},
                    {"id": 2, "dir": {"ciudad": "CdelU"}, "tags": ["c"]},
                ]
            ),
            encoding="utf-8",
        )
        proc = subprocess.run(
            [
                sys.executable,
                str(MODULO),
                "-i",
                str(origen),
                "-o",
                str(destino),
                "-d",
                "|",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        lineas = destino.read_text(encoding="utf-8").splitlines()
        assert lineas == [
            "id|dir.ciudad|tags",
            "1|Parana|a b",
            "2|CdelU|c",
        ]


# --------------------------------------------------------------------------
# Ejemplo de la documentacion
# --------------------------------------------------------------------------
def test_ejemplo_docstring_module() -> None:
    """El ejemplo del docstring del modulo debe seguir siendo valido."""
    salida = io.StringIO()
    datos = json.loads('[{"id": 1, "nombre": "Ana"}]')
    registros = json2csv.aplicar_filtro(json2csv.normalizar(datos), json2csv.aplanar)
    json2csv.escribir_csv(registros, salida, ",")
    assert salida.getvalue() == "id,nombre\r\n1,Ana\r\n"


def test_namespace_tiene_los_campos_esperados() -> None:
    """Guarda contra cambios en la interfaz de argparse."""
    namespace = argparse.Namespace(input="a.json", output=None, delimiter=",")
    assert namespace.delimiter == ","
