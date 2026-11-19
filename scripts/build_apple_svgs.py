#!/usr/bin/env python3
"""Apple Design + Emil Kowalski Craft SVG generator (Dark Titanium & Light Porcelain).

Design rules applied from emilkowalski/skills:
  - apple-design: SF Pro optical typography, negative tracking on headings (-0.025em to -0.032em),
    positive tracking on small uppercase eyebrows (+0.06em), tabular-nums on all numeric metrics,
    elevated Apple surfaces with bright top specular edges, generous padding, and reduced-motion support.
  - emil-design-eng & choreograph: --ease-out cubic-bezier(0.23, 1, 0.32, 1), never scale(0),
    non-uniform shrinking stagger for one-shot entrances, eased multi-stop gradients.
  - remove-animations: zero infinite pulsing/shimmer on functional data (KPIs, charts, skill bars,
    dividers). Motion is reserved strictly where it explains the domain (Hero SE(3) orbital pocket
    and Closed-Loop Active Learning pipeline flow).
"""

from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

THEMES = {
    "light": {
        "canvas_0": "#F5F5F7",
        "canvas_1": "#EFEFF4",
        "card_0": "#FFFFFF",
        "card_1": "#FFFFFF",
        "card_subtle": "#F5F5F7",
        "border": "rgba(0,0,0,0.08)",
        "border_hex": "#E2E2E7",
        "card_border": "#E5E5EA",
        "top_specular": "#FFFFFF",
        "top_specular_op": "0.95",
        "ink": "#1D1D1F",
        "sub": "#424245",
        "muted": "#6E6E73",
        "track": "#E8E8ED",
        "shadow_color": "#000000",
        "shadow_op": "0.055",
        "grid_color": "#86868B",
        "grid_op": "0.08",
        # Apple Light Mode System Accents
        "blue": "#0071E3",
        "blue_soft": "#EDF5FF",
        "blue_border": "#BFDDFC",
        "blue_ink": "#0055B3",
        "purple": "#8944AB",
        "purple_soft": "#F6EFFB",
        "purple_border": "#DFC6F0",
        "purple_ink": "#6B2E8A",
        "green": "#248A3D",
        "green_soft": "#ECF9EF",
        "green_border": "#B8E6C3",
        "green_ink": "#186A2D",
        "amber": "#B25000",
        "amber_bar": "#D97706",
        "amber_soft": "#FFF5EB",
        "amber_border": "#F5D0A9",
        "amber_ink": "#8F3F00",
        "rose": "#D70015",
        "rose_soft": "#FFF0F1",
        "rose_border": "#F8C2C7",
        "rose_ink": "#AD0011",
        "teal": "#007A8C",
        "teal_soft": "#EBF8FA",
        "teal_border": "#B8E3EA",
        "teal_ink": "#005E6C",
        "aura_1_op": "0.10",
        "aura_2_op": "0.08",
    },
    "dark": {
        "canvas_0": "#0A0A0C",
        "canvas_1": "#111114",
        "card_0": "#1C1C1F",
        "card_1": "#161618",
        "card_subtle": "#141416",
        "border": "rgba(255,255,255,0.10)",
        "border_hex": "#2C2C30",
        "card_border": "#2C2C30",
        "top_specular": "#FFFFFF",
        "top_specular_op": "0.14",
        "ink": "#F5F5F7",
        "sub": "#D1D1D6",
        "muted": "#8E8E93",
        "track": "#2C2C30",
        "shadow_color": "#000000",
        "shadow_op": "0.35",
        "grid_color": "#FFFFFF",
        "grid_op": "0.035",
        # Apple Dark Mode System Accents
        "blue": "#0A84FF",
        "blue_soft": "#10233B",
        "blue_border": "#1F4B7A",
        "blue_ink": "#64B5FF",
        "purple": "#BF5AF2",
        "purple_soft": "#281736",
        "purple_border": "#522D70",
        "purple_ink": "#DDA0FF",
        "green": "#30D158",
        "green_soft": "#102B19",
        "green_border": "#1E5933",
        "green_ink": "#6EE792",
        "amber": "#FF9F0A",
        "amber_bar": "#FF9F0A",
        "amber_soft": "#33220B",
        "amber_border": "#664415",
        "amber_ink": "#FFC66D",
        "rose": "#FF375F",
        "rose_soft": "#36121C",
        "rose_border": "#6B2236",
        "rose_ink": "#FF859D",
        "teal": "#40C8E0",
        "teal_soft": "#0E2930",
        "teal_border": "#1C5361",
        "teal_ink": "#7CE0F2",
        "aura_1_op": "0.16",
        "aura_2_op": "0.13",
    },
}

FONT_CSS = """
      .display { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
      .text { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
      .mono { font-family: ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Monaco, Consolas, monospace; }
      .num { font-variant-numeric: tabular-nums; }
"""

ENTRANCE_CSS = """
      /* Restraint (remove-animations): zero hidden opacity:0 start states on static/functional cards */
"""


def card_shadow_def(t: dict) -> str:
    return f"""    <filter id="cardShadow" x="-8%" y="-12%" width="116%" height="128%">
      <feDropShadow dx="0" dy="2" stdDeviation="5" flood-color="{t['shadow_color']}" flood-opacity="{t['shadow_op']}"/>
    </filter>"""


