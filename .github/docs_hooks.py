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


def on_page_content(html, page, config, files):
    """Give local images a new cache key only when their contents change."""
    from hashlib import sha256
    from html import escape, unescape
    from urllib.parse import parse_qsl, unquote, urlencode, urlunsplit

    def version_image(match):
        prefix, raw_url, suffix = match.groups()
        parsed = urlsplit(unescape(raw_url))
        if parsed.scheme or parsed.netloc or parsed.path.startswith("/"):
            return match[0]
        target = (DOCS / page.file.src_uri).parent / unquote(parsed.path)
        target = target.resolve()
        if not target.is_relative_to(DOCS) or not target.is_file():
            return match[0]
        version = sha256(target.read_bytes()).hexdigest()[:12]
        query = [(key, value) for key, value in parse_qsl(parsed.query)
                 if key != "v"]
        query.append(("v", version))
        url = urlunsplit(parsed._replace(query=urlencode(query)))
        return prefix + escape(url, quote=True) + suffix

    return re.sub(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', version_image, html)


_PRINT_PAGES = []
_PRINT_NAV = []


def on_nav(nav, config, files):
    """Capture reading order for the complete printable publication."""
    _PRINT_PAGES.clear()
    _PRINT_PAGES.extend(nav.pages)
    _PRINT_NAV.clear()
    _PRINT_NAV.extend(nav.items)


def on_post_build(config):
    """Publish one printable document from the same rendered chapter content."""
    from html import escape
    from urllib.parse import urljoin

    pages = {page.url: "chapter-" + str(i) for i, page in enumerate(_PRINT_PAGES)}
    sections = []
    contents = []
    for page in _PRINT_PAGES:
        prefix = pages[page.url]
        contents.append(f'<li><a href="#{prefix}">{escape(page.title)}</a></li>')
        content = page.content
        content = re.sub(r'id="([^"]+)"', lambda m: f'id="{prefix}-{m[1]}"', content)

        def link(match):
            attr, value = match.groups()
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith("/"):
                return match[0]
            target = urlsplit(urljoin(page.url, value))
            if attr == "href" and target.path in pages:
                value = "#" + pages[target.path]
                if target.fragment:
                    value += "-" + target.fragment
            else:
                value = urljoin(page.url, value)
            return f'{attr}="{value}"'

        content = re.sub(r'(href|src)="([^"]+)"', link, content)
        sections.append(f'<section id="{prefix}" class="chapter">{content}</section>')
    css = """
    * { box-sizing: border-box; }
    body { color:#1a1e33; font:11pt/1.4 'Sofia Pro',Calibri,Arial,sans-serif; max-width:8.5in; margin:auto; padding:.7in; }
    h1,h2,h3,h4 { font-family:'Big Caslon',Caslon,'Times New Roman',serif; line-height:1.2; break-after:avoid; }
    h1 { font-size:26pt; color:#2e4294; } h2 { font-size:17pt; color:#2e4294; } h3 { font-size:14pt; color:#2e4294; }
    img { max-width:100%; height:auto; } .publication-cover { width:100%; display:block; }

/* Matching landscape frames preserve the action while trimming the lower foreground. */
.story-image { position: relative; width: 100%; padding-top: 60%; overflow: hidden; margin: .85rem 0 .45rem; break-inside: avoid; }
.story-image img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; object-position: center top; margin: 0; }
    h2:has(+ .section-subhead) { margin-bottom:.12em; }
    .section-subhead { font-family:"Big Caslon",Caslon,"Times New Roman",serif; font-size:1.05em; font-style:italic; line-height:1.3; margin-top:0; margin-bottom:.65em; }
    .cover-anchor { display:none; }
    pre { white-space:pre-wrap; overflow-wrap:anywhere; background:#f5f1ee; padding:10px; font-size:9pt; }
    a { color:#2e4294; } .headerlink,.print-guide-link { display:none; }
    blockquote,.admonition { border-left:3px solid #6b93a8; margin:1em 0; padding:.2em 1em; }
    .admonition-title { font-weight:bold; } .chapter { margin-top:2em; }
    .contents ul { list-style:none; padding:0; margin:.3em 0 .7em; }
    .contents ul ul { padding-left:1.2em; margin:.15em 0 .6em; }
    .contents li { margin:.15em 0; font-size:9pt; }
    .contents a { color:#1a1e33; text-decoration:none; }
    .toc-chapter { font-weight:bold; }
    blockquote { border:1px solid #2e4294; background:#edf1f8; padding:.65em .9em; }
    @media print {
      @page { size:letter; margin:.7in .7in .8in;
        @bottom-center { content:"ELIASSEN GROUP"; font:10pt Arial,sans-serif; color:white; background:#2e4294; width:100%; }
        @bottom-right { content:counter(page); font:9pt Arial,sans-serif; color:white; background:#2e4294; }
      }
      .contents a::after { content:leader('.') target-counter(attr(href), page); }
      body { padding:0; max-width:none; }
      .print-controls { display:none; } .chapter { break-before:page; margin:0; }
      .chapter:first-of-type { break-before:auto; }
      @page cover { size:letter; margin:0; @bottom-center { content:none; } @bottom-right { content:none; } }
      .cover-page { page:cover; width:8.5in; height:11in; margin:0; padding:0; break-after:page; overflow:hidden; }
      .cover-page .publication-cover { width:8.5in; height:11in; display:block; }
      .chapter:first-of-type { break-before:auto; }
      .contents { break-before:page; } tr,figure { break-inside:avoid; }
    }
    """
    controls = '<div class="print-controls"><a href="guide.pdf">Download the formatted PDF</a> · <button onclick="window.print()">Print this page</button><p>Choose Save as PDF, Letter paper, and turn off browser headers and footers.</p></div>'
    # Keep the cover and introduction first, followed by the contents and all chapters.
    toc_entries = []
    for page in _PRINT_PAGES:
        prefix = pages[page.url]
        title = 'Introduction' if page == _PRINT_PAGES[0] else page.title
        subheads = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', page.content, re.S)
        children = []
        for anchor, label in subheads:
            label = re.sub(r'<a class="headerlink".*?</a>', '', label)
            label = re.sub(r'<[^>]+>', '', label)
            children.append(f'<li><a href="#{prefix}-{anchor}">{label}</a></li>')
        toc_entries.append(f'<li><a class="toc-chapter" href="#{prefix}">{escape(title)}</a><ul>' + ''.join(children) + '</ul></li>')
    toc = '<nav class="contents"><h1>Contents</h1><ul>' + ''.join(toc_entries) + '</ul></nav>'
    cover_match = re.search(r'<p>\s*(<img[^>]+class="publication-cover"[^>]*>)\s*</p>', sections[0])
    if not cover_match:
        raise ValueError("Printable guide is missing its cover image")
    cover = '<div class="cover-page">' + cover_match[1] + '</div>'
    introduction = sections[0].replace(cover_match[0], '').replace('<h1 id="chapter-0-cover" class="cover-anchor" aria-label="Cover"></h1>', '')
    body = controls + cover + toc + introduction + ''.join(sections[1:])
    output = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Build better agents — complete guide</title><style>' + css + '</style><link rel="stylesheet" href="stylesheets/tables.css?v=1"></head><body class="publication">' + body + '<script src="javascripts/demo-return.js?v=1"></script></body></html>'
    (Path(config["site_dir"]) / "print.html").write_text(output)
