# Build and maintain the guide

The chapters under `docs/` are the sources for both GitHub reading and the documentation
website. `mkdocs.yml` defines the chapter order. Do not create a second copy of the text.
The editorial structure and source mapping are in [OUTLINE.md](OUTLINE.md).
The [deck audit](DECK-AUDIT.md) records how the talk material was incorporated or intentionally omitted.

From the repository root:

```bash
python3 -m venv /tmp/todo-docs
/tmp/todo-docs/bin/pip install -r requirements-docs.txt
/tmp/todo-docs/bin/mkdocs serve
```

Open the address printed by MkDocs. To create the static guide:

```bash
/tmp/todo-docs/bin/mkdocs build --strict
```

Output is in `site/guide/`. Dependencies are separate from the application's requirements.
The site uses relative HTML links, local assets and system fonts. Search needs an HTTP server;
for an offline preview, serve `site/` with `python3 -m http.server --directory site`.

The **Publish documentation and evaluation example** GitHub Actions workflow builds the guide
at `/guide/` alongside the existing report at `/`. It publishes only documentation and the
explicit public example files, never `.env`, `todos.json` or local `runs/`.
Run the workflow manually after reviewing a documentation change.

Links to repository code are rewritten to GitHub during the build by `.github/docs_hooks.py`;
relative source links stay useful when reading Markdown. Keep the old chapter paths and anchors
when editing references, since they are linked from reports and prior discussions.

Diagrams are SVG adaptations of the October 13 talk's diagram bodies. Keep headings and captions
in Markdown. Internal labels belong in the diagram, but slide titles, chevrons, decorative
footers and fixed slide canvases do not. Inspect at desktop and narrow widths after changes.

Before publishing: build strictly, check local links and anchors, visually inspect the main
chapters and diagrams, and verify that the evaluation report remains available at its old URL.
Documentation edits do not require paid model evaluations.

Diagram layouts use a 560-unit-wide canvas, with 22-unit labels and body text where possible.
Keep content stacked for the reading column; do not shrink a slide to fit. The registry uses
18-unit code with explanations below each group. Render at the intended display width when
checking text fit. Page titles remain in Markdown.
