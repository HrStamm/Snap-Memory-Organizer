# Snapchat Memory Unfucker

Snapchat has recently imposed a limit on the amount of memories you can store in their app (previously unlimited) – the limit is 5 GB, and most of us who've had the app for 10+ years have a shit ton more than that.

But hey, Snapchat is being nice! They've made a download feature so we can save our digital memories. The problem? They apparently designed the whole thing while they were on drugs.

The data is such a pain in the ass to download and such a hassle to deal with. Furthermore, it's completely unstructured with insanely long numeric filenames and doesn't come sorted in any way whatsoever. To top it off, for pictures and videos where you've written text on them, it comes in a zip file where the text layer and the original picture or video are separated into different files.

All of this, of course, because they'd rather have you pay for their monthly subscription. But fuck that – I made a solution to all of this.

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
