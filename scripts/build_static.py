#!/usr/bin/env python3
"""Builds the static SVG assets (hero, glance tiles, stack list, project cards).

Run from the repo root:  python scripts/build_static.py
Edit the CONTENT section below, re-run, commit the regenerated files in assets/.
"""
from pathlib import Path
from xml.sax.saxutils import escape as esc

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

FONT = ("-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text','Inter',"
        "'Segoe UI',Roboto,Helvetica,Arial,sans-serif")

# Apple dark palette
BG, CARD, ELEV, LINE = "#000000", "#111113", "#1c1c1e", "#2c2c2e"
TXT, TXT2, TXT3 = "#f5f5f7", "#a1a1a6", "#86868b"
BLUE, GREEN, ORANGE, PURPLE, PINK, TEAL = "#0a84ff", "#30d158", "#ff9f0a", "#bf5af2", "#ff375f", "#64d2ff"


def svg(w, h, body, defs="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}">\n<defs>{defs}</defs>\n'
            f'<style>text{{font-family:{FONT};}}</style>\n{body}\n</svg>\n')


def save(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print("wrote", name)


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1000, 360
    defs = f"""
    <linearGradient id="ink" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#b4b4ba"/>
    </linearGradient>
    <radialGradient id="a1"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
    <radialGradient id="a2"><stop offset="0" stop-color="{PURPLE}"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
    <radialGradient id="a3"><stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
    <radialGradient id="a4"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000" stop-opacity="0.92"/><stop offset="0.5" stop-color="#000" stop-opacity="0.55"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
    </linearGradient>
    <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="38"/></filter>
    <clipPath id="clip"><rect width="{W}" height="{H}" rx="30"/></clipPath>
    """
    pills = ["Cum Laude, GPA 3.88", "Backend", "Spatial data", "GA4 and SEO"]
    x, px = 56, []
    for p in pills:
        w = int(len(p) * 8.1 + 34)
        px.append((x, w, p)); x += w + 10
    pill_svg = "".join(
        f'<rect x="{x}" y="296" width="{w}" height="34" rx="17" fill="#ffffff" fill-opacity="0.08" stroke="#ffffff" stroke-opacity="0.14"/>'
        f'<text x="{x + w/2}" y="318" text-anchor="middle" font-size="14" font-weight="500" fill="{TXT}">{esc(p)}</text>'
        for x, w, p in px)
    body = f"""
    <g clip-path="url(#clip)">
      <rect width="{W}" height="{H}" fill="{BG}"/>
      <g filter="url(#soft)" opacity="0.95">
        <circle cx="790" cy="70"  r="150" fill="url(#a1)"/>
        <circle cx="930" cy="250" r="170" fill="url(#a2)"/>
        <circle cx="690" cy="330" r="120" fill="url(#a3)"/>
        <circle cx="980" cy="60"  r="90"  fill="url(#a4)"/>
      </g>
      <rect width="{W}" height="{H}" fill="url(#fade)"/>
    </g>
    <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="29.5" fill="none" stroke="{LINE}"/>
    <text x="56" y="132" font-size="60" font-weight="700" letter-spacing="-1.8" fill="url(#ink)">I Gusti Ngurah</text>
    <text x="56" y="200" font-size="60" font-weight="700" letter-spacing="-1.8" fill="url(#ink)">Bagus Lanang P.</text>
    <text x="56" y="252" font-size="22" font-weight="400" fill="{TXT2}">Backend architect and data analytics specialist.</text>
    {pill_svg}
    """
    save("hero.svg", svg(W, H, body, defs, "I Gusti Ngurah Bagus Lanang P. — Backend architect and data analytics specialist"))


# ---------------------------------------------------------------- glance tiles
def glance():
    W, H = 1000, 150
    tiles = [
        ("3.88", "GPA, Cum Laude", "Udayana University", BLUE),
        ("2026", "Informatics graduate", "Class of July 2026", GREEN),
        ("1st", "Best Capstone Project", "MSIB RevoU", ORANGE),
        ("2", "Industry roles", "Marketing and public sector", PURPLE),
    ]
    tw, gap = 233, 22.67
    body = ""
    for i, (big, l1, l2, c) in enumerate(tiles):
        x = i * (tw + gap)
        body += f"""
        <rect x="{x+0.5}" y="0.5" width="{tw-1}" height="{H-1}" rx="24" fill="{CARD}" stroke="{LINE}"/>
        <circle cx="{x+30}" cy="34" r="5" fill="{c}"/>
        <text x="{x+24}" y="92" font-size="46" font-weight="700" letter-spacing="-1.2" fill="{TXT}">{big}</text>
        <text x="{x+24}" y="118" font-size="14" font-weight="600" fill="{TXT}">{esc(l1)}</text>
        <text x="{x+24}" y="136" font-size="13" fill="{TXT3}">{esc(l2)}</text>
        """
    save("glance.svg", svg(W, H, body, "", "Highlights: GPA 3.88 Cum Laude, graduating 2026, 1st place capstone, two industry roles"))


# ---------------------------------------------------------------- stack (settings-style list)
def stack():
    W = 1000
    groups = [
        ("Backend", [("Laravel", "#ff2d20"), ("Node.js", GREEN), ("Bun", "#f9f1e1"), ("ElysiaJS", PURPLE),
                     ("Python", "#4b8bbe"), ("JavaScript", "#f7df1e")]),
        ("Database", [("MySQL", "#4479a1"), ("Drizzle ORM", "#c5f74f")]),
        ("DevOps and cloud", [("Docker", "#2496ed"), ("AWS", ORANGE)]),
        ("Data and analytics", [("Data modeling", TEAL), ("Spatial analysis", GREEN), ("QGIS", "#93b023"),
                                ("LULC modeling", BLUE), ("GA4 event tagging", ORANGE), ("Technical SEO", PINK)]),
    ]
    left, right = 250, W - 28
    rows, y = [], 0
    for name, items in groups:
        x, line, lines = left, 0, [[]]
        for t, c in items:
            w = int(len(t) * 8.2 + 46)
            if x + w > right:
                x, line = left, line + 1
                lines.append([])
            lines[line].append((x, w, t, c)); x += w + 10
        h = 24 + len(lines) * 44
        rows.append((y, h, name, lines)); y += h
    H = y
    body = f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="26" fill="{CARD}" stroke="{LINE}"/>'
    for i, (ry, h, name, lines) in enumerate(rows):
        if i:
            body += f'<line x1="28" x2="{W-28}" y1="{ry}" y2="{ry}" stroke="{LINE}"/>'
        body += f'<text x="32" y="{ry + 12 + 30}" font-size="16" font-weight="600" fill="{TXT}">{esc(name)}</text>'
        for li, items in enumerate(lines):
            py = ry + 14 + li * 44
            for x, w, t, c in items:
                body += (f'<rect x="{x}" y="{py}" width="{w}" height="34" rx="17" fill="{ELEV}" stroke="{LINE}"/>'
                         f'<circle cx="{x+18}" cy="{py+17}" r="5" fill="{c}"/>'
                         f'<text x="{x+32}" y="{py+22}" font-size="14" font-weight="500" fill="{TXT}">{esc(t)}</text>')
    save("stack.svg", svg(W, H, body, "", "Tech stack: backend, database, DevOps and cloud, data and analytics"))


# ---------------------------------------------------------------- project cards
ICONS = {
    "plant": '<path d="M13 33C13 17 25 10 38 10C38 25 30 35 13 33Z"/><path d="M13 33L26 20"/>',
    "map": '<path d="M25 9C18 9 14 14 14 20C14 28 25 40 25 40C25 40 36 28 36 20C36 14 32 9 25 9Z"/><circle cx="25" cy="20" r="4"/>',
    "cart": '<path d="M9 13H15L19 31H36L40 18H16"/><circle cx="21" cy="37" r="2.2"/><circle cx="34" cy="37" r="2.2"/>',
}


def project(fname, icon, grad, title, badge, lines, tags, label):
    W, H = 300, 304
    a, b = grad
    defs = (f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/>'
            f'<stop offset="1" stop-color="{b}"/></linearGradient>')
    body = f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="26" fill="{CARD}" stroke="{LINE}"/>'
    body += (f'<g transform="translate(24,24)"><rect width="52" height="52" rx="14" fill="url(#g)"/>'
             f'<g transform="translate(1,1)" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g></g>')
    if badge:
        bw = int(len(badge) * 7 + 24)
        body += (f'<rect x="{W-24-bw}" y="38" width="{bw}" height="26" rx="13" fill="{ORANGE}" fill-opacity="0.16"/>'
                 f'<text x="{W-24-bw/2}" y="56" text-anchor="middle" font-size="12" font-weight="600" fill="{ORANGE}">{esc(badge)}</text>')
    body += f'<text x="24" y="112" font-size="21" font-weight="700" letter-spacing="-0.4" fill="{TXT}">{esc(title)}</text>'
    for i, l in enumerate(lines):
        body += f'<text x="24" y="{140 + i*20}" font-size="14" fill="{TXT2}">{esc(l)}</text>'
    tx = 24
    for t in tags:
        w = int(len(t) * 7.4 + 22)
        body += (f'<rect x="{tx}" y="{H-70}" width="{w}" height="26" rx="13" fill="{ELEV}" stroke="{LINE}"/>'
                 f'<text x="{tx+w/2}" y="{H-52.5}" text-anchor="middle" font-size="12" font-weight="500" fill="{TXT}">{esc(t)}</text>')
        tx += w + 8
    body += f'<text x="24" y="{H-22}" font-size="14" font-weight="500" fill="{BLUE}">View on GitHub</text>'
    save(fname, svg(W, H, body, defs, label))


def projects():
    project("project-plantpal.svg", "plant", (GREEN, "#0a7d3a"), "PlantPal Chatbot", "1st place, MSIB RevoU",
            ["AI assistant hosted on AWS with the", "LLaMA API and Streamlit, giving", "localized crop diagnostics from", "geographical specifications."],
            ["AWS", "LLaMA", "Streamlit"], "PlantPal Chatbot, best capstone project")
    project("project-lulc.svg", "map", (BLUE, "#5e5ce6"), "LULC Badung Webmap", None,
            ["Independent spatial analytics system", "that predicts Land Use and Land", "Cover change with Random Forest", "and CA-Markov models."],
            ["Random Forest", "CA-Markov"], "LULC Badung Webmap")
    project("project-harvesthub.svg", "cart", (ORANGE, PINK), "Harvest Hub", None,
            ["Multi-role agricultural e-commerce", "engine that connects local farmers,", "land managers, and gardening", "service providers."],
            ["Laravel", "MySQL"], "Harvest Hub")


if __name__ == "__main__":
    hero(); glance(); stack(); projects()
