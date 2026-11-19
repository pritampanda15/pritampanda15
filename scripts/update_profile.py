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
    bg0, bg1 = ("#060A16", "#0D1429") if dark else ("#FFFFFF", "#F1F5F9")
    card0, card1 = ("#111B36", "#0A1022") if dark else ("#FFFFFF", "#F8FAFC")
    border = "#1E293B" if dark else "#CBD5E1"
    track = "#1E293B" if dark else "#E2E8F0"
    ink = "#F8FAFC" if dark else "#0F172A"
    sub = "#CBD5E1" if dark else "#334155"
    muted = "#94A3B8" if dark else "#475569"
    header_col = "#38BDF8" if dark else "#0284C7"
    pill_bg = "#0F172A" if dark else "#F1F5F9"

    lang_colors = {
        "Python": "#38BDF8" if dark else "#0284C7",
        "HTML": "#F97316",
        "Jupyter Notebook": "#A78BFA" if dark else "#7C3AED",
        "TypeScript": "#3B82F6",
        "JavaScript": "#FBBF24" if dark else "#D97706",
        "Shell": "#34D399" if dark else "#059669",
        "Swift": "#FB7185" if dark else "#E11D48",
        "Nextflow": "#10B981",
        "R": "#60A5FA" if dark else "#2563EB",
        "Other": "#64748B",
    }

    # Build stacked language bar (total width=530, x=18, y=58)
    langs = stats["top_langs"]
    gap = 2.0
    bar_w = 530.0 - gap * max(0, len(langs) - 1)
    x_cursor = 18.0
    bar_segments: list[str] = []
    legend_items: list[str] = []
    total_lang = sum(c for _, c in langs) or 1

    for idx, (lang, count) in enumerate(langs):
        pct = count / total_lang
        seg_w = max(8.0, round(bar_w * pct, 1))
        if idx == len(langs) - 1:
            seg_w = max(4.0, round(18.0 + 530.0 - x_cursor, 1))
        col = lang_colors.get(lang, "#64748B")
        bar_segments.append(
            f'      <rect x="{x_cursor:.1f}" y="58" width="{seg_w:.1f}" height="12" rx="3" fill="{col}" class="p-bar"/>'
        )
        x_cursor += seg_w + gap

        # 2 columns x 3 rows legend
        col_i = idx % 2
        row_i = idx // 2
        lx = 18 + col_i * 264
        ly = 95 + row_i * 25
        short_lang = lang if len(lang) <= 18 else lang[:16] + "…"
        legend_items.append(
            f'      <circle cx="{lx + 5}" cy="{ly - 4}" r="4.5" fill="{col}"/>\n'
            f'      <text x="{lx + 16}" y="{ly}" class="mono" font-size="11.2" fill="{sub}">{html.escape(short_lang)}</text>\n'
            f'      <text x="{lx + 244}" y="{ly}" text-anchor="end" class="mono" font-size="11.2" font-weight="700" fill="{ink}">{pct * 100:.1f}% <tspan fill="{muted}" font-weight="400">({count})</tspan></text>'
        )

    # Top 4 repositories mini-leaderboard (right card)
    repo_rows: list[str] = []
    max_stars = max((r["stars"] for r in stats["top_repos"]), default=1) or 1
    row_colors = [
        "#F59E0B",
        "#06B6D4" if dark else "#0891B2",
        "#8B5CF6" if dark else "#7C3AED",
        "#10B981" if dark else "#059669",
    ]
    for idx, repo in enumerate(stats["top_repos"][:4]):
        ry = 56 + idx * 30
        name = repo["name"]
        if len(name) > 22:
            name = name[:20] + "…"
        bar_len = max(14, int(195 * (repo["stars"] / max_stars)))
        col = row_colors[idx % len(row_colors)]
        repo_rows.append(
            f'      <text x="18" y="{ry + 11}" class="mono" font-size="11.5" font-weight="700" fill="{ink}">{html.escape(name)}</text>\n'
            f'      <rect x="218" y="{ry + 2}" width="195" height="9" rx="4.5" fill="{track}"/>\n'
            f'      <rect x="218" y="{ry + 2}" width="{bar_len}" height="9" rx="4.5" fill="{col}" class="p-bar"/>\n'
            f'      <text x="534" y="{ry + 11}" text-anchor="end" class="mono" font-size="11" font-weight="700" fill="{sub}">★ {repo["stars"]}  <tspan fill="{muted}" font-weight="400">⑂ {repo["forks"]}</tspan></text>'
        )

    updated = stats["updated_utc"]
    kpis = [
        ("TOTAL STARS", f'{stats["stars"]:,}', "Owned original repos", "#F59E0B", "#FDE68A" if dark else "#B45309"),
        ("ORIGINAL REPOS", f'{stats["original_repos"]}', f'{stats["public_repos"]} total public', "#22D3EE" if dark else "#0891B2", "#67E8F9" if dark else "#0E7490"),
        ("TOTAL FORKS", f'{stats["forks"]:,}', "Community adoption", "#8B5CF6" if dark else "#7C3AED", "#DDD6FE" if dark else "#5B21B6"),
        ("FOLLOWERS", f'{stats["followers"]:,}', "Global research network", "#10B981" if dark else "#059669", "#6EE7B7" if dark else "#047857"),
    ]
    kpi_blocks: list[str] = []
    for idx, (label, val, caption, stroke_col, accent_col) in enumerate(kpis):
        kx = 24 + idx * 292
        kpi_blocks.append(
            f'  <g transform="translate({kx}, 46)">\n'
            f'    <rect x="0" y="0" width="276" height="92" rx="13" fill="url(#gtCard)" stroke="{stroke_col}" stroke-opacity="0.4" stroke-width="1.2"/>\n'
            f'    <circle cx="18" cy="20" r="3.5" fill="{stroke_col}" class="p-dot"/>\n'
            f'    <text x="29" y="24" class="mono" font-size="10" font-weight="700" fill="{accent_col}" letter-spacing="0.8">{label}</text>\n'
            f'    <text x="18" y="60" class="sans" font-size="31" font-weight="800" fill="{ink}" letter-spacing="-0.6">{val}</text>\n'
            f'    <text x="18" y="79" class="mono" font-size="10.5" fill="{muted}">{caption}</text>\n'
            f"  </g>"
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 342" width="100%" role="img" aria-label="Live GitHub Engineering Telemetry for pritampanda15">
  <defs>
    <linearGradient id="gtBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg0}"/>
      <stop offset="100%" stop-color="{bg1}"/>
    </linearGradient>
    <linearGradient id="gtCard" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{card0}" stop-opacity="0.96"/>
      <stop offset="100%" stop-color="{card1}" stop-opacity="0.98"/>
    </linearGradient>
    <style>
      .sans {{ font-family: 'SF Pro Display', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
      .mono {{ font-family: 'SF Mono', 'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace; }}
      @keyframes pulseSoft {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.65; }}
      }}
      .p-bar {{ animation: pulseSoft 3.6s ease-in-out infinite; }}
      .p-dot {{ animation: pulseSoft 2.4s ease-in-out infinite; }}
    </style>
  </defs>

  <rect x="2" y="2" width="1196" height="338" rx="20" fill="url(#gtBg)" stroke="{border}" stroke-width="1.5"/>

  <text x="26" y="31" class="mono" font-size="11.5" font-weight="700" fill="{header_col}" letter-spacing="1.5">GITHUB ENGINEERING TELEMETRY · @PRITAMPANDA15</text>
  <rect x="976" y="13" width="200" height="22" rx="6" fill="{pill_bg}" stroke="{border}"/>
  <text x="1076" y="27.5" text-anchor="middle" class="mono" font-size="10" fill="{muted}">SYNCED {updated}</text>

{chr(10).join(kpi_blocks)}

  <!-- Bottom Left: Language Distribution across Original Repositories -->
  <g transform="translate(24, 152)">
    <rect x="0" y="0" width="566" height="172" rx="14" fill="url(#gtCard)" stroke="{border}" stroke-width="1.2"/>
    <text x="18" y="27" class="sans" font-size="14.5" font-weight="700" fill="{ink}">Primary Language Distribution</text>
    <text x="548" y="27" text-anchor="end" class="mono" font-size="10.2" fill="{muted}">ACROSS {stats["original_repos"]} ORIGINAL REPOS</text>
    <rect x="18" y="58" width="530" height="12" rx="4" fill="{track}"/>
{chr(10).join(bar_segments)}
{chr(10).join(legend_items)}
  </g>

  <!-- Bottom Right: Most-Starred Open-Source Repositories -->
  <g transform="translate(610, 152)">
    <rect x="0" y="0" width="566" height="172" rx="14" fill="url(#gtCard)" stroke="{border}" stroke-width="1.2"/>
    <text x="18" y="27" class="sans" font-size="14.5" font-weight="700" fill="{ink}">Top Starred Open-Source Tools</text>
    <text x="548" y="27" text-anchor="end" class="mono" font-size="10.2" fill="{muted}">LIVE GITHUB STARS &amp; FORKS</text>
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