def build_hero(t: dict, mode: str) -> str:
    title_grad = (
        f'<stop offset="0%" stop-color="#1D1D1F"/><stop offset="70%" stop-color="#1D1D1F"/><stop offset="100%" stop-color="#0055B3"/>'
        if mode == "light"
        else f'<stop offset="0%" stop-color="#FFFFFF"/><stop offset="65%" stop-color="#F5F5F7"/><stop offset="100%" stop-color="#64B5FF"/>'
    )
    center_ring_fill = "#FFFFFF" if mode == "light" else "#1C1C1F"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400" width="100%" role="img" aria-label="Pritam Kumar Panda, PhD — AI for Science, Computational Drug Discovery and Agentic Bio-AI at Stanford Medicine">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{t['canvas_0']}"/>
      <stop offset="100%" stop-color="{t['canvas_1']}"/>
    </linearGradient>
    <!-- Eased multi-stop ambient washes (no harsh edge) -->
    <radialGradient id="auraBlue" cx="82%" cy="46%" r="44%">
      <stop offset="0%" stop-color="{t['blue']}" stop-opacity="{t['aura_1_op']}"/>
      <stop offset="35%" stop-color="{t['blue']}" stop-opacity="0.06"/>
      <stop offset="70%" stop-color="{t['blue']}" stop-opacity="0.015"/>
      <stop offset="100%" stop-color="{t['blue']}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="auraPurple" cx="15%" cy="15%" r="48%">
      <stop offset="0%" stop-color="{t['purple']}" stop-opacity="{t['aura_2_op']}"/>
      <stop offset="40%" stop-color="{t['purple']}" stop-opacity="0.04"/>
      <stop offset="75%" stop-color="{t['purple']}" stop-opacity="0.01"/>
      <stop offset="100%" stop-color="{t['purple']}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="titleInk" x1="0%" y1="0%" x2="100%" y2="0%">
      {title_grad}
    </linearGradient>
    <linearGradient id="ligandRing" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{t['blue']}"/>
      <stop offset="55%" stop-color="{t['purple']}"/>
      <stop offset="100%" stop-color="{t['teal']}"/>
    </linearGradient>
    <pattern id="fineGrid" width="44" height="44" patternUnits="userSpaceOnUse">
      <path d="M 44 0 L 0 0 0 44" fill="none" stroke="{t['grid_color']}" stroke-opacity="{t['grid_op']}" stroke-width="1"/>
    </pattern>
    {card_shadow_def(t)}
    <clipPath id="clipHero"><rect x="2" y="2" width="1196" height="396" rx="26"/></clipPath>
    <style>
{FONT_CSS}
{ENTRANCE_CSS}
      @keyframes dashFlow {{ to {{ stroke-dashoffset: -40; }} }}
      .hbond {{ stroke-dasharray: 5 5; animation: dashFlow 3.2s linear infinite; }}
      @media (prefers-reduced-motion: reduce) {{
        .hbond {{ animation: none !important; }}
      }}
    </style>
  </defs>

  <g clip-path="url(#clipHero)">
    <rect x="0" y="0" width="1200" height="400" fill="url(#bg)"/>
    <rect x="0" y="0" width="1200" height="400" fill="url(#fineGrid)"/>
    <rect x="0" y="0" width="1200" height="400" fill="url(#auraPurple)"/>
    <rect x="0" y="0" width="1200" height="400" fill="url(#auraBlue)"/>
    <!-- Apple specular top highlight edge -->
    <line x1="28" y1="3" x2="1172" y2="3" stroke="{t['top_specular']}" stroke-opacity="{t['top_specular_op']}" stroke-width="1.5"/>

    <!-- Status Capsule (Decoration: fades gently with Lead) -->
    <g transform="translate(52, 42)" class="e-dec">
      <rect x="0" y="0" width="438" height="34" rx="17" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
      <circle cx="19" cy="17" r="5" fill="{t['green']}"/>
      <text x="34" y="21.5" class="text" font-size="13.5" font-weight="600" fill="{t['ink']}" letter-spacing="0.01em">Stanford Medicine · Open to Research &amp; AI Roles</text>
    </g>

    <!-- Lead: Display Name (Optical sizing: 54px, negative tracking -0.03em) -->
    <g class="e-lead">
      <text x="52" y="138" class="display" font-size="54" font-weight="800" fill="url(#titleInk)" letter-spacing="-1.6">Pritam Kumar Panda<tspan font-size="28" font-weight="700" fill="{t['blue']}" dx="10" letter-spacing="-0.4">PhD</tspan></text>
    </g>

    <!-- Support 1: Role Subtitle -->
    <g class="e-sup1">
      <text x="52" y="178" class="display" font-size="22" font-weight="600" fill="{t['sub']}" letter-spacing="-0.3">
        AI for Science <tspan fill="{t['blue']}">·</tspan> Computational Drug Discovery <tspan fill="{t['purple']}">·</tspan> Agentic Bio-AI
      </text>
    </g>

    <!-- Support 2: Concise Body Copy (16.5px, comfortable leading, ~64ch max) -->
    <g class="e-sup2">
      <text x="52" y="217" class="text" font-size="16.5" font-weight="400" fill="{t['muted']}">
        Building protein foundation models, SE(3)-equivariant GNNs, GPU docking &amp;
      </text>
      <text x="52" y="242" class="text" font-size="16.5" font-weight="400" fill="{t['muted']}">
        alchemical FEP engines, virtual-cell models, and eval-driven bio-AI harnesses.
      </text>
    </g>

    <!-- Support 3: 4 Apple-tinted Capability Capsules (13.5px) -->
    <g transform="translate(52, 272)" class="e-sup3">
      <rect x="0" y="0" width="166" height="34" rx="17" fill="{t['blue_soft']}" stroke="{t['blue_border']}" stroke-width="1"/>
      <text x="83" y="21.5" text-anchor="middle" class="text" font-size="13.5" font-weight="600" fill="{t['blue_ink']}">AF3 · Boltz-2 · JAX</text>

      <rect x="178" y="0" width="180" height="34" rx="17" fill="{t['purple_soft']}" stroke="{t['purple_border']}" stroke-width="1"/>
      <text x="268" y="21.5" text-anchor="middle" class="text" font-size="13.5" font-weight="600" fill="{t['purple_ink']}">PandaDock · OpenFE</text>

      <rect x="370" y="0" width="194" height="34" rx="17" fill="{t['green_soft']}" stroke="{t['green_border']}" stroke-width="1"/>
      <text x="467" y="21.5" text-anchor="middle" class="text" font-size="13.5" font-weight="600" fill="{t['green_ink']}">2,000+ Bio-Agent Skills</text>

      <rect x="576" y="0" width="174" height="34" rx="17" fill="{t['amber_soft']}" stroke="{t['amber_border']}" stroke-width="1"/>
      <text x="663" y="21.5" text-anchor="middle" class="text" font-size="13.5" font-weight="600" fill="{t['amber_ink']}">#1 Alchemistry 2027</text>
    </g>

    <!-- Bottom Hairline & Institutional Path (13.5px) -->
    <line x1="52" y1="334" x2="778" y2="334" stroke="{t['card_border']}" stroke-width="1"/>
    <text x="52" y="364" class="text" font-size="13.8" font-weight="500" fill="{t['muted']}">
      <tspan fill="{t['ink']}" font-weight="600">Stanford, CA</tspan>   ·   PhD Uppsala · Karolinska · DKFZ   ·   <tspan fill="{t['ink']}" font-weight="600">Nextflow Ambassador</tspan> · Sigma Xi
    </text>

    <!-- RIGHT EXPLANATORY MOTION GRAPHIC: SE(3) PROTEIN-LIGAND BINDING POCKET -->
    <g transform="translate(974, 200)">
      <!-- Calm rotating concentric binding-pocket orbitals -->
      <g opacity="0.78">
        <ellipse cx="0" cy="0" rx="142" ry="66" fill="none" stroke="{t['blue']}" stroke-opacity="0.28" stroke-width="1.3" stroke-dasharray="6 6">
          <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="42s" repeatCount="indefinite"/>
        </ellipse>
        <ellipse cx="0" cy="0" rx="124" ry="56" fill="none" stroke="{t['purple']}" stroke-opacity="0.30" stroke-width="1.3" transform="rotate(60)">
          <animateTransform attributeName="transform" type="rotate" from="60 0 0" to="-300 0 0" dur="34s" repeatCount="indefinite"/>
        </ellipse>
        <ellipse cx="0" cy="0" rx="112" ry="50" fill="none" stroke="{t['teal']}" stroke-opacity="0.24" stroke-width="1.2" transform="rotate(-55)">
          <animateTransform attributeName="transform" type="rotate" from="-55 0 0" to="305 0 0" dur="38s" repeatCount="indefinite"/>
        </ellipse>
      </g>

      <!-- Non-covalent H-bond & pi-stacking tracks with explanatory interaction packets -->
      <path d="M -114 -68 Q -58 -50 -30 -18" fill="none" stroke="{t['blue']}" stroke-width="1.6" class="hbond" opacity="0.65"/>
      <path d="M 118 -58 Q 64 -40 30 -18" fill="none" stroke="{t['purple']}" stroke-width="1.6" class="hbond" opacity="0.65"/>
      <path d="M 108 82 Q 54 54 30 18" fill="none" stroke="{t['green']}" stroke-width="1.6" class="hbond" opacity="0.65"/>
      <path d="M -110 76 Q -56 48 -30 18" fill="none" stroke="{t['rose']}" stroke-width="1.6" class="hbond" opacity="0.65"/>
      <path d="M 0 -122 Q 10 -72 0 -36" fill="none" stroke="{t['amber_bar']}" stroke-width="1.5" class="hbond" opacity="0.65"/>

      <circle r="3.4" fill="{t['blue']}" opacity="0">
        <animateMotion dur="3.0s" repeatCount="indefinite" path="M -114 -68 Q -58 -50 -30 -18"/>
        <animate attributeName="opacity" values="0;0.95;0.95;0" keyTimes="0;0.14;0.86;1" dur="3.0s" repeatCount="indefinite"/>
      </circle>
      <circle r="3.4" fill="{t['purple']}" opacity="0">
        <animateMotion dur="3.5s" repeatCount="indefinite" path="M 118 -58 Q 64 -40 30 -18"/>
        <animate attributeName="opacity" values="0;0.95;0.95;0" keyTimes="0;0.14;0.86;1" dur="3.5s" repeatCount="indefinite"/>
      </circle>
      <circle r="3.2" fill="{t['green']}" opacity="0">
        <animateMotion dur="3.2s" repeatCount="indefinite" path="M 108 82 Q 54 54 30 18"/>
        <animate attributeName="opacity" values="0;0.95;0.95;0" keyTimes="0;0.14;0.86;1" dur="3.2s" repeatCount="indefinite"/>
      </circle>
      <circle r="3.2" fill="{t['rose']}" opacity="0">
        <animateMotion dur="3.8s" repeatCount="indefinite" path="M -110 76 Q -56 48 -30 18"/>
        <animate attributeName="opacity" values="0;0.95;0.95;0" keyTimes="0;0.14;0.86;1" dur="3.8s" repeatCount="indefinite"/>
      </circle>

      <!-- Binding-pocket residue nodes -->
      <circle cx="-114" cy="-68" r="7.5" fill="{center_ring_fill}" stroke="{t['blue']}" stroke-width="2.4"/>
      <circle cx="118" cy="-58" r="7.5" fill="{center_ring_fill}" stroke="{t['purple']}" stroke-width="2.4"/>
      <circle cx="108" cy="82" r="7.5" fill="{center_ring_fill}" stroke="{t['green']}" stroke-width="2.4"/>
      <circle cx="-110" cy="76" r="7" fill="{center_ring_fill}" stroke="{t['rose']}" stroke-width="2.4"/>
      <circle cx="0" cy="-122" r="6.5" fill="{center_ring_fill}" stroke="{t['amber_bar']}" stroke-width="2.4"/>

      <!-- Central Aromatic Ligand Core (calm, anchored — no 0.2 Hz bobbing) -->
      <polygon points="0,-36 31,-18 31,18 0,36 -31,18 -31,-18" fill="{center_ring_fill}" stroke="url(#ligandRing)" stroke-width="3" filter="url(#cardShadow)"/>
      <polygon points="0,-23 20,-11.5 20,11.5 0,23 -20,11.5 -20,-11.5" fill="none" stroke="{t['blue']}" stroke-opacity="0.4" stroke-width="1.4" stroke-dasharray="14 6"/>
      <line x1="31" y1="-18" x2="56" y2="-31" stroke="{t['purple']}" stroke-width="2.4"/>
      <circle cx="58" cy="-32" r="5.5" fill="{t['purple']}"/>
      <line x1="-31" y1="18" x2="-56" y2="31" stroke="{t['blue']}" stroke-width="2.4"/>
      <circle cx="-58" cy="32" r="5.5" fill="{t['blue']}"/>
      <line x1="0" y1="36" x2="0" y2="62" stroke="{t['green']}" stroke-width="2.4"/>
      <circle cx="0" cy="64" r="5.2" fill="{t['green']}"/>
      <text x="0" y="5" text-anchor="middle" class="mono" font-size="13" font-weight="700" fill="{t['ink']}">SE(3)</text>

      <!-- Clean Anchored Micro-Tags (12.5px, static for effortless reading) -->
      <g transform="translate(-170, -142)">
        <rect x="0" y="0" width="106" height="28" rx="14" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
        <text x="53" y="18.5" text-anchor="middle" class="mono" font-size="12.2" font-weight="600" fill="{t['blue_ink']}">ΔΔG · FEP</text>
      </g>
      <g transform="translate(86, -142)">
        <rect x="0" y="0" width="102" height="28" rx="14" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
        <text x="51" y="18.5" text-anchor="middle" class="mono" font-size="12.2" font-weight="600" fill="{t['green_ink']}">MLIP · QM</text>
      </g>
      <g transform="translate(78, 118)">
        <rect x="0" y="0" width="112" height="28" rx="14" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
        <text x="56" y="18.5" text-anchor="middle" class="mono num" font-size="12.2" font-weight="600" fill="{t['purple_ink']}">R = 0.88</text>
      </g>
    </g>
  </g>

  <rect x="2" y="2" width="1196" height="396" rx="26" fill="none" stroke="{t['border_hex']}" stroke-width="1.2"/>
