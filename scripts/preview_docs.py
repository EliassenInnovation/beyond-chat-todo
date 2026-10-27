"""Serve the release layout with live reload, without generating a PDF per edit."""
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen
from livereload import Server
from prepare_docs_site import prepare
import site_urls

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site/preview"
PDF = ROOT / "site/preview-last-export.pdf"
PUBLIC = site_urls.site_root()


def build():
    subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict",
                    "--site-dir", str(SITE / "guide")], cwd=ROOT, check=True)
    prepare(SITE)
    # The sources and theme are identical; only the deployment origin changes.
    for pattern in ("*.html", "*.js"):
        for path in SITE.rglob(pattern):
            text = path.read_text()
            path.write_text(text.replace(PUBLIC, "/"))
    if PDF.exists():
        (SITE / "guide/guide.pdf").write_bytes(PDF.read_bytes())
    print("Preview updated: http://127.0.0.1:%s/guide/" % PORT, flush=True)


if __name__ == "__main__":
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    if not PDF.exists():
        try:
            with urlopen(PUBLIC + "guide/guide.pdf", timeout=15) as response:
                data = response.read()
            PDF.parent.mkdir(parents=True, exist_ok=True)
            PDF.write_bytes(data)
        except OSError as error:
            print(f"Last PDF export unavailable: {error}. Web preview will still work.")
    build()
    server = Server()
    for source in ("docs", "mkdocs.yml", ".github/docs_hooks.py", "examples/evaluation-review",
                   "scripts/prepare_docs_site.py"):
        server.watch(str(ROOT / source), build)
    server.serve(root=str(SITE), host="127.0.0.1", port=PORT, default_filename="index.html",
                 open_url_delay=None)
