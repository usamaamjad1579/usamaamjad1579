"""Build the SVG images used by the profile README.

Static images (banner, terminal, quote, project cards) come from profile.json.
The trophies use live data from the GitHub API, so the daily workflow keeps
them current. Only the Python standard library is needed.

    python scripts/build_assets.py                      # static images only
    GITHUB_TOKEN=... python scripts/build_assets.py     # also trophies
"""

import html
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PROFILE = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))

# Colours chosen to match the "tokyonight" analytics cards.
BG = "#1a1b27"
BG_DEEP = "#0d1117"
BORDER = "#2b3044"
TEXT = "#c0caf5"
MUTED = "#8b93b8"
BLUE = "#70a5fd"
PURPLE = "#bb9af7"
TEAL = "#38bdae"
CHIP = "#24283b"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; opacity: 1 !important; } }"


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def text_width(text: str, size: float, bold: bool = False) -> float:
    """Rough rendered width of UI-font text, good enough for layout."""
    return len(text) * size * (0.6 if bold else 0.55)


def wrap(text: str, max_width: float, size: float) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if current and text_width(trial, size) > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    return lines + [current] if current else lines


def svg(width: int, height: int, title: str, body: str, style: str = "", defs: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title" font-family="{FONT}">
<title id="title">{esc(title)}</title>
<defs>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{PURPLE}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
  {defs}
</defs>
<style>{style} {REDUCED_MOTION}</style>
{body}
</svg>
"""


def chip(x: float, y: float, label: str, size: float = 12) -> tuple[float, str]:
    width = text_width(label, size, bold=True) + 22
    return width, (
        f'<rect x="{x:.0f}" y="{y}" width="{width:.0f}" height="26" rx="13" fill="{CHIP}" stroke="{BORDER}"/>'
        f'<text x="{x + width / 2:.0f}" y="{y + 17.5}" text-anchor="middle" font-size="{size}" font-weight="600" fill="{TEXT}">{esc(label)}</text>'
    )


# ---------------------------------------------------------------- banner


def banner() -> str:
    W, H = 1280, 330
    layers = [(80, [110, 175, 240]), (190, [80, 140, 200, 260]), (300, [110, 175, 240]), (400, [145, 205])]
    edges, nodes = [], []
    for (x1, ys1), (x2, ys2) in zip(layers, layers[1:]):
        for y1 in ys1:
            for y2 in ys2:
                edges.append(f'<line class="edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    delay = 0.0
    for x, ys in layers:
        for y in ys:
            nodes.append(
                f'<circle cx="{x}" cy="{y}" r="13" fill="{BG}" stroke="url(#edge)" stroke-width="2.5"/>'
                f'<circle class="pulse" style="animation-delay:{delay:.1f}s" cx="{x}" cy="{y}" r="5" fill="{PURPLE}"/>'
            )
            delay += 0.25

    # A document and a cited answer floating around the network: RAG in a picture.
    doc = (
        f'<rect width="92" height="116" rx="10" fill="{CHIP}" stroke="{BORDER}"/>'
        + "".join(
            f'<rect x="16" y="{22 + i * 16}" width="{60 - (i % 2) * 18}" height="6" rx="3" fill="{BLUE if i == 0 else MUTED}" opacity="{1 if i == 0 else 0.6}"/>'
            for i in range(5)
        )
    )
    bubble = (
        f'<rect width="150" height="46" rx="12" fill="{CHIP}" stroke="{BORDER}"/>'
        f'<text x="16" y="29" font-size="14" fill="{TEXT}" font-family="{MONO}">answer [1][2]</text>'
    )

    name = PROFILE["name"].upper()
    subtitle = "   |   ".join(["AI/ML Engineer", "RAG", "AI Agents", "Deep Learning", "BS AI @ UMT"])
    tags_x, tags = 0.0, []
    for tag in PROFILE["tags"]:
        width, markup = chip(0, 0, tag, 13)
        tags.append((tags_x, width, markup))
        tags_x += width + 10
    tags_start = 925 - tags_x / 2
    tag_markup = "".join(f'<g transform="translate({tags_start + x:.0f} 228)">{m}</g>' for x, _, m in tags)

    defs = f"""
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG_DEEP}"/></linearGradient>
  <linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="70" y1="0" x2="410" y2="0"><stop offset="0" stop-color="{PURPLE}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
  <radialGradient id="glow1" cx="0.22" cy="0.5" r="0.45"><stop offset="0" stop-color="{PURPLE}" stop-opacity="0.28"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="glow2" cx="0.85" cy="0.2" r="0.4"><stop offset="0" stop-color="{BLUE}" stop-opacity="0.18"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{BORDER}" stroke-width="0.6" opacity="0.5"/></pattern>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>"""
    style = f"""
  .edge {{ stroke: url(#edge); stroke-width: 1.4; opacity: 0.35; stroke-dasharray: 5 9; animation: flow 3s linear infinite; }}
  .pulse {{ animation: pulse 3s ease-in-out infinite; }}
  .float {{ animation: bob 6s ease-in-out infinite; }}
  .float2 {{ animation: bob 7s ease-in-out infinite reverse; }}
  @keyframes flow {{ to {{ stroke-dashoffset: -28; }} }}
  @keyframes pulse {{ 0%, 100% {{ opacity: 0.35; }} 50% {{ opacity: 1; }} }}
  @keyframes bob {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}"""
    body = f"""
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <rect width="{W}" height="{H}" fill="url(#glow1)"/>
  <rect width="{W}" height="{H}" fill="url(#glow2)"/>
  {''.join(edges)}
  {''.join(nodes)}
  <g class="float"><g transform="translate(455 40)">{doc}</g></g>
  <g class="float2"><g transform="translate(430 238)">{bubble}</g></g>
  <text x="925" y="128" text-anchor="middle" font-family="'Arial Black', 'Segoe UI Black', {FONT}" font-weight="900" font-size="48" letter-spacing="1" fill="#ffffff" textLength="640" lengthAdjust="spacingAndGlyphs">{esc(name)}</text>
  <rect x="725" y="150" width="400" height="3" rx="1.5" fill="url(#accent)"/>
  <text x="925" y="190" text-anchor="middle" font-size="17" font-weight="600" fill="{TEXT}">{esc(subtitle)}</text>
  {tag_markup}
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{BORDER}"/>"""
    return svg(W, H, f"{PROFILE['name']}: {PROFILE['title']}", body, style, defs)


