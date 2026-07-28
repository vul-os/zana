"""Gates on site/ — Zana's product mini-site.

`site/` is copied verbatim into vulos.org by
`vulos-static/scripts/collect-repo-landings.mjs` and framed at /products/zana.
Nothing on the other side checks it, so this file does.

WHAT CHANGED, AND WHY: this suite used to assert that the pages carried the
shared product-site template byte-for-byte — a ratified 13-token `:root` block,
a trailing one-line accent override, and a fixed class vocabulary. Zana has
since left that template, as the rest of the suite has, for a hardware-native
art direction of its own (drafting grid, title block, dimension lines, copper
artwork lifted out of the boards). Pinning the abandoned vocabulary would have
gated the site against a design it no longer has.

The three things that template was actually protecting are still protected, and
they are the ones that matter across repos:

  * self-containment — the page must render with the network unplugged,
  * resolvability — every local path must survive the copy,
  * attribution — the Vulos badge, the standalone-promise band, and the shared
    footer line.

And three new gates protect what is specific to a hardware repo: the page must
not quote a dimension the mesh does not have, it must not overstate what is
finished, and its type must be vendored rather than fetched.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
PAGES = ("index.html", "docs.html")

# The nine colours of the Zana brand spec, verbatim. These are constants, not
# theme values: the stylesheet declares them once and both themes address them
# through role tokens (--accent, --bg, --text…). Changing one here without
# changing the spec is how a brand quietly stops being a brand.
SPEC_COLOURS = {
    "amber": "#f2a72c",      # marigold amber  — primary accent, dominant
    "bronze": "#8f5608",     # deep bronze     — amber for light surfaces only
    "black": "#0a0b0d",      # near-black      — page ground
    "charcoal": "#22242a",   # warm charcoal   — cards, raised surfaces
    "paper": "#f7f4ec",      # paper           — the trace, headings
    "cream": "#ece7dc",      # cream           — body text
    "warm-grey": "#8a8378",  # warm grey       — hairlines, muted, disabled
    "verdigris": "#4e9b86",  # verdigris       — secondary / info, sparingly
    "oxide": "#b34a2e",      # oxide red       — errors and destructive only
}

# vulos-static's product-site template ships this as its placeholder accent;
# shipping it would mean the accent was never set.
PLACEHOLDER_ACCENT = "#5B8DEF"

# DESIGN_SYSTEM.md: the sentence every conforming product site shares.
FOOTER_INVARIANT = (
    'Part of <a href="https://vulos.org" target="_blank" rel="noopener" '
    'style="color:var(--text)">Vulos</a> — open, self-hostable apps.'
)


def read(name: str) -> str:
    p = SITE / name
    assert p.is_file(), f"{p} is missing — the site cannot be collected without it"
    return p.read_text(encoding="utf-8")


def stylesheet() -> str:
    return read("assets/zana.css")


# ── The theme ───────────────────────────────────────────────────────────────


def test_the_nine_spec_colours_are_declared_verbatim():
    """The brand spec's palette, exactly. No substitutions, no near-misses."""
    css = stylesheet()
    wrong = []
    for name, value in SPEC_COLOURS.items():
        m = re.search(rf"--{re.escape(name)}:\s*(#[0-9A-Fa-f]{{3,8}})\s*;", css)
        if not m:
            wrong.append(f"--{name} is not declared")
        elif m.group(1).lower() != value:
            wrong.append(f"--{name} is {m.group(1)}, spec says {value}")
    assert not wrong, "assets/zana.css has drifted from the brand spec:\n  " + "\n  ".join(wrong)
    assert PLACEHOLDER_ACCENT.lower() not in css.lower(), (
        "the shared template's placeholder accent is still in the stylesheet"
    )


def test_amber_is_dark_only_and_light_surfaces_get_bronze():
    """The spec's one hard rule about applying the palette.

    "Amber is a dark-mode accent — it fails contrast on cream, so light
    surfaces use bronze #8f5608 instead." If the vellum theme ever inherits
    amber, every accent on it drops below readable.
    """
    css = stylesheet()
    dark = re.search(r":root\s*\{(.*?)\n\}", css, re.DOTALL)
    light = re.search(r'\[data-theme="light"\]\s*\{(.*?)\n\}', css, re.DOTALL)
    assert dark and light, "could not isolate the two theme blocks"

    assert re.search(r"--accent:\s*var\(--amber\)", dark.group(1)), (
        "the graphite theme's accent is not amber"
    )
    assert re.search(r"--accent:\s*var\(--bronze\)", light.group(1)), (
        "the vellum theme's accent is not bronze — amber fails contrast on cream"
    )


