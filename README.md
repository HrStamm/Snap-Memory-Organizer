# Snapchat Data Cleaning

> Pipeline til at downloade, udpakke og sortere dine Snapchat memories.

## Workflow

```
1_download.py  →  2_unzip.py  →  3_sort.py
```

| Trin | Script | Beskrivelse |
|------|--------|-------------|
| 1 | `scripts/1_download.py` | Download memories fra Snapchat's servere via HTML-eksport |
| 2 | `scripts/2_unzip.py` | Udpak ZIP-filer (overlay-memories) og behold kun mediefilen |
| 3 | `scripts/3_sort.py` | Omdøb til dansk datoformat og sortér i år/måned-mapper |

## Quick Start

1. Placér din `memories_history.html` i `input/`-mappen
2. Kør scripts i rækkefølge:

```bash
python scripts/1_download.py
python scripts/2_unzip.py
python scripts/3_sort.py
```

3. Dine sorterede minder ligger nu i `data/sorted/`

## Mappestruktur

```
├── input/                  ← Din memories_history.html (gitignored)
├── data/
│   ├── raw/                ← Downloaded rå-filer (trin 1+2)
│   └── sorted/             ← Færdigt resultat (trin 3)
│       └── YYYY/
│           └── MM-måned/
│               └── DD-MM-YYYY (HH.MM).ext
└── scripts/
    ├── 1_download.py
    ├── 2_unzip.py
    └── 3_sort.py
```

_Detaljeret README følger._
