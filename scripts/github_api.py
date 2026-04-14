"""GitHub API client for fetching org data."""

import os
import json
import subprocess
from datetime import datetime, timezone
from typing import Any

from config import ORG_NAME, GROUPS


def gh_api(endpoint: str) -> Any:
    """Call GitHub API via gh CLI."""
    result = subprocess.run(
        ["gh", "api", endpoint, "--paginate"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Warning: gh api {endpoint} failed: {result.stderr}")
        return []
    return json.loads(result.stdout)


def gh_graphql(query: str, variables: dict | None = None) -> Any:
    """Call GitHub GraphQL API via gh CLI."""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    if variables:
        for key, value in variables.items():
            cmd.extend(["-f", f"{key}={value}"])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Warning: GraphQL query failed: {result.stderr}")
        return {}
    return json.loads(result.stdout)


def fetch_repo_info(repo_name: str) -> dict:
    """Fetch detailed repo information."""
    data = gh_api(f"/repos/{ORG_NAME}/{repo_name}")
    if not data:
        return {}
    return {
        "name": data.get("name", repo_name),
        "description": data.get("description", ""),
        "language": data.get("language", "Unknown"),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "updated_at": data.get("pushed_at", data.get("updated_at", "")),
        "url": data.get("html_url", f"https://github.com/{ORG_NAME}/{repo_name}"),
        "default_branch": data.get("default_branch", "main"),
    }


def fetch_repo_languages(repo_name: str) -> dict[str, int]:
    """Fetch language breakdown for a repo."""
    return gh_api(f"/repos/{ORG_NAME}/{repo_name}/languages") or {}


def fetch_recent_commits(repo_name: str, limit: int = 5) -> list[dict]:
    """Fetch recent commits for a repo."""
    commits = gh_api(
        f"/repos/{ORG_NAME}/{repo_name}/commits?per_page={limit}"
    )
    if not isinstance(commits, list):
        return []
    return [
        {
            "sha": c["sha"][:7],
            "message": c["commit"]["message"].split("\n")[0][:60],
            "author": c["commit"]["author"]["name"],
            "date": c["commit"]["author"]["date"],
        }
        for c in commits[:limit]
    ]


def fetch_contributors(repo_name: str) -> list[dict]:
    """Fetch contributors for a repo."""
    contribs = gh_api(f"/repos/{ORG_NAME}/{repo_name}/contributors?per_page=100")
    if not isinstance(contribs, list):
        return []
    return [
        {
            "login": c["login"],
            "avatar_url": c["avatar_url"],
            "contributions": c["contributions"],
            "url": c["html_url"],
        }
        for c in contribs
        if c.get("type") == "User"
    ]


def fetch_open_prs(repo_name: str) -> int:
    """Fetch open PR count for a repo."""
    prs = gh_api(f"/repos/{ORG_NAME}/{repo_name}/pulls?state=open&per_page=1")
    if isinstance(prs, list):
        # Use the link header trick — just count what we get
        return len(gh_api(f"/repos/{ORG_NAME}/{repo_name}/pulls?state=open&per_page=100"))
    return 0


def fetch_group_data(group_name: str, repos: list[str]) -> dict:
    """Fetch all data for a project group."""
    group_data = {
        "name": group_name,
        "repos": [],
        "total_stars": 0,
        "total_forks": 0,
        "total_open_issues": 0,
        "total_open_prs": 0,
        "languages": {},
        "contributors": {},
        "recent_activity": [],
    }

    for repo_name in repos:
        print(f"  Fetching {repo_name}...")
        info = fetch_repo_info(repo_name)
        if not info:
            continue

        languages = fetch_repo_languages(repo_name)
        commits = fetch_recent_commits(repo_name, limit=3)
        contributors = fetch_contributors(repo_name)
        open_prs = fetch_open_prs(repo_name)

        info["languages"] = languages
        info["recent_commits"] = commits
        info["contributors"] = contributors
        info["open_prs"] = open_prs
        group_data["repos"].append(info)

        # Aggregate
        group_data["total_stars"] += info["stars"]
        group_data["total_forks"] += info["forks"]
        group_data["total_open_issues"] += info["open_issues"]
        group_data["total_open_prs"] += open_prs

        for lang, bytes_count in languages.items():
            group_data["languages"][lang] = (
                group_data["languages"].get(lang, 0) + bytes_count
            )

        for contrib in contributors:
            login = contrib["login"]
            if login in group_data["contributors"]:
                group_data["contributors"][login]["contributions"] += contrib[
                    "contributions"
                ]
            else:
                group_data["contributors"][login] = {**contrib}

        for commit in commits:
            group_data["recent_activity"].append(
                {**commit, "repo": repo_name}
            )

    # Sort recent activity by date
    group_data["recent_activity"].sort(
        key=lambda x: x.get("date", ""), reverse=True
    )
    group_data["recent_activity"] = group_data["recent_activity"][:5]

    # Sort contributors by total contributions
    group_data["top_contributors"] = sorted(
        group_data["contributors"].values(),
        key=lambda x: x["contributions"],
        reverse=True,
    )[:10]

    return group_data


def fetch_all_data() -> dict:
    """Fetch data for all configured groups."""
    all_data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "org": ORG_NAME,
        "groups": {},
    }

    for group_name, group_config in GROUPS.items():
        print(f"Fetching group: {group_name}")
        group_data = fetch_group_data(group_name, group_config["repos"])
        group_data["emoji"] = group_config["emoji"]
        group_data["description"] = group_config["description"]
        all_data["groups"][group_name] = group_data

    return all_data
