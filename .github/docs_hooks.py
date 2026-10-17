"""Keep source links useful on GitHub and in the published guide."""
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPO = "https://github.com/bobfischer/beyond-chat-todo/blob/main/"


def on_page_markdown(markdown, page, config, files):
    source = DOCS / page.file.src_uri

    def rewrite(match):
        href = match.group(1)
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
            return match.group(0)
        target = (source.parent / parsed.path).resolve()
        if target.is_relative_to(DOCS):
            return match.group(0)
        if not target.is_relative_to(ROOT) or not target.exists():
            raise ValueError(f"Invalid repository link in {source}: {href}")
        url = REPO + target.relative_to(ROOT).as_posix()
        if parsed.fragment:
            url += "#" + parsed.fragment
        return "](" + url + ")"

    return re.sub(r"\]\(([^)]+)\)", rewrite, markdown)
