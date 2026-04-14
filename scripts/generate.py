#!/usr/bin/env python3
"""Main generator — fetches data, generates SVGs, assembles README."""

import os
import sys

# Ensure scripts dir is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import GROUPS, ORG_NAME
from github_api import fetch_all_data
from svg_generator import generate_header_svg, generate_group_card_svg, generate_footer_svg


ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
PROFILE_DIR = os.path.join(os.path.dirname(__file__), "..", "profile")


def write_svg(filename: str, content: str) -> None:
    """Write SVG file to assets directory."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    path = os.path.join(ASSETS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Written: {path}")


def build_readme(data: dict) -> str:
    """Build the profile README markdown."""
    lines = []

    # Header
    lines.append('<p align="center">')
    lines.append('  <img src="../assets/header.svg" alt="PaquitosCodeLab" width="800"/>')
    lines.append("</p>")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Group cards
    for group_name, group_data in data["groups"].items():
        safe_name = group_name.replace(" ", "-").replace("(", "").replace(")", "").lower()
        lines.append(f'<p align="center">')
        lines.append(f'  <img src="../assets/group-{safe_name}.svg" alt="{group_name}" width="800"/>')
        lines.append(f"</p>")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Footer
    lines.append('<p align="center">')
    lines.append('  <img src="../assets/footer.svg" alt="Footer" width="800"/>')
    lines.append("</p>")

    return "\n".join(lines)


def main() -> None:
    print("=" * 60)
    print(f"Generating profile for {ORG_NAME}")
    print("=" * 60)

    # Fetch all data
    data = fetch_all_data()

    # Generate header SVG
    print("\nGenerating SVGs...")
    write_svg("header.svg", generate_header_svg(ORG_NAME, data["generated_at"]))

    # Generate group cards
    for group_name, group_data in data["groups"].items():
        safe_name = group_name.replace(" ", "-").replace("(", "").replace(")", "").lower()
        write_svg(
            f"group-{safe_name}.svg",
            generate_group_card_svg(group_data),
        )

    # Generate footer
    write_svg("footer.svg", generate_footer_svg(data["generated_at"]))

    # Build and write README
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
