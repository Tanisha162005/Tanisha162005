"""
Fetches all public repositories for the configured GitHub user
and updates the README.md between the <!--START_SECTION:repos--> and
<!--END_SECTION:repos--> markers with a formatted table.

Runs as part of the "Update README with Repositories" GitHub Actions workflow.
"""

import os
import requests

GITHUB_USERNAME = "Tanisha162005"
README_PATH = "README.md"
START_MARKER = "<!--START_SECTION:repos-->"
END_MARKER = "<!--END_SECTION:repos-->"


def fetch_repos():
    """Fetch all public, non-fork repositories for the configured user."""
    repos = []
    page = 1
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    while True:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
        params = {
            "per_page": 100,
            "page": page,
            "type": "owner",
            "sort": "updated",
            "direction": "desc",
        }
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1

    # Filter out forks and the profile repo itself
    repos = [
        r
        for r in repos
        if not r["fork"] and r["name"] != GITHUB_USERNAME
    ]

    return repos


def language_badge(lang):
    """Return a small inline badge for a language, or empty string."""
    if not lang:
        return ""
    colors = {
        "Python": "3776AB",
        "JavaScript": "F7DF1E",
        "TypeScript": "3178C6",
        "HTML": "E34F26",
        "CSS": "1572B6",
        "Java": "ED8B00",
        "C": "A8B9CC",
        "C++": "00599C",
        "Jupyter Notebook": "F37626",
        "Shell": "4EAA25",
        "R": "276DC3",
        "Dart": "0175C2",
        "Kotlin": "7F52FF",
        "Go": "00ADD8",
        "Rust": "000000",
        "Ruby": "CC342D",
        "PHP": "777BB4",
        "Swift": "F05138",
    }
    color = colors.get(lang, "555555")
    logo = lang.lower().replace(" ", "").replace("+", "%2B")
    return (
        f'<img src="https://img.shields.io/badge/{lang.replace(" ", "%20")}-{color}'
        f'?style=flat-square&logo={logo}&logoColor=white" height="20"/>'
    )


def star_count(stars):
    """Format star count with emoji."""
    if stars == 0:
        return ""
    return f" ⭐ {stars}"


def build_repo_section(repos):
    """Build the markdown table that goes between the markers."""
    if not repos:
        return "\n| — | *No public repositories found* | — |\n"

    lines = []
    lines.append("")
    lines.append("| # | Repository | Language | Description |")
    lines.append("|:-:|:-----------|:--------:|:------------|")

    for idx, repo in enumerate(repos, 1):
        name = repo["name"]
        url = repo["html_url"]
        desc = (repo["description"] or "—").replace("|", "∣")  # escape pipes
        lang = repo["language"] or ""
        badge = language_badge(lang) if lang else "—"
        stars = star_count(repo["stargazers_count"])

        lines.append(
            f"| {idx} | [**{name}**]({url}){stars} | {badge} | {desc} |"
        )

    lines.append("")
    return "\n".join(lines)


def update_readme(section_content):
    """Replace content between the markers in README.md."""
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)

    new_readme = readme[:start] + section_content + readme[end:]

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme)

    print(f"✅ README updated with {section_content.count('[**')} repositories.")


def main():
    repos = fetch_repos()
    section = build_repo_section(repos)
    update_readme(section)


if __name__ == "__main__":
    main()
