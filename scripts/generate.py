#!/usr/bin/env python3
"""Generate org profile README with cyberpunk styling.

All data fetched via GitHub API (PAT). No external badge services.
Generates pure markdown + HTML — zero image files.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from config import GROUPS, ORG_NAME
from github_api import fetch_all_data

PROFILE_DIR = os.path.join(os.path.dirname(__file__), "..", "profile")


def _badge(label: str, value: str | int, color: str) -> str:
    """Inline HTML badge — no external services."""
    return (
        f'<code style="background:#{color}20;color:#{color};padding:2px 8px;'
        f'border:1px solid #{color};border-radius:4px">'
        f'{label}: {value}</code>'
    )


def _pill(text: str, color: str) -> str:
    """Small colored pill."""
    return (
        f'<img src="https://img.shields.io/static/v1?label=&message={text}'
        f'&color={color}&style=flat-square"/>'
    )


def lang_icon(lang: str) -> str:
    """Return emoji for language."""
    icons = {
        "TypeScript": "🔷",
        "C#": "🟣",
        "Astro": "🚀",
        "Go": "🔵",
        "Python": "🐍",
        "JavaScript": "🟡",
        "HTML": "🟠",
        "CSS": "🎨",
        "Shell": "🐚",
        "Dockerfile": "🐳",
    }
    return icons.get(lang, "⚪")


def make_repo_table(repos: list[dict]) -> str:
    """Generate markdown table for repos, sorted by updated desc."""
    sorted_repos = sorted(repos, key=lambda r: r.get("updated_at", ""), reverse=True)
    rows = []
    for repo in sorted_repos:
        name = repo["name"]
        url = repo["url"]
        lang = repo.get("language") or "—"
        icon = lang_icon(lang)
        updated = repo.get("updated_at", "")[:10]
        issues = repo.get("open_issues", 0)
        prs = repo.get("open_prs", 0)
        commits = repo.get("recent_commits", [])
        last_msg = commits[0]["message"][:40] if commits else "—"

        issues_display = f"🟡 {issues}" if issues > 0 else "✅ 0"
        prs_display = f"🟣 {prs}" if prs > 0 else "✅ 0"

        rows.append(
            f"| {icon} [`{name}`]({url}) | `{lang}` | {issues_display} | {prs_display} | `{updated}` | _{last_msg}_ |"
        )

    header = "| Repository | Language | Issues | PRs | Updated | Last Commit |\n"
    header += "|:-----------|:---------|:-------|:----|:--------|:------------|\n"
    return header + "\n".join(rows)


def make_contributor_section(top_contributors: list[dict]) -> str:
    """Generate contributor avatars."""
    if not top_contributors:
        return "_No contributor data_"
    parts = []
    for c in top_contributors[:8]:
        login = c["login"]
        avatar = c["avatar_url"]
        url = c["url"]
        commits = c["contributions"]
        parts.append(
            f'<a href="{url}" title="{login}">'
            f'<img src="{avatar}&s=64" width="48" height="48" alt="{login}"/>'
            f'</a>'
            f' <sub><b>{login}</b></sub>'
            f' <sup>({commits})</sup>'
        )
    return " &nbsp;&nbsp; ".join(parts)


def make_activity_table(recent_activity: list[dict]) -> str:
    """Generate recent activity."""
    if not recent_activity:
        return "_No recent activity_"
    rows = []
    for act in recent_activity[:6]:
        sha = act["sha"]
        msg = act["message"][:50]
        repo = act["repo"]
        date = act.get("date", "")[:10]
        author = act.get("author", "unknown")
        rows.append(f"| `{sha}` | {msg} | **{repo}** | {author} | {date} |")

    header = "| SHA | Message | Repo | Author | Date |\n"
    header += "|:----|:--------|:-----|:-------|:-----|\n"
    return header + "\n".join(rows)


def lang_breakdown(languages: dict) -> str:
    """Text-based language bar."""
    total = sum(languages.values()) or 1
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]
    parts = []
    for lang, byte_count in sorted_langs:
        pct = (byte_count / total) * 100
        bar_len = max(1, int(pct / 4))
        bar = "█" * bar_len + "░"
        icon = lang_icon(lang)
        parts.append(f"{icon} **{lang}** `{bar}` {pct:.1f}%")
    return "<br>".join(parts)


def build_readme(data: dict) -> str:
    """Build the full profile README."""
    generated = data["generated_at"]
    lines = []

    # ── HEADER ──
    lines.append(f"""\