</svg>
'''


def build_impact_bento(t: dict, mode: str) -> str:
    tiles = [
        ("SCHOLARSHIP", "6,560", "+", "Citations · 89 Q1", "h-index 49 · i10 105", t["blue"], t["blue_ink"], "e-lead"),
        ("ALCHEMISTRY '27", "#1", " Indep.", "2nd Overall · RBFE", "OpenFE τ=0.48 · ρ=0.66", t["amber_bar"], t["amber_ink"], "e-sup1"),
        ("ACTIVE LEARNING", "2.5B", "+", "Molecules · Phase II", "DoD/DARPA · -60% lab", t["purple"], t["purple_ink"], "e-sup2"),
        ("AGENTIC BIO-AI", "2,000", "+", "Bio-Agent Skills", "15 PandaVerse · Evals", t["green"], t["green_ink"], "e-sup3"),
        ("TRANSLATION", "$8M", "+", "Funding & 1 Patent", "US20250339544A1", t["rose"], t["rose_ink"], "e-sup4"),
    ]
    blocks = []
    for i, (eyebrow, big, suffix, line1, line2, accent, accent_ink, cls) in enumerate(tiles):
        x = 24 + i * 234
        suffix_size = 19 if "Indep" in suffix else 28
        blocks.append(f'''  <g transform="translate({x}, 54)">
    <g class="{cls}">
      <rect x="0" y="0" width="216" height="162" rx="18" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
      <line x1="18" y1="1" x2="198" y2="1" stroke="{t['top_specular']}" stroke-opacity="{t['top_specular_op']}" stroke-width="1.2"/>
      <rect x="18" y="18" width="32" height="4" rx="2" fill="{accent}"/>
      <text x="18" y="42" class="text" font-size="11.5" font-weight="700" fill="{accent_ink}" letter-spacing="0.06em">{eyebrow}</text>
      <text x="18" y="92" class="display num" font-size="40" font-weight="800" fill="{t['ink']}" letter-spacing="-1.3">{big}<tspan font-size="{suffix_size}" font-weight="700" fill="{accent}">{suffix}</tspan></text>
      <text x="18" y="121" class="text" font-size="14.5" font-weight="600" fill="{t['sub']}">{html.escape(line1)}</text>
      <text x="18" y="144" class="text num" font-size="13" font-weight="400" fill="{t['muted']}">{html.escape(line2)}</text>
    </g>
  </g>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 288" width="100%" role="img" aria-label="Research Impact and Blind Benchmark Leadership">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{t['canvas_0']}"/>
      <stop offset="100%" stop-color="{t['canvas_1']}"/>
    </linearGradient>
    {card_shadow_def(t)}
    <style>
{FONT_CSS}
{ENTRANCE_CSS}
    </style>
  </defs>

  <rect x="2" y="2" width="1196" height="284" rx="24" fill="url(#bg)" stroke="{t['border_hex']}" stroke-width="1.2"/>
  <line x1="26" y1="3" x2="1174" y2="3" stroke="{t['top_specular']}" stroke-opacity="{t['top_specular_op']}" stroke-width="1.2"/>

  <text x="28" y="34" class="text" font-size="13" font-weight="700" fill="{t['muted']}" letter-spacing="0.08em">RESEARCH IMPACT &amp; BLIND BENCHMARK LEADERSHIP</text>
  <text x="1172" y="34" text-anchor="end" class="text" font-size="13" font-weight="600" fill="{t['blue_ink']}">Stanford Medicine · 8+ Years</text>

