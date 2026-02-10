#!/usr/bin/env python3
"""
Trin 3: Sortér og omdøb Snapchat memories til dansk datoformat.

1. Bruger download_progress.json (korrekt rækkefølge) + HTML (timestamps)
2. Skipper duplikater (kun første forekomst af hver UUID)
3. Omdøber filer til dansk datoformat: "11-01-2026 (21.13).jpg"
4. Sorterer i mapper: YYYY/MM-måned/

Brug:
    python scripts/3_sort.py

Input:  data/raw/*  +  input/memories_history.html
Output: data/sorted/YYYY/MM-måned/DD-MM-YYYY (HH.MM).ext
"""

import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ─── Konfiguration ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
HTML_FILE = PROJECT_ROOT / "input" / "memories_history.html"
JSON_FILE = PROJECT_ROOT / "data" / "raw" / "download_progress.json"
SOURCE_FOLDER = PROJECT_ROOT / "data" / "raw"
OUTPUT_FOLDER = PROJECT_ROOT / "data" / "sorted"

# Danske månedsnavne
MONTHS_DA = {
    1: "januar", 2: "februar", 3: "marts", 4: "april",
    5: "maj", 6: "juni", 7: "juli", 8: "august",
    9: "september", 10: "oktober", 11: "november", 12: "december",
}


# ─── Hjælpefunktioner ────────────────────────────────────────────────────────

