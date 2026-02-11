# Snapchat Memory Unfucker

Snapchat has recently imposed a limit on the amount of memories you can store in their app (previously unlimited), the limit is 5 GB, and most of us who've had the app for 10+ years have a shit ton more than that.

But hey, Snapchat is being nice! They've made a download feature so we can save our digital memories. The problem? They apparently designed the whole thing while they were on drugs.

The data is such a pain in the ass to download and such a hassle to deal with. Furthermore, it's completely unstructured with insanely long numeric filenames and doesn't come sorted in any way whatsoever. To top it off, for pictures and videos where you've written text on them, it comes in a zip file where the text layer and the original picture or video are separated into different files.

All of this, of course, because they'd rather have you pay for their monthly subscription. But fuck that – I made a solution to all of this.

## How to Unfuck Your Memories

### Step 0: Get your data from Snapchat

1. Open Snapchat → Settings → **My Data**
2. Request your **Memories** (just select Memories, not everything)
3. Wait for Snapchat to email you a download link (can take a few hours to a day)
4. Download the ZIP file and extract it
5. Find the `memories_history.html` file and drop it in the `input/` folder

### The 3-Step Pipeline

| Step | Script | What it does |
|------|--------|--------------|
| **1** | `1_download.py` | Downloads all your memories from Snapchat's servers. **Takes hours** – Snapchat's direct download link is garbage (skips files, downloads duplicates). This script ensures everything is downloaded correctly with progress tracking, so you can pause and resume anytime. |
| **2** | `2_unzip.py` | Handles Snapchat's ZIP bullshit. Extracts the actual photo/video from those ZIPs, deletes the text layer, and renames everything to match the format of non-zipped files. **Takes seconds to minutes.** |
| **3** | `3_sort.py` | Maps each memory to its correct timestamp using the HTML file, organizes them into year/month folders (2016/01-January/, 2017/05-May/, etc.), and renames files to the exact date and time (down to the minute). **Quick.** |

### Running the scripts

```bash
python scripts/1_download.py   # Go make coffee. Or sleep. This takes forever.
python scripts/2_unzip.py      # Quick
python scripts/3_sort.py       # Quick
```

**About Step 1:** If you have 1000+ memories, leave your computer running overnight. The script saves progress continuously, so if it crashes or you need to shut down, just restart it and it picks up where it left off. Unlike Snapchat's download, which starts from scratch every time.

### Done!

Your sorted memories are now in `data/sorted/` – organized by year and month, with actual readable filenames like `15-01-2024 (14.32).jpg` instead of UUID garbage.

## Folder Structure

```
├── input/                  ← Your memories_history.html (gitignored)
├── data/
│   ├── raw/                ← Downloaded raw files (step 1+2)
│   └── sorted/             ← Final result (step 3)
│       └── YYYY/
│           └── MM-month/
│               └── DD-MM-YYYY (HH.MM).file
└── scripts/
    ├── 1_download.py
    ├── 2_unzip.py
    └── 3_sort.py
```

