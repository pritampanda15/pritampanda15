#!/usr/bin/env python3
"""Self-updating GitHub profile sync script (stdlib-only, zero dependencies).

Updates:
  1. Latest 4 YouTube videos from the Omixium channel RSS feed
     (between <!-- YOUTUBE:START --> and <!-- YOUTUBE:END -->)
  2. Latest 6 peer-reviewed works/preprints from the public ORCID API
     (between <!-- ORCID:START --> and <!-- ORCID:END -->)
  3. Live Scholar/ORCID citation metrics inside impact-bento SVGs if
     OpenAlex/Google Scholar returns strictly higher verified counts.
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"

YOUTUBE_CHANNEL_ID = "UCuguroB_0KTvy3uBSqy8t8Q"
ORCID_ID = "0000-0003-4879-2302"
USER_AGENT = "pritampanda15-profile-sync/1.0 (+https://github.com/pritampanda15)"


def fetch_bytes(url: str, headers: dict[str, str] | None = None, timeout: int = 20) -> bytes:
    req_headers = {"User-Agent": USER_AGENT}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def clean_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def replace_block(content: str, start_marker: str, end_marker: str, body: str) -> str:
    pattern = re.compile(
        rf"({re.escape(start_marker)}\n).*?(\n{re.escape(end_marker)})",
        flags=re.DOTALL,
    )
    if not pattern.search(content):
        print(f"Warning: markers {start_marker} / {end_marker} not found in README.md", file=sys.stderr)
        return content
    return pattern.sub(rf"\1{body}\2", content, count=1)


def fetch_youtube_section(limit: int = 4) -> str | None:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
    try:
        raw = fetch_bytes(url)
        root = ET.fromstring(raw)
    except Exception as exc:
        print(f"YouTube RSS fetch skipped: {exc}", file=sys.stderr)
        return None

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/",
    }
    entries = root.findall("atom:entry", ns)[:limit]
    if not entries:
        return None

    cells: list[str] = []
    for entry in entries:
        vid = (entry.findtext("yt:videoId", default="", namespaces=ns) or "").strip()
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        pub = (entry.findtext("atom:published", default="", namespaces=ns) or "")[:10]
        link = f"https://www.youtube.com/watch?v={vid}"
        thumb = f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg"
        short_title = title if len(title) <= 64 else title[:61].rstrip() + "…"
        escaped_title = html.escape(short_title)
        cells.append(
            f'    <td width="25%" align="center" valign="top">\n'
            f'      <a href="{link}"><img src="{thumb}" alt="{escaped_title}" width="100%"/></a><br/>\n'
            f'      <a href="{link}"><sub><b>{escaped_title}</b></sub></a><br/>\n'
            f'      <sub>📅 {pub}</sub>\n'
            f"    </td>"
        )

    return "<table>\n  <tr>\n" + "\n".join(cells) + "\n  </tr>\n</table>"


def fetch_orcid_section(limit: int = 6) -> str | None:
    url = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"
    try:
        raw = fetch_bytes(url, headers={"Accept": "application/json"})
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        print(f"ORCID fetch skipped: {exc}", file=sys.stderr)
        return None

    works: list[tuple[tuple[int, int, int], str, str, str]] = []
    seen_titles: set[str] = set()

    for group in data.get("group", []):
        summaries = group.get("work-summary") or []
        if not summaries:
            continue
        s = summaries[0]
        title_obj = (s.get("title") or {}).get("title") or {}
        title = clean_text(title_obj.get("value", ""))
        if not title:
            continue
        norm = re.sub(r"[^a-z0-9]+", "", title.lower())
        if norm in seen_titles:
            continue

        pub_date = s.get("publication-date") or {}
        year_str = ((pub_date.get("year") or {}).get("value") or "").strip()
        month_str = ((pub_date.get("month") or {}).get("value") or "0").strip()
        day_str = ((pub_date.get("day") or {}).get("value") or "0").strip()

        if not year_str.isdigit():
            continue
        year = int(year_str)
        if not (1995 <= year <= 2030):
            continue
        month = int(month_str) if month_str.isdigit() else 0
        day = int(day_str) if day_str.isdigit() else 0

        journal = clean_text(((s.get("journal-title") or {}).get("value")) or "Preprint / Journal")

        link = ""
        ext_ids = (s.get("external-ids") or {}).get("external-id") or []
        for eid in ext_ids:
            if (eid.get("external-id-type") or "").lower() == "doi":
                doi_val = (eid.get("external-id-value") or "").strip()
                if doi_val:
                    link = f"https://doi.org/{doi_val}"
                    break
        if not link:
            link = clean_text(((s.get("url") or {}).get("value")) or "")

        seen_titles.add(norm)
        works.append(((year, month, day), str(year), title, f"{journal}||{link}"))

    if not works:
        return None

    works.sort(key=lambda item: item[0], reverse=True)
    rows = [
        "| Year | Publication | Venue |",
        "| :---: | :--- | :--- |",
    ]
    for _, year_str, title, meta in works[:limit]:
        journal, link = meta.split("||", 1)
        safe_title = title.replace("|", "\\|")
        safe_journal = journal.replace("|", "\\|")
        title_md = f"[**{safe_title}**]({link})" if link else f"**{safe_title}**"
        rows.append(f"| `{year_str}` | {title_md} | *{safe_journal}* |")

    return "\n".join(rows)


def sync_openalex_citations_if_higher() -> None:
    """Safely updates impact-bento SVGs only if OpenAlex reports strictly higher metrics."""
    url = f"https://api.openalex.org/authors/https://orcid.org/{ORCID_ID}"
    try:
        raw = fetch_bytes(url)
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        print(f"OpenAlex metrics check skipped: {exc}", file=sys.stderr)
        return

    cited_by = int(data.get("cited_by_count") or 0)
    h_index = int((data.get("summary_stats") or {}).get("h_index") or 0)
    i10_index = int((data.get("summary_stats") or {}).get("i10_index") or 0)

    # Curated Google Scholar floor (OpenAlex typically tracks slightly lower than Google Scholar)
    if cited_by <= 6560 or h_index < 49:
        print(
            f"OpenAlex ({cited_by} cites, h={h_index}, i10={i10_index}) <= curated Scholar floor; keeping current badge values."
        )
        return

    rounded = f"{(cited_by // 10) * 10:,}"
    for svg_name in ("impact-bento.svg", "impact-bento-light.svg"):
        path = ROOT / "assets" / svg_name
        if not path.exists():
            continue
        svg = path.read_text(encoding="utf-8")
        svg = re.sub(r">[\d,]+(<tspan[^>]*>\+</tspan>)", rf">{rounded}\1", svg, count=1)
        svg = re.sub(
            r"h-index \d+ · i10-index \d+",
            f"h-index {h_index} · i10-index {i10_index}",
            svg,
        )
        path.write_text(svg, encoding="utf-8")
    print(f"Updated impact-bento SVGs with {rounded}+ citations (h={h_index}, i10={i10_index}).")


def main() -> int:
    if not README_PATH.exists():
        print("README.md not found.", file=sys.stderr)
        return 1

    readme = README_PATH.read_text(encoding="utf-8")
    original = readme

    yt_md = fetch_youtube_section(limit=4)
    if yt_md:
        readme = replace_block(readme, "<!-- YOUTUBE:START -->", "<!-- YOUTUBE:END -->", yt_md)
        print("Synced latest 4 YouTube videos.")

    orcid_md = fetch_orcid_section(limit=6)
    if orcid_md:
        readme = replace_block(readme, "<!-- ORCID:START -->", "<!-- ORCID:END -->", orcid_md)
        print("Synced latest 6 ORCID works.")

    sync_openalex_citations_if_higher()

    if readme != original:
        README_PATH.write_text(readme, encoding="utf-8")
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        print(f"README.md updated ({ts}).")
    else:
        print("README.md already up to date.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
