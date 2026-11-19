#!/usr/bin/env python3
"""Self-updating GitHub profile sync script (stdlib-only, zero dependencies).

Updates:
  1. Custom Dark + Light animated GitHub Telemetry SVG cards
     (assets/github-telemetry.svg & assets/github-telemetry-light.svg)
     using live public GitHub REST API data across ALL owned repositories.
  2. Latest 4 YouTube videos from the Omixium channel RSS feed
     (between <!-- YOUTUBE:START --> and <!-- YOUTUBE:END -->)
  3. Latest 6 peer-reviewed works/preprints from the public ORCID API
     (between <!-- ORCID:START --> and <!-- ORCID:END -->)
  4. Live OpenAlex citation check (updates impact-bento SVGs only if strictly higher).
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"

GITHUB_USER = "pritampanda15"
YOUTUBE_CHANNEL_ID = "UCuguroB_0KTvy3uBSqy8t8Q"
ORCID_ID = "0000-0003-4879-2302"
USER_AGENT = "pritampanda15-profile-sync/2.0 (+https://github.com/pritampanda15)"


def fetch_bytes(url: str, headers: dict[str, str] | None = None, timeout: int = 20) -> bytes:
    req_headers = {"User-Agent": USER_AGENT}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def gh_get_json(url: str) -> object:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return json.loads(fetch_bytes(url, headers=headers).decode("utf-8"))


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


def render_github_telemetry_svg(stats: dict, theme: str = "dark") -> str:
    dark = theme == "dark"
    bg0, bg1 = ("#0A0A0C", "#111114") if dark else ("#F5F5F7", "#EFEFF4")
    card = "#1C1C1F" if dark else "#FFFFFF"
    border = "#2C2C30" if dark else "#E2E2E7"
    card_border = "#2C2C30" if dark else "#E5E5EA"
    top_spec_op = "0.14" if dark else "0.95"
    shadow_op = "0.35" if dark else "0.055"
    track = "#2C2C30" if dark else "#E8E8ED"
    ink = "#F5F5F7" if dark else "#1D1D1F"
    sub = "#D1D1D6" if dark else "#424245"
    muted = "#8E8E93" if dark else "#6E6E73"
    pill_bg = "#1C1C1F" if dark else "#FFFFFF"

    lang_colors = {
        "Python": "#0A84FF" if dark else "#0071E3",
        "HTML": "#FF9F0A" if dark else "#D97706",
        "Jupyter Notebook": "#BF5AF2" if dark else "#8944AB",
        "TypeScript": "#40C8E0" if dark else "#007A8C",
        "JavaScript": "#FFD60A" if dark else "#C27803",
        "Shell": "#30D158" if dark else "#248A3D",
        "Swift": "#FF375F" if dark else "#D70015",
        "Nextflow": "#30D158" if dark else "#248A3D",
        "R": "#64D2FF" if dark else "#0284C7",
        "Other": "#8E8E93" if dark else "#86868B",
    }

    # Build stacked language bar (total width=522, x=22, y=64)
    langs = stats["top_langs"]
    gap = 3.0
    bar_w = 522.0 - gap * max(0, len(langs) - 1)
    x_cursor = 22.0
    bar_segments: list[str] = []
    legend_items: list[str] = []
    total_lang = sum(c for _, c in langs) or 1

    for idx, (lang, count) in enumerate(langs):
        pct = count / total_lang
        seg_w = max(8.0, round(bar_w * pct, 1))
        if idx == len(langs) - 1:
            seg_w = max(4.0, round(22.0 + 522.0 - x_cursor, 1))
        col = lang_colors.get(lang, "#8E8E93")
        bar_segments.append(
            f'      <rect x="{x_cursor:.1f}" y="64" width="{seg_w:.1f}" height="14" rx="4" fill="{col}"/>'
        )
        x_cursor += seg_w + gap

        col_i = idx % 2
        row_i = idx // 2
        lx = 22 + col_i * 268
        ly = 108 + row_i * 30
        short_lang = lang if len(lang) <= 16 else lang[:15] + "…"
        legend_items.append(
            f'      <circle cx="{lx + 6}" cy="{ly - 4.5}" r="5" fill="{col}"/>\n'
            f'      <text x="{lx + 18}" y="{ly}" class="text" font-size="13.8" font-weight="500" fill="{sub}">{html.escape(short_lang)}</text>\n'
            f'      <text x="{lx + 248}" y="{ly}" text-anchor="end" class="text num" font-size="13.8" font-weight="700" fill="{ink}">{pct * 100:.1f}% <tspan fill="{muted}" font-weight="400">({count})</tspan></text>'
        )

    # Top 4 repositories leaderboard (right card)
    repo_rows: list[str] = []
    max_stars = max((r["stars"] for r in stats["top_repos"]), default=1) or 1
    row_colors = [
        "#FF9F0A" if dark else "#D97706",
        "#0A84FF" if dark else "#0071E3",
        "#BF5AF2" if dark else "#8944AB",
        "#30D158" if dark else "#248A3D",
    ]
    for idx, repo in enumerate(stats["top_repos"][:4]):
        ry = 62 + idx * 34
        name = repo["name"]
        if len(name) > 19:
            name = name[:18] + "…"
        bar_len = max(14, int(196 * (repo["stars"] / max_stars)))
        col = row_colors[idx % len(row_colors)]
        repo_rows.append(
            f'      <text x="22" y="{ry + 12}" class="text" font-size="14" font-weight="600" fill="{ink}">{html.escape(name)}</text>\n'
            f'      <rect x="208" y="{ry + 2}" width="196" height="11" rx="5.5" fill="{track}"/>\n'
            f'      <rect x="208" y="{ry + 2}" width="{bar_len}" height="11" rx="5.5" fill="{col}" class="bar-in"/>\n'
            f'      <text x="544" y="{ry + 12}" text-anchor="end" class="text num" font-size="13.8" font-weight="700" fill="{ink}">★ {repo["stars"]}  <tspan fill="{muted}" font-weight="500">⑂ {repo["forks"]}</tspan></text>'
        )

    updated = stats["updated_utc"]
    kpis = [
        ("TOTAL STARS", f'{stats["stars"]:,}', "Owned original repos", "#FF9F0A" if dark else "#D97706", "#FFC66D" if dark else "#8F3F00"),
        ("ORIGINAL REPOS", f'{stats["original_repos"]}', f'{stats["public_repos"]} total public', "#0A84FF" if dark else "#0071E3", "#64B5FF" if dark else "#0055B3"),
        ("TOTAL FORKS", f'{stats["forks"]:,}', "Community adoption", "#BF5AF2" if dark else "#8944AB", "#DDA0FF" if dark else "#6B2E8A"),
        ("FOLLOWERS", f'{stats["followers"]:,}', "Global research network", "#30D158" if dark else "#248A3D", "#6EE792" if dark else "#186A2D"),
    ]
    kpi_blocks: list[str] = []
    for idx, (label, val, caption, accent, accent_ink) in enumerate(kpis):
        kx = 24 + idx * 292
        kpi_blocks.append(
            f'  <g transform="translate({kx}, 54)">\n'
            f'    <rect x="0" y="0" width="276" height="116" rx="18" fill="{card}" stroke="{card_border}" stroke-width="1" filter="url(#cardShadow)"/>\n'
            f'    <rect x="20" y="18" width="28" height="4" rx="2" fill="{accent}"/>\n'
            f'    <text x="20" y="40" class="text" font-size="11.5" font-weight="700" fill="{accent_ink}" letter-spacing="0.06em">{label}</text>\n'
            f'    <text x="20" y="82" class="display num" font-size="38" font-weight="800" fill="{ink}" letter-spacing="-1.2">{val}</text>\n'
            f'    <text x="20" y="103" class="text" font-size="13.2" fill="{muted}">{caption}</text>\n'
            f"  </g>"
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 404" width="100%" role="img" aria-label="Live GitHub Engineering Telemetry for pritampanda15">
  <defs>
    <linearGradient id="gtBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg0}"/>
      <stop offset="100%" stop-color="{bg1}"/>
    </linearGradient>
    <filter id="cardShadow" x="-8%" y="-12%" width="116%" height="128%">
      <feDropShadow dx="0" dy="2" stdDeviation="5" flood-color="#000000" flood-opacity="{shadow_op}"/>
    </filter>
    <style>
      .display {{ font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
      .text {{ font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
      .num {{ font-variant-numeric: tabular-nums; }}
    </style>
  </defs>

  <rect x="2" y="2" width="1196" height="400" rx="24" fill="url(#gtBg)" stroke="{border}" stroke-width="1.2"/>
  <line x1="26" y1="3" x2="1174" y2="3" stroke="#FFFFFF" stroke-opacity="{top_spec_op}" stroke-width="1.2"/>

  <text x="28" y="34" class="text" font-size="13" font-weight="700" fill="{muted}" letter-spacing="0.08em">GITHUB ENGINEERING TELEMETRY · @PRITAMPANDA15</text>
  <rect x="978" y="14" width="198" height="28" rx="14" fill="{pill_bg}" stroke="{card_border}"/>
  <text x="1077" y="32" text-anchor="middle" class="text num" font-size="12" font-weight="600" fill="{muted}">Synced {updated}</text>

{chr(10).join(kpi_blocks)}

  <!-- Bottom Left: Primary Language Distribution -->
  <g transform="translate(24, 186)">
    <rect x="0" y="0" width="566" height="196" rx="18" fill="{card}" stroke="{card_border}" stroke-width="1" filter="url(#cardShadow)"/>
    <text x="22" y="34" class="display" font-size="18.5" font-weight="700" fill="{ink}" letter-spacing="-0.25">Primary Languages</text>
    <text x="544" y="34" text-anchor="end" class="text" font-size="13" font-weight="500" fill="{muted}">{stats["original_repos"]} Original Repos</text>
    <rect x="22" y="64" width="522" height="14" rx="5" fill="{track}"/>
{chr(10).join(bar_segments)}
{chr(10).join(legend_items)}
  </g>

  <!-- Bottom Right: Top Starred Open-Source Tools -->
  <g transform="translate(610, 186)">
    <rect x="0" y="0" width="566" height="196" rx="18" fill="{card}" stroke="{card_border}" stroke-width="1" filter="url(#cardShadow)"/>
    <text x="22" y="34" class="display" font-size="18.5" font-weight="700" fill="{ink}" letter-spacing="-0.25">Top Starred Open-Source</text>
    <text x="544" y="34" text-anchor="end" class="text" font-size="13" font-weight="500" fill="{muted}">Live Stars &amp; Forks</text>
{chr(10).join(repo_rows)}
  </g>
</svg>
'''


def sync_github_telemetry_svgs() -> bool:
    try:
        user = gh_get_json(f"https://api.github.com/users/{GITHUB_USER}")
        repos: list[dict] = []
        page = 1
        while page <= 5:
            batch = gh_get_json(
                f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&type=owner&page={page}"
            )
            if not batch:
                break
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
    except Exception as exc:
        print(f"GitHub telemetry fetch skipped: {exc}", file=sys.stderr)
        return False

    owned = [r for r in repos if not r.get("fork")]
    if not owned:
        return False

    lang_counts = Counter(r["language"] for r in owned if r.get("language"))
    top_five = lang_counts.most_common(5)
    other_count = sum(lang_counts.values()) - sum(c for _, c in top_five)
    if other_count > 0:
        top_five.append(("Other", other_count))

    top_repos = [
        {
            "name": r["name"],
            "stars": int(r.get("stargazers_count") or 0),
            "forks": int(r.get("forks_count") or 0),
        }
        for r in sorted(owned, key=lambda x: (-int(x.get("stargazers_count") or 0), x["name"]))[:4]
    ]

    stats = {
        "followers": int(user.get("followers") or 0),
        "public_repos": int(user.get("public_repos") or len(repos)),
        "original_repos": len(owned),
        "stars": sum(int(r.get("stargazers_count") or 0) for r in owned),
        "forks": sum(int(r.get("forks_count") or 0) for r in owned),
        "top_langs": top_five,
        "top_repos": top_repos,
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d UTC"),
    }

    (ROOT / "assets" / "github-telemetry.svg").write_text(
        render_github_telemetry_svg(stats, theme="dark"), encoding="utf-8"
    )
    (ROOT / "assets" / "github-telemetry-light.svg").write_text(
        render_github_telemetry_svg(stats, theme="light"), encoding="utf-8"
    )
    print(
        f"Generated GitHub telemetry SVGs ({stats['stars']}★, {stats['original_repos']} original / {stats['public_repos']} public repos, {stats['followers']} followers)."
    )
    return True


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

    sync_github_telemetry_svgs()

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
