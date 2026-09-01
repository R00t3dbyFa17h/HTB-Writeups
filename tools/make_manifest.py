#!/usr/bin/env python3
"""
Build an editable manifest from a Medium export.

Emits a TSV: ACTION <tab> DEST <tab> FILENAME <tab> TITLE

Edit the ACTION and DEST columns, then feed the file to sort_posts.py.

ACTIONS
  machine    HTB box writeup      DEST = difficulty (very-easy|easy|medium|hard|insane)
  challenge  HTB challenge        DEST = category (web|crypto|pwn|rev|forensics|misc)
  ctf        non-HTB CTF writeup  DEST = event slug (heroctf|uoftctf|vulnhub-dc)
  note       methodology piece    DEST = ignored
  skip       leave on Medium      DEST = ignored
  drop       comment / junk       DEST = ignored
"""

import argparse
import os
import re
import sys

COMMENT_HINTS = [
    "thank you", "thanks", "great read", "great work", "appreciate",
    "keep up", "you too", "absolutely", "hey ", "hello ", "no i just",
    "if you", "excellent read", "this was a great", "love seeing",
    "can t wait", "yes sir", "so i need to be", "you re asking",
]

TITLE_TAG = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_TAG = re.compile(r'<h1[^>]*>(.*?)</h1>', re.IGNORECASE | re.DOTALL)
TAGS = re.compile(r"<[^>]+>")


def clean(text):
    text = TAGS.sub("", text)
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    text = text.replace("&amp;", "&").replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def title_of(path, fallback):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = fh.read(20000)
    except OSError:
        return fallback
    for pat in (H1_TAG, TITLE_TAG):
        m = pat.search(head)
        if m:
            t = clean(m.group(1))
            t = re.sub(r"\s*[-|]\s*Medium\s*$", "", t)
            if t:
                return t
    return fallback


def slug_title(name):
    s = re.sub(r"^(draft_)?(\d{4}-\d{2}-\d{2}_)?", "", name)
    s = re.sub(r"-[0-9a-f]{8,}$", "", s)
    return re.sub(r"-+", " ", s).strip()


def guess(title, size):
    low = title.lower()
    if size < 3000 and any(h in low for h in COMMENT_HINTS):
        return "drop", ""
    if any(h in low for h in COMMENT_HINTS) and len(title) < 90:
        return "drop", ""
    if re.search(r"\b(htb|hack the box|hackthebox)\b", low):
        return "machine", "REVIEW"
    if re.search(r"\b(walk[- ]?through|walkthrough|write[- ]?up)\b", low):
        return "ctf", "REVIEW"
    return "skip", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("posts_dir")
    ap.add_argument("-o", "--output", default="manifest.tsv")
    args = ap.parse_args()

    if not os.path.isdir(args.posts_dir):
        print(f"not a directory: {args.posts_dir}", file=sys.stderr)
        return 1

    rows = []
    for name in sorted(os.listdir(args.posts_dir)):
        if not name.endswith(".html"):
            continue
        full = os.path.join(args.posts_dir, name)
        size = os.path.getsize(full)
        title = title_of(full, slug_title(name))
        action, dest = guess(title, size)
        rows.append((action, dest, name, title))

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write("# ACTION\tDEST\tFILENAME\tTITLE\n")
        fh.write("# actions: machine challenge ctf note skip drop\n")
        for row in rows:
            fh.write("\t".join(row) + "\n")

    counts = {}
    for action, *_ in rows:
        counts[action] = counts.get(action, 0) + 1

    print(f"wrote {args.output} ({len(rows)} entries)")
    for k in sorted(counts):
        print(f"  {k:10} {counts[k]}")
    print("\nEdit ACTION and DEST columns, then run sort_posts.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