def test_both_themes_define_every_role_token():
    """A role defined in only one theme is invisible until someone flips the
    switch, which is exactly when nobody is looking."""
    css = stylesheet()
    dark = re.search(r":root\s*\{(.*?)\n\}", css, re.DOTALL)
    light = re.search(r'\[data-theme="light"\]\s*\{(.*?)\n\}', css, re.DOTALL)
    assert dark and light, "assets/zana.css is missing a theme block"

    names = lambda block: {m.group(1) for m in re.finditer(r"(--[\w-]+)\s*:", block)}
    dark_tokens, light_tokens = names(dark.group(1)), names(light.group(1))

    # The spec palette and the geometry/type tokens are theme-independent by
    # design; the ROLE tokens are the ones both themes have to answer for.
    fixed = {f"--{n}" for n in SPEC_COLOURS} | {
        "--r", "--r-xs", "--r-sm", "--r-lg", "--max", "--gut", "--hdr",
        "--ease", "--ease-out", "--display", "--sans", "--mono",
    }
    roles = dark_tokens - fixed
    assert len(roles) >= 15, f"only {len(roles)} role tokens found — the scan is broken"
    assert not (roles - light_tokens), (
        f"roles defined for graphite but not vellum: {sorted(roles - light_tokens)}"
    )

@pytest.mark.parametrize("page", PAGES)
def test_page_applies_the_stored_theme_before_first_paint(page):
    """Otherwise a vellum reader gets a graphite flash on every navigation."""
    html = read(page)
    assert 'data-theme="dark"' in html, f"site/{page} does not set a default theme on <html>"
    assert re.search(r'localStorage\.getItem\("zana-theme"\)', html), (
        f"site/{page} has no pre-paint theme script"
    )
    # The script must come before the stylesheet's first use, i.e. in <head>.
    head = html.split("</head>", 1)[0]
    assert "zana-theme" in head, f"site/{page}'s theme script is not in <head>"


# ── The three non-negotiables ───────────────────────────────────────────────


@pytest.mark.parametrize("page", PAGES)
def test_header_carries_the_vulos_badge(page):
    html = read(page)
    assert re.search(r'<a class="vulos-badge"[^>]*href="https://vulos\.org"', html), (
        f"site/{page} is missing the .vulos-badge link to vulos.org"
    )
    assert 'src="./assets/vulos-logo.png"' in html


def test_landing_carries_the_standalone_band():
    html = read("index.html")
    m = re.search(r'class="[^"]*\bvulos-band\b[^"]*"', html)
    assert m, "index.html is missing the .vulos-band section"
    band = html[m.end():m.end() + 1400]
    assert "never requires Vulos infrastructure to run" in band, (
        "the band no longer states the standalone promise — that sentence is the "
        "point of the band, and it has to stay true of the repo"
    )


@pytest.mark.parametrize("page", PAGES)
def test_footer_invariant(page):
    assert FOOTER_INVARIANT in read(page), (
        f"site/{page}'s footer line differs from the one every conforming site shares"
    )


# ── Self-containment ────────────────────────────────────────────────────────


@pytest.mark.parametrize("page", PAGES)
def test_page_makes_no_third_party_request(page):
    """A product site must work with the network unplugged.

    Only fetching references count. An <a href> is a place the reader may
    choose to go, and <link rel="canonical"> is metadata a crawler reads — the
    browser requests neither while rendering the page.
    """
    html = read(page)
    fetching = re.sub(r"<a\b[^>]*>", "", html, flags=re.I)
    fetching = re.sub(r'<link\b[^>]*rel="canonical"[^>]*>', "", fetching, flags=re.I)
    remote_assets = re.findall(r'(?:src|href)\s*=\s*"(https?://[^"]+)"', fetching)
    assert not remote_assets, f"site/{page} loads remote assets: {remote_assets}"
    for banned in ("fonts.googleapis", "fonts.gstatic", "cdn.jsdelivr", "unpkg.com", "cdnjs"):
        assert banned not in html, f"site/{page} references {banned}"


