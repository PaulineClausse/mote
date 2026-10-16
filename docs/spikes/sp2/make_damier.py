"""Damier de calibration pour SP-2, en PDF vectoriel A4 paysage, sans dépendance.

  python docs/spikes/sp2/make_damier.py                      # damier_A4.pdf : 10 x 7 cases de 25 mm
  python docs/spikes/sp2/make_damier.py --cols 8 --rows 5 --square 30 --out damier_30mm.pdf

Le damier a une dimension paire et l'autre impaire : son orientation n'est jamais ambiguë pour la détection des coins.
Une réglette de 100 mm permet de vérifier, à la règle, que l'impression est en taille réelle.
Les dimensions sont des réglages : un autre format de papier ou d'autres cases se génèrent de la même façon.
"""
from __future__ import annotations

import argparse
from pathlib import Path

MM = 72 / 25.4                       # points PDF par millimètre
PAGES = {"A4": (297.0, 210.0), "A3": (420.0, 297.0), "LETTER": (279.4, 215.9)}   # paysage, mm


def pdf(objects: list[bytes]) -> bytes:
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for o in offsets:
        out += b"%010d 00000 n \n" % o
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    return bytes(out)


def text(x_mm: float, y_mm: float, size: float, s: str) -> bytes:
    enc = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("cp1252")
    return b"BT /F1 %.2f Tf %.3f %.3f Td (" % (size, x_mm * MM, y_mm * MM) + enc + b") Tj ET\n"


def damier(cols: int, rows: int, square_mm: float, page: str) -> bytes:
    pw, ph = PAGES[page]
    bw, bh = cols * square_mm, rows * square_mm
    if bw > pw - 20 or bh > ph - 30:
        raise SystemExit(f"{cols} x {rows} cases de {square_mm} mm ne tiennent pas sur une page {page}")
    x0 = (pw - bw) / 2
    y0 = (ph - bh) / 2 + 5                        # place sous le damier pour la réglette et la légende
    ops = bytearray(b"0 g\n")
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2 == 0:
                ops += b"%.3f %.3f %.3f %.3f re\n" % ((x0 + c * square_mm) * MM, (y0 + r * square_mm) * MM,
                                                     square_mm * MM, square_mm * MM)
    ops += b"f\n"
    # Réglette de 100 mm, graduée tous les 10 mm.
    ry = y0 - 9
    ops += b"0.4 w %.3f %.3f m %.3f %.3f l S\n" % (x0 * MM, ry * MM, (x0 + 100) * MM, ry * MM)
    for k in range(11):
        h = 3 if k % 5 == 0 else 1.5
        ops += b"%.3f %.3f m %.3f %.3f l S\n" % ((x0 + 10 * k) * MM, ry * MM, (x0 + 10 * k) * MM, (ry + h) * MM)
    ops += text(x0 + 103, ry - 1, 8, "100 mm : à vérifier à la règle (impression en taille réelle, 100 %)")
    inner = f"{cols - 1} x {rows - 1} coins intérieurs"
    ops += text(x0, y0 + bh + 3, 9,
                f"mote SP-2 : damier {cols} x {rows} cases de {square_mm:g} mm ({inner}). "
                f"Coller bien à plat sur un support rigide.")
    content = bytes(ops)
    return pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.3f %.3f] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>" % (pw * MM, ph * MM),
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cols", type=int, default=10, help="cases en largeur (défaut 10)")
    ap.add_argument("--rows", type=int, default=7, help="cases en hauteur (défaut 7)")
    ap.add_argument("--square", type=float, default=25.0, help="côté d'une case en mm (défaut 25)")
    ap.add_argument("--page", choices=sorted(PAGES), default="A4")
    ap.add_argument("--out", type=Path, default=Path(__file__).with_name("damier_A4.pdf"))
    a = ap.parse_args()
    if (a.cols + a.rows) % 2 == 0:
        raise SystemExit("une dimension paire et l'autre impaire, pour une orientation sans ambiguïté")
    a.out.write_bytes(damier(a.cols, a.rows, a.square, a.page))
    print(a.out)


if __name__ == "__main__":
    main()
