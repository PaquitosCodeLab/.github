"""Configuration for the org profile generator."""

ORG_NAME = "PaquitosCodeLab"

# Project groups — each group gets its own card in the README
GROUPS = {
    "MCH (Medical Center Hub)": {
        "emoji": "🏥",
        "description": "Microservices-based medical center platform",
        "repos": [
            "medical-center",
            "medical-center-design",
            "mch.apigateway.service",
            "mch.user.service",
            "mch.notification.service",
            "mch.people.service",
            "mch.audit.service",
            "mch.sharedkernel",
            "mch.monitoring.infrastructure",
        ],
    },
    "Latitud Web": {
        "emoji": "🌐",
        "description": "Web products — landings, rental management, finance tools",
        "repos": [
            "latitudweb-landing",
            "rental-management",
            "rental-management-landing",
            "project-finance",
        ],
    },
}

# Cyberpunk color palette
COLORS = {
    "bg_dark": "#0a0a0f",
    "bg_card": "#12121a",
    "bg_card_alt": "#1a1a2e",
    "neon_cyan": "#00f0ff",
    "neon_magenta": "#ff00aa",
    "neon_purple": "#b400ff",
    "neon_green": "#39ff14",
    "neon_yellow": "#ffe600",
    "text_primary": "#e0e0ff",
    "text_secondary": "#8888aa",
    "border_glow": "#00f0ff",
    "grid_line": "#1a1a3a",
}

# Language color mapping
LANG_COLORS = {
    "TypeScript": "#3178c6",
    "C#": "#178600",
    "Astro": "#ff5a03",
    "Go": "#00ADD8",
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "Dockerfile": "#384d54",
}
