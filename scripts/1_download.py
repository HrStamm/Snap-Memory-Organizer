#!/usr/bin/env python3
"""
Trin 1: Download af ALLE Snapchat memories fra HTML eksport.

Sikrer at ingen filer mangler ved at downloade direkte fra Snapchat's servere.
Gemmer progress løbende så download kan genoptages.

Brug:
    python scripts/1_download.py

Input:  input/memories_history.html
Output: data/raw/*.{jpg,mp4,zip}
"""

import re
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import json
from pymediainfo import MediaInfo

# ─── Konfiguration ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
HTML_FILE = PROJECT_ROOT / "input" / "memories_history.html"
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"

DELAY_SECONDS = 3       # Delay mellem downloads
MAX_RETRIES = 5          # Max antal forsøg per fil
RETRY_DELAY = 10         # Sekunder at vente ved fejl før retry

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'X-Snap-Route-Tag': 'mem-dmd',
    'Accept': '*/*',
}

progress_file = OUTPUT_DIR / 'download_progress.json'


# ─── Hjælpefunktioner ────────────────────────────────────────────────────────

def load_progress():
    """Indlæs tidligere download progress."""
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {'downloaded': [], 'failed': []}


def save_progress(progress):
    """Gem download progress — bevar rækkefølge."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def parse_html():
    """Parse HTML og udtræk alle download URLs med metadata."""
    print(f"📄 Læser HTML fil: {HTML_FILE}")

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Find alle download URLs
    urls = re.findall(
        r'(https://[^"\'<>\s]+api\.snapchat\.com/dmd/mm[^"\'<>\s]*)', content
    )
    print(f"✅ Fundet {len(urls)} download URLs")

    # Udtræk timestamps fra HTML tabeller
    memories = []
    tables = soup.find_all('table')

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                media_type_cell = cells[0].get_text(strip=True)
                date_cell = cells[1].get_text(strip=True)

                for cell in cells:
                    links = cell.find_all(href=re.compile(r'snapchat\.com'))
                    if links:
                        url = links[0].get('href')
                        if url and 'api.snapchat.com/dmd/mm' in url:
                            memories.append({
                                'url': url,
                                'date': date_cell,
                                'type': media_type_cell,
                            })

    # Hvis table parsing ikke fandt URLs, brug regex URLs
    if len(memories) < len(urls):
        print(f"⚠️  Table parsing fandt kun {len(memories)} entries, bruger alle {len(urls)} URLs")
        memories = [{'url': url, 'date': None, 'type': None} for url in urls]

    return memories


def extract_filename_from_url(url):
    """Udtræk UUID/ID fra URL til filnavn."""
    match = re.search(r'mid=([A-F0-9-]+)', url, re.IGNORECASE)
    if match:
        return match.group(1)
    return f"memory_{int(time.time() * 1000)}"


def verify_file(filename):
    """Verificer at en downloaded fil er valid (ikke korrupt)."""
    try:
        if filename.suffix.lower() == '.zip':
            import zipfile
            try:
                with zipfile.ZipFile(filename, 'r'):
                    return True
            except zipfile.BadZipFile:
                return False
        elif filename.suffix.lower() in ['.mp4', '.mov', '.avi']:
            media_info = MediaInfo.parse(str(filename))
            has_video = any(t.track_type == 'Video' for t in media_info.tracks)
            has_general = any(t.track_type == 'General' for t in media_info.tracks)
            return has_video or has_general
        elif filename.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            return filename.stat().st_size > 1024
        else:
            return filename.stat().st_size > 1024
    except Exception:
        return False


def download_file(url, base_filename, retry_count=0):
    """
    Download en enkelt fil med retry logik og verification.

    Returns:
        (file_size_mb, filename) hvis success, (False, None) hvis fejl
    """
    filename = None
    try:
        print(f"📥 Downloader: {base_filename}...", end=' ', flush=True)

        response = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')

        # Bestem korrekt extension fra content-type
        if 'video' in content_type:
            ext = '.mp4'
        elif 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        elif 'image' in content_type:
            ext = '.jpg'
        else:
            ext = '.mp4'

        filename = OUTPUT_DIR / f"{base_filename}{ext}"
        print(f"({ext}) ", end='', flush=True)

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size_mb = filename.stat().st_size / 1024 / 1024
        print(f"✅ ({file_size_mb:.2f} MB)", end=' ', flush=True)

        # Tjek om det faktisk er en ZIP fil (overlay)
        with open(filename, 'rb') as f:
            magic = f.read(4)
            if magic == b'PK\x03\x04':
                zip_filename = filename.with_suffix('.zip')
                filename.rename(zip_filename)
                filename = zip_filename
                print("📦 ZIP detected! ", end='', flush=True)

        # Verificer filen
        print("🔍", end=' ', flush=True)
        if verify_file(filename):
            print("✅ Valid")
            return (file_size_mb, filename)
        else:
            print("❌ KORRUPT!")
            filename.unlink()
            raise Exception("Fil er korrupt efter download")

    except Exception as e:
        print(f"❌ FEJL: {e}")

        if filename and filename.exists():
            filename.unlink()

        if retry_count < MAX_RETRIES:
            print(f"⏳ Venter {RETRY_DELAY}s før retry {retry_count + 1}/{MAX_RETRIES}...")
            time.sleep(RETRY_DELAY)
            return download_file(url, base_filename, retry_count + 1)
        else:
            print(f"💥 FAILED efter {MAX_RETRIES} forsøg!")
            return (False, None)


# ─── Hovedfunktion ────────────────────────────────────────────────────────────

def main():
    """Hoved download proces."""
    print("=" * 80)
    print("🎬 SNAPCHAT MEMORIES DOWNLOADER")
    print("=" * 80)
    print()

    if not HTML_FILE.exists():
        print(f"❌ HTML fil ikke fundet: {HTML_FILE}")
        print(f"   Placér din memories_history.html i input/-mappen.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Parse HTML
    memories = parse_html()
    total = len(memories)

    print()
    print(f"📊 TOTAL: {total} filer at downloade")
    print(f"⏱️  Estimeret tid: ~{(total * DELAY_SECONDS) / 60:.1f} minutter")
    print(f"⏱️  Delay: {DELAY_SECONDS}s mellem hver fil")
    print(f"💾 Output mappe: {OUTPUT_DIR}")
    print()

    # Indlæs tidligere progress
    progress = load_progress()
    already_downloaded_list = progress.get('downloaded', [])
    already_downloaded = set(already_downloaded_list)

    if already_downloaded:
        print(f"♻️  Genoptager: {len(already_downloaded)} allerede downloaded")
        print()

    # Start download
    start_time = time.time()
    success_count = 0
    skip_count = len(already_downloaded)
    fail_count = 0
    failed_urls = []
    downloaded_order = already_downloaded_list.copy()

    for i, memory in enumerate(memories, 1):
        url = memory['url']
        base_filename = extract_filename_from_url(url)

        if base_filename in already_downloaded:
            continue

        print(f"\n[{i}/{total}] ", end='')

        result = download_file(url, base_filename)
        file_size_mb, filename = result if result[0] else (False, None)

        if file_size_mb:
            success_count += 1
            downloaded_order.append(base_filename)
            save_progress({'downloaded': downloaded_order, 'failed': failed_urls})

            if i < total:
                print(f"⏳ Venter {DELAY_SECONDS}s...")
                time.sleep(DELAY_SECONDS)
        else:
            fail_count += 1
            failed_urls.append(url)
            save_progress({'downloaded': downloaded_order, 'failed': failed_urls})

    # Afslutning
    elapsed = time.time() - start_time
    print()
    print("=" * 80)
    print("✅ DOWNLOAD FÆRDIG!")
    print("=" * 80)
    print(f"✅ Success: {success_count}")
    print(f"⏭️  Skipped: {skip_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"⏱️  Tid: {elapsed / 60:.1f} minutter")
    print(f"💾 Filer i: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
