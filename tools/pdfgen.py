"""Gerador de PDF mínimo, baseado apenas na biblioteca padrão do Python.

Produz um PDF paginado com suporte a títulos, parágrafos, marcadores, tabelas simples
e regras horizontais, usando as fontes base Helvetica (WinAnsi). Sem dependências
externas — necessário porque o sandbox está offline e não há pandoc/latex/reportlab.

Limitações conscientes: layout de fluxo simples (uma coluna), quebra de página
automática, quebra de linha por largura estimada de caractere. Suficiente para um
relatório de status legível e apresentável.
"""

from __future__ import annotations

import textwrap


# Métricas de página (A4, em pontos)
PAGE_W = 595.276
PAGE_H = 841.890
MARGIN = 56.0
CONTENT_W = PAGE_W - 2 * MARGIN

# Aproximação de largura média de caractere por ponto de fonte (Helvetica ~0.5 em).
CHAR_W_FACTOR = 0.50


# Mapa de caracteres tipográficos comuns (fora do latin-1) para code points WinAnsi.
_WINANSI_MAP = {
    "\u2013": 0o226,  # – en dash
    "\u2014": 0o227,  # — em dash
    "\u2018": 0o221,  # ‘ left single quote
    "\u2019": 0o222,  # ’ right single quote
    "\u201c": 0o223,  # " left double quote
    "\u201d": 0o224,  # " right double quote
    "\u2022": 0o225,  # • bullet
    "\u2026": 0o205,  # … ellipsis
    "\u2192": None,   # → (sem glifo WinAnsi) — substituído por "->"
}


def _esc(s: str) -> str:
    """Escapa caracteres especiais de string PDF e mapeia para WinAnsi."""
    out = []
    for ch in s:
        o = ord(ch)
        if ch in "()\\":
            out.append("\\" + ch)
        elif o < 128:
            out.append(ch)
        elif o <= 255:
            # latin-1 casa com os acentos usuais do português em WinAnsi
            out.append("\\%03o" % o)
        elif ch in _WINANSI_MAP:
            code = _WINANSI_MAP[ch]
            if code is None:
                out.append("->")
            else:
                out.append("\\%03o" % code)
        else:
            out.append("?")
    return "".join(out)


class _Block:
    pass


