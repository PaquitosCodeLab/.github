"""SVG generator for cyberpunk-styled profile cards."""

from config import COLORS, LANG_COLORS


def _escape(text: str) -> str:
    """Escape XML special characters."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _lang_color(lang: str) -> str:
    return LANG_COLORS.get(lang, "#888888")


def _format_number(n: int) -> str:
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def generate_header_svg(org_name: str, generated_at: str) -> str:
    """Generate the main cyberpunk header banner."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200" viewBox="0 0 800 200">
  <defs>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{COLORS["neon_purple"]};stop-opacity:0.3"/>
      <stop offset="50%" style="stop-color:{COLORS["bg_dark"]};stop-opacity:1"/>
      <stop offset="100%" style="stop-color:{COLORS["neon_cyan"]};stop-opacity:0.3"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="glowStrong">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <rect width="800" height="200" fill="{COLORS["bg_dark"]}" rx="10"/>
  <rect width="800" height="200" fill="url(#headerGrad)" rx="10"/>

  <!-- Grid lines -->
  <g opacity="0.1" stroke="{COLORS["neon_cyan"]}">
    <line x1="0" y1="40" x2="800" y2="40" stroke-width="0.5"/>
    <line x1="0" y1="80" x2="800" y2="80" stroke-width="0.5"/>
    <line x1="0" y1="120" x2="800" y2="120" stroke-width="0.5"/>
    <line x1="0" y1="160" x2="800" y2="160" stroke-width="0.5"/>
    <line x1="100" y1="0" x2="100" y2="200" stroke-width="0.5"/>
    <line x1="200" y1="0" x2="200" y2="200" stroke-width="0.5"/>
    <line x1="300" y1="0" x2="300" y2="200" stroke-width="0.5"/>
    <line x1="400" y1="0" x2="400" y2="200" stroke-width="0.5"/>
    <line x1="500" y1="0" x2="500" y2="200" stroke-width="0.5"/>
    <line x1="600" y1="0" x2="600" y2="200" stroke-width="0.5"/>
    <line x1="700" y1="0" x2="700" y2="200" stroke-width="0.5"/>
  </g>

  <!-- Scan line effect -->
  <rect width="800" height="1" y="65" fill="{COLORS["neon_cyan"]}" opacity="0.15"/>
  <rect width="800" height="1" y="135" fill="{COLORS["neon_magenta"]}" opacity="0.15"/>

  <!-- Border glow -->
  <rect x="1" y="1" width="798" height="198" rx="10" fill="none"
        stroke="{COLORS["neon_cyan"]}" stroke-width="1.5" opacity="0.6" filter="url(#glow)"/>

  <!-- Corner accents -->
  <path d="M10,2 L2,2 L2,10" fill="none" stroke="{COLORS["neon_magenta"]}" stroke-width="2" opacity="0.8"/>
  <path d="M790,2 L798,2 L798,10" fill="none" stroke="{COLORS["neon_magenta"]}" stroke-width="2" opacity="0.8"/>
  <path d="M10,198 L2,198 L2,190" fill="none" stroke="{COLORS["neon_magenta"]}" stroke-width="2" opacity="0.8"/>
  <path d="M790,198 L798,198 L798,190" fill="none" stroke="{COLORS["neon_magenta"]}" stroke-width="2" opacity="0.8"/>

  <!-- Org name -->
  <text x="400" y="85" text-anchor="middle" font-family="\'Courier New\', monospace"
        font-size="36" font-weight="bold" fill="{COLORS["neon_cyan"]}" filter="url(#glowStrong)">
    {_escape(org_name)}
  </text>

  <!-- Tagline -->
  <text x="400" y="120" text-anchor="middle" font-family="\'Courier New\', monospace"
        font-size="14" fill="{COLORS["text_secondary"]}">
    // building the future, one commit at a time
  </text>

  <!-- Status bar -->
  <text x="20" y="175" font-family="\'Courier New\', monospace" font-size="10" fill="{COLORS["neon_green"]}">
    &#9679; SYSTEMS ONLINE
  </text>
  <text x="780" y="175" text-anchor="end" font-family="\'Courier New\', monospace"
        font-size="10" fill="{COLORS["text_secondary"]}">
    Last scan: {_escape(generated_at)}
  </text>
