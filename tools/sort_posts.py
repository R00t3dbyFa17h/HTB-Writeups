#!/usr/bin/env python3
"""
Convert and file Medium posts according to an edited manifest.

Reads manifest.tsv, runs pandoc on everything not marked drop/skip,
cleans the Medium markup, and writes each file into the right place
in the repo tree.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

DEST_ROOT = {
    "machine": "machines",
    "challenge": "challenges",
    "ctf": "ctf",
    "note": "notes",
}

DIFFICULTIES = {"very-easy", "easy", "medium", "hard", "insane"}

DIV_LINE = re.compile(r"^\s*</?(div|section|figure|figcaption)[^>]*>\s*$")
FENCE_LANG = re.compile(r"^``` +(graf.*|postField.*|markup.*)$")
ATTR_BLOCK = re.compile(r"\{#[A-Za-z0-9_-]+[^}]*\}")
PANDOC_DIV = re.compile(r"^:::")


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return re.sub(r"-+", "-", text) or "untitled"


def base_slug(filename):
    s = re.sub(r"\.html$", "", filename)
    s = re.sub(r"^draft_", "", s)
    s = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", s)
    s = re.sub(r"-[0-9a-f]{8,}$", "", s)
    return slugify(s)


def clean_markdown(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    out = []
    for line in lines:
        if DIV_LINE.match(line) or PANDOC_DIV.match(line):
            continue
        line = FENCE_LANG.sub("```", line)
        line = ATTR_BLOCK.sub("", line)
        out.append(line.rstrip())

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"!\[\]\(\s*\)\n?", "", text)

    text = re.sub(
        r'<img\s+src="([^"]+)"[^>]*/?>',
        lambda m: f"![]({m.group(1)})",
        text,
    )
    text = re.sub(r'\{[^}]*data-image-id[^}]*\}', "", text)
    text = re.sub(r"^-{10,}$", "---", text, flags=re.MULTILINE)
    text = re.sub(
        r"(?m)^#+ .*(Not a Member|Click Here to Read).*$\n?", "", text)
    text = re.sub(
        r"(?m)^\*\*Not a Member.*$\n?", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def read_manifest(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for num, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                print(f"  line {num}: malformed, skipping", file=sys.stderr)
                continue
            action = parts[0].strip().lower()
            dest = parts[1].strip()
            filename = parts[2].strip()
            title = parts[3].strip() if len(parts) > 3 else ""
            slug = parts[4].strip() if len(parts) > 4 else ""
            rows.append((action, dest, filename, title, slug, num))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("posts_dir")
    ap.add_argument("-r", "--root", default=".", help="repo root")
    ap.add_argument("-n", "--dry-run", action="store_true")
    args = ap.parse_args()

    if not shutil.which("pandoc"):
        print("pandoc not found on PATH", file=sys.stderr)
        return 1

    rows = read_manifest(args.manifest)
    placed, dropped, problems = 0, 0, []

    for action, dest, filename, title, slug, num in rows:
        src = os.path.join(args.posts_dir, filename)

        if action in ("drop", "skip"):
            dropped += 1
            continue

        if action not in DEST_ROOT:
            problems.append(f"line {num}: unknown action '{action}'")
            continue

        if not os.path.isfile(src):
            problems.append(f"line {num}: missing file {filename}")
            continue

        if action == "machine":
            if dest.lower() not in DIFFICULTIES:
                problems.append(
                    f"line {num}: '{dest}' is not a difficulty ({filename})")
                continue
            subdir = dest.lower()
        elif action in ("challenge", "ctf"):
            if not dest or dest.upper() == "REVIEW":
                problems.append(f"line {num}: DEST not set ({filename})")
                continue
            subdir = slugify(dest)
        else:
            subdir = ""

        out_dir = os.path.join(args.root, DEST_ROOT[action], subdir)
        out_name = (slugify(slug) if slug else base_slug(filename)) + ".md"
        out_path = os.path.join(out_dir, out_name)

        print(f"  {action:9} {out_path}")
        if args.dry_run:
            placed += 1
            continue

        os.makedirs(out_dir, exist_ok=True)
        subprocess.run(
            ["pandoc", "--from=html", "--to=gfm", "--wrap=none",
             "--strip-comments", "-o", out_path, src],
            check=True,
        )
        text = clean_markdown(out_path)
        if title and not text.startswith("# "):
            text = f"# {title}\n\n{text}"
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(text)
        placed += 1

    print()
    print(f"placed: {placed}   skipped/dropped: {dropped}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