def test_type_is_vendored_not_fetched():
    """The stylesheet may only @font-face onto files that ship in the bundle."""
    css = stylesheet()
    assert "@import" not in css, "assets/zana.css uses @import — inline it or link it"
    faces = re.findall(r"@font-face\s*\{[^}]*?url\('([^']+)'\)", css)
    assert len(faces) >= 4, f"only {len(faces)} @font-face rules found — the scan is broken"
    for rel in faces:
        assert not rel.startswith("http"), f"font fetched from a third party: {rel}"
        assert (SITE / "assets" / rel.lstrip("./")).is_file(), f"missing vendored font: {rel}"
    assert (SITE / "assets" / "fonts" / "IBM-Plex.LICENSE").is_file(), (
        "the OFL requires the licence to travel with the font files"
    )


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
    refs |= {m for m in re.findall(r'fetch\("(\.{1,2}/[^"]+)"', html)}
    assert len(refs) >= 4, f"only {len(refs)} local references found in {page}"
    missing = sorted(r for r in refs if not (SITE / r).exists())
    assert not missing, f"site/{page} points at files that do not exist: {missing}"


def test_stylesheet_url_references_resolve():
    css = stylesheet()
    urls = {u for u in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", css)
            if not u.startswith(("data:", "http"))}
    assert urls, "no url() references found in the stylesheet — the scan is broken"
    missing = sorted(u for u in urls if not (SITE / "assets" / u.lstrip("./")).is_file())
    assert not missing, f"assets/zana.css points at files that do not exist: {missing}"


def test_no_build_step_is_required():
    """Anything needing compilation in this repo cannot be collected from it."""
    unexpected = sorted(
        p.name for p in SITE.iterdir()
        if p.name in {"package.json", "vite.config.js", "webpack.config.js", "Makefile"}
    )
    assert not unexpected, f"site/ acquired a build step: {unexpected}"


# ── The renders are of real meshes ──────────────────────────────────────────


def test_every_render_comes_from_a_tracked_mesh():
    """site/gen_renders.py's manifest must describe meshes that actually exist.

    The landing's whole claim about itself is that the parts pictured are the
    parts in the repo. A render left behind after its source mesh was deleted
    or renamed would quietly turn the page into an illustration of something
    that is no longer here.
    """
    manifest = json.loads((SITE / "assets" / "renders" / "parts.json").read_text(encoding="utf-8"))
    assert len(manifest) >= 6, f"only {len(manifest)} renders in the manifest"
    for part in manifest:
        assert (REPO / part["source"]).is_file(), (
            f"{part['slug']} was rendered from {part['source']}, which no longer exists"
        )
        assert (SITE / part["file"].lstrip("./")).is_file(), f"missing render: {part['file']}"
        assert part["triangles"] > 0 and all(d > 0 for d in part["size_mm"])


def test_landing_quotes_no_dimension_the_mesh_does_not_have():
    """Every "A × B × C mm" and facet count on the page must match the manifest.

    Hand-typed specs beside a generated render are the classic way a hardware
    page starts lying: the mesh gets revised, the caption does not. Re-running
    site/gen_renders.py updates the manifest, and this fails until the page
    agrees with it again.
    """
    html = read("index.html")
    manifest = json.loads((SITE / "assets" / "renders" / "parts.json").read_text(encoding="utf-8"))

    def trim(v: float) -> str:
        return f"{v:g}"

    checked = 0
    problems = []
    for part in manifest:
        if part["file"] not in html:          # not every render has to be shown
            continue
        checked += 1
        dims = " × ".join(trim(d) for d in part["size_mm"])
        # The hero states its dimensions one axis at a time; the cards state
        # them as a triple. Accept either, but demand one of them.
        axes_present = all(f"{trim(d)} mm" in html for d in part["size_mm"])
        if dims not in html and not axes_present:
            problems.append(f"{part['slug']}: page never states {dims} mm")

        facets = f"{part['triangles']:,}".replace(",", " ")
        if facets not in html and str(part["triangles"]) not in html:
            problems.append(f"{part['slug']}: page never states {facets} facets")

    assert checked >= 6, f"only {checked} rendered parts are shown on the landing"
    assert not problems, "the landing disagrees with the meshes:\n  " + "\n  ".join(problems)


# ── Honesty ─────────────────────────────────────────────────────────────────


def test_landing_states_what_is_not_in_the_repo():
    """The repo has no firmware, no BOM and no assembly guide. Say so.

    This is the overstatement a hardware landing page reaches for by default,
    and the one that costs a reader a whole evening.
    """
    html = read("index.html").lower()
    for missing_thing in ("firmware", "bill of materials", "assembly guide"):
        assert missing_thing in html, f"the landing never mentions {missing_thing}"
    assert re.search(r"none in this repo|not yet written", html), (
        "the landing lists those items without saying they are absent"
    )
    assert "prototype" in html, "the landing does not state that this is prototype-stage"


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