# ---------------------------------------------------------------- terminal


# A real session with rag-document-chat: the chunk count and similarity scores
# come from running it on the sample documents. The answer text is the LLM's.
TERMINAL_LINES = [
    ("prompt", "$ python"),
    ("code", ">>> from rag import *"),
    ("code", ">>> from rag.llm import GroqChat"),
    ("code", ">>> store = VectorStore()"),
    ("code", '>>> docs = load_folder("data/sample")'),
    ("code", ">>> store.add(chunk_pages(docs, 500, 100))"),
    ("out", "15"),
    ("code", '>>> q = ("How many days of annual "'),
    ("code", '...      "leave do I get?")'),
    ("code", ">>> for h in store.search(q, k=2):"),
    ("code", '...     print(f"{h.score:.2f}", h.source)'),
    ("out", "0.79 northwind_handbook.md"),
    ("out", "0.56 northwind_handbook.md"),
    ("code", ">>> llm = GroqChat(api_key, model)"),
    ("code", ">>> rag = RAGPipeline(store, llm)"),
    ("code", ">>> print(rag.answer(q).text)"),
    ("answer", "Full-time employees receive 20"),
    ("answer", "days of paid annual leave per"),
    ("answer", "calendar year [1]."),
]


def terminal() -> str:
    W, line_h, top, size = 460, 26, 78, 15.5
    H = top + line_h * len(TERMINAL_LINES) + 30
    colours = {"prompt": TEAL, "code": TEXT, "out": MUTED, "answer": "#9ece6a"}
    rows = []
    for i, (kind, text) in enumerate(TERMINAL_LINES):
        y = top + i * line_h
        if text[:4] in (">>> ", "... "):
            content = f'<tspan fill="{PURPLE}">{esc(text[:4])}</tspan>{esc(text[4:])}'
        else:
            content = esc(text)
        rows.append(
            f'<text class="line" style="animation-delay:{0.4 + i * 0.45:.2f}s" x="24" y="{y}" '
            f'font-family="{MONO}" font-size="{size}" xml:space="preserve" fill="{colours[kind]}">{content}</text>'
        )
    cursor_y = top + len(TERMINAL_LINES) * line_h
    rows.append(
        f'<text class="line" style="animation-delay:{0.4 + len(TERMINAL_LINES) * 0.45:.2f}s" x="24" y="{cursor_y}" '
        f'font-family="{MONO}" font-size="{size}" fill="{PURPLE}">&gt;&gt;&gt; <tspan class="cursor" fill="{TEXT}">▌</tspan></text>'
    )
    H += line_h
    style = """
  .line { opacity: 0; animation: show 0.3s ease-out forwards; }
  .cursor { animation: blink 1s steps(1) infinite; }
  @keyframes show { to { opacity: 1; } }
  @keyframes blink { 50% { opacity: 0; } }"""
    dots = "".join(f'<circle cx="{26 + i * 22}" cy="26" r="7" fill="{c}"/>' for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
    body = f"""
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 14.5a14 14 0 0 1 14-14h{W - 29}a14 14 0 0 1 14 14v37h-{W - 1}z" fill="{CHIP}"/>
{dots}
<text x="{W / 2}" y="31" text-anchor="middle" font-size="13" fill="{MUTED}">rag-document-chat  ·  python</text>
{''.join(rows)}"""
    return svg(W, H, "Terminal: retrieving cited answers with rag-document-chat", body, style)


# ---------------------------------------------------------------- pipeline


PIPELINE_STEPS = [
    ("Upload", "PDF, TXT or Markdown"),
    ("Chunk", "500 characters, 100 overlap"),
    ("Embed", "all-MiniLM-L6-v2, on your machine"),
    ("Search", "ChromaDB, top-4 by cosine similarity"),
    ("Filter", "drop passages scoring below 0.25"),
    ("Generate", "Llama 3.3 on Groq, strict prompt"),
    ("Answer", "every claim cited, or \"not found\""),
]


def pipeline() -> str:
    W, top, step_h, box_h = 460, 66, 54, 42
    H = top + step_h * len(PIPELINE_STEPS) + 6
    parts = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="24" y="42" font-size="17" font-weight="700" fill="{BLUE}">How RAG Document Chat answers</text>',
    ]
    for i, (name, detail) in enumerate(PIPELINE_STEPS):
        y = top + i * step_h
        last = i == len(PIPELINE_STEPS) - 1
        parts.append(
            f'<g class="step" style="animation-delay:{i * 0.35:.2f}s">'
            f'<rect x="24" y="{y}" width="{W - 48}" height="{box_h}" rx="10" fill="{CHIP}" stroke="{TEAL if last else BORDER}"/>'
            f'<circle cx="52" cy="{y + box_h / 2}" r="13" fill="url(#accent)"/>'
            f'<text x="52" y="{y + box_h / 2 + 5}" text-anchor="middle" font-size="13" font-weight="800" fill="{BG}">{i + 1}</text>'
            f'<text x="78" y="{y + 18}" font-size="15" font-weight="700" fill="{TEXT}">{esc(name)}</text>'
            f'<text x="78" y="{y + 35}" font-size="13" fill="{MUTED}">{esc(detail)}</text></g>'
        )
        if not last:
            parts.append(f'<line class="arrow" x1="52" y1="{y + box_h}" x2="52" y2="{y + step_h}" stroke="{PURPLE}" stroke-width="2"/>')
    style = """
  .step { opacity: 0; animation: show 0.4s ease-out forwards; }
  .arrow { stroke-dasharray: 3 4; animation: flow 1.2s linear infinite; }
  @keyframes show { to { opacity: 1; } }
  @keyframes flow { to { stroke-dashoffset: -14; } }"""
    return svg(W, H, "RAG pipeline: upload, chunk, embed, search, filter, generate, answer with citations", "".join(parts), style)