{chr(10).join(blocks)}

  <!-- Bottom Clean Summary Bar (14px) -->
  <g transform="translate(24, 230)">
    <rect x="0" y="0" width="1152" height="40" rx="12" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1"/>
    <text x="576" y="25" text-anchor="middle" class="text num" font-size="13.8" font-weight="500" fill="{t['sub']}">
      <tspan fill="{t['green_ink']}" font-weight="700">Arc Virtual Cell '26:</tspan> 1,648 teams · 900 CRISPRi knockdowns     ·     <tspan fill="{t['blue_ink']}" font-weight="700">PandaDock:</tspan> Pearson R = 0.88 (8.5–35× GPU)     ·     <tspan fill="{t['purple_ink']}" font-weight="700">SAIR:</tspan> 5.2M Boltz-1x
    </text>
  </g>
</svg>
'''


def build_benchmarks(t: dict, mode: str) -> str:
    spark_heights = [16, 26, 13, 30, 22, 19, 32, 20, 28, 15, 26, 22, 30, 18, 25, 21]
    spark_cols = [
        t["blue"], t["blue"], t["purple"], t["purple"], t["teal"], t["green"], t["purple"], t["blue"],
        t["green"], t["amber_bar"], t["purple"], t["blue"], t["green"], t["purple"], t["blue"], t["purple"],
    ]
    bars = []
    pts = []
    for idx, (h, col) in enumerate(zip(spark_heights, spark_cols)):
        bx = 16 + idx * 17
        by = 46 - h
        bars.append(f'        <rect x="{bx}" y="{by}" width="11" height="{h}" rx="3" fill="{col}" fill-opacity="0.82"/>')
        pts.append(f"{bx + 5.5},{by}")
    poly = " ".join(pts)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 404" width="100%" role="img" aria-label="Quantitative Benchmarks across Alchemistry 2027, PandaDock, Arc Virtual Cell 2026 and Revilico">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{t['canvas_0']}"/>
      <stop offset="100%" stop-color="{t['canvas_1']}"/>
    </linearGradient>
    {card_shadow_def(t)}
    <style>
{FONT_CSS}
{ENTRANCE_CSS}
    </style>
  </defs>

  <rect x="2" y="2" width="1196" height="400" rx="24" fill="url(#bg)" stroke="{t['border_hex']}" stroke-width="1.2"/>
  <line x1="26" y1="3" x2="1174" y2="3" stroke="{t['top_specular']}" stroke-opacity="{t['top_specular_op']}" stroke-width="1.2"/>

  <text x="28" y="34" class="text" font-size="13" font-weight="700" fill="{t['muted']}" letter-spacing="0.08em">QUANTITATIVE BENCHMARKS &amp; BLIND CHALLENGES</text>
  <text x="1172" y="34" text-anchor="end" class="text" font-size="13" font-weight="500" fill="{t['muted']}">Verified Prospective &amp; Production Telemetry</text>

  <!-- CARD 1: Alchemistry 2027 -->
  <g transform="translate(24, 54)">
    <g class="e-lead">
      <rect x="0" y="0" width="566" height="158" rx="18" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
      <text x="22" y="34" class="display" font-size="19" font-weight="700" fill="{t['ink']}" letter-spacing="-0.3">OpenADMET / Alchemistry 2027</text>
      <rect x="372" y="14" width="174" height="28" rx="14" fill="{t['amber_soft']}" stroke="{t['amber_border']}"/>
      <text x="459" y="32.5" text-anchor="middle" class="text" font-size="12" font-weight="700" fill="{t['amber_ink']}">#1 Indep. · 2nd Overall</text>
      <text x="22" y="60" class="text" font-size="14" fill="{t['muted']}">Blind RBFE in OpenFE · Crystal #1 Zero-Fit Affinity Ranking</text>

      <text x="22" y="96" class="text" font-size="14" font-weight="600" fill="{t['sub']}">Spearman ρ</text>
      <rect x="128" y="84" width="352" height="14" rx="7" fill="{t['track']}"/>
      <rect x="128" y="84" width="232" height="14" rx="7" fill="{t['amber_bar']}" class="bar-in"/>
      <text x="546" y="96" text-anchor="end" class="display num" font-size="16" font-weight="700" fill="{t['amber_ink']}">0.66</text>

      <text x="22" y="132" class="text" font-size="14" font-weight="600" fill="{t['sub']}">Kendall τ</text>
      <rect x="128" y="120" width="352" height="14" rx="7" fill="{t['track']}"/>
      <rect x="128" y="120" width="169" height="14" rx="7" fill="{t['blue']}" class="bar-in"/>
      <text x="546" y="132" text-anchor="end" class="display num" font-size="16" font-weight="700" fill="{t['blue_ink']}">0.48</text>
    </g>
  </g>

  <!-- CARD 2: PandaDock -->
  <g transform="translate(610, 54)">
    <g class="e-sup1">
      <rect x="0" y="0" width="566" height="158" rx="18" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
      <text x="22" y="34" class="display" font-size="19" font-weight="700" fill="{t['ink']}" letter-spacing="-0.3">PandaDock · SE(3) GNN + CUDA</text>
      <rect x="394" y="14" width="152" height="28" rx="14" fill="{t['blue_soft']}" stroke="{t['blue_border']}"/>
      <text x="470" y="32.5" text-anchor="middle" class="text num" font-size="12.2" font-weight="700" fill="{t['blue_ink']}">Pearson R = 0.88</text>
      <text x="22" y="60" class="text" font-size="14" fill="{t['muted']}">Trained on 741k complexes · PDBbind Refined · 17-Engine Suite</text>

      <text x="22" y="96" class="text" font-size="14" font-weight="600" fill="{t['sub']}">PDBbind R</text>
      <rect x="128" y="84" width="340" height="14" rx="7" fill="{t['track']}"/>
      <rect x="128" y="84" width="299" height="14" rx="7" fill="{t['blue']}" class="bar-in"/>
      <text x="546" y="96" text-anchor="end" class="display num" font-size="16" font-weight="700" fill="{t['blue_ink']}">0.88</text>

      <text x="22" y="132" class="text" font-size="14" font-weight="600" fill="{t['sub']}">GPU Speed</text>
      <rect x="128" y="120" width="340" height="14" rx="7" fill="{t['track']}"/>
      <rect x="128" y="120" width="316" height="14" rx="7" fill="{t['purple']}" class="bar-in"/>
      <text x="546" y="132" text-anchor="end" class="display num" font-size="15.5" font-weight="700" fill="{t['purple_ink']}">8.5–35×</text>
    </g>
  </g>

  <!-- CARD 3: Arc Virtual Cell 2026 -->
  <g transform="translate(24, 228)">
    <g class="e-sup2">
      <rect x="0" y="0" width="566" height="156" rx="18" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
      <text x="22" y="34" class="display" font-size="19" font-weight="700" fill="{t['ink']}" letter-spacing="-0.3">Arc Virtual Cell Challenge 2026</text>
      <rect x="418" y="14" width="128" height="28" rx="14" fill="{t['purple_soft']}" stroke="{t['purple_border']}"/>
      <text x="482" y="32.5" text-anchor="middle" class="text num" font-size="12.2" font-weight="700" fill="{t['purple_ink']}">1,648 Teams</text>
      <text x="22" y="60" class="text" font-size="14" fill="{t['muted']}">Blind Zero-Shot CRISPRi Perturbation across 900 Knockdowns</text>

      <g transform="translate(22, 78)">
        <rect x="0" y="0" width="298" height="58" rx="12" fill="{t['card_subtle']}" stroke="{t['card_border']}"/>
{chr(10).join(bars)}
        <polyline points="{poly}" fill="none" stroke="{t['ink']}" stroke-opacity="0.7" stroke-width="1.6"/>
      </g>

      <g transform="translate(336, 78)">
        <rect x="0" y="0" width="100" height="58" rx="12" fill="{t['purple_soft']}" stroke="{t['purple_border']}"/>
        <text x="50" y="29" text-anchor="middle" class="display num" font-size="22" font-weight="800" fill="{t['purple_ink']}">900</text>
        <text x="50" y="48" text-anchor="middle" class="text" font-size="11.5" font-weight="600" fill="{t['muted']}">Knockdowns</text>

        <rect x="110" y="0" width="100" height="58" rx="12" fill="{t['blue_soft']}" stroke="{t['blue_border']}"/>
        <text x="160" y="29" text-anchor="middle" class="display num" font-size="22" font-weight="800" fill="{t['blue_ink']}">0.099</text>
        <text x="160" y="48" text-anchor="middle" class="text" font-size="11.5" font-weight="600" fill="{t['muted']}">Blind Score</text>
      </g>
    </g>
  </g>

  <!-- CARD 4: Revilico Virtual Cell OS & Active Learning -->
  <g transform="translate(610, 228)">
    <g class="e-sup3">
      <rect x="0" y="0" width="566" height="156" rx="18" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
      <text x="22" y="34" class="display" font-size="19" font-weight="700" fill="{t['ink']}" letter-spacing="-0.3">Virtual Cell OS &amp; Active Learning</text>
      <rect x="394" y="14" width="152" height="28" rx="14" fill="{t['green_soft']}" stroke="{t['green_border']}"/>
      <text x="470" y="32.5" text-anchor="middle" class="text" font-size="12.2" font-weight="700" fill="{t['green_ink']}">Phase II Clinical</text>
      <text x="22" y="60" class="text" font-size="14" fill="{t['muted']}">Revilico RevViability (467k pairs) · DoD/DARPA Active Learning</text>

      <text x="22" y="96" class="text" font-size="14" font-weight="600" fill="{t['sub']}">RevViab R²</text>
      <rect x="128" y="84" width="340" height="14" rx="7" fill="{t['track']}"/>
      <rect x="128" y="84" width="296" height="14" rx="7" fill="{t['green']}" class="bar-in"/>
      <text x="546" y="96" text-anchor="end" class="display num" font-size="16" font-weight="700" fill="{t['green_ink']}">0.87</text>

      <text x="22" y="132" class="text" font-size="14" font-weight="600" fill="{t['sub']}">Wet-Lab Cut</text>
      <rect x="128" y="120" width="340" height="14" rx="7" fill="{t['track']}"/>
      <rect x="128" y="120" width="204" height="14" rx="7" fill="{t['rose']}" class="bar-in"/>
      <text x="546" y="132" text-anchor="end" class="display num" font-size="16" font-weight="700" fill="{t['rose_ink']}">−60%</text>
    </g>
  </g>
</svg>
'''


