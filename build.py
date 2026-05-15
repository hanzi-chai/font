#!/usr/bin/env python3
"""Build OTF, WOFF, and WOFF2 fonts from UFO sources in sources/masters/."""

import sys
from pathlib import Path
import ufo2ft
from defcon import Font
from fontTools.ttLib import TTFont


def _rename_ufo_glyphs(ufo) -> None:
    """Rename non-ASCII glyph names to uniXXXX in the in-memory UFO.

    CFF only allows latin-1 glyph names, so Chinese names must be converted
    before compiling. We operate on the in-memory defcon.Font rather than on
    disk so the source UFO is never modified.
    """
    layer = ufo.layers.defaultLayer
    rename = {}
    for glyph in layer:
        if not glyph.name.isascii():
            if glyph.unicodes:
                new_name = "uni" + "".join(f"{u:04X}" for u in glyph.unicodes)
            else:
                new_name = f"glyph{abs(hash(glyph.name)) % 100000:05d}"
            rename[glyph.name] = new_name

    for old, new in rename.items():
        layer[old].name = new  # defcon propagates the rename to the layer dict

    for glyph in layer:
        for component in glyph.components:
            if component.baseGlyph in rename:
                component.baseGlyph = rename[component.baseGlyph]

    if "public.glyphOrder" in ufo.lib:
        ufo.lib["public.glyphOrder"] = [
            rename.get(n, n) for n in ufo.lib["public.glyphOrder"]
        ]


def build(ufo_path: Path, dist_dir: Path) -> None:

    print(f"Compiling {ufo_path.name} ...")
    ufo = Font(str(ufo_path))
    _rename_ufo_glyphs(ufo)
    # useProductionNames=False: we already renamed; avoids an internal
    # save/reload that would fail on non-ASCII names.
    # optimizeCFF=0: skips subroutinization (also triggers a save internally).
    otf = ufo2ft.compileOTF(ufo, useProductionNames=False, optimizeCFF=0)

    # "Chai Sans-Regular" → "NotoSansChaiSC-Regular"
    stem = ufo_path.stem.replace(" ", "")
    dist_dir.mkdir(parents=True, exist_ok=True)

    otf_path = dist_dir / f"{stem}.otf"
    otf.save(str(otf_path))
    print(f"  → {otf_path.relative_to(Path.cwd())}")

    for flavor, ext in (("woff", ".woff"), ("woff2", ".woff2")):
        out = dist_dir / f"{stem}{ext}"
        f = TTFont(str(otf_path))
        f.flavor = flavor
        f.save(str(out))
        print(f"  → {out.relative_to(Path.cwd())}")


if __name__ == "__main__":
    root = Path(__file__).parent
    ufos = sorted((root / "sources" / "masters").glob("*.ufo"))
    if not ufos:
        sys.exit("No .ufo files found in sources/masters/")

    dist = root / "dist"
    for ufo in ufos:
        build(ufo, dist)

    print("Done.")
