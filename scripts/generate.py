#!/usr/bin/env python3
"""Generate org profile README with cyberpunk styling.

Uses shields.io for real-time badges (no images generated).
GitHub Action only regenerates contributor/activity tables.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from config import GROUPS, ORG_NAME, COLORS
from github_api import fetch_all_data

PROFILE_DIR = os.path.join(os.path.dirname(__file__), "..", "profile")

# Shields.io cyberpunk style params
BADGE_STYLE = "for-the-badge"
LABEL_COLOR = COLORS["bg_dark"].lstrip("#")
NEON_CYAN = COLORS["neon_cyan"].lstrip("#")
NEON_MAGENTA = COLORS["neon_magenta"].lstrip("#")
NEON_GREEN = COLORS["neon_green"].lstrip("#")
NEON_PURPLE = COLORS["neon_purple"].lstrip("#")
NEON_YELLOW = COLORS["neon_yellow"].lstrip("#")


def shields_badge(label: str, message: str, color: str, logo: str = "") -> str:
    """Generate a shields.io badge URL."""
    label_enc = label.replace("-", "--").replace(" ", "%20")
    message_enc = str(message).replace("-", "--").replace(" ", "%20")
    base = f"https://img.shields.io/badge/{label_enc}-{message_enc}-{color}"
    params = f"?style={BADGE_STYLE}&labelColor={LABEL_COLOR}"
    if logo:
        params += f"&logo={logo}&logoColor={NEON_CYAN}"
    return base + params


def shields_github_badge(repo: str, kind: str) -> str:
    """Generate a shields.io GitHub dynamic badge (real-time)."""
    full = f"{ORG_NAME}/{repo}"
    base = {
        "last-commit": f"https://img.shields.io/github/last-commit/{full}",
        "issues": f"https://img.shields.io/github/issues/{full}",
        "prs": f"https://img.shields.io/github/issues-pr/{full}",
        "language": f"https://img.shields.io/github/languages/top/{full}",
        "stars": f"https://img.shields.io/github/stars/{full}",
        "commit-activity": f"https://img.shields.io/github/commit-activity/m/{full}",
    }.get(kind, "")
    if not base:
        return ""
    return f"{base}?style=flat-square&labelColor={LABEL_COLOR}&color={NEON_CYAN}"


def make_repo_table(repos: list[dict]) -> str:
    """Generate markdown table for repos in a group."""
    rows = []
    for repo in repos:
        name = repo["name"]
        url = repo["url"]
        lang_badge = f'![lang]({shields_github_badge(name, "language")})'
        commit_badge = f'![commit]({shields_github_badge(name, "last-commit")})'
        issues_badge = f'![issues]({shields_github_badge(name, "issues")})'
        prs_badge = f'![prs]({shields_github_badge(name, "prs")})'

        rows.append(
            f"| [`{name}`]({url}) | {lang_badge} | {commit_badge} | {issues_badge} | {prs_badge} |"
        )

    header = "| Repository | Language | Last Commit | Issues | PRs |\n"
    header += "|:-----------|:---------|:------------|:-------|:----|\n"
    return header + "\n".join(rows)


def make_contributor_section(top_contributors: list[dict]) -> str:
    """Generate contributor avatars with links."""
    if not top_contributors:
        return "_No contributors data available_"
    parts = []
    for c in top_contributors[:8]:
        login = c["login"]
        avatar = c["avatar_url"]
        url = c["url"]
        commits = c["contributions"]
        parts.append(
            f'<a href="{url}" title="{login} — {commits} commits">'
            f'<img src="{avatar}&s=64" width="64" height="64" alt="{login}" '
            f'style="border-radius:50%;border:2px solid #{NEON_CYAN}"/></a>'
        )
    return " ".join(parts)


def make_activity_table(recent_activity: list[dict]) -> str:
    """Generate recent activity table."""
    if not recent_activity:
        return "_No recent activity_"
    rows = []
    for act in recent_activity[:8]:
        sha = act["sha"]
        msg = act["message"][:55]
        repo = act["repo"]
        date = act.get("date", "")[:10]
        author = act.get("author", "unknown")
        rows.append(f"| `{sha}` | {msg} | `{repo}` | {author} | {date} |")

    header = "| SHA | Message | Repo | Author | Date |\n"
    header += "|:----|:--------|:-----|:-------|:-----|\n"
    return header + "\n".join(rows)


def lang_bar_text(languages: dict) -> str:
    """Generate a text-based language breakdown."""
    total = sum(languages.values()) or 1
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]
    parts = []
    for lang, bytes_count in sorted_langs:
        pct = (bytes_count / total) * 100
        bar_len = max(1, int(pct / 5))
        bar = "█" * bar_len
        parts.append(f"`{lang}` {bar} {pct:.1f}%")
    return " &nbsp; ".join(parts)


def build_readme(data: dict) -> str:
    """Build the full profile README."""
    generated = data["generated_at"]
    lines = []

    # ── HEADER ──
    lines.append(f"""
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

![status](https://img.shields.io/badge/SYSTEMS-ONLINE-{NEON_GREEN}?style=for-the-badge&labelColor={LABEL_COLOR})
![repos](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Forgs%2F{ORG_NAME}&query=%24.public_repos&label=PUBLIC%20REPOS&style=for-the-badge&labelColor={LABEL_COLOR}&color={NEON_CYAN})

</div>

<br>
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

        # Group header
        lines.append(f"""
<div align="center">

```
░▒▓█ {group_name.upper()} █▓▒░
```

_{description}_

![repos](https://img.shields.io/badge/REPOS-{total_repos}-{NEON_CYAN}?style=flat-square&labelColor={LABEL_COLOR})
![issues](https://img.shields.io/badge/OPEN%20ISSUES-{total_issues}-{NEON_YELLOW}?style=flat-square&labelColor={LABEL_COLOR})
![prs](https://img.shields.io/badge/OPEN%20PRs-{total_prs}-{NEON_MAGENTA}?style=flat-square&labelColor={LABEL_COLOR})

</div>

""")

        # Repo table
        lines.append(make_repo_table(repos))
        lines.append("")

        # Language breakdown
        if languages:
            lines.append(f"\n<details><summary><b>📊 Language Breakdown</b></summary>\n")
            lines.append(f"<br>\n\n{lang_bar_text(languages)}\n")
            lines.append(f"</details>\n")

        # Recent activity
        if recent:
            lines.append(f"<details><summary><b>⚡ Recent Activity</b></summary>\n")
            lines.append(f"<br>\n\n{make_activity_table(recent)}\n")
            lines.append(f"</details>\n")

        # Contributors
        if top_contribs:
            lines.append(f"<details open><summary><b>👥 Top Contributors</b></summary>\n")
            lines.append(f"<br>\n<div align=\"center\">\n\n{make_contributor_section(top_contribs)}\n\n</div>\n")
            lines.append(f"</details>\n")

        lines.append("\n---\n")

    # ── FOOTER ──
    lines.append(f"""
<div align="center">

```
╔════════════════════════════════════════════════════╗
║  Auto-generated • Last scan: {generated:<20s} ║
║  Powered by GitHub Actions + shields.io            ║
╚════════════════════════════════════════════════════╝
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