def parse_html_for_timestamps(html_path):
    """
    Parser HTML og udtrækker UUID → timestamp mapping.
    Kun FØRSTE forekomst af hver UUID tages (skipper duplikater).

    Returns:
        dict: {uuid: datetime} mapping (kun første forekomst)
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    uuid_to_timestamp = {}
    seen_uuids = set()
    duplicates_skipped = 0

    rows = re.findall(
        r'<tr><td>(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC</td>.*?mid=([A-F0-9-]{36})',
        content, re.DOTALL | re.IGNORECASE,
    )

    for timestamp_str, uuid in rows:
        uuid = uuid.upper()

        if uuid in seen_uuids:
            duplicates_skipped += 1
            continue

        seen_uuids.add(uuid)

        try:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            uuid_to_timestamp[uuid] = dt
        except ValueError as e:
            print(f"⚠️  Kunne ikke parse timestamp: {timestamp_str} — {e}")

    print(f"   🔍 Skippede {duplicates_skipped} duplikater i HTML")
    return uuid_to_timestamp


def load_json_order(json_path):
    """
    Læser download_progress.json og returnerer UUID liste i korrekt rækkefølge.
    """
    if not json_path.exists():
        return None

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get('downloaded', [])


def format_danish_filename(dt, extension):
    """
    Formaterer datetime til dansk filnavn format.

    Format: "11-01-2026 (21.13).jpg"
    Note: Bruger "." i stedet for ":" da macOS Finder viser ":" som "/"
    """
    return f"{dt.day:02d}-{dt.month:02d}-{dt.year} ({dt.hour:02d}.{dt.minute:02d}){extension}"


def get_month_folder_name(dt):
    """Returnerer mappenavn for måneden: '01-januar'"""
    return f"{dt.month:02d}-{MONTHS_DA[dt.month]}"


# ─── Hovedfunktion ────────────────────────────────────────────────────────────

def main():
    """Sortér og omdøb minder."""
    print("=" * 60)
    print("📂 SNAPCHAT MEMORIES SORTERING")
    print("=" * 60)
    print()

    # Valider at input filer findes
    if not HTML_FILE.exists():
        print(f"❌ HTML fil ikke fundet: {HTML_FILE}")
        print(f"   Placér din memories_history.html i input/-mappen.")
        return

    if not SOURCE_FOLDER.exists():
        print(f"❌ Source mappe ikke fundet: {SOURCE_FOLDER}")
        print(f"   Kør først: python scripts/1_download.py")
        return

    # Parse HTML timestamps
    print("📖 Parser HTML fil...")
    uuid_to_timestamp = parse_html_for_timestamps(HTML_FILE)
    print(f"   Fandt {len(uuid_to_timestamp)} unikke timestamps i HTML\n")

    # Læs JSON rækkefølge
    print("📄 Læser JSON rækkefølge...")
    json_order = load_json_order(JSON_FILE)
    if json_order:
        print(f"   Bruger JSON rækkefølge ({len(json_order)} UUIDs)\n")
    else:
        print("   ⚠️  Ingen JSON fil fundet — bruger filsystem rækkefølge\n")

    # Opret output mappe
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    # Find alle mediefiler i source (ekskl. JSON)
    all_source_files = {
        f.stem.upper(): f
        for f in SOURCE_FOLDER.glob('*.*')
        if not f.name.endswith('.json')
    }
    print(f"📁 Fandt {len(all_source_files)} filer i source mappe\n")

    # Bestem rækkefølge
    if json_order:
        uuids_to_process = [
            uuid.upper() for uuid in json_order if uuid.upper() in all_source_files
        ]
    else:
        uuids_to_process = list(all_source_files.keys())

    # Første pass: tæl filer per minut (til nummerering af duplikater)
    minute_counts = defaultdict(int)
    file_timestamps = []

    for uuid in uuids_to_process:
        if uuid in uuid_to_timestamp and uuid in all_source_files:
            file_path = all_source_files[uuid]
            dt = uuid_to_timestamp[uuid]
            minute_key = (dt.year, dt.month, dt.day, dt.hour, dt.minute)
            file_timestamps.append((file_path, dt, minute_key))
            minute_counts[minute_key] += 1

    # Andet pass: flyt og omdøb filer
    minute_index = defaultdict(int)
    matched = 0
    unmatched = 0
    unmatched_files = []

    print("🚀 Starter sortering...\n")

    for file_path, dt, minute_key in file_timestamps:
        extension = file_path.suffix.lower()

        # Output mappe: YYYY/MM-måned/
        year_folder = OUTPUT_FOLDER / str(dt.year)
        month_folder = year_folder / get_month_folder_name(dt)
        month_folder.mkdir(parents=True, exist_ok=True)

        # Filnavn i dansk format
        base_name = format_danish_filename(dt, "")

        # Hvis flere filer på samme minut → tilføj nummer
        if minute_counts[minute_key] > 1:
            minute_index[minute_key] += 1
            new_filename = f"{base_name} {minute_index[minute_key]}{extension}"
        else:
            new_filename = f"{base_name}{extension}"

        output_path = month_folder / new_filename

        # Flyt fil
        shutil.move(str(file_path), str(output_path))
        matched += 1

        if matched % 100 == 0:
            print(f"   ✅ Flyttet {matched} filer...")

    # Håndter filer uden timestamp-match
    for uuid, file_path in all_source_files.items():
        if uuid not in uuid_to_timestamp and file_path.exists():
            unmatched += 1
            unmatched_files.append(file_path.name)

    if unmatched_files:
        unmatched_folder = OUTPUT_FOLDER / "(ingen dato)"
        unmatched_folder.mkdir(parents=True, exist_ok=True)

        for uuid, file_path in all_source_files.items():
            if uuid not in uuid_to_timestamp and file_path.exists():
                shutil.move(str(file_path), str(unmatched_folder / file_path.name))

    # Opsummering
    print(f"\n{'=' * 60}")
    print(f"✨ Sortering færdig!")
    print(f"📊 Matched og flyttet: {matched} filer")
    print(f"❌ Uden match: {unmatched} filer")
    print(f"💾 Output: {OUTPUT_FOLDER}")
    print(f"{'=' * 60}")

    if unmatched_files[:10]:
        print(f"\n⚠️  Første 10 unmatched filer:")
        for f in unmatched_files[:10]:
            print(f"   - {f}")


if __name__ == "__main__":
    main()
