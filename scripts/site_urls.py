"""The guide's public addresses, from mkdocs.yml unless DOCS_SITE_URL / DOCS_REPO_URL override them."""
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[1]


def _setting(key):
    match = re.search(rf"^{key}:\s*(\S+)\s*$", (ROOT / "mkdocs.yml").read_text(), re.M)
    if not match:
        raise ValueError(f"{key} is not set in mkdocs.yml")
    return match.group(1)


def site_url():
    """Where the guide is published, with a trailing slash (ends in /guide/)."""
    return os.environ.get("DOCS_SITE_URL") or _setting("site_url")


def site_root():
    """Where the whole site is published: the guide's address without /guide/."""
    url = site_url().rstrip("/")
    return (url[:-len("/guide")] if url.endswith("/guide") else url) + "/"


def repo_url():
    return (os.environ.get("DOCS_REPO_URL") or _setting("repo_url")).rstrip("/")


def source_url():
    """Base for links to files in the repository."""
    return repo_url() + "/blob/main/"


if __name__ == "__main__":
    import sys
    print({"site": site_url, "root": site_root, "repo": repo_url}[sys.argv[1]]())
