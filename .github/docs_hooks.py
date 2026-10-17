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


_PRINT_PAGES = []


def on_nav(nav, config, files):
    """Capture reading order for the complete printable publication."""
    _PRINT_PAGES.clear()
    _PRINT_PAGES.extend(nav.pages)


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
    body { color:#1a1e33; font:11pt/1.45 'Sofia Pro',Calibri,Arial,sans-serif; max-width:8.5in; margin:auto; padding:.7in; }
    h1,h2,h3,h4 { font-family:'Big Caslon',Caslon,'Times New Roman',serif; line-height:1.2; break-after:avoid; }
    h1 { font-size:28pt; } h2 { font-size:20pt; } h3 { font-size:16pt; }
    img { max-width:100%; height:auto; } .publication-cover { width:100%; display:block; }
    table { width:100%; border-collapse:collapse; font-size:9pt; } th,td { padding:6px; border:1px solid #ccc; text-align:left; }
    .cover-anchor { display:none; }
    pre { white-space:pre-wrap; overflow-wrap:anywhere; background:#f5f1ee; padding:10px; font-size:9pt; }
    a { color:#2e4294; } .headerlink,.print-guide-link { display:none; }
    blockquote,.admonition { border-left:3px solid #6b93a8; margin:1em 0; padding:.2em 1em; }
    .admonition-title { font-weight:bold; } .chapter { margin-top:2em; }
    @media print {
      @page { size:letter; margin:.7in; }
      body { padding:0; max-width:none; }
      .print-controls { display:none; } .chapter { break-before:page; margin:0; }
      .chapter:first-of-type { break-before:auto; }
      @page cover { size:letter; margin:0; }
      .cover-page { page:cover; width:8.5in; height:11in; margin:0; padding:0; break-after:page; overflow:hidden; }
      .cover-page .publication-cover { width:8.5in; height:11in; display:block; }
      .chapter:first-of-type { break-before:auto; }
      .contents { break-before:page; } tr,figure { break-inside:avoid; }
    }
    """
    controls = '<div class="print-controls"><button onclick="window.print()">Print / Save as PDF</button><p>Choose Save as PDF, Letter paper, and turn off browser headers and footers.</p></div>'
    # Keep the cover and introduction first, followed by the contents and all chapters.
    toc = '<nav class="contents"><h1>Contents</h1><ol>' + ''.join(contents[1:]) + '</ol></nav>'
    cover_match = re.search(r'<p>\s*(<img[^>]+class="publication-cover"[^>]*>)\s*</p>', sections[0])
    if not cover_match:
        raise ValueError("Printable guide is missing its cover image")
    cover = '<div class="cover-page">' + cover_match[1] + '</div>'
    introduction = sections[0].replace(cover_match[0], '')
    body = controls + cover + introduction + toc + ''.join(sections[1:])
    output = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Build better agents — complete guide</title><style>' + css + '</style></head><body>' + body + '</body></html>'
    (Path(config["site_dir"]) / "print.html").write_text(output)
