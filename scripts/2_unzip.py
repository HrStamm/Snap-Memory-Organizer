#!/usr/bin/env python3
"""
Trin 2: Udpak ZIP-filer fra Snapchat memories.

Snapchat pakker memories med text-overlays som ZIP-filer.
Hver ZIP indeholder en mediefil (stort) og et overlay (lille).
Vi udpakker kun mediefilen og omdøber den til det originale UUID.

Brug:
    python scripts/2_unzip.py

Input:  data/raw/*.zip
Output: data/raw/*.{jpg,mp4}  (ZIP-filer slettes efter udpakning)
"""

import shutil
import zipfile
from pathlib import Path

# ─── Konfiguration ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKING_FOLDER = PROJECT_ROOT / "data" / "raw"


# ─── Extraction ──────────────────────────────────────────────────────────────

def extract_zip_inplace(zip_path):
    """
    Udpak ZIP fil in-place og behold original UUID som filnavn.

    ZIP filer fra Snapchat indeholder typisk:
    - En video/billede fil (hovedindhold — størst)
    - Eventuelt en overlay fil (mindst)

    Vi udpakker den største fil og omdøber den til ZIP'ens UUID.
    """
    uuid = zip_path.stem
    parent_folder = zip_path.parent

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Få liste over filer (ekskl. mapper)
            file_list = [f for f in zip_ref.infolist() if not f.is_dir()]

            if not file_list:
                return False, uuid, 0, "Tom ZIP fil"

            # Find største fil (hovedindholdet, ikke overlay)
            main_file = max(file_list, key=lambda f: f.file_size)

            # Få filendelse fra den udpakkede fil
            extension = Path(main_file.filename).suffix.lower()

            # Output filnavn: UUID + original extension
            output_filename = f"{uuid}{extension}"
            output_path = parent_folder / output_filename

            # Udpak kun hovedfilen
            with zip_ref.open(main_file) as source, open(output_path, 'wb') as target:
                shutil.copyfileobj(source, target)

            return True, uuid, main_file.file_size, extension

    except zipfile.BadZipFile:
        return False, uuid, 0, "Korrupt ZIP fil"
    except Exception as e:
        return False, uuid, 0, str(e)


# ─── Hovedfunktion ────────────────────────────────────────────────────────────

def main():
    """Udpak alle ZIP-filer i data/raw/."""
    print("=" * 60)
    print("📦 SNAPCHAT ZIP UNPACKER")
    print("=" * 60)
    print()

    if not WORKING_FOLDER.exists():
        print(f"❌ Mappe ikke fundet: {WORKING_FOLDER}")
        print(f"   Kør først: python scripts/1_download.py")
        return

    # Find ZIP filer
    zip_files = list(WORKING_FOLDER.glob('*.zip'))
    zip_count = len(zip_files)

    print(f"📁 Arbejdsmappe: {WORKING_FOLDER}")
    print(f"📦 Fandt {zip_count} ZIP filer der skal udpakkes")
    print(f"💾 Ledig diskplads: {shutil.disk_usage(WORKING_FOLDER).free / (1024**3):.2f} GB")
    print()

    if zip_count == 0:
        print("⚠️  Ingen ZIP filer fundet — intet at udpakke.")
        return

    # Process alle ZIP filer
    print("🚀 Starter udpakning...\n")

    processed_count = 0
    failed_count = 0
    failed_files = []
    total_size = 0

    for zip_file in zip_files:
        success, uuid, file_size, info = extract_zip_inplace(zip_file)

        if success:
            processed_count += 1
            total_size += file_size
            print(f"✅ {uuid} → {info} ({file_size / (1024 * 1024):.2f} MB)")

            # Slet original ZIP fil efter succesfuld udpakning
            zip_file.unlink()
        else:
            failed_count += 1
            failed_files.append((uuid, info))
            print(f"❌ {uuid}: {info}")

    # Opsummering
    print(f"\n{'=' * 60}")
    print(f"✨ Udpakning færdig!")
    print(f"📊 Udpakket: {processed_count} filer")
    print(f"❌ Fejlet: {failed_count} filer")
    print(f"💾 Total størrelse: {total_size / (1024**3):.2f} GB")
    print(f"{'=' * 60}")

    if failed_files:
        print(f"\n⚠️  Fejlede filer:")
        for uuid, info in failed_files:
            print(f"   - {uuid}: {info}")

    # Verificering
    print(f"\n🔍 Verificering:")
    all_files = [f for f in WORKING_FOLDER.glob('*') if f.is_file()]
    mp4_count = len(list(WORKING_FOLDER.glob('*.mp4')))
    jpg_count = len(list(WORKING_FOLDER.glob('*.jpg')))
    remaining_zips = len(list(WORKING_FOLDER.glob('*.zip')))

    print(f"   Totalt antal filer: {len(all_files)}")
    print(f"   - MP4 videoer: {mp4_count}")
    print(f"   - JPG billeder: {jpg_count}")
    print(f"   Resterende ZIP filer: {remaining_zips}")

    if remaining_zips == 0:
        print(f"\n✅ Alle ZIP filer er udpakket!")
        print(f"📁 {len(all_files)} minder klar til sortering (trin 3)")
    else:
        print(f"\n⚠️  {remaining_zips} ZIP filer udestår stadig")


if __name__ == "__main__":
    main()