class PDF:
    """Documento de fluxo simples. Adicione blocos e chame save()."""

    def __init__(self):
        self.blocks: list[dict] = []

    # --- API de conteúdo ---------------------------------------------------
    def title(self, text: str):
        self.blocks.append({"t": "text", "s": text, "size": 20, "bold": True, "gap": 10})

    def h1(self, text: str):
        self.blocks.append({"t": "rule", "gap": 6})
        self.blocks.append({"t": "text", "s": text, "size": 14, "bold": True, "gap": 6})

    def h2(self, text: str):
        self.blocks.append({"t": "text", "s": text, "size": 11.5, "bold": True, "gap": 4})

    def para(self, text: str, size: float = 10):
        self.blocks.append({"t": "text", "s": text, "size": size, "bold": False, "gap": 5})

    def bullet(self, text: str, size: float = 10):
        self.blocks.append({"t": "text", "s": "•  " + text, "size": size, "bold": False,
                            "gap": 2, "indent": 10})

    def small(self, text: str):
        self.blocks.append({"t": "text", "s": text, "size": 8.5, "bold": False,
                            "gap": 4, "gray": True})

    def spacer(self, h: float = 6):
        self.blocks.append({"t": "space", "h": h})

    def rule(self):
        self.blocks.append({"t": "rule", "gap": 6})

    def table(self, headers: list[str], rows: list[list[str]], widths: list[float] | None = None):
        self.blocks.append({"t": "table", "headers": headers, "rows": rows, "widths": widths,
                            "gap": 8})

    # --- layout ------------------------------------------------------------
    def _wrap(self, text: str, size: float, width: float) -> list[str]:
        max_chars = max(4, int(width / (size * CHAR_W_FACTOR)))
        lines: list[str] = []
        for raw in text.split("\n"):
            if not raw:
                lines.append("")
                continue
            wrapped = textwrap.wrap(raw, width=max_chars, break_long_words=True,
                                    break_on_hyphens=False)
            lines.extend(wrapped or [""])
        return lines

    def _emit_text(self, streams, x, y, s, size, bold, gray=False):
        font = "F2" if bold else "F1"
        col = " 0.35 0.35 0.35 rg" if gray else " 0 0 0 rg"
        streams.append(
            f"BT /{font} {size:.1f} Tf{col} 1 0 0 1 {x:.2f} {y:.2f} Tm ({_esc(s)}) Tj ET"
        )

    def _build_pages(self):
        pages: list[list[str]] = []
        cur: list[str] = []
        y = PAGE_H - MARGIN

        def newpage():
            nonlocal cur, y
            if cur:
                pages.append(cur)
            cur = []
            y = PAGE_H - MARGIN

        def ensure(space):
            nonlocal y
            if y - space < MARGIN:
                newpage()

        for b in self.blocks:
            if b["t"] == "space":
                y -= b["h"]
                continue
            if b["t"] == "rule":
                ensure(b.get("gap", 6) + 4)
                cur.append(f"0.6 w 0.7 0.7 0.7 RG {MARGIN:.2f} {y:.2f} m {PAGE_W-MARGIN:.2f} {y:.2f} l S")
                y -= b.get("gap", 6)
                continue
            if b["t"] == "text":
                size = b["size"]
                lh = size * 1.35
                indent = b.get("indent", 0)
                lines = self._wrap(b["s"], size, CONTENT_W - indent)
                for ln in lines:
                    ensure(lh)
                    self._emit_text(cur, MARGIN + indent, y - size, ln, size,
                                    b.get("bold", False), b.get("gray", False))
                    y -= lh
                y -= b.get("gap", 4)
                continue
            if b["t"] == "table":
                headers = b["headers"]
                rows = b["rows"]
                ncol = len(headers)
                widths = b["widths"] or [CONTENT_W / ncol] * ncol
                size = 9.0
                lh = size * 1.3
                pad = 3.0

                def draw_row(cells, bold, yy):
                    # calcula linhas por célula
                    cell_lines = [self._wrap(str(c), size, widths[i] - 2 * pad)
                                  for i, c in enumerate(cells)]
                    rows_h = max(len(cl) for cl in cell_lines)
                    row_h = rows_h * lh + 2 * pad
                    # fundo do cabeçalho
                    if bold:
                        cur.append(f"0.90 0.90 0.90 rg {MARGIN:.2f} {yy-row_h:.2f} {CONTENT_W:.2f} {row_h:.2f} re f")
                    # texto
                    xoff = MARGIN
                    for i, cl in enumerate(cell_lines):
                        ty = yy - pad - size
                        for ln in cl:
                            self._emit_text(cur, xoff + pad, ty, ln, size, bold)
                            ty -= lh
                        xoff += widths[i]
                    # bordas horizontais
                    cur.append(f"0.4 w 0.75 0.75 0.75 RG {MARGIN:.2f} {yy:.2f} m {MARGIN+CONTENT_W:.2f} {yy:.2f} l S")
                    cur.append(f"{MARGIN:.2f} {yy-row_h:.2f} m {MARGIN+CONTENT_W:.2f} {yy-row_h:.2f} l S")
                    return row_h

                # cabeçalho
                ensure(lh * 2)
                y -= draw_row(headers, True, y)
                for r in rows:
                    # estimativa de altura para quebra de página
                    est = max(len(self._wrap(str(c), size, widths[i] - 2 * pad))
                              for i, c in enumerate(r)) * lh + 2 * pad
                    if y - est < MARGIN:
                        newpage()
                        y -= draw_row(headers, True, y)
                    y -= draw_row(r, False, y)
                y -= b.get("gap", 8)
                continue
        newpage()
        return pages

    # --- serialização PDF --------------------------------------------------
    def save(self, path: str):
        pages_content = self._build_pages()
        objects: list[str] = []

        # fontes
        # 1: F1 Helvetica, 2: F2 Helvetica-Bold
        # estrutura: catalog, pages, [page + content]*, fonts
        n_pages = len(pages_content)
        # ids: 1 catalog, 2 pages, fonts 3,4, depois pares page/content
        font_reg = 3
        font_bold = 4
        first_page_obj = 5

        page_obj_ids = []
        content_obj_ids = []
        for i in range(n_pages):
            page_obj_ids.append(first_page_obj + i * 2)
            content_obj_ids.append(first_page_obj + i * 2 + 1)

        # Catalog
        objects.append((1, "<< /Type /Catalog /Pages 2 0 R >>"))
        # Pages
        kids = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
        objects.append((2, f"<< /Type /Pages /Count {n_pages} /Kids [{kids}] >>"))
        # Fonts
        objects.append((font_reg, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"))
        objects.append((font_bold, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"))

        for i, content in enumerate(pages_content):
            pid = page_obj_ids[i]
            cid = content_obj_ids[i]
            page_dict = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W:.3f} {PAGE_H:.3f}] "
                f"/Resources << /Font << /F1 {font_reg} 0 R /F2 {font_bold} 0 R >> >> "
                f"/Contents {cid} 0 R >>"
            )
            objects.append((pid, page_dict))
            stream = "\n".join(content)
            objects.append((cid, f"<< /Length {len(stream.encode('latin-1', 'replace'))} >>\nstream\n{stream}\nendstream"))

        # ordena por id
        objects.sort(key=lambda o: o[0])
        max_id = objects[-1][0]

        # monta arquivo com xref
        out = bytearray()
        out += b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
        offsets = {}
        for oid, body in objects:
            offsets[oid] = len(out)
            out += f"{oid} 0 obj\n{body}\nendobj\n".encode("latin-1", "replace")

        xref_pos = len(out)
        out += f"xref\n0 {max_id+1}\n".encode()
        out += b"0000000000 65535 f \n"
        for oid in range(1, max_id + 1):
            if oid in offsets:
                out += f"{offsets[oid]:010d} 00000 n \n".encode()
            else:
                out += b"0000000000 65535 f \n"
        out += f"trailer\n<< /Size {max_id+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()

        with open(path, "wb") as fh:
            fh.write(out)
        return path
