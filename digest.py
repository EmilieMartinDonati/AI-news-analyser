from datetime import date
import os


def write_digest(groups):
    digest = build_digest(groups)
    os.makedirs("digests", exist_ok=True)
    path = f"digests/{date.today().isoformat()}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(digest)


def build_digest(groups):
    lines = [f"# AI digest – {date.today().isoformat()}", ""]

    for category, articles in groups.items():
        lines.append(f"## {category.capitalize()}")
        lines.append("")
        for a in articles:
            lines.append(f"- [{a['title']}]({a['source']})")
            lines.append(f"  {a['summary']}")
        lines.append("")            # blank line between sections

    return "\n".join(lines)
