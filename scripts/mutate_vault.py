"""Make exactly one edit, one add and one delete in the built vault.

This is the "change the source, re-sync, look at the graph" step. Each change carries a
marker sentence nobody would write by accident, so a CHUNKS search afterwards proves whether
the change reached cognee (edit and add should hit, delete should not). The deleted note's
title is recorded so its absence can be checked too.

  python scripts/mutate_vault.py --vault vault                # picks targets, prints what it did
  python scripts/mutate_vault.py --vault vault --edit articles/x.md --delete articles/y.md
  python scripts/mutate_vault.py --vault vault --undo         # restore from mutation.json

Targets are chosen deterministically: EDIT = the most-linked-to article (so the edit is
visible in a well-connected part of the graph); DELETE = an article that other notes link to
(so the deletion leaves dangling links the connector must re-render); ADD = a new note that
links to the edited one. The record of what changed is written to ``proof/mutation.json`` (outside the vault, so the
connector never sees it).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

WIKILINK_RE = re.compile(r"(!?)\[\[([^\[\]\n]+?)\]\]")
STAMP = time.strftime("%Y%m%d-%H%M")
EDIT_MARKER = f"Marker {STAMP}: the Zagreb Hackfest 2026 is hosted by Collabwriting at the Lauba hall."
ADD_MARKER = f"Marker {STAMP}: the Quokka palette ships with Inkscape 1.5 and was drawn by Mira Kovac."
ADD_PATH = "articles/99999999-quokka-palette.md"


def inbound_counts(vault: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for note in vault.rglob("*.md"):
        for _, inner in WIKILINK_RE.findall(note.read_text(encoding="utf-8")):
            target = inner.split("|")[0].split("#")[0].strip()
            counts[target] = counts.get(target, 0) + 1
    return counts


def pick_targets(vault: Path) -> tuple[Path, Path]:
    counts = inbound_counts(vault)
    articles = sorted(p for p in (vault / "articles").glob("*.md"))
    ranked = sorted(articles, key=lambda p: (-counts.get(p.relative_to(vault).with_suffix("").as_posix(), 0), p.name))
    edit = ranked[0]
    delete = next(p for p in ranked[1:] if counts.get(p.relative_to(vault).with_suffix("").as_posix(), 0) >= 2)
    return edit, delete


def undo(vault: Path, record_path: Path) -> None:
    record = json.loads(record_path.read_text())
    (vault / record["edit"]["path"]).write_text(record["edit"]["original"], encoding="utf-8")
    (vault / record["delete"]["path"]).write_text(record["delete"]["original"], encoding="utf-8")
    (vault / record["add"]["path"]).unlink(missing_ok=True)
    print(f"restored {record['edit']['path']} and {record['delete']['path']}, removed {record['add']['path']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", type=Path, default=Path("vault"))
    ap.add_argument("--edit", help="vault-relative path to edit (default: most-linked article)")
    ap.add_argument("--delete", help="vault-relative path to delete (default: a linked-to article)")
    ap.add_argument("--record", type=Path, help="where to write mutation.json (default: proof/mutation.json)")
    ap.add_argument("--undo", action="store_true", help="restore the vault from the record")
    a = ap.parse_args()
    vault = a.vault.resolve()
    record_path = a.record or Path("proof") / "mutation.json"
    if a.undo:
        undo(vault, record_path)
        return 0
    if not (vault / "articles").is_dir():
        sys.exit(f"no articles/ folder under {vault}; build the vault first")

    edit, delete = pick_targets(vault)
    if a.edit:
        edit = vault / a.edit
    if a.delete:
        delete = vault / a.delete
    if edit.resolve() == delete.resolve():
        sys.exit("edit and delete targets must differ")
    edit_rel = edit.relative_to(vault).as_posix()
    delete_rel = delete.relative_to(vault).as_posix()
    edit_original = edit.read_text(encoding="utf-8")
    delete_original = delete.read_text(encoding="utf-8")
    delete_title = re.search(r"^title:\s*(.+)$", delete_original, re.M)

    # 1. EDIT: append the marker as a new paragraph (mtime and size change, content hash changes)
    edit.write_text(edit_original.rstrip("\n") + f"\n\n{EDIT_MARKER}\n", encoding="utf-8")
    # 2. ADD: a new note that links to the edited note, so the new document has an outgoing edge
    added = (
        "---\n"
        f"title: Quokka palette for Inkscape 1.5 ({STAMP})\n"
        "tags: [article, proof]\n"
        "---\n"
        f"{ADD_MARKER}\n\nSee also [[{edit_rel[:-3]}|the edited note]].\n"
    )
    (vault / ADD_PATH).write_text(added, encoding="utf-8")
    # 3. DELETE: remove a note other notes link to (its inbound links become unresolved)
    delete.unlink()

    record = {
        "stamp": STAMP,
        "edit": {"path": edit_rel, "marker": EDIT_MARKER, "original": edit_original},
        "add": {"path": ADD_PATH, "marker": ADD_MARKER},
        "delete": {"path": delete_rel, "title": delete_title.group(1).strip() if delete_title else None,
                   "inbound_links": inbound_counts(vault).get(delete_rel[:-3], 0), "original": delete_original},
    }
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=1, ensure_ascii=False))

    print(f"EDITED  {edit_rel}\n  marker: {EDIT_MARKER}")
    print(f"ADDED   {ADD_PATH}\n  marker: {ADD_MARKER}")
    print(f"DELETED {delete_rel}  (title: {record['delete']['title']!r}, {record['delete']['inbound_links']} notes link to it)")
    print(f"\nrecord: {record_path}\nNow: docker compose run --rm sync   # expect: 2 + N re-rendered emitted, 1 deleted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