# ---------------------------------------------------------------- quote


def quote() -> str:
    W, H = 660, 130
    q = PROFILE["quote"]
    body = f"""
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>
<rect x="0" y="18" width="4" height="{H - 36}" rx="2" fill="url(#accent)"/>
<text x="34" y="78" font-family="Georgia, 'Times New Roman', serif" font-size="80" fill="{PURPLE}" opacity="0.35">“</text>
<text x="{W / 2}" y="62" text-anchor="middle" font-size="22" font-style="italic" fill="{TEXT}">{esc(q['text'])}</text>
<text x="{W - 34}" y="100" text-anchor="end" font-size="15" fill="{BLUE}">— {esc(q['author'])}</text>"""
    return svg(W, H, f"Quote: {q['text']} ({q['author']})", body)


# ---------------------------------------------------------------- project cards


def project_card(project: dict) -> str:
    W, H = 640, 250
    pad = 30
    desc = wrap(project["description"], W - 2 * pad, 15)[:2]
    desc_markup = "".join(
        f'<text x="{pad}" y="{112 + i * 22}" font-size="15" fill="{MUTED}">{esc(line)}</text>' for i, line in enumerate(desc)
    )
    x, highlights = pad, []
    for item in project["highlights"]:
        highlights.append(
            f'<circle cx="{x + 4}" cy="172" r="4" fill="{TEAL}"/>'
            f'<text x="{x + 14}" y="177" font-size="14" font-weight="600" fill="{TEXT}">{esc(item)}</text>'
        )
        x += text_width(item, 14, bold=True) + 40
    x, chips = pad, []
    for tech in project["tech"]:
        width, markup = chip(x, 200, tech)
        chips.append(markup)
        x += width + 8
    body = f"""
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>
<rect x="{pad}" y="0" width="80" height="4" rx="2" fill="url(#accent)"/>
<text x="{pad}" y="44" font-size="12.5" font-weight="700" letter-spacing="2" fill="{PURPLE}">{esc(project['kind'])}</text>
<text x="{pad}" y="78" font-size="25" font-weight="700" fill="{BLUE}">{esc(project['title'])}</text>
<text x="{W - pad}" y="46" text-anchor="end" font-size="13" fill="{MUTED}">View repo ↗</text>
{desc_markup}
{''.join(highlights)}
{''.join(chips)}"""
    return svg(W, H, f"{project['title']}: {project['description']}", body)


