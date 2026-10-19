"""Add the public evaluation example beside the guide, for preview and release."""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def prepare(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "collection.json"):
        shutil.copy2(ROOT / "examples/evaluation-review" / name, destination / name)
    page = destination / "index.html"
    text = page.read_text()
    base = "https://github.com/bobfischer/beyond-chat-todo/blob/main/"
    text = text.replace('href="../../docs/guides/evaluation-results.md"',
                        'href="guide/guides/evaluation-results.html"')
    text = text.replace('href="README.md#what-this-example-measures"',
                        f'href="{base}examples/evaluation-review/README.md#what-this-example-measures"')
    page.write_text(text)


if __name__ == "__main__":
    prepare(sys.argv[1])
