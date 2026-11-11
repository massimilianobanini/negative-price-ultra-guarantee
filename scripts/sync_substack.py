#!/usr/bin/env python3
"""Append new Substack articles from the public sitemap archive, safely.

The private Google Sheet remains the authoritative source for editorial titles and
subtitles. Existing records are NEVER changed by this automation. New records
are marked provisional until they are reconciled with that editorial map.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlparse

PREFIX = "https://theminusoneguarantee.substack.com/p/"
SOURCE_REFERENCE = "https://github.com/massimilianobanini/theminusoneguarantee-sitemap/blob/main/articles.json"
JSON_FILE = Path("fonti/substack-articles.json")
MARKDOWN_FILE = Path("fonti/substack-articoli.md")
ID_REGEX = re.compile(r"^SUB-(\d{3,})$")
SLUG_REGEX = re.compile(r"^/p/[a-z0-9-]+$")
MONTHS = (
    "", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
)


class SyncError(ValueError):
    """Upstream changed unexpectedly; fail without writing data."""


def iso_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise SyncError(f"Data pubblicazione non valida: {value!r}") from exc


def check_url(url: str) -> str:
    if not isinstance(url, str) or not url.startswith(PREFIX):
        raise SyncError(f"URL non appartenente alla pubblicazione: {url!r}")
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.netloc != "theminusoneguarantee.substack.com"
            or not SLUG_REGEX.fullmatch(parsed.path) or parsed.query or parsed.fragment
            or parsed.params or url != PREFIX + parsed.path[3:]):
        raise SyncError(f"URL non canonico o non valido: {url!r}")
    return url


def check_existing(catalog: dict) -> list[dict]:
    if not isinstance(catalog, dict) or not isinstance(catalog.get("records"), list):
        raise SyncError("Catalogo locale JSON non valido")
    records = catalog["records"]
    if not records or catalog.get("count") != len(records):
        raise SyncError("Numero di record del catalogo incoerente")
    urls = set()
    previous_date = None
    for index, row in enumerate(records, 1):
        match = ID_REGEX.fullmatch(str(row.get("id", "")))
        if not match or int(match.group(1)) != index:
            raise SyncError(f"ID locale non consecutivo alla riga {index}")
        url = check_url(row.get("url"))
        if url in urls:
            raise SyncError(f"URL duplicato nel catalogo locale: {url}")
        urls.add(url)
        date = iso_date(row.get("date"))
        if previous_date is not None and date < previous_date:
            raise SyncError(f"Date locali non ordinate alla riga {index}")
        previous_date = date
    return records


def check_source(source: list[dict]) -> list[dict]:
    if not isinstance(source, list) or not source:
        raise SyncError("L'archivio sorgente non è una lista non vuota")
    seen = set()
    for row in source:
        if not isinstance(row, dict):
            raise SyncError("Voce dell'archivio sorgente non valida")
        url = check_url(row.get("url"))
        if url in seen:
            raise SyncError(f"URL duplicato nell'archivio sorgente: {url}")
        seen.add(url)
        iso_date(row.get("date"))
        if not isinstance(row.get("title"), str) or not row["title"].strip():
            raise SyncError(f"Titolo mancante nella sorgente: {url}")
        timestamp = row.get("datetime_utc", "")
        if timestamp:
            try:
                dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except (ValueError, TypeError) as exc:
                raise SyncError(f"Timestamp sorgente non valido per {url}") from exc
    return source


def reconcile(catalog: dict, source: list[dict], *, today: str | None = None) -> tuple[dict, int]:
    current = check_existing(catalog)
    upstream = check_source(source)
    old_urls = {row["url"] for row in current}
    source_urls = {row["url"] for row in upstream}
    missing = old_urls - source_urls
    if missing:
        raise SyncError(f"La sorgente non contiene {len(missing)} URL già archiviati; nessuna cancellazione automatica. Esempio: {sorted(missing)[0]}")
    additions = [row for row in upstream if row["url"] not in old_urls]
    if not additions:
        return catalog, 0
    additions.sort(key=lambda r: (r["date"], r.get("datetime_utc", ""), r["url"]))
    latest_existing = iso_date(current[-1]["date"])
    first_new_date = iso_date(additions[0]["date"])
    if first_new_date <= latest_existing:
        raise SyncError(f"Nuovo URL storico o dello stesso giorno ({first_new_date}), impossibile assegnare un ID senza riconciliazione della mappa editoriale")
    updated = copy.deepcopy(catalog)
    current_rows = updated["records"]
    for article in additions:
        url = article["url"]
        raw_subtitle = article.get("subtitle") or ""
        subtitle = raw_subtitle.strip()
        if subtitle.lower().startswith("view this post on the web at"):
            subtitle = ""  # A Gmail boilerplate, NOT the author-written subtitle.
        title = article["title"].strip()
        row = {
            "id": f"SUB-{len(current_rows) + 1:03d}",
            "date": article["date"],
            "title": title,
            "subtitle": subtitle,
            "url": url,
            "metadata_status": "provvisorio_da_verificare_con_mappa_editoriale",
            "title_may_be_truncated": title.endswith(("…", "...")),
            "source": "public_github_sitemap",
        }
        current_rows.append(row)
    updated["count"] = len(current_rows)
    updated["snapshot_date"] = today or dt.datetime.now(dt.timezone.utc).date().isoformat()
    updated["last_recorded_publication_date"] = current_rows[-1]["date"]
    updated["sync_source"] = SOURCE_REFERENCE
    check_existing(updated)
    return updated, len(additions)


def fmt_italian(date: str) -> str:
    value = iso_date(date)
    return f"{value.day} {MONTHS[value.month]} {value.year}"


def markdown_text(text: str) -> str:
    return " ".join(str(text).split()).replace("|", r"\|")


def render_markdown(catalog: dict) -> str:
    rows = check_existing(catalog)
    count = len(rows)
    date_range = f"dal {fmt_italian(rows[0]['date'])} al {fmt_italian(rows[-1]['date'])}"
    header = (
        "# The -1 Guarantee — indice completo degli articoli pubblicati\n\n"
        f"**{count} articoli**, {date_range}. Catalogo sincronizzato il "
        f"**{fmt_italian(catalog['snapshot_date'])}** con l'archivio GitHub pubblico.\n\n"
        "**Fonte pubblica:** https://theminusoneguarantee.substack.com/\n\n"
        "Le righe sono riferimenti bibliografici, non copie integrali degli articoli. "
        "**I metadati degli articoli importati automaticamente dopo SUB-301 sono provvisori**: "
        "titoli e sottotitoli vanno confrontati con il Google Sheet editoriale privato. "
        "L'automazione non modifica titoli e sottotitoli dei record già verificati.\n\n"
        "| ID | Data | Titolo | Articolo originale |\n"
        "| --- | --- | --- | --- |\n"
    )
    body = "\n".join(
        f"| {row['id']} | {row['date']} | "
        f"{markdown_text(row['title'])}" +
        (" *(titolo da verificare)*" if row.get("title_may_be_truncated") else "") +
        f" | [Leggi]({row['url']}) |"
        for row in rows
    )
    return header + body + "\n\nVedi anche [dataset strutturato](substack-articles.json) e [procedura di aggiornamento](../SYNC-EDITORIALE.md).\n"


def sync(source_path: Path, root: Path) -> int:
    source = json.loads(source_path.read_text(encoding="utf-8-sig"))
    file_json = root / JSON_FILE
    file_md = root / MARKDOWN_FILE
    local = json.loads(file_json.read_text(encoding="utf-8-sig"))
    updated, added = reconcile(local, source)
    if not added:
        print(f"Nessuna modifica: {len(local['records'])} URL canonici già sincronizzati.")
        return 0
    file_json.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    file_md.write_text(render_markdown(updated), encoding="utf-8")
    print(f"Sincronizzati {added} nuovi articoli. Totale: {updated['count']}. Ultima data: {updated['last_recorded_publication_date']}.")
    print("I nuovi metadati sono PROVVISORI fino alla verifica con la mappa editoriale privata.")
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="JSON dall'archivio GitHub pubblico")
    parser.add_argument("--root", type=Path, default=Path("."), help="Cartella principale del repository locale")
    args = parser.parse_args()
    try:
        sync(args.source, args.root)
    except (SyncError, json.JSONDecodeError, OSError) as exc:
        parser.exit(1, f"ERRORE SICUREZZA SINCRONIZZAZIONE: {exc}\n")


if __name__ == "__main__":
    main()