def test_landing_says_the_simulator_is_source_only():
    html = read("index.html")
    if re.search(r"simulator", html, re.I):
        window = html[max(0, html.lower().index("simulator") - 600):]
        assert re.search(r"source only|not built|not tested", window[:1400], re.I), (
            "index.html mentions the simulator without stating that it is source only"
        )


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


def test_docs_shell_keeps_the_class_hooks_its_script_drives():
    """The viewer addresses these by class; renaming one silently breaks it."""
    html = read("docs.html")
    for cls in ("docs-shell", "docs-nav", "docs-main", "docs-title", "markdown", "docs-error", "active"):
        assert re.search(rf"[\"'\s.]{re.escape(cls)}[\"'\s{{,)]", html), (
            f"docs.html no longer contains the {cls!r} hook"
        )


# ── Contrast ────────────────────────────────────────────────────────────────


def _srgb(hex_: str) -> tuple[float, float, float]:
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _luminance(hex_: str) -> float:
    def lin(v: float) -> float:
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in _srgb(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _mix(a: str, b: str, pct: float) -> str:
    """`color-mix(in srgb, A pct%, B)` — plain sRGB interpolation."""
    ca, cb = _srgb(a), _srgb(b)
    return "#" + "".join(f"{round((x * pct + y * (1 - pct)) * 255):02x}"
                         for x, y in zip(ca, cb))


MIX_RE = re.compile(
    r"color-mix\(in srgb,\s*var\(--([\w-]+)\)\s*([\d.]+)%,\s*var\(--([\w-]+)\)\s*\)")


def resolve(token: str, block: str) -> str | None:
    """Resolve one role token to a hex, following var() and one color-mix()."""
    m = re.search(rf"--{re.escape(token)}:\s*([^;]+);", block)
    if not m:
        return None
    value = m.group(1).strip()
    if value.startswith("#"):
        return value
    if (v := re.fullmatch(r"var\(--([\w-]+)\)", value)):
        return SPEC_COLOURS.get(v.group(1))
    if (mix := MIX_RE.fullmatch(value)):
        a, pct, b = mix.group(1), float(mix.group(2)) / 100, mix.group(3)
        if a in SPEC_COLOURS and b in SPEC_COLOURS:
            return _mix(SPEC_COLOURS[a], SPEC_COLOURS[b], pct)
    return None


def _theme_blocks() -> tuple[str, str]:
    css = stylesheet()
    dark = re.search(r":root\s*\{(.*?)\n\}", css, re.DOTALL)
    light = re.search(r'\[data-theme="light"\]\s*\{(.*?)\n\}', css, re.DOTALL)
    assert dark and light, "could not isolate the two theme blocks"
    return dark.group(1), light.group(1)


def test_every_readable_text_tier_clears_aa():
    """--text-4 and --text-5 carry real copy, so they owe 4.5:1.

    Warm grey is spec'd for "hairlines, muted, disabled" — as type it is only
    4.14:1 on the charcoal cards and 3.04:1 on cream, i.e. under AA for
    anything below 24px. Both themes therefore derive their readable muted
    tiers off it, and this pins that they actually landed above the line
    against the WORST ground each theme puts them on (charcoal in graphite,
    cream in vellum — not the more forgiving near-black and paper).
    """
    dark, light = _theme_blocks()
    problems = []
    for label, block, ground in (
        ("graphite", dark, SPEC_COLOURS["charcoal"]),
        ("vellum", light, SPEC_COLOURS["cream"]),
    ):
        checked = 0
        for tier in ("text-2", "text-3", "text-4", "text-5"):
            value = resolve(tier, block)
            assert value, f"{label}: could not resolve --{tier}"
            checked += 1
            r = contrast(value, ground)
            if r < 4.5:
                problems.append(f"{label} --{tier} {value} on {ground}: {r:.2f}:1")
        assert checked == 4, f"{label}: resolved {checked} tiers, expected 4"

    assert not problems, "text tiers below AA:\n  " + "\n  ".join(problems)


def test_filled_accent_button_label_clears_aa_in_both_themes():
    """The trap the amber→bronze swap sets.

    Amber is a LIGHT fill and takes the near-black label; bronze is a DARK fill
    and must flip to paper. Substituting the accent without re-checking what
    sits on top of it drops the primary button to 3.28:1.
    """
    dark, light = _theme_blocks()
    for label, block in (("graphite", dark), ("vellum", light)):
        accent = resolve("accent", block)
        on_accent = resolve("on-accent", block)
        assert accent and on_accent, f"{label}: --accent/--on-accent unresolved"
        r = contrast(on_accent, accent)
        assert r >= 4.5, (
            f"{label}: the filled accent button is {on_accent} on {accent} = {r:.2f}:1"
        )
