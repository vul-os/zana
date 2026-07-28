"""Gates on site/ — Zana's product mini-site.

`site/` is copied verbatim into vulos.org by
`vulos-static/scripts/collect-repo-landings.mjs` and framed at
/products/zana. That means three things have to hold and nothing checks them
on the other side: the pages must be self-contained (no build step, no
third-party request), every local path must resolve after the copy, and the
three shared elements that make 25 separately-authored sites read as one suite
must be present.

The token block below is the vocabulary ratified in
vulos-static/DESIGN_SYSTEM.md and shipped in
vulos-static/templates/product-site/tokens.css. It is written out here rather
than read from that repo on purpose: vulos-static is a sibling checkout that
does not exist in this repo's CI, and a gate that silently skips when its
input is missing is exactly the failure this suite refuses.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
PAGES = ("index.html", "docs.html")

RATIFIED_TOKENS = {
    "bg": "#09090B",
    "bg-soft": "#0E0E10",
    "panel": "#131316",
    "panel-2": "#18181B",
    "border": "rgba(255,255,255,.08)",
    "border-2": "rgba(255,255,255,.13)",
    "text": "#FAFAFA",
    "muted": "#A1A1AA",
    "faint": "#71717A",
    "radius": "16px",
    "max": "1120px",
    "mono": 'ui-monospace,SFMono-Regular,"SF Mono","Geist Mono",Menlo,Consolas,monospace',
    "sans": '-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif',
}

# Zana's colour. The template's placeholder is #5B8DEF; shipping that would
# mean the accent was never set.
ACCENT = "#f2a72c"
ACCENT_2 = "#C97C10"
PLACEHOLDER_ACCENT = "#5B8DEF"

# DESIGN_SYSTEM.md: "Everything up to and including 'open, self-hostable
# apps.' is identical in all six, so that is the invariant the test asserts."
FOOTER_INVARIANT = (
    'Part of <a href="https://vulos.org" target="_blank" rel="noopener" '
    'style="color:var(--text)">Vulos</a> — open, self-hostable apps.'
)


def read(name: str) -> str:
    p = SITE / name
    assert p.is_file(), f"{p} is missing — the site cannot be collected without it"
    return p.read_text(encoding="utf-8")


def parse_root_block(css: str) -> dict:
    """The declarations of the FIRST :root{...} block."""
    m = re.search(r":root\{(.*?)\}", css, re.DOTALL)
    assert m, "no :root{} block found"
    out = {}
    for decl in m.group(1).split(";"):
        decl = decl.strip()
        if not decl.startswith("--"):
            continue
        name, _, value = decl.partition(":")
        out[name.strip()[2:]] = value.strip()
    return out


# ── The ratified vocabulary ─────────────────────────────────────────────────


def test_site_ships_the_canonical_token_file():
    css = read("tokens.css")
    tokens = parse_root_block(css)
    assert tokens == RATIFIED_TOKENS, (
        "site/tokens.css has drifted from the vocabulary ratified in "
        "vulos-static/DESIGN_SYSTEM.md"
    )
    assert len(RATIFIED_TOKENS) == 13

    # The second :root block is the accent pair, and it must agree with the
    # pages — a tokens.css still holding the template placeholder is a copied
    # file nobody finished.
    accents = re.findall(r":root\{\s*--accent:\s*(#[0-9A-Fa-f]{6});\s*--accent-2:\s*(#[0-9A-Fa-f]{6});?\s*\}", css)
    assert accents == [(ACCENT, ACCENT_2)], (
        f"site/tokens.css declares {accents}, expected [('{ACCENT}', '{ACCENT_2}')]"
    )


@pytest.mark.parametrize("page", PAGES)
def test_every_page_inlines_the_same_token_block(page):
    """Inlined, not linked: the pages must render with no extra request."""
    tokens = parse_root_block(read(page))
    assert tokens == RATIFIED_TOKENS, (
        f"site/{page} does not carry the ratified token block byte-for-byte"
    )


@pytest.mark.parametrize("page", PAGES)
def test_accent_lives_in_its_own_trailing_style_element(page):
    """One greppable line holds the product's colour — DESIGN_SYSTEM.md's rule."""
    html = read(page)
    m = re.search(r"<style>:root\{--accent:(#[0-9A-Fa-f]{6});--accent-2:(#[0-9A-Fa-f]{6})\}</style>", html)
    assert m, f"site/{page} has no standalone accent <style> element"
    assert m.group(1) == ACCENT and m.group(2) == ACCENT_2
    assert PLACEHOLDER_ACCENT.lower() not in html.lower(), (
        f"site/{page} still contains the template's placeholder accent"
    )
    # It must come after the main block, so it cannot be overridden by it.
    assert html.index(m.group(0)) > html.index(":root{"), "accent block is not last"


# ── The three non-negotiables ───────────────────────────────────────────────


@pytest.mark.parametrize("page", PAGES)
def test_header_carries_the_vulos_badge(page):
    html = read(page)
    m = re.search(r'<a class="vulos-badge"[^>]*href="https://vulos\.org"', html)
    assert m, f"site/{page} is missing the .vulos-badge link to vulos.org"
    assert 'src="./assets/vulos-logo.png"' in html


def test_landing_carries_the_standalone_band():
    html = read("index.html")
    assert 'class="vulos-band"' in html, "index.html is missing the .vulos-band section"
    band = html.split('class="vulos-band"', 1)[1][:1400]
    assert "never requires Vulos infrastructure to run" in band, (
        "the band no longer states the standalone promise — that sentence is the "
        "point of the band, and it has to stay true of the repo"
    )


@pytest.mark.parametrize("page", PAGES)
def test_footer_invariant(page):
    assert FOOTER_INVARIANT in read(page), (
        f"site/{page}'s footer line differs from the one all six conforming sites share"
    )


@pytest.mark.parametrize("page", PAGES)
def test_shared_class_vocabulary_is_present(page):
    """The class names a seventh site inherits the family look from."""
    common = {"wrap", "site-header", "nav", "nav-spacer", "nav-links", "brand",
              "vulos-badge", "site-footer", "foot", "accent"}
    landing = {"btn", "btn-primary", "btn-ghost", "hero", "eyebrow", "cta-row",
               "section", "grid", "card", "quick", "codeblock", "steps",
               "decent", "vulos-band"}
    docs = {"docs-shell", "docs-nav", "docs-main", "docs-title", "markdown",
            "docs-error", "active"}
    expected = common | (landing if page == "index.html" else docs)

    html = read(page)
    missing = sorted(c for c in expected if not re.search(rf"[\"'\s.]{re.escape(c)}[\"'\s{{,]", html))
    assert not missing, f"site/{page} is missing shared classes: {missing}"
    assert len(expected) >= 17


# ── Self-containment ────────────────────────────────────────────────────────


@pytest.mark.parametrize("page", PAGES)
def test_page_makes_no_third_party_request(page):
    """A product site must work with the network unplugged."""
    html = read(page)
    remote_assets = re.findall(r'(?:src|href)\s*=\s*"(https?://[^"]+)"',
                               re.sub(r"<a\b[^>]*>", "", html, flags=re.I))
    assert not remote_assets, f"site/{page} loads remote assets: {remote_assets}"
    for banned in ("@import", "fonts.googleapis", "cdn.jsdelivr", "unpkg.com", "cdnjs"):
        assert banned not in html, f"site/{page} references {banned}"


def test_markdown_renderer_is_vendored():
    vendored = SITE / "assets" / "vendor" / "marked.umd.js"
    assert vendored.is_file() and vendored.stat().st_size > 10_000, (
        "marked.umd.js is not vendored — docs.html would have to reach a CDN"
    )
    assert (SITE / "assets" / "vendor" / "marked.umd.js.LICENSE").is_file()
    assert 'src="./assets/vendor/marked.umd.js"' in read("docs.html")


@pytest.mark.parametrize("page", PAGES)
def test_every_local_reference_resolves(page):
    """Every ./path in the page exists after site/ is copied verbatim."""
    html = read(page)
    refs = {r for r in re.findall(r'(?:src|href)\s*=\s*"(\.{1,2}/[^"#]+)"', html)}
    refs |= {m for m in re.findall(r'"path"\s*:\s*"(\.{1,2}/[^"]+)"', html)}
    assert len(refs) >= 4, f"only {len(refs)} local references found in {page}"
    missing = sorted(r for r in refs if not (SITE / r).exists())
    assert not missing, f"site/{page} points at files that do not exist: {missing}"


def test_no_build_step_is_required():
    """Anything needing compilation in this repo cannot be collected from it."""
    unexpected = sorted(
        p.name for p in SITE.iterdir()
        if p.name in {"package.json", "vite.config.js", "webpack.config.js", "Makefile"}
    )
    assert not unexpected, f"site/ acquired a build step: {unexpected}"


# ── Docs shell wiring ───────────────────────────────────────────────────────


def test_docs_sidebar_and_docs_array_agree():
    html = read("docs.html")
    array = re.search(r"const DOCS = \[(.*?)\];", html, re.DOTALL)
    assert array, "docs.html has no DOCS[] array"
    entries = re.findall(r'"slug"\s*:\s*"([^"]+)"\s*,\s*"title"\s*:\s*"([^"]+)"\s*,\s*"path"\s*:\s*"([^"]+)"',
                         array.group(1))
    sidebar = re.findall(r'<a data-slug="([^"]+)"[^>]*href="#([^"]+)"', html)

    assert len(entries) == 4, f"expected 4 docs, DOCS[] has {len(entries)}"
    assert len(sidebar) == len(entries), (
        f"sidebar has {len(sidebar)} rows for {len(entries)} docs — they must match 1:1"
    )
    assert [s for s, _ in sidebar] == [s for s, _, _ in entries], "sidebar order/slugs differ from DOCS[]"
    assert all(slug == href for slug, href in sidebar), "a sidebar data-slug does not match its href"

    for _, _, path in entries:
        assert (SITE / path).is_file(), f"DOCS[] points at missing {path}"


def test_docs_markdown_is_not_a_stale_second_copy_of_the_readme():
    """The docs are their own prose, but must not contradict the repo's status."""
    overview = (SITE / "docs" / "overview.md").read_text(encoding="utf-8")
    mower_doc = (SITE / "docs" / "mower-design.md").read_text(encoding="utf-8")

    # The simulator is source-only. Any page that mentions it must say so —
    # this repo previously advertised it as a working simulator while every
    # file at mower/simulator/*.{cpp,py} was zero bytes.
    for name, text in (("overview.md", overview), ("mower-design.md", mower_doc)):
        if "simulator" in text.lower():
            assert re.search(r"source only|not built|not tested", text, re.I), (
                f"site/docs/{name} mentions the simulator without stating that it "
                "is source only — that is the overstatement this gate exists for"
            )
