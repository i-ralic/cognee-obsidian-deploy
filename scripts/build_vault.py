"""Build an Obsidian vault from the help-centre source (Astro Starlight content).

The help centre (https://help.cluing.io, repo Collabwriting/help) is a Starlight site:
``src/content/docs/en/{articles,collections}/*.md[x]`` with YAML frontmatter and
site-absolute markdown links (``[text](/en/articles/<slug>/)``). It has no ``.obsidian/``
folder and no wikilinks. This script turns the *published* pages into a vault so the
Obsidian link graph exists:

* pages with ``draft: true`` are skipped — they are not public and must not leave the repo;
* frontmatter is kept verbatim, plus ``url`` (from ``intercom.url``) and ``tags`` (the
  Intercom collection name, slugified) so the connector lifts them;
* internal links become ``[[articles/<slug>|text]]`` / ``[[collections/<slug>|text]]``
  wikilinks (path form, which Obsidian resolves from the vault root);
* Starlight ``:::note[Title]`` asides become Obsidian ``> [!note] Title`` callouts;
* ``.mdx``: ESM ``import``/``export`` lines and JSX components are removed and the note is
  written as ``.md`` (Obsidian only opens ``.md``);
* a ``vault-manifest.json`` records every source → note mapping, link conversion counts and
  skipped drafts (by path only, no content).

Usage::

    python scripts/build_vault.py --source ../help/src/content/docs/en --out vault
    python scripts/build_vault.py --source ... --out vault --limit 50     # smaller vault
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", re.DOTALL)
INTERNAL_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(/en/(articles|collections)/([^)\s#?]+?)/?(#[^)\s]*)?\)")
ASIDE_RE = re.compile(r"^:::(note|tip|caution|danger)(?:\[([^\]]*)\])?[ \t]*\n(.*?)^:::[ \t]*$", re.S | re.M)
ESM_RE = re.compile(r"^(?:import|export)\s[^\n]*$", re.M)
JSX_RE = re.compile(r"<([A-Z][A-Za-z0-9.]*)\b[^>]*?/>|<([A-Z][A-Za-z0-9.]*)\b[^>]*?>.*?</\2\s*>", re.S)
CALLOUT_KIND = {"note": "note", "tip": "tip", "caution": "warning", "danger": "danger"}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def split_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    return (data if isinstance(data, dict) else {}), text[match.end() :]


def convert_links(body: str, known: set[str], stats: dict) -> str:
    """``[text](/en/articles/slug/#h)`` → ``[[articles/slug#h|text]]``; unknown targets too
    (they become *unresolved* wikilinks, which is what the connector must cope with)."""

    def repl(match: re.Match) -> str:
        text, kind, slug, anchor = match.groups()
        target = f"{kind}/{slug}"
        stats["links_converted"] += 1
        if target not in known:
            stats["links_to_missing_or_draft"] += 1
        heading = ""
        if anchor and len(anchor) > 1:
            heading = "#" + anchor[1:].replace("-", " ")
        alias = text.strip()
        return f"[[{target}{heading}|{alias}]]" if alias and alias != slug else f"[[{target}{heading}]]"

    return INTERNAL_LINK_RE.sub(repl, body)


def convert_asides(body: str) -> str:
    def repl(match: re.Match) -> str:
        kind, title, inner = match.groups()
        lines = [f"> [!{CALLOUT_KIND[kind]}]" + (f" {title}" if title else "")]
        lines += [("> " + line).rstrip() for line in inner.strip("\n").splitlines()]
        return "\n".join(lines)

    return ASIDE_RE.sub(repl, body)


def strip_mdx(body: str) -> str:
    body = ESM_RE.sub("", body)
    body = JSX_RE.sub("", body)
    return re.sub(r"\n{3,}", "\n\n", body)


def build(source: Path, out: Path, limit: int | None) -> dict:
    pages = sorted(p for p in source.rglob("*") if p.suffix in (".md", ".mdx") and p.is_file())
    published: list[tuple[Path, dict, str]] = []
    skipped_drafts: list[str] = []
    for page in pages:
        front, body = split_frontmatter(page.read_text(encoding="utf-8"))
        if front.get("draft") is True:
            skipped_drafts.append(page.relative_to(source).as_posix())
            continue
        published.append((page, front, body))
    if limit:
        published = published[:limit]
    known = {p.relative_to(source).with_suffix("").as_posix() for p, _, _ in published}

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    stats = {"links_converted": 0, "links_to_missing_or_draft": 0, "mdx_converted": 0, "asides": 0}
    notes = []
    for page, front, body in published:
        rel = page.relative_to(source).with_suffix(".md")
        if page.suffix == ".mdx":
            body = strip_mdx(body)
            stats["mdx_converted"] += 1
        stats["asides"] += len(ASIDE_RE.findall(body))
        body = convert_asides(body)
        body = convert_links(body, known, stats)
        intercom = front.get("intercom") or {}
        if isinstance(intercom, dict) and intercom.get("url") and "url" not in front:
            front["url"] = intercom["url"]
        collection = intercom.get("collection") if isinstance(intercom, dict) else None
        tags = [slugify(collection)] if collection else []
        tags.append(rel.parts[0].rstrip("s"))  # "article" / "collection"
        front.setdefault("tags", tags)
        text = "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n" + body.lstrip("\n")
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        notes.append({"source": page.relative_to(source).as_posix(), "note": rel.as_posix(),
                      "title": front.get("title"), "url": front.get("url"), "bytes": len(text.encode())})
    manifest = {
        "source": str(source), "notes": len(notes), "skipped_drafts": len(skipped_drafts),
        "skipped_draft_paths": skipped_drafts, "stats": stats, "mapping": notes,
    }
    (out / "vault-manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--source", required=True, type=Path, help="…/src/content/docs/en of the help repo")
    ap.add_argument("--out", required=True, type=Path, help="vault directory to (re)create")
    ap.add_argument("--limit", type=int, help="only the first N published pages")
    args = ap.parse_args()
    if not args.source.is_dir():
        print(f"source not found: {args.source}", file=sys.stderr)
        return 2
    manifest = build(args.source, args.out, args.limit)
    print(json.dumps({k: v for k, v in manifest.items() if k not in ("mapping", "skipped_draft_paths")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
