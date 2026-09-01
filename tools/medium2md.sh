#!/usr/bin/env bash
set -euo pipefail

EXPORT_DIR="${1:-}"
OUT_DIR="${2:-./converted}"

if [[ -z "$EXPORT_DIR" || ! -d "$EXPORT_DIR" ]]; then
    echo "usage: $0 <medium-export-dir> [out-dir]" >&2
    echo "  <medium-export-dir> is the unzipped export containing posts/" >&2
    exit 1
fi

POSTS_DIR="$EXPORT_DIR"
[[ -d "$EXPORT_DIR/posts" ]] && POSTS_DIR="$EXPORT_DIR/posts"

mkdir -p "$OUT_DIR"

shopt -s nullglob
count=0
skipped=0

for html in "$POSTS_DIR"/*.html; do
    base="$(basename "$html" .html)"

    if [[ "$base" == draft_* ]]; then
        skipped=$((skipped + 1))
        continue
    fi

    slug="$(echo "$base" \
        | sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}_//' \
        | sed -E 's/-[0-9a-f]{8,}$//' \
        | tr '[:upper:]' '[:lower:]' \
        | sed -E 's/[^a-z0-9]+/-/g' \
        | sed -E 's/^-+|-+$//g')"

    [[ -z "$slug" ]] && slug="$base"

    pandoc \
        --from=html \
        --to=gfm \
        --wrap=none \
        --strip-comments \
        --output="$OUT_DIR/$slug.md" \
        "$html"

    sed -i -E '/^:::/d; /^\{\.graf/d; s/\{#[a-z0-9]+ \.[^}]*\}//g' "$OUT_DIR/$slug.md"
    sed -i -E '/^<\/?div[^>]*>$/d; /^<\/?section[^>]*>$/d; /^<\/?figure[^>]*>$/d' "$OUT_DIR/$slug.md"
    sed -i -E 's/^``` +(graf|graf--pre|postField.*)$/```/' "$OUT_DIR/$slug.md"
    sed -i -E 's/[[:space:]]+$//' "$OUT_DIR/$slug.md"
    sed -i -E '/^$/{N;/^\n$/D}' "$OUT_DIR/$slug.md"

    count=$((count + 1))
    echo "  -> $slug.md"
done

echo
echo "converted: $count   skipped drafts: $skipped"
echo "output: $OUT_DIR"