<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ██████╗  █████╗  ██████╗ ██╗   ██╗██╗████████╗ ██████╗     ║
║     ██╔══██╗██╔══██╗██╔═══██╗██║   ██║██║╚══██╔══╝██╔═══██╗    ║
║     ██████╔╝███████║██║   ██║██║   ██║██║   ██║   ██║   ██║    ║
║     ██╔═══╝ ██╔══██║██║▄▄ ██║██║   ██║██║   ██║   ██║   ██║    ║
║     ██║     ██║  ██║╚██████╔╝╚██████╔╝██║   ██║   ╚██████╔╝    ║
║     ╚═╝     ╚═╝  ╚═╝ ╚══▀▀═╝  ╚═════╝ ╚═╝   ╚═╝    ╚═════╝     ║
║                    C O D E   L A B                               ║
║                                                                  ║
║          // building the future, one commit at a time            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

`⚡ SYSTEMS ONLINE` &nbsp; `📡 LAST SCAN: {generated}` &nbsp; `🔒 PRIVATE REPOS`

</div>

---
""")

    # ── GROUPS ──
    for group_name, group_data in data["groups"].items():
        emoji = group_data.get("emoji", "")
        description = group_data.get("description", "")
        repos = group_data.get("repos", [])
        languages = group_data.get("languages", {})
        top_contribs = group_data.get("top_contributors", [])
        recent = group_data.get("recent_activity", [])

        total_repos = len(repos)
        total_issues = group_data["total_open_issues"]
        total_prs = group_data["total_open_prs"]

        lines.append(f"""\

<div align="center">

```
░▒▓█ {emoji} {group_name.upper()} █▓▒░
```

_{description}_

`📦 {total_repos} repos` &nbsp; `⚠️ {total_issues} issues` &nbsp; `🔀 {total_prs} PRs`

</div>

""")

        # Repo table
        lines.append(make_repo_table(repos))
        lines.append("")

        # Language breakdown
        if languages:
            lines.append("<details><summary><b>📊 Language Breakdown</b></summary>\n<br>\n")
            lines.append(lang_breakdown(languages))
            lines.append("\n</details>\n")

        # Recent activity
        if recent:
            lines.append("<details><summary><b>⚡ Recent Activity</b></summary>\n<br>\n")
            lines.append(make_activity_table(recent))
            lines.append("\n</details>\n")

        # Contributors
        if top_contribs:
            lines.append("<details open><summary><b>👥 Top Contributors</b></summary>\n<br>\n<div align=\"center\">\n")
            lines.append(make_contributor_section(top_contribs))
            lines.append("\n</div>\n</details>\n")

        lines.append("\n---\n")

    # ── FOOTER ──
    lines.append(f"""\

<div align="center">

```
╔════════════════════════════════════════════════════════╗
║  🤖 Auto-generated by GitHub Actions                   ║
║  📡 Last scan: {generated:<39s} ║
║  🔄 Updates every 6 hours                               ║
╚════════════════════════════════════════════════════════╝
```

</div>
""")

    return "\n".join(lines)


def main() -> None:
    print("=" * 60)
    print(f"Generating profile for {ORG_NAME}")
    print("=" * 60)

    data = fetch_all_data()

    print("\nBuilding README...")
    readme_content = build_readme(data)
    os.makedirs(PROFILE_DIR, exist_ok=True)
    readme_path = os.path.join(PROFILE_DIR, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"  Written: {readme_path}")
    print("\nDone!")


if __name__ == "__main__":
    main()