# ---------------------------------------------------------------- trophies

TROPHY_QUERY = """query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      nodes { stargazerCount languages(first: 20) { nodes { name } } }
    }
    contributionsCollection { totalCommitContributions restrictedContributionsCount }
  }
}"""

# Points needed for each rank, lowest first: C, B, A, AA, AAA, S, SS, SSS.
RANKS = ["C", "B", "A", "AA", "AAA", "S", "SS", "SSS"]
THRESHOLDS = {
    "Commits": [1, 10, 50, 100, 200, 500, 1000, 2000],
    "Repositories": [1, 5, 10, 20, 30, 50, 80, 100],
    "Languages": [1, 3, 5, 7, 9, 11, 13, 15],
    "Experience": [0.25, 1, 2, 3, 4, 6, 8, 10],
    "Stars": [1, 10, 30, 50, 100, 200, 500, 1000],
    "Followers": [1, 10, 20, 50, 100, 200, 500, 1000],
    "Pull Requests": [1, 10, 20, 50, 100, 200, 500, 1000],
    "Issues": [1, 10, 20, 50, 100, 200, 500, 1000],
}
RANK_COLOURS = {"S": ("#ffe680", "#f0b400"), "A": ("#c7d2fe", "#7c8cf8"), "B": ("#f5c48a", "#c77d2e"), "C": ("#cbd5e1", "#7d8aa3")}


