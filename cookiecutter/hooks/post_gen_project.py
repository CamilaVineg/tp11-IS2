"""Hook executed after Cookiecutter renders the project template.

Verifica que el modulo principal y su carpeta de pruebas se hayan generado y
muestra los siguientes pasos al usuario.
"""

import sys
from pathlib import Path

RAIZ = Path.cwd()


def main() -> int:
    """Comprueba la estructura generada y resume los comandos de uso."""
    modulo = RAIZ / "src" / f"{sys.argv[1]}.py" if len(sys.argv) > 1 else None

    if not (RAIZ / "tests").is_dir():
        print("ERROR: no se genero la carpeta tests/", file=sys.stderr)
        return 1

    print("Proyecto generado correctamente.")
    if modulo is not None:
        print(f"  Modulo principal: {modulo}")
    print("  Siguientes pasos:")
    print("    python -m venv .venv")
    print("    .venv\\Scripts\\pip install -r requirements-dev.txt")
    print("    .venv\\Scripts\\python -m pytest")
    return 0


if __name__ == "__main__":
    sys.exit(main())