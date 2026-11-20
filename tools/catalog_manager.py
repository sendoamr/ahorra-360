#!/usr/bin/env python3
"""Excel-based catalogue manager for Ahorra360. Requires openpyxl."""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.utils import get_column_letter
except ImportError:
    print("Falta openpyxl. Instálalo con: python -m pip install openpyxl", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "data" / "opportunities.json"
FIELDS = [
    "id", "slug", "title", "subtitle", "category", "scope", "region",
    "status", "statusLabel", "amount", "amountNote", "audience",
    "requirements", "howTo", "deadline", "notes", "verifiedAt",
    "reviewFrequency", "confidence", "editorialStatus",
]
REQUIRED = [
    "id", "slug", "title", "category", "scope", "region", "status",
    "statusLabel", "amount", "audience", "requirements", "verifiedAt",
    "editorialStatus",
]
CATEGORIES = ["vivienda", "suministros", "reformas", "fiscalidad", "transporte", "familia", "educacion", "otros"]
STATUSES = ["vigente", "permanente", "proxima", "informativo", "revision", "cerrada"]
EDITORIAL = ["draft", "published", "archived", "pending_review"]
CONFIDENCE = ["alta", "media", "baja"]
SOURCE_TYPES = ["primary", "official", "secondary"]

def slugify(value: str) -> str:
    import unicodedata
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value

def load_catalog(path: Path) -> list[dict]:
    if not path.exists():
        raise ValueError(f"No existe el catálogo: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("El catálogo debe ser una lista JSON.")
    return data

def validate_catalog(items: list[dict]) -> list[str]:
    errors = []
    ids, slugs = set(), set()
    for n, item in enumerate(items, start=1):
        label = item.get("title") or f"fila {n}"
        if not isinstance(item, dict):
            errors.append(f"Fila {n}: no es un objeto.")
            continue
        for key in REQUIRED:
            value = item.get(key)
            if value is None or value == "" or value == []:
                errors.append(f"{label}: falta el campo obligatorio '{key}'.")
        ident, slug = item.get("id"), item.get("slug")
        if ident in ids:
            errors.append(f"{label}: ID duplicado '{ident}'.")
        if slug in slugs:
            errors.append(f"{label}: slug duplicado '{slug}'.")
        if ident: ids.add(ident)
        if slug: slugs.add(slug)
        if item.get("category") and item["category"] not in CATEGORIES:
            errors.append(f"{label}: categoría '{item['category']}' no reconocida.")
        if item.get("status") and item["status"] not in STATUSES:
            errors.append(f"{label}: estado '{item['status']}' no reconocido.")
        if item.get("editorialStatus") and item["editorialStatus"] not in EDITORIAL:
            errors.append(f"{label}: editorialStatus '{item['editorialStatus']}' no reconocido.")
        verified = item.get("verifiedAt")
        if verified:
            try: date.fromisoformat(str(verified))
            except ValueError: errors.append(f"{label}: verifiedAt debe tener formato AAAA-MM-DD.")
        reqs = item.get("requirements")
        if not isinstance(reqs, list) or not reqs or not all(isinstance(x, str) and x.strip() for x in reqs):
            errors.append(f"{label}: requirements debe contener al menos un requisito.")
        sources = item.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label}: añade al menos una fuente.")
        else:
            for s in sources:
                if not isinstance(s, dict) or not s.get("name") or not s.get("url"):
                    errors.append(f"{label}: cada fuente necesita nombre y URL.")
                    continue
                parsed = urlparse(s["url"])
                if parsed.scheme not in ("http", "https") or not parsed.netloc:
                    errors.append(f"{label}: URL no válida en fuente '{s.get('name')}'.")
    return errors

def style_header(ws):
    fill = PatternFill("solid", fgColor="176B45")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = fill
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

def set_widths(ws, widths):
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

def export_xlsx(catalog_path: Path, output: Path):
    items = load_catalog(catalog_path)
    errors = validate_catalog(items)
    if errors:
        print("Aviso: el catálogo actual contiene observaciones:")
        for e in errors: print(" -", e)
    wb = Workbook()
    ws = wb.active
    ws.title = "Oportunidades"
    ws.append(FIELDS)
    for item in items:
        row = []
        for field in FIELDS:
            value = item.get(field, "")
            if field == "requirements":
                value = "\n".join(value) if isinstance(value, list) else str(value or "")
            row.append(value)
        ws.append(row)
    style_header(ws)
    widths = {"A":34,"B":38,"C":52,"D":55,"E":18,"F":18,"G":28,"H":18,"I":55,"J":22,"K":55,"L":60,"M":65,"N":70,"O":60,"P":70,"Q":16,"R":20,"S":16,"T":22}
    set_widths(ws, widths)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        ws.row_dimensions[row[0].row].height = 60
    # Drop-downs reduce typing errors.
    for col, values in [("E", CATEGORIES), ("H", STATUSES), ("S", CONFIDENCE), ("T", EDITORIAL)]:
        dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}5000")

    src = wb.create_sheet("Fuentes")
    src.append(["opportunity_id", "name", "url", "type"])
    for item in items:
        for source in item.get("sources", []):
            src.append([item.get("id", ""), source.get("name", ""), source.get("url", ""), source.get("type", "primary")])
    style_header(src)
    set_widths(src, {"A":38,"B":55,"C":90,"D":20})
    for row in src.iter_rows(min_row=2):
        for cell in row: cell.alignment = Alignment(vertical="top", wrap_text=True)
    dv = DataValidation(type="list", formula1='"' + ",".join(SOURCE_TYPES) + '"', allow_blank=False)
    src.add_data_validation(dv)
    dv.add("D2:D10000")

    guide = wb.create_sheet("LEEME")
    guide.append(["GUÍA DE EDICIÓN DEL CATÁLOGO AHORRA360"])
    guide.append(["1", "Edita o añade filas en Oportunidades. No cambies los nombres de las columnas."])
    guide.append(["2", "En requirements, escribe un requisito por línea dentro de la celda."])
    guide.append(["3", "Añade las fuentes en Fuentes; opportunity_id debe coincidir exactamente con el id de Oportunidades."])
    guide.append(["4", "Cada oportunidad publicada debe tener al menos una fuente oficial/primaria y verifiedAt."])
    guide.append(["5", "Para retirar una ficha, cambia editorialStatus a archived; no borres el registro."])
    guide.append(["6", "La importación actualiza por id y conserva fichas que no aparezcan en el Excel."])
    guide.append(["7", "El script valida estructura y URLs, pero no comprueba que la ayuda siga abierta ni que la fuente diga la verdad."])
    guide.column_dimensions["A"].width = 12
    guide.column_dimensions["B"].width = 125
    guide["A1"].font = Font(bold=True, size=14, color="176B45")
    for row in guide.iter_rows():
        for cell in row: cell.alignment = Alignment(vertical="top", wrap_text=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    print(f"Excel exportado: {output} ({len(items)} oportunidades).")

def cell_text(value):
    if value is None: return ""
    if isinstance(value, (datetime, date)): return value.isoformat()[:10]
    return str(value).strip()

def import_xlsx(input_path: Path, catalog_path: Path, replace: bool = False):
    wb = load_workbook(input_path, data_only=True)
    if "Oportunidades" not in wb.sheetnames or "Fuentes" not in wb.sheetnames:
        raise ValueError("El Excel debe contener las hojas 'Oportunidades' y 'Fuentes'.")
    ws = wb["Oportunidades"]
    headers = [cell_text(c.value) for c in ws[1]]
    missing = [f for f in FIELDS if f not in headers]
    if missing: raise ValueError("Faltan columnas: " + ", ".join(missing))
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        record = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
        if not any(v not in (None, "") for v in record.values()): continue
        item = {}
        for field in FIELDS:
            value = record.get(field)
            if field == "requirements":
                item[field] = [x.strip(" •-\t") for x in cell_text(value).splitlines() if x.strip(" •-\t")]
            elif field == "verifiedAt":
                item[field] = cell_text(value)
            else:
                item[field] = cell_text(value)
        if not item.get("slug") and item.get("title"):
            item["slug"] = slugify(item["title"])
        rows.append(item)

    sources_by_id = {}
    sws = wb["Fuentes"]
    sheaders = [cell_text(c.value) for c in sws[1]]
    required_source_cols = ["opportunity_id", "name", "url", "type"]
    if any(c not in sheaders for c in required_source_cols):
        raise ValueError("La hoja Fuentes necesita columnas: " + ", ".join(required_source_cols))
    for row in sws.iter_rows(min_row=2, values_only=True):
        rec = {sheaders[i]: row[i] for i in range(min(len(sheaders), len(row)))}
        if not any(rec.get(k) not in (None, "") for k in required_source_cols): continue
        oid = cell_text(rec.get("opportunity_id"))
        if not oid: raise ValueError("Hay una fuente sin opportunity_id.")
        sources_by_id.setdefault(oid, []).append({
            "name": cell_text(rec.get("name")),
            "url": cell_text(rec.get("url")),
            "type": cell_text(rec.get("type")) or "primary",
        })
    for item in rows:
        item["sources"] = sources_by_id.get(item.get("id"), [])

    existing = load_catalog(catalog_path) if catalog_path.exists() else []
    if replace:
        merged = rows
    else:
        by_id = {item.get("id"): copy.deepcopy(item) for item in existing}
        for item in rows:
            if not item.get("id"): continue
            previous = by_id.get(item["id"], {})
            previous.update(item)
            by_id[item["id"]] = previous
        merged = list(by_id.values())

    errors = validate_catalog(merged)
    if errors:
        print(f"Importación cancelada: {len(errors)} error(es).", file=sys.stderr)
        for error in errors: print(" - " + error, file=sys.stderr)
        raise SystemExit(1)

    backup = catalog_path.with_suffix(catalog_path.suffix + ".bak")
    if catalog_path.exists():
        shutil.copy2(catalog_path, backup)
        print(f"Copia de seguridad: {backup}")
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    temp = catalog_path.with_suffix(".json.tmp")
    temp.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(catalog_path)
    print(f"Catálogo actualizado: {catalog_path}")
    print(f"Total: {len(merged)} oportunidades ({len(rows)} importadas desde Excel).")

def main():
    parser = argparse.ArgumentParser(description="Gestor Excel del catálogo Ahorra360")
    sub = parser.add_subparsers(dest="command", required=True)
    exp = sub.add_parser("export", help="Exportar el JSON actual a Excel")
    exp.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    exp.add_argument("--output", type=Path, default=ROOT / "catalogo-ahorra360.xlsx")
    imp = sub.add_parser("import", help="Importar cambios desde Excel al JSON")
    imp.add_argument("--input", type=Path, required=True)
    imp.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    imp.add_argument("--replace", action="store_true", help="Reemplazar todo el catálogo (por defecto fusiona por id)")
    val = sub.add_parser("validate", help="Validar el JSON del catálogo")
    val.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    try:
        if args.command == "export":
            export_xlsx(args.catalog, args.output)
        elif args.command == "import":
            import_xlsx(args.input, args.catalog, args.replace)
        elif args.command == "validate":
            errors = validate_catalog(load_catalog(args.catalog))
            if errors:
                print(f"Se encontraron {len(errors)} errores:")
                for e in errors: print(" -", e)
                raise SystemExit(1)
            print("Catálogo válido.")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