def fetch_trophy_data(login: str, token: str) -> dict:
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": TROPHY_QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    user = payload["data"]["user"]
    repos = user["repositories"]["nodes"]
    created = datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    contributions = user["contributionsCollection"]
    return {
        "Commits": contributions["totalCommitContributions"] + contributions["restrictedContributionsCount"],
        "Repositories": user["repositories"]["totalCount"],
        "Languages": len({lang["name"] for repo in repos for lang in repo["languages"]["nodes"]}),
        "Experience": round((datetime.now(timezone.utc) - created).days / 365.25, 1),
        "Stars": sum(repo["stargazerCount"] for repo in repos),
        "Followers": user["followers"]["totalCount"],
        "Pull Requests": user["pullRequests"]["totalCount"],
        "Issues": user["issues"]["totalCount"],
    }


def rank_for(category: str, value: float) -> str | None:
    rank = None
    for name, needed in zip(RANKS, THRESHOLDS[category]):
        if value >= needed:
            rank = name
    return rank


def describe(category: str, value: float) -> str:
    if category == "Experience":
        return f"{value:g} years" if value >= 1 else f"{round(value * 12)} months"
    unit = {"Commits": "commits", "Repositories": "repos", "Languages": "languages", "Stars": "stars",
            "Followers": "followers", "Pull Requests": "PRs", "Issues": "issues"}[category]
    return f"{value} {unit}"


def trophies(data: dict) -> str:
    earned = [(c, v, rank_for(c, v)) for c, v in data.items() if rank_for(c, v)]
    earned.sort(key=lambda item: RANKS.index(item[2]), reverse=True)
    size, gap = 120, 10
    W = max(len(earned), 1) * (size + gap) - gap
    H = 150
    gradients, cups = [], []
    for i, (category, value, rank) in enumerate(earned):
        light, dark = RANK_COLOURS[rank[0]]
        gid = f"cup{i}"
        gradients.append(
            f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{light}"/><stop offset="1" stop-color="{dark}"/></linearGradient>'
        )
        x = i * (size + gap)
        cups.append(f"""
<g transform="translate({x} 0)">
  <rect x="0.5" y="0.5" width="{size - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
  <text x="{size / 2}" y="24" text-anchor="middle" font-size="12" font-weight="700" fill="{BLUE}">{esc(category)}</text>
  <path d="M38 38h44v18a22 22 0 0 1-44 0z" fill="url(#{gid})"/>
  <path d="M38 42h-8a10 10 0 0 0 10 14M82 42h8a10 10 0 0 1-10 14" fill="none" stroke="url(#{gid})" stroke-width="4"/>
  <rect x="55" y="77" width="10" height="12" fill="url(#{gid})"/>
  <rect x="44" y="89" width="32" height="7" rx="2" fill="url(#{gid})"/>
  <text x="{size / 2}" y="60" text-anchor="middle" font-size="{16 if len(rank) < 3 else 13}" font-weight="900" fill="{BG}">{rank}</text>
  <text x="{size / 2}" y="118" text-anchor="middle" font-size="12.5" font-weight="600" fill="{TEXT}">{esc(describe(category, value))}</text>
  <text x="{size / 2}" y="136" text-anchor="middle" font-size="11" fill="{MUTED}">Rank {rank}</text>
</g>""")
    return svg(W, H, "GitHub trophies earned from public activity", "".join(cups), defs="".join(gradients))


# ---------------------------------------------------------------- main


def write(name: str, content: str) -> None:
    path = ASSETS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    write("banner.svg", banner())
    write("terminal.svg", terminal())
    write("pipeline.svg", pipeline())
    write("quote.svg", quote())
    for project in PROFILE["projects"]:
        write(f"projects/{project['repo']}.svg", project_card(project))

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set: skipped trophies")
        return
    data = fetch_trophy_data(PROFILE["login"], token)
    print("trophy data:", data)
    write("trophies.svg", trophies(data))


if __name__ == "__main__":
    main()
