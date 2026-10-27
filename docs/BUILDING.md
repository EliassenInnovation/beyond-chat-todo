# Build and maintain the guide

The chapters under `docs/` are the sources for both GitHub reading and the documentation
website. `mkdocs.yml` defines the chapter order. Do not create a second copy of the text.
The editorial structure and source mapping are in [OUTLINE.md](OUTLINE.md).
The [deck audit](DECK-AUDIT.md) records how the talk material was incorporated or intentionally omitted.

## Edit and review locally

Run `./preview.sh` from the repository root, then open **http://127.0.0.1:8000/guide/**.
The script creates an isolated documentation environment on first use. Leave it running;
changes to chapters, images, styles, navigation and the public report rebuild the site and
reload the browser. Stop it with Ctrl-C. An optional port can be supplied: `./preview.sh 8001`.

The preview uses the same MkDocs configuration, theme, assets and page structure as the
published site. The guide is under `/guide/`, the evaluation report is at `/`, and the
recorded demo stays in the guide. Links within the publication stay local. Source-code
and research links still go to their original destinations.

The preview retains the last published PDF; it does not regenerate PDFs during editing.
Web edits stay local until an explicit release. Do not deploy each editorial change.

## Publish a complete release

After reviewing locally, run:

```bash
./publish.sh "Update guide examples"
```

This commits documentation and release-tool changes, pushes `main`, and starts the GitHub
Actions release. It waits for a strict site build, fresh PDF generation, link checks and
publication. A failure returns a nonzero exit status; the previous public site remains in
place until deployment succeeds. Git and authenticated GitHub CLI (`gh auth login`) are
required. Existing staged changes must be committed or unstaged first. Application and
test edits are not included in the documentation commit. Previously committed changes on
`main` are pushed with the release.

The release includes only the guide and explicitly public evaluation example, never `.env`,
`todos.json` or local `runs/`. To change the public report itself, commit its source changes
before publishing. The PDF and web guide are built from the same commit.

Links to repository code are rewritten to GitHub during the build by `.github/docs_hooks.py`;
relative source links stay useful when reading Markdown. Keep the old chapter paths and anchors
when editing references, since they are linked from reports and prior discussions.

Diagrams are SVG adaptations of the October 13 talk's diagram bodies. Keep headings and captions
in Markdown. Internal labels belong in the diagram, but slide titles, chevrons, decorative
footers and fixed slide canvases do not. Inspect at desktop and narrow widths after changes.

Before the public release, make the sample repository public and verify that its HTTPS
clone URL works without authentication. The reader-facing setup instructions assume public
access.

Before publishing: build strictly, check local links and anchors, visually inspect the main
chapters and diagrams, and verify that the evaluation report remains available at its old URL.
Documentation edits do not require paid model evaluations.

Also check the coding-agent export against the built site and repository:

```bash
python3 .github/check_agent_export.py site/guide "$(python3 scripts/site_urls.py site)" "$(python3 scripts/site_urls.py repo)"
```

Use the configured `site_url` and `repo_url` if those addresses change. The checker validates
local export anchors, built page and asset destinations, and repository-file links.


Diagram layouts use an 800-unit-wide canvas and preserve paired columns, layers and cycles.
Use larger labels and wrapped text rather than shrinking a slide or making every element
a separate vertical card. Render at the reading-column width to check fit.

Use regular-weight prose rather than bold emphasis for words or sentences. Keep headings
and table headers distinct through their existing styles.
