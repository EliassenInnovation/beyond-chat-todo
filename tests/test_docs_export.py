"""A page omitted from the combined export must still have a usable link."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('docs_hooks', ROOT / '.github/docs_hooks.py')
hooks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hooks)


def test_export_resolves_included_and_omitted_pages_from_source_folder(tmp_path, monkeypatch):
    docs = tmp_path / 'docs'
    (docs / 'guide').mkdir(parents=True)
    (docs / 'reference').mkdir()
    site = tmp_path / 'site'
    site.mkdir()
    (docs / 'guide/apply.md').write_text(
        '# Apply\n\n[builder](checklist-builder.md#choose)\n'
        '[same folder](other.md#detail)\n'
        '[other folder](../reference/help.md#help)\n'
        '[local](#apply)\n'
        '[image](../images/example.png)\n'
        '```text\n[unchanged](checklist-builder.md)\n```\n')
    (docs / 'guide/other.md').write_text('# Other\n\n## Detail\n')
    (docs / 'guide/checklist-builder.md').write_text('# Builder\n')
    (docs / 'reference/help.md').write_text('# Help\n')
    pages = [SimpleNamespace(file=SimpleNamespace(src_uri=src), title=title, content=html)
             for src, title, html in [
                 ('guide/apply.md', 'Apply', '<h1 id="apply">Apply</h1>'),
                 ('guide/other.md', 'Other', '<h1 id="other">Other</h1><h2 id="detail">Detail</h2>')]]
    monkeypatch.setattr(hooks, 'ROOT', tmp_path)
    monkeypatch.setattr(hooks, 'DOCS', docs)
    monkeypatch.setattr(hooks, '_PRINT_PAGES', pages)
    monkeypatch.setattr(hooks, '_PAGE_URLS', {
        Path('guide/checklist-builder.md'): 'guide/checklist-builder.html',
        Path('reference/help.md'): 'reference/help.html',
    })
    hooks.export_agent_markdown({'site_dir': str(site), 'site_url': 'https://example.org/guide/'})
    text = (site / 'agent-guide.md').read_text()
    assert '[builder](https://example.org/guide/guide/checklist-builder.html#choose)' in text
    assert '[same folder](#guide-1-detail)' in text
    assert '[other folder](https://example.org/guide/reference/help.html#help)' in text
    assert '[local](#guide-0-apply)' in text
    assert '[image](https://example.org/guide/images/example.png)' in text
    assert '```text\n[unchanged](checklist-builder.md)\n```' in text
