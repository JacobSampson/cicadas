# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

"""
GitHub wiki navigation and invisible per-doc metadata for `.cicadas/` when it is a wiki repo.

Writes Home.md and _Sidebar.md (GitHub wiki index conventions). Prepends an HTML comment to each
spec markdown file for machine-readable section/kind/title (comments are not shown in the wiki HTML
viewer — YAML frontmatter would render as visible text).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

WIKI_META_PREFIX = "<!-- cicadas-wiki"
WIKI_RESERVED_NAMES = frozenset(
    n.lower() for n in ("Home.md", "_Sidebar.md", "_Footer.md", "_Header.md")
)

_KIND_LABELS: dict[str, str] = {
    "prd": "PRD",
    "ux": "UX",
    "tech-design": "Tech design",
    "approach": "Approach",
    "tasks": "Tasks",
    "review": "Review",
    "buglet": "Buglet",
    "tweaklet": "Tweaklet",
    "eval-spec": "Eval spec",
    "summary": "Summary",
    "product-overview": "Product overview",
    "tech-overview": "Tech overview",
    "skill": "Skill",
}


def _is_reserved_wiki_file(name: str) -> bool:
    return name.lower() in WIKI_RESERVED_NAMES


def _rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _doc_kind(filename: str) -> str:
    stem = Path(filename).stem.lower()
    if stem == "skill":
        return "skill"
    return stem


def _kind_label(kind: str) -> str:
    return _KIND_LABELS.get(kind, kind.replace("-", " ").title())


def _strip_leading_wiki_html_comment(text: str) -> str:
    t = text.lstrip()
    if t.startswith(WIKI_META_PREFIX):
        nl = t.find("\n")
        if nl == -1:
            return ""
        return t[nl + 1 :].lstrip("\n")
    return text


def _extract_title(markdown: str) -> str:
    """First real ATX H1, or first sensible H2+, after wiki comment and optional YAML frontmatter."""
    text = markdown.lstrip()
    text = _strip_leading_wiki_html_comment(text)
    # Do not scan for YAML --- pairs: specs often use --- as Markdown horizontal rules, which
    # would truncate the document and hide the real H1 (e.g. PRDs). Prefer ATX H1 detection only.
    for line in text.splitlines():
        stripped = line.strip()
        m = re.match(r"^#(?!#)\s*(.+)$", stripped)
        if m:
            return m.group(1).strip()
    for line in text.splitlines():
        m = re.match(r"^##+\s+(.+)$", line.strip())
        if m:
            frag = m.group(1).strip()
            low = frag.lower()
            if "next_section" in low or low.startswith("yaml ") or low.startswith("json "):
                continue
            return frag
    return ""


def _archive_folder_parts(folder_name: str) -> tuple[str, str] | None:
    m = re.match(r"^(\d{8}-\d{6})-(.+)$", folder_name)
    if not m:
        return None
    return m.group(1), m.group(2)


def infer_doc_record(cicadas: Path, md_path: Path, *, content: str | None = None) -> dict:
    rel = _rel_posix(md_path, cicadas)
    parts = Path(rel).parts
    text = content if content is not None else md_path.read_text(encoding="utf-8")
    title = _extract_title(text)
    if not title:
        title = _kind_label(_doc_kind(md_path.name))

    section = parts[0] if parts else ""
    subsection = ""
    archive_ts = ""
    archive_slug = ""
    initiative = ""

    if section == "canon":
        if len(parts) > 2 and parts[1] == "modules":
            subsection = "modules"
    elif section == "active" and len(parts) >= 2:
        initiative = parts[1]
    elif section == "drafts" and len(parts) >= 2:
        initiative = parts[1]
    elif section == "archive" and len(parts) >= 2:
        ap = _archive_folder_parts(parts[1])
        if ap:
            archive_ts, archive_slug = ap
            subsection = parts[1]

    kind = _doc_kind(md_path.name)
    return {
        "rel": rel,
        "section": section,
        "subsection": subsection,
        "initiative": initiative,
        "archive_ts": archive_ts,
        "archive_slug": archive_slug,
        "kind": kind,
        "title": title,
        "path": md_path,
    }


def wiki_link_target(rel_posix: str) -> str:
    """GitHub wiki page path without .md (uses forward slashes)."""
    return rel_posix.removesuffix(".md") if rel_posix.endswith(".md") else rel_posix


def detect_wiki_web_base(cicadas: Path) -> str | None:
    """
    Base URL for the GitHub wiki web UI, e.g. https://github.com/owner/repo/wiki

    Used so Home/Sidebar links work when the markdown is viewed from raw.githubusercontent.com
    (relative links would resolve without /master/ and without .md and 404).

    Order: config.json ``wiki_web_base``, then ``git remote get-url origin`` (https or ssh).
    """
    cicadas = cicadas.resolve()
    cfg_path = cicadas / "config.json"
    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        base = data.get("wiki_web_base")
        if isinstance(base, str) and base.strip():
            return base.strip().rstrip("/")

    if not (cicadas / ".git").exists():
        return None
    try:
        out = subprocess.check_output(
            ["git", "-C", str(cicadas), "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None

    # https://github.com/OWNER/REPO.wiki.git  or  .../REPO.git
    # git@github.com:OWNER/REPO.wiki.git
    m = re.search(r"github\.com[:/]+([^/]+)/([^/.]+)(?:\.wiki)?(?:\.git)?", out, re.I)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    return f"https://github.com/{owner}/{repo}/wiki"


def _wiki_page_href(rel_posix: str, wiki_web_base: str | None) -> str:
    page = wiki_link_target(rel_posix)
    if wiki_web_base:
        return f"{wiki_web_base}/{page}"
    return page


def format_wiki_meta_comment(rec: dict) -> str:
    """Single-line HTML comment safe for titles with double-quotes removed."""
    title = rec["title"].replace("\n", " ").replace('"', "'")[:200]
    return (
        f'{WIKI_META_PREFIX} section={rec["section"]} kind={rec["kind"]} '
        f'title="{title}" relpath={rec["rel"]} -->'
    )


def discover_markdown_docs(cicadas: Path) -> list[dict]:
    roots = [
        cicadas / "canon",
        cicadas / "active",
        cicadas / "drafts",
        cicadas / "archive",
    ]
    out: list[dict] = []
    for base in roots:
        if not base.is_dir():
            continue
        for md_path in sorted(base.rglob("*.md")):
            if _is_reserved_wiki_file(md_path.name):
                continue
            try:
                out.append(infer_doc_record(cicadas, md_path))
            except OSError:
                continue
    out.sort(key=lambda r: r["rel"])
    return out


def ensure_wiki_metadata_comment(cicadas: Path, md_path: Path, *, refresh: bool = False) -> bool:
    """
    Prepend cicadas-wiki HTML comment if missing. With refresh=True, strip an existing
    comment and rewrite from the body. Returns True if the file was modified.
    """
    if _is_reserved_wiki_file(md_path.name):
        return False
    raw = md_path.read_text(encoding="utf-8")
    if raw.lstrip().startswith(WIKI_META_PREFIX):
        if not refresh:
            return False
        body = _strip_leading_wiki_html_comment(raw)
    else:
        body = raw
    rec = infer_doc_record(cicadas, md_path, content=body)
    meta = format_wiki_meta_comment(rec)
    new_body = meta + "\n\n" + body.lstrip()
    if new_body == raw:
        return False
    md_path.write_text(new_body, encoding="utf-8")
    return True


def annotate_all_markdown(cicadas: Path, *, refresh: bool = False) -> int:
    """Ensure metadata comments on all spec markdown files. Returns count of files updated."""
    n = 0
    for rec in discover_markdown_docs(cicadas):
        if ensure_wiki_metadata_comment(cicadas, rec["path"], refresh=refresh):
            n += 1
    return n


def _md_link(title: str, rel: str, wiki_web_base: str | None) -> str:
    return f"- [{title}]({_wiki_page_href(rel, wiki_web_base)})"


def _sidebar_section(heading: str, lines: list[str]) -> str:
    if not lines:
        return ""
    body = "\n".join(lines)
    return f"### {heading}\n{body}\n"


def write_home_md(cicadas: Path, docs: list[dict], *, wiki_web_base: str | None = None) -> str:
    canon = [d for d in docs if d["section"] == "canon" and d["subsection"] != "modules"]
    modules = [d for d in docs if d["section"] == "canon" and d["subsection"] == "modules"]
    active = [d for d in docs if d["section"] == "active"]
    drafts = [d for d in docs if d["section"] == "drafts"]
    archive = [d for d in docs if d["section"] == "archive"]

    lines = [
        "<!-- cicadas-wiki section=home kind=index title=\"Cicadas wiki home\" relpath=Home.md -->",
        "",
        "# Cicadas state",
        "",
        "This wiki mirrors **`.cicadas/`**: canon (synthesized truth), active specs, drafts, and archive. "
        "Use the sidebar for quick navigation; sections below list every page.",
        "",
    ]
    if wiki_web_base:
        lines.append(
            f"_Links below point at the [GitHub wiki]({wiki_web_base}) so they work from raw URLs and clones._"
        )
        lines.append("")
    lines.extend(
        [
            "## Canon",
            "",
            "Authoritative documentation synthesized from code at initiative completion.",
            "",
        ]
    )
    for d in canon:
        lines.append(_md_link(d["title"], d["rel"], wiki_web_base))
    if modules:
        lines.extend(["", "### Module snapshots", ""])
        for d in modules:
            lines.append(_md_link(d["title"], d["rel"], wiki_web_base))

    lines.extend(["", "## Active initiatives", ""])
    if not active:
        lines.append("_No active specs._")
    else:
        by_init: dict[str, list[dict]] = {}
        for d in active:
            by_init.setdefault(d["initiative"], []).append(d)
        for init in sorted(by_init):
            lines.extend(["", f"### `{init}`", ""])
            for d in sorted(by_init[init], key=lambda x: x["kind"]):
                lines.append(_md_link(d["title"], d["rel"], wiki_web_base))

    lines.extend(["", "## Drafts", ""])
    if not drafts:
        lines.append("_No drafts._")
    else:
        by_d: dict[str, list[dict]] = {}
        for d in drafts:
            by_d.setdefault(d["initiative"], []).append(d)
        for name in sorted(by_d):
            lines.extend(["", f"### `{name}`", ""])
            for d in sorted(by_d[name], key=lambda x: x["kind"]):
                lines.append(_md_link(d["title"], d["rel"], wiki_web_base))

    lines.extend(["", "## Archive", ""])
    if not archive:
        lines.append("_No archived specs._")
    else:
        by_folder: dict[str, list[dict]] = {}
        for d in archive:
            key = d["subsection"] or "other"
            by_folder.setdefault(key, []).append(d)
        for folder in sorted(by_folder.keys(), reverse=True):
            parts = _archive_folder_parts(folder)
            label = f"`{folder}`"
            if parts:
                label = f"`{parts[1]}` ({parts[0]})"
            lines.extend(["", f"### {label}", ""])
            for d in sorted(by_folder[folder], key=lambda x: x["kind"]):
                lines.append(_md_link(d["title"], d["rel"], wiki_web_base))

    lines.append("")
    return "\n".join(lines)


def write_sidebar_md(cicadas: Path, docs: list[dict], *, wiki_web_base: str | None = None) -> str:
    canon_top = [d for d in docs if d["section"] == "canon" and d["subsection"] != "modules"]
    modules = [d for d in docs if d["subsection"] == "modules"]
    active = [d for d in docs if d["section"] == "active"]
    drafts = [d for d in docs if d["section"] == "drafts"]

    home_href = wiki_web_base if wiki_web_base else "Home"
    archive_href = f"{wiki_web_base}/Home#archive" if wiki_web_base else "Home#archive"

    chunks: list[str] = [
        "<!-- cicadas-wiki section=nav kind=sidebar title=\"Sidebar\" relpath=_Sidebar.md -->",
        "",
        "### Wiki",
        f"- [Home]({home_href})",
        "",
    ]

    canon_lines = [_md_link(d["title"], d["rel"], wiki_web_base) for d in canon_top]
    chunks.append(_sidebar_section("Canon", canon_lines))

    if modules:
        mod_lines = [_md_link(d["title"], d["rel"], wiki_web_base) for d in modules[:30]]
        more = len(modules) - 30
        if more > 0:
            mod_lines.append(f"- _…and {more} more (see Home)_")
        chunks.append(_sidebar_section("Canon modules", mod_lines))

    if active:
        by_init: dict[str, list[dict]] = {}
        for d in active:
            by_init.setdefault(d["initiative"], []).append(d)
        for init in sorted(by_init):
            sub = [
                _md_link(d["title"], d["rel"], wiki_web_base)
                for d in sorted(by_init[init], key=lambda x: x["kind"])
            ]
            chunks.append(_sidebar_section(f"Active · {init}", sub))

    if drafts:
        by_d: dict[str, list[dict]] = {}
        for d in drafts:
            by_d.setdefault(d["initiative"], []).append(d)
        for name in sorted(by_d):
            sub = [
                _md_link(d["title"], d["rel"], wiki_web_base)
                for d in sorted(by_d[name], key=lambda x: x["kind"])
            ]
            chunks.append(_sidebar_section(f"Draft · {name}", sub))

    chunks.extend(
        [
            "### Archive",
            f"- [Full archive index →]({archive_href})",
            "",
        ]
    )

    return "\n".join(chunks)


def refresh_wiki_navigation(cicadas: Path) -> tuple[bool, bool]:
    """
    Regenerate Home.md and _Sidebar.md under cicadas. Returns (home_written, sidebar_written)
    where each is True if the file content changed.
    """
    cicadas = cicadas.resolve()
    wiki_web_base = detect_wiki_web_base(cicadas)
    docs = discover_markdown_docs(cicadas)
    home_content = write_home_md(cicadas, docs, wiki_web_base=wiki_web_base)
    sidebar_content = write_sidebar_md(cicadas, docs, wiki_web_base=wiki_web_base)

    home_path = cicadas / "Home.md"
    sidebar_path = cicadas / "_Sidebar.md"

    home_changed = not home_path.exists() or home_path.read_text(encoding="utf-8") != home_content
    side_changed = not sidebar_path.exists() or sidebar_path.read_text(encoding="utf-8") != sidebar_content

    if home_changed:
        home_path.write_text(home_content, encoding="utf-8")
    if side_changed:
        sidebar_path.write_text(sidebar_content, encoding="utf-8")

    return home_changed, side_changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh GitHub wiki Home/Sidebar and optional doc metadata in .cicadas")
    parser.add_argument(
        "--annotate-docs",
        action="store_true",
        help="Prepend cicadas-wiki HTML comments to markdown files that do not already have them",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="With --annotate-docs, rewrite existing cicadas-wiki comment lines (re-infer titles)",
    )
    args = parser.parse_args()
    root = Path.cwd()
    cicadas = root / ".cicadas"
    if not cicadas.is_dir():
        print(f"[ERR]  No .cicadas directory at {cicadas}")
        raise SystemExit(1)
    h, s = refresh_wiki_navigation(cicadas)
    print(f"[OK]   Home.md {'updated' if h else 'unchanged'}, _Sidebar.md {'updated' if s else 'unchanged'}")
    if args.annotate_docs:
        n = annotate_all_markdown(cicadas, refresh=args.refresh)
        print(f"[OK]   Annotated {n} markdown file(s)")
    elif args.refresh:
        print("[WARN] --refresh applies only with --annotate-docs")


if __name__ == "__main__":
    main()
