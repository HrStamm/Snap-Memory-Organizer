# Snapchat Memory Unfucker

Snapchat has recently imposed a limit on the amount of memories you can store in their app (previously unlimited) – the limit is 5 GB, and most of us who've had the app for 10+ years have a shit ton more than that.

But hey, Snapchat is being nice! They've made a download feature so we can save our digital memories. The problem? They apparently designed the whole thing while they were on drugs.

The data is such a pain in the ass to download and such a hassle to deal with. Furthermore, it's completely unstructured with insanely long numeric filenames and doesn't come sorted in any way whatsoever. To top it off, for pictures and videos where you've written text on them, it comes in a zip file where the text layer and the original picture or video are separated into different files.

All of this, of course, because they'd rather have you pay for their monthly subscription. But fuck that – I made a solution to all of this.

## How to Unfuck Your Memories

### Step 1: Get your shitty HTML file from Snapchat

First, you need to request your data from Snapchat. They'll email you a link to download it – it's a massive ZIP file with all your memories and a `memories_history.html` file that actually has the timestamps and metadata.

Once you have it, drop the `memories_history.html` file into the `input/` folder.

### Step 2: Download everything (grab a coffee... or three)

```bash
python scripts/1_download.py
```

This script goes through the HTML file and downloads every single memory from Snapchat's servers. It has a 3-second delay between each download to avoid getting rate-limited.

**Fair warning:** If you have 1000+ memories, this is gonna take a while. Like, hours. Maybe half a day if you've been using Snapchat since 2015. The script will give you an estimate, but basically – start it before bed or before you leave for work.

The good news? It saves progress as it goes, so if your internet dies or your computer crashes, just run it again and it'll continue where it left off. You can even close your laptop (just don't close the terminal).

### Step 3: Unpack the ZIP hell

```bash
python scripts/2_unzip.py
```

This one's quick – usually done in seconds to a few minutes. It goes through all those stupid ZIP files (the ones with text overlays), extracts the actual photo/video, and throws away the overlay layer. Because who the fuck needs that separated?

### Step 4: Make it actually usable

```bash
python scripts/3_sort.py
```

Also quick. This script renames all your files from `7a8f3b2e-9c4d-11eb-a8b3-0242ac130003.jpg` to something you can actually read like `15-01-2024 (14.32).jpg`, and organizes them into year/month folders.

Now you can actually browse your memories like a normal human being.

### Done!

Your sorted, renamed, and organized memories are now in `data/sorted/` – arranged by year and month, with proper filenames that tell you when they were taken.

No more UUID bullshit. No more scattered files. Just your memories, the way they should've been from the start.

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

_Detailed README coming soon._
