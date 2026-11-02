#!/usr/bin/env python3
"""Generates assets/stats.svg, assets/contributions.svg and assets/languages.svg.

Live mode (used by the GitHub Action):
    GH_TOKEN=... GH_USER=your-username python scripts/generate_stats.py
Preview / first-commit modes (no network):
    python scripts/generate_stats.py --demo          # fake sample data, for previewing the design
    python scripts/generate_stats.py --placeholder   # empty state shown until the first Action run

Only the Python standard library is used.
"""
import json, os, random, sys, urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape as esc

OUT = Path(os.environ.get("OUT_DIR") or Path(__file__).resolve().parent.parent / "assets")
OUT.mkdir(parents=True, exist_ok=True)

FONT = ("-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text','Inter',"
        "'Segoe UI',Roboto,Helvetica,Arial,sans-serif")
BG, CARD, ELEV, LINE = "#000000", "#111113", "#1c1c1e", "#2c2c2e"
TXT, TXT2, TXT3 = "#f5f5f7", "#a1a1a6", "#86868b"
BLUE, GREEN, ORANGE, PURPLE, PINK, TEAL = "#0a84ff", "#30d158", "#ff9f0a", "#bf5af2", "#ff375f", "#64d2ff"
FALLBACK = [BLUE, GREEN, ORANGE, PURPLE, PINK, TEAL, "#ffd60a", "#5e5ce6"]


# ------------------------------------------------------------------ data
QUERY = """
query($login:String!){
  user(login:$login){
    followers{totalCount}
    allRepos: repositories(ownerAffiliations:OWNER){totalCount}
    repositories(ownerAffiliations:OWNER, isFork:false, first:100, orderBy:{field:PUSHED_AT, direction:DESC}){
      nodes{
        stargazerCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}){edges{size node{name color}}}
      }
    }
    pullRequests{totalCount}
    contributionsCollection{
      totalCommitContributions
      contributionCalendar{
        totalContributions
        weeks{contributionDays{date contributionCount weekday}}
      }
    }
  }
}"""


def fetch(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload or not payload.get("data", {}).get("user"):
        raise SystemExit(f"GitHub API error: {payload.get('errors') or 'user not found'}")
    u = payload["data"]["user"]
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    langs = {}
    stars = 0
    for repo in u["repositories"]["nodes"]:
        stars += repo["stargazerCount"]
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            cur = langs.get(n, (0, e["node"]["color"]))
            langs[n] = (cur[0] + e["size"], cur[1] or e["node"]["color"])
    return dict(
        repos=u["allRepos"]["totalCount"], stars=stars, followers=u["followers"]["totalCount"],
        prs=u["pullRequests"]["totalCount"], commits=cc["totalCommitContributions"],
        total=cal["totalContributions"],
        weeks=[[(d["date"], d["contributionCount"], d["weekday"]) for d in w["contributionDays"]]
               for w in cal["weeks"]],
        langs=sorted(((n, c, s) for n, (s, c) in langs.items()), key=lambda x: -x[2]),
    )


def blank_weeks(counts=None, seed=7):
    """53 weeks ending today. counts=None -> all zero (placeholder); otherwise random demo data."""
    rnd = random.Random(seed)
    today = date.today()
    start = today - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    weeks, d = [], start
    while d <= today:
        week = []
        for _ in range(7):
            if d <= today:
                n = 0
                if counts == "demo":
                    n = 0 if rnd.random() < 0.3 else int(rnd.expovariate(1 / 4)) + (rnd.random() < 0.1) * 12
                week.append((d.isoformat(), n, (d.weekday() + 1) % 7))
            d += timedelta(days=1)
        weeks.append(week)
    return weeks


def demo():
    weeks = blank_weeks("demo")
    return dict(repos=24, stars=18, followers=9, prs=31, commits=412,
                total=sum(c for w in weeks for _, c, _ in w), weeks=weeks,
                langs=[("PHP", "#4F5D95", 420), ("JavaScript", "#f1e05a", 310), ("Python", "#3572A5", 260),
                       ("Blade", "#f7523f", 120), ("TypeScript", "#3178c6", 90), ("CSS", "#563d7c", 60),
                       ("Jupyter Notebook", "#DA5B0B", 40)])


def placeholder():
    return dict(repos=None, stars=None, followers=None, prs=None, commits=None, total=None,
                weeks=blank_weeks(None), langs=[])


# ------------------------------------------------------------------ helpers
def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}">\n<style>text{{font-family:{FONT};}}</style>\n{body}\n</svg>\n')


