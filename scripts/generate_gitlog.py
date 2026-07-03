#!/usr/bin/env python3
"""Generate terminal-style `git log --oneline` SVG cards from recent public activity."""

import json
import os
import urllib.request
from xml.sax.saxutils import escape

USER = "son-daehyeon"
LIMIT = 6
OUT = {
    "dark": "assets/gitlog-dark.svg",
    "light": "assets/gitlog-light.svg",
}

PALETTES = {
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "bar": "#161b22",
        "title": "#8b949e", "prompt": "#7ee787", "tilde": "#79c0ff",
        "cmd": "#e6edf3", "sha": "#ffbd2e", "repo": "#79c0ff",
        "msg": "#e6edf3", "cursor": "#e6edf3",
    },
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "bar": "#f6f8fa",
        "title": "#57606a", "prompt": "#1a7f37", "tilde": "#0969da",
        "cmd": "#1f2328", "sha": "#9a6700", "repo": "#0969da",
        "msg": "#1f2328", "cursor": "#24292f",
    },
}


def collect_commits():
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        "https://api.github.com/search/commits"
        f"?q=author:{USER}&sort=author-date&order=desc&per_page=30",
        headers=headers,
    )
    with urllib.request.urlopen(req) as res:
        items = json.load(res).get("items", [])

    commits = []
    for item in items:
        if item["repository"].get("private"):
            continue
        message = item["commit"]["message"].splitlines()[0]
        if message.startswith("Merge "):
            continue
        repo = item["repository"]["name"]
        commits.append((
            item["sha"][:7],
            repo[:28],
            message[:50] + ("…" if len(message) > 50 else ""),
        ))
        if len(commits) >= LIMIT:
            break
    return commits


def render(commits, palette):
    p = palette
    lines = []
    y = 128
    for sha, repo, message in commits:
        lines.append(
            f'  <text x="36" y="{y}" font-size="15">'
            f'<tspan fill="{p["sha"]}">{sha}</tspan>'
            f'<tspan fill="{p["repo"]}" dx="12">{escape(repo)}</tspan>'
            f'<tspan fill="{p["msg"]}" dx="12">{escape(message)}</tspan>'
            f"</text>"
        )
        y += 26
    if not commits:
        lines.append(
            f'  <text x="36" y="128" font-size="15" fill="{p["msg"]}">no recent public commits</text>'
        )
        y = 154

    prompt_y = y + 20
    height = prompt_y + 32

    return f"""<svg width="880" height="{height}" viewBox="0 0 880 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    text {{ font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Menlo, Consolas, monospace; white-space: pre; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
  </style>
  <rect x="1" y="1" width="878" height="{height - 2}" rx="16" fill="{p["bg"]}" stroke="{p["border"]}" stroke-width="2"/>
  <rect x="2" y="2" width="876" height="48" rx="15" fill="{p["bar"]}"/>
  <rect x="2" y="36" width="876" height="14" fill="{p["bar"]}"/>
  <line x1="2" y1="50" x2="878" y2="50" stroke="{p["border"]}" stroke-width="1"/>
  <circle cx="30" cy="26" r="7" fill="#ff5f56"/>
  <circle cx="54" cy="26" r="7" fill="#ffbd2e"/>
  <circle cx="78" cy="26" r="7" fill="#27c93f"/>
  <text x="440" y="31" fill="{p["title"]}" font-size="13" text-anchor="middle">daehyeon@zighang: ~/activity</text>
  <text x="36" y="94" font-size="16">
    <tspan fill="{p["prompt"]}" font-weight="700">&#10148;</tspan>
    <tspan fill="{p["tilde"]}" dx="6">~</tspan>
    <tspan fill="{p["cmd"]}" dx="10">git log --oneline -{LIMIT}</tspan>
  </text>
{chr(10).join(lines)}
  <text x="36" y="{prompt_y}" font-size="16">
    <tspan fill="{p["prompt"]}" font-weight="700">&#10148;</tspan>
    <tspan fill="{p["tilde"]}" dx="6">~</tspan>
  </text>
  <rect class="cursor" x="86" y="{prompt_y - 14}" width="10" height="18" fill="{p["cursor"]}"/>
</svg>
"""


def main():
    commits = collect_commits()
    for mode, path in OUT.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(commits, PALETTES[mode]))
        print(f"wrote {path} ({len(commits)} commits)")


if __name__ == "__main__":
    main()
