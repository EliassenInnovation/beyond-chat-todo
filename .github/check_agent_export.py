"""Validate local destinations in the portable Markdown export against build/source files.

Usage: python .github/check_agent_export.py SITE_DIR SITE_URL REPO_URL
External sources are outside this check; site and repository URLs are mapped to local files.
"""
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


class Anchors(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])


def check(site, site_url, repo_url):
    root = Path(__file__).resolve().parents[1]
    text = (site / 'agent-guide.md').read_text()
    text = re.sub(r'^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$', '', text, flags=re.M | re.S)
    ids = Anchors(text).ids
    links = re.findall(r'\]\(([^)\s]+)\)', text) + re.findall(r'(?:href|src)="([^"]+)"', text)
    site_url = site_url.rstrip('/') + '/'
    code_url = repo_url.rstrip('/') + '/blob/main/'
    errors = []
    checked = 0
    for link in links:
        link = unescape(link)
        parsed = urlsplit(link)
        if link.startswith('#'):
            checked += 1
            if unquote(parsed.fragment) not in ids:
                errors.append((link, 'missing export anchor'))
            continue
        if link.startswith(site_url):
            target = site / unquote(urlsplit(link[len(site_url):]).path)
        elif link.startswith(code_url):
            target = root / unquote(urlsplit(link[len(code_url):]).path)
        elif parsed.scheme or parsed.netloc:
            continue
        else:
            errors.append((link, 'relative link in portable export'))
            continue
        checked += 1
        if target.is_dir():
            target = target / 'index.html'
        if not target.is_file():
            errors.append((link, 'missing file'))
        elif target.suffix == '.html' and parsed.fragment:
            if unquote(parsed.fragment) not in Anchors(target.read_text()).ids:
                errors.append((link, 'missing page anchor'))
    print(f'Checked {checked} export links; {len(errors)} broken destinations')
    for link, reason in errors:
        print(reason, link)
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(check(Path(sys.argv[1]), sys.argv[2], sys.argv[3]))