def fmt(n):
    return "—" if n is None else f"{n:,}"


def streaks(weeks):
    days = [(d, c) for w in weeks for d, c, _ in w]
    longest = cur = 0
    for _, c in days:
        cur = cur + 1 if c > 0 else 0
        longest = max(longest, cur)
    s = 0
    for i, (_, c) in enumerate(reversed(days)):
        if c > 0:
            s += 1
        elif i == 0:      # today may still be empty
            continue
        else:
            break
    return s, longest


# ------------------------------------------------------------------ stats card
def render_stats(d):
    W, H = 1000, 160
    items = [("Repositories", d["repos"], BLUE), ("Stars earned", d["stars"], ORANGE),
             ("Commits this year", d["commits"], GREEN), ("Pull requests", d["prs"], PURPLE),
             ("Followers", d["followers"], PINK)]
    cw = (W - 56) / len(items)
    body = f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="26" fill="{CARD}" stroke="{LINE}"/>'
    for i, (label, val, c) in enumerate(items):
        x = 28 + i * cw
        if i:
            body += f'<line x1="{x}" x2="{x}" y1="34" y2="{H-34}" stroke="{LINE}"/>'
        px = x + (0 if i == 0 else 26)
        body += (f'<circle cx="{px+5}" cy="42" r="5" fill="{c}"/>'
                 f'<text x="{px+18}" y="47" font-size="14" font-weight="500" fill="{TXT3}">{esc(label)}</text>'
                 f'<text x="{px}" y="112" font-size="50" font-weight="700" letter-spacing="-1.5" fill="{TXT}">{fmt(val)}</text>')
    return svg(W, H, body, "GitHub statistics: repositories, stars, commits, pull requests, followers")


# ------------------------------------------------------------------ contribution graph
def render_contrib(d, is_placeholder=False):
    W, H = 1000, 292
    cell, gap = 13, 4
    pitch = cell + gap
    weeks = d["weeks"]
    left, top = 62, 112
    levels = sorted(c for w in weeks for _, c, _ in w if c > 0)

    def level(c):
        if c <= 0 or not levels:
            return 0
        q = lambda p: levels[min(len(levels) - 1, int(len(levels) * p))]
        return 1 if c <= q(.25) else 2 if c <= q(.5) else 3 if c <= q(.75) else 4

    op = {0: None, 1: .30, 2: .55, 3: .78, 4: 1.0}
    body = f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="26" fill="{CARD}" stroke="{LINE}"/>'
    body += f'<text x="32" y="54" font-size="22" font-weight="700" letter-spacing="-0.4" fill="{TXT}">Contributions</text>'
    sub = "Updating after the first workflow run" if is_placeholder else f"{fmt(d['total'])} in the last year"
    body += f'<text x="{W-32}" y="54" text-anchor="end" font-size="15" fill="{TXT3}">{esc(sub)}</text>'

    # month labels
    last_m, last_x = None, -99
    for ci, w in enumerate(weeks):
        m = date.fromisoformat(w[0][0]).strftime("%b")
        x = left + ci * pitch
        if m != last_m and x - last_x >= 38:
            body += f'<text x="{x}" y="{top-12}" font-size="12" fill="{TXT3}">{m}</text>'
            last_m, last_x = m, x
        elif m != last_m:
            last_m = m
    # weekday labels
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        body += f'<text x="{left-12}" y="{top + row*pitch + 11}" text-anchor="end" font-size="11" fill="{TXT3}">{name}</text>'
    # cells
    for ci, w in enumerate(weeks):
        for dt, c, wd in w:
            x, y = left + ci * pitch, top + wd * pitch
            lv = level(c)
            if lv == 0:
                body += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3.5" fill="{ELEV}"/>'
            else:
                body += (f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3.5" fill="{GREEN}" '
                         f'fill-opacity="{op[lv]}"><title>{c} on {dt}</title></rect>')
    # footer
    cur, lng = streaks(weeks) if not is_placeholder else (None, None)
    fy = top + 7 * pitch + 28
    days = lambda n: "—" if n is None else f"{n} day" + ("" if n == 1 else "s")
    body += (f'<text x="32" y="{fy}" font-size="14" fill="{TXT3}">Current streak'
             f'<tspan dx="8" font-weight="600" fill="{TXT}">{days(cur)}</tspan>'
             f'<tspan dx="32" fill="{TXT3}">Longest streak</tspan>'
             f'<tspan dx="8" font-weight="600" fill="{TXT}">{days(lng)}</tspan></text>')
    lx = W - 32 - (5 * pitch) - 70
    body += f'<text x="{lx}" y="{fy}" text-anchor="end" font-size="12" fill="{TXT3}">Less</text>'
    for i in range(5):
        x = lx + 10 + i * pitch
        if i == 0:
            body += f'<rect x="{x}" y="{fy-11}" width="{cell}" height="{cell}" rx="3.5" fill="{ELEV}"/>'
        else:
            body += f'<rect x="{x}" y="{fy-11}" width="{cell}" height="{cell}" rx="3.5" fill="{GREEN}" fill-opacity="{op[i]}"/>'
    body += f'<text x="{lx + 10 + 5*pitch + 6}" y="{fy}" font-size="12" fill="{TXT3}">More</text>'
    return svg(W, H, body, "GitHub contribution graph for the last year")