def build_pipeline(t: dict, mode: str) -> str:
    stages = [
        ("01", "OMICS", "Targets & Cell", ["CRISPRi Perturbation", "scRNA & Spatial", "WES/WGS · Biomarkers"], t["blue"], t["blue_soft"], t["blue_border"], t["blue_ink"]),
        ("02", "GEN-AI", "Foundation ML", ["AlphaFold3 · Boltz-2", "SE(3) GNNs · RFdiff", "PyTorch · JAX · NeMo"], t["purple"], t["purple_soft"], t["purple_border"], t["purple_ink"]),
        ("03", "PHYSICS", "Docking & FEP", ["PandaDock · AutoDock", "OpenFE · PMX · MD", "MLIPs · Psi4 · DFT"], t["green"], t["green_soft"], t["green_border"], t["green_ink"]),
        ("04", "AGENTS", "Agentic Evals", ["Biomni + Antigravity", "AutoHarness Eval Loop", "Graph RAG · MCP"], t["amber_bar"], t["amber_soft"], t["amber_border"], t["amber_ink"]),
        ("05", "CLINIC", "Translation", ["2.5B+ Screened", "Phase II Trials", "PandaVerse Open Tools"], t["rose"], t["rose_soft"], t["rose_border"], t["rose_ink"]),
    ]
    cards = []
    for i, (num, tag, title, bullets, accent, soft, sborder, ink_acc) in enumerate(stages):
        x = 24 + i * 236
        cards.append(f'''  <g transform="translate({x}, 56)">
    <rect x="0" y="0" width="208" height="184" rx="18" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
    <rect x="16" y="16" width="42" height="24" rx="12" fill="{soft}" stroke="{sborder}"/>
    <text x="37" y="32" text-anchor="middle" class="mono num" font-size="12" font-weight="700" fill="{ink_acc}">{num}</text>
    <text x="192" y="32" text-anchor="end" class="text" font-size="11.5" font-weight="700" fill="{t['muted']}" letter-spacing="0.06em">{tag}</text>
    <text x="16" y="68" class="display" font-size="18" font-weight="700" fill="{t['ink']}" letter-spacing="-0.25">{html.escape(title)}</text>
    <line x1="16" y1="82" x2="192" y2="82" stroke="{t['card_border']}" stroke-width="1"/>
    <text x="16" y="108" class="text" font-size="13.5" fill="{t['sub']}">· {html.escape(bullets[0])}</text>
    <text x="16" y="134" class="text" font-size="13.5" fill="{t['sub']}">· {html.escape(bullets[1])}</text>
    <text x="16" y="160" class="text" font-size="13.5" fill="{t['sub']}">· {html.escape(bullets[2])}</text>
  </g>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 344" width="100%" role="img" aria-label="Closed-Loop AI, Physics and Agentic Drug Discovery Architecture">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{t['canvas_0']}"/>
      <stop offset="100%" stop-color="{t['canvas_1']}"/>
    </linearGradient>
    <linearGradient id="fbGrad" x1="100%" y1="0%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="{t['rose']}"/>
      <stop offset="50%" stop-color="{t['green']}"/>
      <stop offset="100%" stop-color="{t['blue']}"/>
    </linearGradient>
    {card_shadow_def(t)}
    <style>
{FONT_CSS}
      @keyframes dashFwd {{ to {{ stroke-dashoffset: -36; }} }}
      @keyframes dashRev {{ to {{ stroke-dashoffset: 48; }} }}
      .fwd {{ stroke-dasharray: 6 6; animation: dashFwd 2.4s linear infinite; }}
      .rev {{ stroke-dasharray: 7 6; animation: dashRev 3.2s linear infinite; }}
      @media (prefers-reduced-motion: reduce) {{
        .fwd, .rev {{ animation: none !important; }}
      }}
    </style>
  </defs>

  <rect x="2" y="2" width="1196" height="340" rx="24" fill="url(#bg)" stroke="{t['border_hex']}" stroke-width="1.2"/>
  <line x1="26" y1="3" x2="1174" y2="3" stroke="{t['top_specular']}" stroke-opacity="{t['top_specular_op']}" stroke-width="1.2"/>

  <text x="28" y="34" class="text" font-size="13" font-weight="700" fill="{t['muted']}" letter-spacing="0.08em">CLOSED-LOOP AI × PHYSICS × AGENTIC DISCOVERY ENGINE</text>
  <text x="1172" y="34" text-anchor="end" class="text" font-size="13" font-weight="500" fill="{t['muted']}">Research-to-Therapeutic Architecture</text>

  <!-- Forward Connectors between stages (x=232..260, 468..496, 704..732, 940..968; y=148) -->
  <path d="M 232 148 L 260 148" stroke="{t['blue']}" stroke-width="2" class="fwd"/>
  <path d="M 468 148 L 496 148" stroke="{t['purple']}" stroke-width="2" class="fwd"/>
  <path d="M 704 148 L 732 148" stroke="{t['green']}" stroke-width="2" class="fwd"/>
  <path d="M 940 148 L 968 148" stroke="{t['amber_bar']}" stroke-width="2" class="fwd"/>

  <circle r="4" fill="{t['blue']}" opacity="0">
    <animateMotion dur="1.8s" repeatCount="indefinite" path="M 232 148 L 260 148"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <circle r="4" fill="{t['purple']}" opacity="0">
    <animateMotion dur="1.8s" begin="0.45s" repeatCount="indefinite" path="M 468 148 L 496 148"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="1.8s" begin="0.45s" repeatCount="indefinite"/>
  </circle>
  <circle r="4" fill="{t['green']}" opacity="0">
    <animateMotion dur="1.8s" begin="0.9s" repeatCount="indefinite" path="M 704 148 L 732 148"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="1.8s" begin="0.9s" repeatCount="indefinite"/>
  </circle>
  <circle r="4" fill="{t['amber_bar']}" opacity="0">
    <animateMotion dur="1.8s" begin="1.35s" repeatCount="indefinite" path="M 940 148 L 968 148"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="1.8s" begin="1.35s" repeatCount="indefinite"/>
  </circle>

{chr(10).join(cards)}

  <!-- Closed-Loop Feedback Curve Returning from Stage 5 -> Stage 1 -->
  <path d="M 1072 240 L 1072 284 Q 1072 302 1054 302 L 146 302 Q 128 302 128 284 L 128 246" fill="none" stroke="url(#fbGrad)" stroke-width="2.2" class="rev"/>
  <polygon points="128,240 121,252 135,252" fill="{t['blue']}"/>

  <circle r="4.2" fill="{t['green']}" opacity="0">
    <animateMotion dur="5.2s" repeatCount="indefinite" path="M 1072 240 L 1072 284 Q 1072 302 1054 302 L 146 302 Q 128 302 128 284 L 128 246"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.06;0.94;1" dur="5.2s" repeatCount="indefinite"/>
  </circle>
  <circle r="3.8" fill="{t['blue']}" opacity="0">
    <animateMotion dur="5.2s" begin="2.6s" repeatCount="indefinite" path="M 1072 240 L 1072 284 Q 1072 302 1054 302 L 146 302 Q 128 302 128 284 L 128 246"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.06;0.94;1" dur="5.2s" begin="2.6s" repeatCount="indefinite"/>
  </circle>

  <g transform="translate(362, 285)">
    <rect x="0" y="0" width="476" height="34" rx="17" fill="{t['card_0']}" stroke="{t['green_border']}" stroke-width="1.2" filter="url(#cardShadow)"/>
    <text x="238" y="21.5" text-anchor="middle" class="text" font-size="13.5" font-weight="600" fill="{t['green_ink']}">⟲ Closed-Loop Active Learning · Wet-Lab Experimental Feedback</text>
  </g>
</svg>
'''


def build_skills(t: dict, mode: str) -> str:
    # 3x2 Apple Bento Cards: 368x208 each; inner pill row width = 332px (x=18..350)
    domains = [
        (
            "Foundation Models & Bio-AI",
            t["blue"], t["blue_soft"], t["blue_border"], t["blue_ink"],
            [
                [("PyTorch", 82), ("JAX", 58), ("AlphaFold3", 104), ("Boltz-2", 72)],
                [("SE(3) GNNs", 108), ("RFdiffusion", 106), ("OpenFold", 104)],
                [("NVIDIA NeMo", 118), ("Pyro", 64), ("3D Gen-SBDD", 136)],
            ],
        ),
        (
            "Agentic AI, Harnesses & Evals",
            t["purple"], t["purple_soft"], t["purple_border"], t["purple_ink"],
            [
                [("Claude Code", 112), ("Gemini CLI", 102), ("MCP Tools", 104)],
                [("Biomni + Antigravity", 174), ("AutoHarness Eval", 148)],
                [("ReAct Agents", 116), ("Graph RAG", 104), ("Local LLMs", 98)],
            ],
        ),
        (
            "Docking, Alchemical FEP & QM",
            t["green"], t["green_soft"], t["green_border"], t["green_ink"],
            [
                [("PandaDock", 104), ("OpenFE · PMX", 118), ("GROMACS", 96)],
                [("AutoDock · Glide", 138), ("MLIPs · SO3krates", 184)],
                [("Psi4 · xTB · SAPT0", 148), ("VASP · SIESTA", 112), ("RDKit", 58)],
            ],
        ),
        (
            "Virtual Cell & Multi-Omics",
            t["amber_bar"], t["amber_soft"], t["amber_border"], t["amber_ink"],
            [
                [("CRISPRi Perturbation", 174), ("Scanpy · Seurat", 148)],
                [("Spatial Omics", 122), ("scRNA-seq", 100), ("WES / WGS", 96)],
                [("Variant Calling", 124), ("Biomarkers", 100), ("Proteomics", 94)],
            ],
        ),
        (
            "GPU Computing, HPC & MLOps",
            t["teal"], t["teal_soft"], t["teal_border"], t["teal_ink"],
            [
                [("CUDA · RAPIDS", 124), ("SLURM · HPC", 110), ("Nextflow", 84)],
                [("Docker · Singularity", 168), ("Snakemake", 92), ("DuckDB", 62)],
                [("AWS HealthOmics", 148), ("GCP · Vertex", 104), ("CI/CD", 66)],
            ],
        ),
        (
            "Scientific Apps & Full-Stack",
            t["rose"], t["rose_soft"], t["rose_border"], t["rose_ink"],
            [
                [("Python · R", 96), ("FastAPI", 82), ("Next.js · React", 140)],
                [("TypeScript", 102), ("Three.js · Mol*", 126), ("Marimo", 90)],
                [("Streamlit · Plotly", 140), ("Jupyter · Bash", 116), ("Nsight", 62)],
            ],
        ),
    ]

    cards = []
    for idx, (title, accent, soft, sborder, ink_acc, rows) in enumerate(domains):
        col_i = idx % 3
        row_i = idx // 3
        cx = 24 + col_i * 392
        cy = 56 + row_i * 224
        pill_svgs = []
        for r_idx, row in enumerate(rows):
            py = 66 + r_idx * 42
            # Distribute pills across 332px cleanly
            total_w = sum(w for _, w in row)
            gap = (332 - total_w) / max(1, len(row) - 1) if len(row) > 1 else 0
            px = 18.0
            for label, pw in row:
                pill_svgs.append(
                    f'      <rect x="{px:.1f}" y="{py}" width="{pw}" height="32" rx="16" fill="{soft}" stroke="{sborder}" stroke-width="1"/>\n'
                    f'      <text x="{px + pw / 2:.1f}" y="{py + 20.5}" text-anchor="middle" class="text" font-size="13" font-weight="600" fill="{ink_acc}">{html.escape(label)}</text>'
                )
                px += pw + gap

        cards.append(f'''  <g transform="translate({cx}, {cy})">
    <rect x="0" y="0" width="368" height="206" rx="18" fill="{t['card_0']}" stroke="{t['card_border']}" stroke-width="1" filter="url(#cardShadow)"/>
    <circle cx="24" cy="28" r="5" fill="{accent}"/>
    <text x="38" y="33.5" class="display" font-size="17.5" font-weight="700" fill="{t['ink']}" letter-spacing="-0.25">{html.escape(title)}</text>
    <line x1="18" y1="50" x2="350" y2="50" stroke="{t['card_border']}" stroke-width="1"/>
{chr(10).join(pill_svgs)}
  </g>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 506" width="100%" role="img" aria-label="2026 Frontier Skill Matrix across AI Foundation Models, Agentic Evals, Physics, Multi-Omics, GPU HPC and Full-Stack">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{t['canvas_0']}"/>
      <stop offset="100%" stop-color="{t['canvas_1']}"/>
    </linearGradient>
    {card_shadow_def(t)}
    <style>
{FONT_CSS}
    </style>
  </defs>

  <rect x="2" y="2" width="1196" height="502" rx="24" fill="url(#bg)" stroke="{t['border_hex']}" stroke-width="1.2"/>
  <line x1="26" y1="3" x2="1174" y2="3" stroke="{t['top_specular']}" stroke-opacity="{t['top_specular_op']}" stroke-width="1.2"/>

  <text x="28" y="34" class="text" font-size="13" font-weight="700" fill="{t['muted']}" letter-spacing="0.08em">2026 FRONTIER SKILL ARCHITECTURE</text>
  <text x="1172" y="34" text-anchor="end" class="text" font-size="13" font-weight="500" fill="{t['muted']}">Foundation Models · Agentic Evals · Physics · Omics · Systems</text>

{chr(10).join(cards)}
</svg>
'''


def build_divider(t: dict, mode: str) -> str:
    # Calm, restrained eased hairline divider (Apple craft — zero frantic bouncing dots)
    line_col = "#86868B" if mode == "light" else "#636366"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 24" width="100%" role="presentation">
  <defs>
    <linearGradient id="easedHairline" gradientUnits="userSpaceOnUse" x1="24" y1="12" x2="1176" y2="12">
      <stop offset="0%" stop-color="{line_col}" stop-opacity="0"/>
      <stop offset="18%" stop-color="{line_col}" stop-opacity="0.16"/>
      <stop offset="50%" stop-color="{line_col}" stop-opacity="0.38"/>
      <stop offset="82%" stop-color="{line_col}" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="{line_col}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="24" y="11.4" width="1152" height="1.2" rx="0.6" fill="url(#easedHairline)"/>
  <g transform="translate(600, 12)">
    <polygon points="-9,0 -4.5,-6 4.5,-6 9,0 4.5,6 -4.5,6" fill="{t['card_0']}" stroke="{t['blue']}" stroke-opacity="0.65" stroke-width="1.3"/>
    <circle cx="0" cy="0" r="2" fill="{t['blue']}"/>
  </g>
</svg>
'''


def build_footer(t: dict, mode: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 148" width="100%" role="img" aria-label="Science moves faster when the models, physics, and tools are open">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{t['canvas_0']}"/>
      <stop offset="100%" stop-color="{t['canvas_1']}"/>
    </linearGradient>
    <radialGradient id="fAura1" cx="25%" cy="100%" r="48%">
      <stop offset="0%" stop-color="{t['blue']}" stop-opacity="0.12"/>
      <stop offset="45%" stop-color="{t['blue']}" stop-opacity="0.035"/>
      <stop offset="100%" stop-color="{t['blue']}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="fAura2" cx="75%" cy="100%" r="48%">
      <stop offset="0%" stop-color="{t['purple']}" stop-opacity="0.11"/>
      <stop offset="45%" stop-color="{t['purple']}" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="{t['purple']}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="clipFoot"><rect x="2" y="2" width="1196" height="144" rx="22"/></clipPath>
    <style>
{FONT_CSS}
    </style>
  </defs>

  <g clip-path="url(#clipFoot)">
    <rect x="0" y="0" width="1200" height="148" fill="url(#bg)"/>
    <rect x="0" y="0" width="1200" height="148" fill="url(#fAura1)"/>
    <rect x="0" y="0" width="1200" height="148" fill="url(#fAura2)"/>
    <line x1="26" y1="3" x2="1174" y2="3" stroke="{t['top_specular']}" stroke-opacity="{t['top_specular_op']}" stroke-width="1.2"/>

    <text x="600" y="68" text-anchor="middle" class="display" font-size="22" font-weight="700" fill="{t['ink']}" letter-spacing="-0.35">
      “Science moves faster when the models, physics, and tools are open.”
    </text>
    <text x="600" y="102" text-anchor="middle" class="text" font-size="14" font-weight="500" fill="{t['muted']}" letter-spacing="0.03em">
      Pritam Kumar Panda, PhD  ·  Stanford Medicine  ·  PandaVerse  ·  atomodyssey.com
    </text>
  </g>

  <rect x="2" y="2" width="1196" height="144" rx="22" fill="none" stroke="{t['border_hex']}" stroke-width="1.2"/>
</svg>
'''


def main() -> None:
    generators = {
        "hero-banner": build_hero,
        "impact-bento": build_impact_bento,
        "benchmarks-card": build_benchmarks,
        "pipeline-motion": build_pipeline,
        "skills-architecture": build_skills,
        "divider-wave": build_divider,
        "footer-wave": build_footer,
    }
    for name, fn in generators.items():
        (ASSETS / f"{name}.svg").write_text(fn(THEMES["dark"], "dark"), encoding="utf-8")
        (ASSETS / f"{name}-light.svg").write_text(fn(THEMES["light"], "light"), encoding="utf-8")
    print(f"Generated {len(generators) * 2} Apple-design Dark + Light SVGs.")


if __name__ == "__main__":
    main()
