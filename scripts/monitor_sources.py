#!/usr/bin/env python3
"""Comprueba accesibilidad y cambios de contenido en fuentes oficiales registradas.
No extrae ni publica ayudas automáticamente: solo genera señales para revisión editorial.
"""
from __future__ import annotations
import hashlib, json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "sources.json"
STATE = ROOT / "data" / "source-monitor.json"
MAX_BYTES = 2_000_000
TIMEOUT = 18


def clean(raw: bytes) -> bytes:
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"<script\b[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style\b[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<!--([\s\S]*?)-->", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.encode("utf-8")


def inspect(source: dict, previous: dict) -> dict:
    result = {"id": source["id"], "name": source["name"], "url": source["url"], "scope": source["scope"], "checkedAt": datetime.now(timezone.utc).isoformat(), "status": "error", "httpStatus": None, "hash": None, "change": "unknown", "error": None}
    try:
        req = Request(source["url"], headers={"User-Agent": "Ahorra360SourceMonitor/1.0", "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8"})
        with urlopen(req, timeout=TIMEOUT) as response:
            payload = response.read(MAX_BYTES + 1)
            result["httpStatus"] = response.status
            if len(payload) > MAX_BYTES:
                payload = payload[:MAX_BYTES]
            digest = hashlib.sha256(clean(payload)).hexdigest()
            result["hash"] = digest
            result["status"] = "ok" if 200 <= response.status < 400 else "error"
            final_url = response.geturl()
            if not final_url.startswith("https://"):
                raise ValueError("La redirección final no utiliza HTTPS")
            old_hash = previous.get("hash")
            if not old_hash:
                result["change"] = "first_seen"
            elif old_hash != digest:
                result["change"] = "changed"
            else:
                result["change"] = previous.get("change", "unchanged")
            result["finalUrl"] = final_url
            result["contentType"] = response.headers.get("Content-Type", "")
    except HTTPError as exc:
        result["httpStatus"] = exc.code
        result["error"] = f"HTTP {exc.code}"
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        result["error"] = str(exc)[:300]
    old_hash = previous.get("hash")
    if result["status"] == previous.get("status") and result["hash"] == old_hash and result["httpStatus"] == previous.get("httpStatus") and result["error"] == previous.get("error"):
        result["checkedAt"] = previous.get("checkedAt", result["checkedAt"])
    return result


def main() -> int:
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    old = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"sources": []}
    previous = {row["id"]: row for row in old.get("sources", [])}
    results = []
    for source in sources:
        if not source.get("url", "").startswith("https://"):
            print(f"SKIP invalid URL: {source.get('id')}", file=sys.stderr)
            continue
        row = inspect(source, previous.get(source["id"], {}))
        results.append(row)
        print(f"{row['status'].upper():5} {row['change']:10} {row['name']} {row.get('httpStatus') or row.get('error') or ''}")
        time.sleep(1.0)
    old_rows = {row["id"]: row for row in old.get("sources", [])}
    changed_state = any(
        row["status"] != old_rows.get(row["id"], {}).get("status")
        or row["hash"] != old_rows.get(row["id"], {}).get("hash")
        or row["httpStatus"] != old_rows.get(row["id"], {}).get("httpStatus")
        or row["error"] != old_rows.get(row["id"], {}).get("error")
        for row in results
    ) or len(results) != len(old.get("sources", []))
    generated_at = datetime.now(timezone.utc).isoformat() if changed_state or not old.get("generatedAt") else old["generatedAt"]
    report = {"generatedAt": generated_at, "message": "Los cambios de hash son señales de revisión, no prueba de que una convocatoria haya cambiado.", "sources": results}
    STATE.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errors = sum(1 for row in results if row["status"] != "ok")
    changed = sum(1 for row in results if row["change"] in ("changed", "first_seen"))
    print(f"Resumen: {len(results)} fuentes, {errors} errores, {changed} cambios/primeras observaciones.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
