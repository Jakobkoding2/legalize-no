#!/usr/bin/env python3
"""
build.py — legalize-no
Converts Lovdata XML/HTML law files into Markdown files with YAML frontmatter.
Source: https://api.lovdata.no/v1/publicData/get/gjeldende-lover.tar.bz2
License: NLOD 2.0
"""

import os
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag

INPUT_DIR = Path(__file__).parent / "nl"
OUTPUT_DIR = Path(__file__).parent / "no"


def get_dd_text(soup, css_class: str) -> str:
    dd = soup.find("dd", class_=css_class)
    if not dd:
        return ""
    return dd.get_text(separator=" ", strip=True)


def get_dd_list(soup, css_class: str) -> list[str]:
    dd = soup.find("dd", class_=css_class)
    if not dd:
        return []
    return [li.get_text(strip=True) for li in dd.find_all("li")]


def get_legal_areas(soup) -> list[str]:
    dd = soup.find("dd", class_="legalArea")
    if not dd:
        return []
    areas = []
    for li in dd.find_all("li"):
        links = li.find_all("a")
        if links:
            areas.append(links[-1].get_text(strip=True))
    return areas


def get_misc_text(soup) -> str:
    dd = soup.find("dd", class_="miscInformation")
    if not dd:
        return ""
    return dd.get_text(separator=" ", strip=True)


def node_to_markdown(node, depth=0) -> str:
    """Recursively convert an HTML node to Markdown text."""
    if isinstance(node, NavigableString):
        return str(node)

    tag = node.name
    lines = []

    if tag == "h1":
        text = node.get_text(strip=True)
        lines.append(f"# {text}\n")

    elif tag == "h2":
        text = node.get_text(strip=True)
        lines.append(f"\n## {text}\n")

    elif tag == "h3":
        text = node.get_text(strip=True)
        lines.append(f"\n### {text}\n")

    elif tag == "h4" and "legalArticleHeader" in node.get("class", []):
        text = node.get_text(strip=True)
        lines.append(f"\n#### {text}\n")

    elif tag == "article" and "legalArticle" in node.get("class", []):
        for child in node.children:
            lines.append(node_to_markdown(child, depth))

    elif tag == "article" and "legalP" in node.get("class", []):
        text = node.get_text(separator=" ", strip=True)
        if text:
            lines.append(f"\n{text}\n")

    elif tag == "article" and "changesToParent" in node.get("class", []):
        text = node.get_text(separator=" ", strip=True)
        if text:
            lines.append(f"\n> {text}\n")

    elif tag == "section" and "section" in node.get("class", []):
        for child in node.children:
            lines.append(node_to_markdown(child, depth + 1))

    elif tag == "main":
        for child in node.children:
            lines.append(node_to_markdown(child, depth))

    else:
        for child in node.children:
            lines.append(node_to_markdown(child, depth))

    return "".join(lines)


