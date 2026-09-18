"""
Fetches all public repositories for the configured GitHub user
and updates the README.md between the <!--START_SECTION:repos--> and
<!--END_SECTION:repos--> markers with a beautifully formatted list.

Runs as part of the "Update README with Repositories" GitHub Actions workflow.
"""

import os
import requests
from datetime import datetime

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
        r for r in repos
        if not r["fork"] and r["name"] != GITHUB_USERNAME
    ]

    return repos


# Colors for language badges (background color hex)
LANG_COLORS = {
    "Python": "3776AB",
    "JavaScript": "F7DF1E",
    "TypeScript": "3178C6",
    "HTML": "E34F26",
    "CSS": "1572B6",
    "Java": "ED8B00",
    "C": "A8B9CC",
    "C++": "00599C",
    "C#": "239120",
    "Jupyter Notebook": "F37626",
    "Shell": "4EAA25",
    "R": "276DC3",
    "Dart": "0175C2",
    "Kotlin": "7F52FF",
    "Go": "00ADD8",
    "Rust": "DEA584",
    "Ruby": "CC342D",
    "PHP": "777BB4",
    "Swift": "F05138",
    "Vue": "4FC08D",
    "SCSS": "CC6699",
}

# Emoji for language
LANG_EMOJI = {
    "Python": "🐍",
    "JavaScript": "⚡",
    "TypeScript": "💎",
    "HTML": "🌐",
    "CSS": "🎨",
    "Java": "☕",
    "C": "⚙️",
    "C++": "⚙️",
    "Jupyter Notebook": "📓",
    "Shell": "🐚",
    "R": "📊",
    "Dart": "🎯",
    "Kotlin": "🟣",
    "Go": "🔵",
    "Rust": "🦀",
    "Ruby": "💎",
    "PHP": "🐘",
}


def language_badge(lang):
    """Return a styled badge for a language."""
    if not lang:
        return ""
    color = LANG_COLORS.get(lang, "555555")
    safe_lang = lang.replace(" ", "%20").replace("#", "%23")
    logo = lang.lower().replace(" ", "").replace("+", "%2B").replace("#", "sharp")
    return (
        f'<img src="https://img.shields.io/badge/{safe_lang}-{color}'
        f'?style=flat-square&logo={logo}&logoColor=white" height="18"/>'
    )


def format_stars(count):
    """Format star count as a badge if > 0."""
    if count == 0:
        return ""
    return f' <img src="https://img.shields.io/badge/⭐_{count}-FFD700?style=flat-square&labelColor=0D1117" height="18"/>'


def relative_time(iso_date):
    """Convert ISO date string to a human-readable relative time."""
    updated = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.utcnow()
    diff = now - updated

    if diff.days == 0:
        return "today"
    elif diff.days == 1:
        return "yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif diff.days < 365:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"


def build_repo_section(repos):
    """Build a visually rich markdown section for the repo list."""
    if not repos:
        return "\n\n<p align='center'><i>No public repositories found yet — stay tuned! 🚀</i></p>\n\n"

    lines = []
    lines.append("")
    lines.append("")
    lines.append("<div align='center'>")
    lines.append("")
    lines.append(f"**📦 {len(repos)} Public Repositories** · Sorted by most recently updated")
    lines.append("")
    lines.append("</div>")
    lines.append("")

    # Build table
    lines.append("<table>")
    lines.append("<thead>")
    lines.append("<tr>")
    lines.append('<th align="center">🔢</th>')
    lines.append('<th align="left">Repository</th>')
    lines.append('<th align="center">Language</th>')
    lines.append('<th align="left">Description</th>')
    lines.append('<th align="center">Updated</th>')
    lines.append("</tr>")
    lines.append("</thead>")
    lines.append("<tbody>")

    for idx, repo in enumerate(repos, 1):
        name = repo["name"]
        url = repo["html_url"]
        desc = repo["description"] or "<i>No description</i>"
        # Escape HTML entities in description
        desc = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # But allow our italic tag
        if desc == "&lt;i&gt;No description&lt;/i&gt;":
            desc = "<i>No description</i>"
        lang = repo["language"] or ""
        badge = language_badge(lang) if lang else "—"
        stars = format_stars(repo["stargazers_count"])
        emoji = LANG_EMOJI.get(lang, "📁")
        updated = relative_time(repo["updated_at"])

        lines.append("<tr>")
        lines.append(f'<td align="center"><b>{idx}</b></td>')
        lines.append(
            f'<td align="left">{emoji} <a href="{url}"><b>{name}</b></a>{stars}</td>'
        )
        lines.append(f'<td align="center">{badge}</td>')
        lines.append(f'<td align="left">{desc}</td>')
        lines.append(f'<td align="center"><sub>{updated}</sub></td>')
        lines.append("</tr>")

    lines.append("</tbody>")
    lines.append("</table>")
    lines.append("")
    lines.append(f"<p align='right'><sub>🕐 Last updated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}</sub></p>")
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

    count = section_content.count("<b>") - 1  # subtract header bold
    print(f"✅ README updated with {max(count, 0)} repositories.")


def main():
    repos = fetch_repos()
    section = build_repo_section(repos)
    update_readme(section)


if __name__ == "__main__":
    main()
