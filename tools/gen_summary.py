#!/usr/bin/env python3
"""
Build GitBook SUMMARY.md from the writeup tree.

Walks the section directories, reads each file's first H1 for the display
title, and emits a nested nav. Run from the repo root after adding or
renaming any writeup.
"""

import argparse
import os
import re
import sys

SECTIONS = [
    ("machines", "Machines"),
    ("challenges", "Challenges"),
    ("sherlocks", "Sherlocks"),
    ("prolabs", "Pro Labs"),
    ("ctf", "Other CTFs"),
    ("notes", "Notes & Methodology"),
]

H1 = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
DIFFICULTY_ORDER = {
    "very-easy": 0,
    "easy": 1,
    "medium": 2,
    "hard": 3,
    "insane": 4,
}


def title_of(path, fallback):
    try:
        with open(path, encoding="utf-8") as fh:
            head = fh.read(4096)
    except OSError:
        return fallback
    m = H1.search(head)
    if not m:
        return fallback
    t = m.group(1)
    t = re.sub(r"[*_`]", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    return t.strip() or fallback


def prettify(slug):
    return " ".join(w.capitalize() for w in slug.replace("_", "-").split("-") if w)


def sort_key(name):
    return (DIFFICULTY_ORDER.get(name.lower(), 99), name.lower())


def collect(root, section):
    base = os.path.join(root, section)
    if not os.path.isdir(base):
        return []

    groups = []
    loose = []

    for entry in sorted(os.listdir(base)):
        full = os.path.join(base, entry)
        if entry.startswith("."):
            continue
        if os.path.isdir(full):
            pages = []
            for f in sorted(os.listdir(full)):
                if not f.endswith(".md") or f.upper() == "README.MD":
                    continue
                rel = f"{section}/{entry}/{f}"
                pages.append((title_of(os.path.join(full, f), prettify(f[:-3])), rel))
            if pages:
                groups.append((entry, pages))
        elif entry.endswith(".md") and entry.upper() != "README.MD":
            rel = f"{section}/{entry}"
            loose.append((title_of(full, prettify(entry[:-3])), rel))

    groups.sort(key=lambda g: sort_key(g[0]))
    return groups, loose


def build(root, book_title):
    lines = [f"# {book_title}", "", "* [Introduction](README.md)", ""]

    for section, label in SECTIONS:
        result = collect(root, section)
        if not result:
            continue
        groups, loose = result
        if not groups and not loose:
            continue

        lines.append(f"## {label}")
        lines.append("")

        for group, pages in groups:
            lines.append(f"* [{prettify(group)}]()")
            for title, rel in pages:
                lines.append(f"  * [{title}]({rel})")

        for title, rel in loose:
            lines.append(f"* [{title}]({rel})")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--root", default=".", help="repo root")
    ap.add_argument("-t", "--title", default="Writeups", help="book title")
    ap.add_argument("-o", "--output", default=None, help="defaults to <root>/SUMMARY.md")
    ap.add_argument("--check", action="store_true", help="exit 1 if SUMMARY.md is stale")
    args = ap.parse_args()

    out = args.output or os.path.join(args.root, "SUMMARY.md")
    content = build(args.root, args.title)

    if args.check:
        try:
            with open(out, encoding="utf-8") as fh:
                current = fh.read()
        except OSError:
            current = None
        if current != content:
            print("SUMMARY.md is stale", file=sys.stderr)
            return 1
        print("SUMMARY.md is current")
        return 0

    with open(out, "w", encoding="utf-8") as fh:
        fh.write(content)

    pages = content.count("](")
    print(f"wrote {out} ({pages} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
