#!/usr/bin/env python3
"""Renombra imágenes a nombres 'limpios' para que sus URLs de jsDelivr funcionen.

Espacios, mayúsculas y acentos rompen los links al pegarlos en Tiendup
(quedan como %20 y su editor no los digiere). Este script los normaliza:

    "LMTI Favicon PNG.png"  ->  lmti-favicon-png.png
    "Ñandú café.JPEG"       ->  nandu-cafe.jpeg
    "Mi_Foto__2.PNG"        ->  mi-foto-2.png

Sólo toca imágenes; deja intactos galeria.html, README.md, etc.
Nunca pisa un archivo existente (si el destino ya existe, lo saltea).
"""

import os
import re
import subprocess
import sys
import unicodedata

ROOT = "lmti/lmti-cursos-img"
EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif"}


def slug(stem: str) -> str:
    # Descompone los acentos y descarta las marcas, para no perder la letra base:
    # "ñ" -> "n" + tilde -> "n"   (no "" como haría iconv//TRANSLIT)
    n = unicodedata.normalize("NFKD", stem)
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = n.lower().replace(" ", "-").replace("_", "-")
    n = re.sub(r"[^a-z0-9.-]", "", n)
    n = re.sub(r"-+", "-", n).strip("-.")
    return n


def main() -> int:
    if not os.path.isdir(ROOT):
        print(f"No existe {ROOT}, nada que hacer.")
        return 0

    renamed = 0
    for dirpath, _dirs, files in os.walk(ROOT):
        for fname in sorted(files):
            stem, ext = os.path.splitext(fname)
            if ext.lower() not in EXTS:
                continue

            new_stem = slug(stem)
            if not new_stem:                      # nombre que queda vacío tras limpiar
                print(f"!! salteado (nombre no utilizable): {fname}")
                continue

            new_name = new_stem + ext.lower()
            if new_name == fname:
                continue

            src = os.path.join(dirpath, fname)
            dst = os.path.join(dirpath, new_name)
            if os.path.exists(dst):
                print(f"!! salteado (ya existe el destino): {new_name}")
                continue

            subprocess.run(["git", "mv", "--", src, dst], check=True)
            print(f"   {fname}  ->  {new_name}")
            renamed += 1

    print(f"\nArchivos renombrados: {renamed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