</svg>'''


def generate_group_card_svg(group_data: dict, width: int = 800) -> str:
    """Generate a cyberpunk-styled project group card."""
    name = group_data["name"]
    emoji = group_data.get("emoji", "")
    description = group_data.get("description", "")
    repos = group_data.get("repos", [])
    languages = group_data.get("languages", {})
    top_contributors = group_data.get("top_contributors", [])[:5]
    recent_activity = group_data.get("recent_activity", [])[:5]

    # Calculate dimensions
    repo_rows = len(repos)
    activity_rows = len(recent_activity)
    contrib_row = 1 if top_contributors else 0

    # Language bar
    total_bytes = sum(languages.values()) if languages else 1
    lang_sorted = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]

    card_height = 180 + (repo_rows * 32) + (activity_rows * 22) + (contrib_row * 60) + 80

    # Build repo list
    repo_items = ""
    y_pos = 140
    for repo in repos:
        lang = repo.get("language", "Unknown") or "Unknown"
        color = _lang_color(lang)
        updated = repo.get("updated_at", "")[:10]
        prs = repo.get("open_prs", 0)

        repo_items += f'''
    <g transform="translate(30, {y_pos})">
      <circle cx="0" cy="-4" r="4" fill="{color}"/>
      <text x="14" y="0" font-family="'Courier New', monospace" font-size="12" fill="{COLORS["text_primary"]}">
        {_escape(repo["name"])}
      </text>
      <text x="350" y="0" font-family="'Courier New', monospace" font-size="10" fill="{COLORS["text_secondary"]}">
        {_escape(lang)}
      </text>
      <text x="480" y="0" font-family="'Courier New', monospace" font-size="10" fill="{COLORS["neon_green"]}">
        PRs: {prs}
      </text>
      <text x="560" y="0" font-family="'Courier New', monospace" font-size="10" fill="{COLORS["text_secondary"]}">
        {_escape(updated)}
      </text>
    </g>'''
        y_pos += 32

    # Language bar
    lang_bar = ""
    lang_labels = ""
    x_offset = 30
    bar_width = width - 60
    label_y = y_pos + 45
    for lang, byte_count in lang_sorted:
        pct = byte_count / total_bytes
        seg_width = max(pct * bar_width, 2)
        color = _lang_color(lang)
        lang_bar += f'<rect x="{x_offset}" y="{y_pos + 20}" width="{seg_width}" height="8" fill="{color}" rx="2" opacity="0.85"/>'
        lang_labels += f'''
    <g transform="translate({x_offset}, {label_y})">
      <circle cx="0" cy="-3" r="4" fill="{color}"/>
      <text x="10" y="0" font-family="'Courier New', monospace" font-size="9" fill="{COLORS["text_secondary"]}">
        {_escape(lang)} ({pct:.0%})
      </text>
    </g>'''
        x_offset += seg_width

    y_pos += 70

    # Recent activity
    activity_section = ""
    if recent_activity:
        activity_section += f'''
    <text x="30" y="{y_pos}" font-family="'Courier New', monospace" font-size="13"
          font-weight="bold" fill="{COLORS["neon_magenta"]}">
      &#9656; RECENT ACTIVITY
    </text>'''
        y_pos += 22
        for act in recent_activity:
            activity_section += f'''
    <text x="40" y="{y_pos}" font-family="'Courier New', monospace" font-size="10" fill="{COLORS["text_secondary"]}">
      <tspan fill="{COLORS["neon_yellow"]}">{_escape(act["sha"])}</tspan>
      {_escape(act["message"][:50])}
      <tspan fill="{COLORS["text_secondary"]}">({_escape(act["repo"])})</tspan>
    </text>'''
            y_pos += 22

    y_pos += 15

    # Contributors
    contrib_section = ""
    if top_contributors:
        contrib_section += f'''
    <text x="30" y="{y_pos}" font-family="'Courier New', monospace" font-size="13"
          font-weight="bold" fill="{COLORS["neon_magenta"]}">
      &#9656; TOP CONTRIBUTORS
    </text>'''
        y_pos += 20
        cx = 55
        for contrib in top_contributors:
            contrib_section += f'''
    <g transform="translate({cx}, {y_pos})">
      <clipPath id="clip-{_escape(contrib["login"])}">
        <circle cx="0" cy="0" r="16"/>
      </clipPath>
      <circle cx="0" cy="0" r="17" fill="{COLORS["neon_cyan"]}" opacity="0.3"/>
      <image href="{_escape(contrib["avatar_url"])}&amp;s=32" x="-16" y="-16" width="32" height="32"
             clip-path="url(#clip-{_escape(contrib["login"])})"/>
      <text x="0" y="28" text-anchor="middle" font-family="'Courier New', monospace"
            font-size="8" fill="{COLORS["text_secondary"]}">
        {_escape(contrib["login"][:10])}
      </text>
      <text x="0" y="38" text-anchor="middle" font-family="'Courier New', monospace"
            font-size="8" fill="{COLORS["neon_green"]}">
        {_escape(str(contrib["contributions"]))} commits
      </text>
    </g>'''
            cx += 90
        y_pos += 55

    card_height = y_pos + 20

    # Stats bar
    stats = f'''
    <g transform="translate(30, 95)">
      <text font-family="'Courier New', monospace" font-size="11" fill="{COLORS["neon_cyan"]}">
        <tspan>&#9733; {group_data["total_stars"]}</tspan>
        <tspan dx="20">&#9741; {group_data["total_forks"]}</tspan>
        <tspan dx="20">&#9888; {group_data["total_open_issues"]} issues</tspan>
        <tspan dx="20">&#9658; {group_data["total_open_prs"]} PRs</tspan>
        <tspan dx="20">&#9776; {len(repos)} repos</tspan>
      </text>
    </g>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{card_height}" viewBox="0 0 {width} {card_height}">
  <defs>
    <linearGradient id="cardGrad-{name.replace(" ", "")}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{COLORS["neon_cyan"]};stop-opacity:0.05"/>
      <stop offset="100%" style="stop-color:{COLORS["neon_purple"]};stop-opacity:0.1"/>
    </linearGradient>
    <filter id="cardGlow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="{width}" height="{card_height}" fill="{COLORS["bg_card"]}" rx="8"/>
  <rect width="{width}" height="{card_height}" fill="url(#cardGrad-{name.replace(" ", "")})" rx="8"/>

  <!-- Border -->
  <rect x="1" y="1" width="{width - 2}" height="{card_height - 2}" rx="8" fill="none"
        stroke="{COLORS["neon_cyan"]}" stroke-width="1" opacity="0.4"/>

  <!-- Header -->
  <text x="30" y="40" font-family="'Courier New', monospace" font-size="22" font-weight="bold"
        fill="{COLORS["neon_cyan"]}" filter="url(#cardGlow)">
    {_escape(emoji)} {_escape(name)}
  </text>
  <text x="30" y="65" font-family="'Courier New', monospace" font-size="12"
        fill="{COLORS["text_secondary"]}">
    {_escape(description)}
  </text>

  <!-- Divider -->
  <line x1="30" y1="75" x2="{width - 30}" y2="75" stroke="{COLORS["neon_cyan"]}" stroke-width="0.5" opacity="0.3"/>

  {stats}

  <!-- Divider -->
  <line x1="30" y1="115" x2="{width - 30}" y2="115" stroke="{COLORS["neon_cyan"]}" stroke-width="0.5" opacity="0.3"/>

  <!-- Repo header -->
  <text x="30" y="135" font-family="'Courier New', monospace" font-size="10" fill="{COLORS["text_secondary"]}">
    REPOSITORY                               LANGUAGE        PRs        UPDATED
  </text>

  {repo_items}

  <!-- Language bar -->
  {lang_bar}
  {lang_labels}

  {activity_section}
  {contrib_section}
</svg>'''


def generate_footer_svg(generated_at: str) -> str:
    """Generate a small footer SVG."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="50" viewBox="0 0 800 50">
  <rect width="800" height="50" fill="{COLORS["bg_dark"]}" rx="6"/>
  <rect x="1" y="1" width="798" height="48" rx="6" fill="none"
        stroke="{COLORS["neon_cyan"]}" stroke-width="0.5" opacity="0.3"/>
  <text x="400" y="30" text-anchor="middle" font-family="'Courier New', monospace"
        font-size="10" fill="{COLORS["text_secondary"]}">
    Auto-generated by GitHub Actions &#8226; Last updated: {_escape(generated_at)} &#8226; Powered by PaquitosCodeLab
  </text>
</svg>'''
