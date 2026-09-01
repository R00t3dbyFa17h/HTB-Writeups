# Setup

## 1. Convert the Medium export

Unzip the Medium export, then run the converter against it. It skips drafts,
slugifies filenames, and strips Medium's wrapper markup.

    ./tools/medium2md.sh ~/Downloads/medium-export ./converted

Move each converted file into the right section directory. Machines go under
a difficulty folder, challenges under a category folder.

## 2. Regenerate the nav

    python3 tools/gen_summary.py -t "Iron-Breach Writeups"

Machine difficulty folders sort in real difficulty order, not alphabetically.
Run with `--check` to fail CI when the nav is stale.

## 3. Push to GitHub

    git init && git add . && git commit -m "initial import"
    git branch -M main
    git remote add origin git@github.com:R00t3dbyFa17h/REPO.git
    git push -u origin main

## 4. Connect GitBook

Create a space, then Configure → Git Sync → GitHub, pick the repo and the
`main` branch, and set the direction to bidirectional. GitBook reads
`.gitbook.yaml` for the README and SUMMARY paths.

## Notes

Obsidian callouts (`> [!Quick Reference]`) do not render in GitBook. Use the
`{% hint %}` blocks in `templates/machine-template.md` instead.

Mind maps need a fenced code block in GitBook. Markdown collapses the
whitespace on raw text, which breaks the tree alignment.
