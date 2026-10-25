"""Source parser for the browser-only coding-agent handoff builder."""
from hashlib import sha256
from pathlib import Path
import re
import subprocess
from urllib.parse import urljoin, urlsplit


def portable(text, source, root, site_url, repo_url):
    def link(match):
        href = match[1]
        u = urlsplit(href)
        if u.scheme or u.netloc or href.startswith('/'):
            return match[0]
        target = (root / 'docs' / source).parent / u.path if u.path else root / 'docs' / source
        target = target.resolve()
        docs = (root / 'docs').resolve()
        if target.is_relative_to(docs):
            relative = target.relative_to(docs)
            if relative.suffix == '.md' and relative.name != 'agent-guide.md':
                relative = relative.with_suffix('.html')
            url = urljoin(site_url, relative.as_posix())
        elif target.is_relative_to(root.resolve()):
            url = repo_url.rstrip('/') + '/blob/main/' + target.relative_to(root.resolve()).as_posix()
        else:
            raise ValueError(f'Link outside repository: {href}')
        return '](' + url + ('#' + u.fragment if u.fragment else '') + ')'
    return re.sub(r'\]\(([^)\s]+)\)', link, text)


def parse_checks(text):
    checks = []
    pattern = r'^<!-- builder: ([a-z,]*) ?-->\n- Check (\d+\.\d+) — (.+)$'
    for match in re.finditer(pattern, text, re.M):
        tags, ident, first = match.groups()
        body = [first]
        # A check is one list item, including indented paragraphs and nested lists.
        for line in text[match.end():].splitlines()[1:]:
            if line and not line.startswith('  '):
                break
            body.append(line[2:] if line.startswith('  ') else line)
        headings = re.findall(r'^### (\d+\. .+)$', text[:match.start()], re.M)
        if not headings:
            raise ValueError(f'Check {ident} has no section')
        checks.append(dict(id=ident, title=first.split('. ', 1)[0],
                           text='\n'.join(body).strip(), section=headings[-1], presets=[tag for tag in tags.split(',') if tag]))
    declared = re.findall(r'^- Check (\d+\.\d+) —', text, re.M)
    ids = [c['id'] for c in checks]
    if not ids or ids != declared or len(ids) != len(set(ids)):
        raise ValueError('Every check needs unique ID and builder metadata')
    return checks


def block(text, title):
    match = re.search(r'^### ' + re.escape(title) + r'\n(.*?)(?=^### |^## |\Z)', text, re.M | re.S)
    if not match:
        raise ValueError(f'Missing instructions: {title}')
    return match[1].strip()


def build_data(root, site_url, pages, repo_url):
    source = 'principles/implementation.md'
    text = (root / 'docs' / source).read_text()
    checks = parse_checks(text)
    revision = re.search(r'^Check revision note — (.+?)(?=\n\n)', text, re.M | re.S)
    if not revision:
        raise ValueError('Missing check revision note')
    digest = sha256()
    for path in sorted((root / 'docs').rglob('*.md')):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    digest.update((root / 'mkdocs.yml').read_bytes())
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--', 'docs', 'mkdocs.yml', '.github/docs_hooks.py', '.github/checklist_data.py'], cwd=root, text=True).strip())
    for c in checks:
        c['text'] = portable(c['text'], source, root, site_url, repo_url)
        c['url'] = urljoin(site_url, 'principles/implementation.html#check-' + c['id'].replace('.', '-'))
    chapters = []
    for src, title, url in pages:
        if src in (source, 'index.md'):
            continue
        md = (root / 'docs' / src).read_text()
        md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
        chapters.append(dict(id=src, title=title, url=urljoin(site_url, url), text=portable(md, src, root, site_url, repo_url)))
    return dict(checks=checks, chapters=chapters, commit=commit, dirty=dirty,
                revision=digest.hexdigest()[:16], revisionNote=revision[0].replace('\n', ' '),
                guideUrl=site_url, ownership=portable(block(text, 'Who owns what'), source, root, site_url, repo_url),
                rules=portable(block(text, 'Seven working rules'), source, root, site_url, repo_url),
                report=portable(block(text, 'Report'), source, root, site_url, repo_url),
                security=re.search(r'^> Security scope: (.+)$', text, re.M)[1])