# ------------------------------------------------------------------ languages (storage-bar style)
def render_langs(d):
    W = 1000
    langs = d["langs"]
    total = sum(s for _, _, s in langs) or 1
    top = langs[:5]
    rest = sum(s for _, _, s in langs[5:])
    rows = [(n, c or FALLBACK[i % len(FALLBACK)], s) for i, (n, c, s) in enumerate(top)]
    if rest:
        rows.append(("Other", "#636366", rest))
    nrows = (len(rows) + 2) // 3
    H = 128 + (nrows - 1) * 36 + 36 if rows else 150
    body = f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="26" fill="{CARD}" stroke="{LINE}"/>'
    body += f'<text x="32" y="54" font-size="22" font-weight="700" letter-spacing="-0.4" fill="{TXT}">Languages</text>'
    bx, bw, by = 32, W - 64, 76
    body += f'<clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="14" rx="7"/></clipPath>'
    body += f'<rect x="{bx}" y="{by}" width="{bw}" height="14" rx="7" fill="{ELEV}"/>'
    x = bx
    for n, c, s in rows:
        w = bw * s / total
        body += f'<rect x="{x:.2f}" y="{by}" width="{max(w-2,1):.2f}" height="14" fill="{c}" clip-path="url(#bar)"/>'
        x += w
    if not rows:
        body += f'<text x="32" y="124" font-size="15" fill="{TXT3}">Language data appears after the first workflow run.</text>'
    colw = (W - 64) / 3
    for i, (n, c, s) in enumerate(rows):
        cx, cy = 32 + (i % 3) * colw, 128 + (i // 3) * 36
        pct = s * 100 / total
        body += (f'<circle cx="{cx+5}" cy="{cy-5}" r="5" fill="{c}"/>'
                 f'<text x="{cx+18}" y="{cy}" font-size="15" font-weight="500" fill="{TXT}">{esc(n)}</text>'
                 f'<text x="{cx+colw-28}" y="{cy}" text-anchor="end" font-size="15" fill="{TXT3}">{pct:.1f}%</text>')
    return svg(W, H, body, "Most used languages")


# ------------------------------------------------------------------ main
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--live"
    if mode == "--demo":
        d, ph = demo(), False
    elif mode == "--placeholder":
        d, ph = placeholder(), True
    else:
        user, token = os.environ.get("GH_USER"), os.environ.get("GH_TOKEN")
        if not user or not token:
            raise SystemExit("Set GH_USER and GH_TOKEN, or use --demo / --placeholder.")
        d, ph = fetch(user, token), False
    (OUT / "stats.svg").write_text(render_stats(d), encoding="utf-8")
    (OUT / "contributions.svg").write_text(render_contrib(d, ph), encoding="utf-8")
    (OUT / "languages.svg").write_text(render_langs(d), encoding="utf-8")
    print(f"wrote stats/contributions/languages ({mode}) to {OUT}")


if __name__ == "__main__":
    main()