def clean_markdown(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text + "\n"


def yaml_str(value: str) -> str:
    value = value.replace('"', '\\"')
    return f'"{value}"'


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    escaped = [f'"{item.replace(chr(34), chr(92)+chr(34))}"' for item in items]
    return "[" + ", ".join(escaped) + "]"


def build_identifier(filename: str, legacy_id: str) -> str:
    """
    Use legacyID directly (it already includes the law number).
    Append -nn for Nynorsk variants (filename ends with -nn.xml).
    e.g. nl-18840614-003.xml + LOV-1884-06-14-3 -> LOV-1884-06-14-3
         nl-18140517-000-nn.xml + LOV-1814-05-17 -> LOV-1814-05-17-nn
    """
    if not legacy_id:
        return filename.replace(".xml", "")
    identifier = legacy_id
    stem = filename.replace(".xml", "")
    if stem.endswith("-nn"):
        identifier += "-nn"
    return identifier


def parse_law(xml_path: Path) -> tuple[str, str] | None:
    """
    Parse a single Lovdata XML file.
    Returns (identifier, markdown_content) or None on error.
    """
    try:
        html = xml_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR reading {xml_path.name}: {e}", file=sys.stderr)
        return None

    soup = BeautifulSoup(html, "html.parser")

    # --- Metadata ---
    title = get_dd_text(soup, "title")
    if not title:
        title = soup.find("title")
        title = title.get_text(strip=True) if title else xml_path.stem

    short_title = get_dd_text(soup, "titleShort")
    legacy_id = get_dd_text(soup, "legacyID")          # e.g. LOV-2005-06-17
    doc_id = get_dd_text(soup, "dokid")                 # e.g. NL/lov/2005-06-17
    ref_id = get_dd_text(soup, "refid")                 # e.g. lov/2005-06-17
    department = get_dd_list(soup, "ministry")
    last_change_in_force = get_dd_text(soup, "lastChangeInForce")
    last_changed_by = get_dd_text(soup, "lastChangedBy")
    subjects = get_legal_areas(soup)
    misc = get_misc_text(soup)

    identifier = build_identifier(xml_path.name, legacy_id)

    # Parse publication date from identifier
    m = re.match(r"LOV-(\d{4}-\d{2}-\d{2})", identifier)
    publication_date = m.group(1) if m else ""

    # Source URL
    source_url = f"https://lovdata.no/dokument/{doc_id}" if doc_id else ""

    # Determine status from misc text
    misc_lower = misc.lower()
    if "opphevet" in misc_lower:
        status = "opphevet"
    else:
        status = "gjeldende"

    # Language from html lang attribute
    html_tag = soup.find("html")
    lang = html_tag.get("lang", "nb") if html_tag else "nb"

    # --- Build YAML frontmatter ---
    frontmatter_lines = [
        "---",
        f"title: {yaml_str(title)}",
    ]
    if short_title:
        frontmatter_lines.append(f"short_title: {yaml_str(short_title)}")
    frontmatter_lines += [
        f"identifier: {yaml_str(identifier)}",
        f"country: \"no\"",
        f"rank: \"lov\"",
        f"lang: {yaml_str(lang)}",
    ]
    if publication_date:
        frontmatter_lines.append(f"publication_date: \"{publication_date}\"")
    if last_change_in_force:
        frontmatter_lines.append(f"last_change_in_force: \"{last_change_in_force}\"")
    if last_changed_by:
        frontmatter_lines.append(f"last_changed_by: {yaml_str(last_changed_by)}")
    frontmatter_lines.append(f"status: \"{status}\"")
    if source_url:
        frontmatter_lines.append(f"source: \"{source_url}\"")
    if department:
        frontmatter_lines.append(f"department: {yaml_list(department)}")
    if subjects:
        frontmatter_lines.append(f"subjects: {yaml_list(subjects)}")
    if misc:
        frontmatter_lines.append(f"misc: {yaml_str(misc)}")
    frontmatter_lines.append("---")

    frontmatter = "\n".join(frontmatter_lines)

    # --- Convert body to Markdown ---
    main = soup.find("main", class_="documentBody")
    if main:
        body_md = node_to_markdown(main)
        body_md = clean_markdown(body_md)
    else:
        body_md = f"# {title}\n"

    content = frontmatter + "\n" + body_md
    return identifier, content


def build_all(dry_run=False):
    if not INPUT_DIR.exists():
        print(f"ERROR: Input directory not found: {INPUT_DIR}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    xml_files = sorted(INPUT_DIR.glob("*.xml"))
    total = len(xml_files)
    print(f"Found {total} law files in {INPUT_DIR}")

    ok = 0
    errors = 0

    for i, xml_path in enumerate(xml_files, 1):
        result = parse_law(xml_path)
        if result is None:
            errors += 1
            continue

        identifier, content = result
        out_path = OUTPUT_DIR / f"{identifier}.md"

        if dry_run:
            print(f"  [{i}/{total}] {xml_path.name} -> {out_path.name}  (dry run)")
        else:
            out_path.write_text(content, encoding="utf-8")
            print(f"  [{i}/{total}] {xml_path.name} -> {out_path.name}")

        ok += 1

    print(f"\nDone: {ok} converted, {errors} errors.")
    if not dry_run:
        print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    build_all(dry_run=dry)
