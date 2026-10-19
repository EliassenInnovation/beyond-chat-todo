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
    # Keep the cover and introduction separately reachable without a deployment URL.
    from mkdocs.structure.nav import Link
    for i, item in enumerate(nav.items):
        if getattr(item, "is_page", False) and item.file.src_uri == "index.md":
            nav.items.insert(i + 1, Link("Introduction", item.url + "#introduction"))
            break
    nav.items.append(Link("Download for coding agents (.md)", "agent-guide.md"))
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
    .admonition.practice { border-color:#8ebfb3; }
    .practice > .admonition-title { background:#8ebfb3; color:#1a1e33; padding:.35em .5em; }
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
      img[src$=".svg"],img[src*=".svg?"] { width:80%; display:block; margin:.45em auto; }

      .print-controls { display:none; } .chapter { break-before:page; margin:0; }
      @page cover { size:letter; margin:0; @bottom-center { content:none; } @bottom-right { content:none; } }
      .cover-page { page:cover; width:8.5in; height:11in; margin:0; padding:0; break-after:page; overflow:hidden; }
      .cover-page .publication-cover { width:8.5in; height:11in; display:block; }
      .contents { break-before:page; } tr,figure { break-inside:avoid; }
      p,li,dd { widows:3; orphans:3; }
      .chapter > p:last-child { break-before:avoid; }
      .contents li { widows:2; orphans:2; }
      .publication table { table-layout:fixed; width:100%; }
      .publication th,.publication td { overflow-wrap:anywhere; }
      .publication td code { overflow-wrap:anywhere; }
      .publication table:has(th:nth-child(5)):not(:has(th:nth-child(6))) th:first-child { width:7%; }
      .publication table:has(th:nth-child(5)):not(:has(th:nth-child(6))) th:nth-child(2) { width:12%; }
      .publication table:has(th:nth-child(5)):not(:has(th:nth-child(6))) th:nth-child(3) { width:11%; }

      .admonition-title { break-after:avoid; }
      p:has(> img),p:has(> a > img) { break-inside:avoid; break-after:avoid; }
      .story-image { break-after:avoid; }
      p:has(> img) + p,p:has(> a > img) + p { break-before:avoid; }

    }
    """
    controls = '<div class="print-controls"><a href="guide.pdf">Download the last PDF export</a> · <button onclick="window.print()">Print this page</button><p>The PDF is exported separately and may lag behind this web guide. To print this version, choose Save as PDF, Letter paper, and turn off browser headers and footers.</p></div>'
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
    export_agent_markdown(config)



def export_agent_markdown(config):
    """Generate a portable text edition from the same sources and navigation as the guide."""
    from hashlib import sha256
    from html import unescape
    from urllib.parse import urljoin, unquote

    sources = {Path(page.file.src_uri): page for page in _PRINT_PAGES}
    prefixes = {source: "guide-" + str(i) for i, source in enumerate(sources)}
    fingerprint = sha256()
    for source in sources:
        fingerprint.update(source.as_posix().encode())
        fingerprint.update((DOCS / source).read_bytes())
    sections = []
    toc = []
    for source, page in sources.items():
        prefix = prefixes[source]
        title = "Introduction" if source == Path("index.md") else page.title
        toc.append(f"- [{title}](#{prefix})")
        markdown = (DOCS / source).read_text()
        # Rendered IDs preserve MkDocs' actual heading slugs, including duplicate headings.
        heading_ids = iter(re.findall(r'<h[1-6]\b[^>]*\bid="([^"]+)"', page.content))
        lines = []
        fence = None
        for line in markdown.splitlines():
            marker = re.match(r"^\s*(`{3,}|~{3,})", line)
            if marker:
                token = marker[1]
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
                lines.append(line)
                continue
            if fence:
                lines.append(line)
                continue
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            html_heading = re.match(r'<h([1-6])\b[^>]*>(.*?)</h\1>', line)
            if heading or html_heading:
                anchor = next(heading_ids)
                if anchor == "cover":
                    continue
                level = len(heading[1]) if heading else int(html_heading[1])
                label = heading[2] if heading else re.sub(r"<[^>]+>", "", html_heading[2])
                lines.append(f'<a id="{prefix}-{anchor}"></a>')
                lines.append("#" * min(level + 1, 6) + " " + label)
                continue
            if ".publication-cover" in line:
                continue
            # Preserve legacy anchors, with a per-chapter namespace.
            line = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}-{m[1]}"', line)
            lines.append(line)
        if next(heading_ids, None) is not None:
            raise ValueError(f"Markdown export missed a heading in {source}")
        markdown = "\n".join(lines)

        def destination(value):
            parsed = urlsplit(unescape(value))
            if parsed.scheme or parsed.netloc or value.startswith("/"):
                return value
            target = (DOCS / source).parent / unquote(parsed.path) if parsed.path else DOCS / source
            target = target.resolve()
            if target.is_relative_to(DOCS):
                relative = target.relative_to(DOCS)
                if relative in sources:
                    return "#" + prefixes[relative] + ("-" + parsed.fragment if parsed.fragment else "")
                return urljoin(config["site_url"], relative.as_posix()) + ("#" + parsed.fragment if parsed.fragment else "")
            if target.is_relative_to(ROOT):
                return REPO + target.relative_to(ROOT).as_posix() + ("#" + parsed.fragment if parsed.fragment else "")
            raise ValueError(f"Export link leaves the repository: {source}: {value}")

        # Rewrite links outside code fences; code examples remain byte-for-byte intact.
        chunks = re.split(r'(^\s*```[^\n]*\n.*?^\s*```\s*$|^\s*~~~[^\n]*\n.*?^\s*~~~\s*$)', markdown,
                          flags=re.M | re.S)
        for i in range(0, len(chunks), 2):
            chunks[i] = re.sub(r'\]\(([^)\s]+)\)', lambda m: "](" + destination(m[1]) + ")", chunks[i])
            chunks[i] = re.sub(r'(href|src)="([^"]+)"',
                               lambda m: m[1] + '="' + destination(m[2]) + '"', chunks[i])
        sections.append(f'<a id="{prefix}"></a>\n\n' + "".join(chunks))
    # The export contains all chapters, appendices and checks, rather than a second summary.
    header = ("# Build better agents — coding-agent edition\n\n"
              "Generated from the guide's maintained Markdown sources. Edit those sources; "
              "this file is regenerated on every build and publication.\n\n"
              f"Source content revision: `{fingerprint.hexdigest()[:16]}`.\n\n"
              "Use the guide to assess an existing application or propose a new architecture. "
              "Adapt its principles, examples and acceptance checks to the application's goals "
              "and agreed scope. The Apply chapter includes an architectural assessment prompt.\n\n"
              "This edition includes the guide text, implementation examples, evaluation guidance, "
              "appendices and acceptance checks. Illustrations and repository code are linked.\n\n"
              "## Contents\n\n")
    (Path(config["site_dir"]) / "agent-guide.md").write_text(header + "\n".join(toc) + "\n\n" + "\n\n---\n\n".join(sections) + "\n")
