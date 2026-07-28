"""Gates on the repo itself.

Zana is mostly CAD and PCB binaries, so most of it cannot be compiled or run.
What can still be checked is whether the repo tells the truth about itself:
that a file a README points at exists, that a tracked file is not an empty
husk, that a script parses, and that nobody's home directory leaked into a
checked-in export.

Every gate here asserts how much it covered. A gate that iterates over an
empty list must fail, not pass quietly.
"""

import os
import py_compile
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

from conftest import git_tracked_files

REPO = Path(__file__).resolve().parent.parent

# Files whose contents we read as text. Everything else in this repo is a mesh,
# a FreeCAD archive or a PDF.
TEXT_SUFFIXES = {
    ".md", ".py", ".sh", ".html", ".css", ".txt", ".yml", ".yaml", ".json",
    ".xml", ".csv", ".svg", ".ini", ".dxf", ".gbrjob", ".drl", ".gbr",
    ".kicad_pro", ".kicad_sch", ".kicad_pcb", ".kicad_sym", ".kicad_prl",
    ".kicad_dru", ".gcode",
}

# Paths named in prose that deliberately do NOT exist. Each needs a reason:
# documenting a gap is fine, documenting it wrongly is not.
KNOWN_ABSENT = {
    "mowbot.stl": "the mesh both simulator implementations load and neither ships; "
                  "mower/simulator/README.md exists to say so",
    "path/to/raylib": "placeholder in cpp/build_wasm.sh, quoted in the README as a defect",
    "path/to/bullet": "placeholder in cpp/build_wasm.sh, quoted in the README as a defect",
    "mowbot_sim": "the binary cpp/CMakeLists.txt would produce; nothing builds it",
    "requirements-dev.txt": "referenced from site/docs, which is copied to a static host "
                            "where the repo root is not served",
}

PATHLIKE = re.compile(r"^[\w][\w./*-]*\.(?:FCStd|stl|3mf|step|dxf|svg|png|py|sh|md|txt|yml|html|css|"
                      r"kicad_pro|kicad_sch|kicad_pcb|kicad_sym|kicad_prl)$")


def _text_files(tracked):
    files = [p for p in tracked if p.suffix in TEXT_SUFFIXES and p.is_file()]
    assert len(files) >= 40, f"only {len(files)} text files found — the scan is not covering the repo"
    return files


# ── Emptiness ───────────────────────────────────────────────────────────────


def test_no_tracked_file_is_empty(tracked):
    """A zero-byte tracked file is a claim the repo cannot back up.

    This repo shipped 30 of them: eight husks shadowing the real simulator
    sources in cpp/ and python/, 21 plot outputs, and two empty scripts —
    all while the README described them as working software.
    """
    empty = [p.relative_to(REPO) for p in tracked if p.is_file() and p.stat().st_size == 0]
    assert len(tracked) >= 230, f"only {len(tracked)} files checked for emptiness"
    assert not empty, "zero-byte tracked files:\n  " + "\n  ".join(str(p) for p in empty)


def test_no_tracked_file_is_also_gitignored():
    """Tracked-but-ignored files mean the ignore rules are lying about the repo."""
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-i", "-c", "--exclude-standard"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    assert not out, "tracked files matched by .gitignore:\n  " + "\n  ".join(out)


# ── Links and paths in prose ────────────────────────────────────────────────


MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def test_markdown_relative_links_resolve(tracked):
    """Every relative link in every tracked markdown file points at something."""
    mds = [p for p in tracked if p.suffix == ".md"]
    assert len(mds) >= 6, f"only {len(mds)} markdown files found"

    checked, broken = 0, []
    for md in mds:
        for target in MD_LINK.findall(md.read_text(encoding="utf-8")):
            if re.match(r"^(https?:|mailto:|#|data:)", target):
                continue
            path, _, _ = target.partition("#")
            if not path:
                continue
            checked += 1
            if not (md.parent / path).exists():
                broken.append(f"{md.relative_to(REPO)} -> {target}")

    # Most cross-references in site/docs/*.md are #slug anchors resolved by
    # docs.html, not file paths; the file-path links live in the READMEs.
    assert checked >= 7, (
        f"only {checked} relative links checked across {len(mds)} markdown files — "
        "this gate is not covering enough to mean anything"
    )
    assert not broken, "broken relative links:\n  " + "\n  ".join(broken)


def test_paths_named_in_code_spans_exist(tracked):
    """`backticked/paths.ext` in docs must resolve, or be a declared known gap.

    A span with a slash is resolved the way a reader would try it: relative to
    the document, then to the repo root, then to mower/. A bare filename has to
    exist somewhere in the repo. Globs are honoured, so `mowbot*.FCStd` counts
    as satisfied by any match.
    """
    mds = [p for p in tracked if p.suffix == ".md"]

    def resolves(md: Path, span: str) -> bool:
        if "/" in span:
            roots = (md.parent, REPO, REPO / "mower")
            return any(
                list(root.glob(span)) if "*" in span else (root / span).exists()
                for root in roots
            )
        return any(REPO.rglob(span))

    checked, missing = 0, []
    for md in mds:
        for span in re.findall(r"`([^`\n]+)`", md.read_text(encoding="utf-8")):
            span = span.strip()
            if span in KNOWN_ABSENT or not PATHLIKE.match(span):
                continue
            checked += 1
            if not resolves(md, span):
                missing.append(f"{md.relative_to(REPO)} names `{span}` — no such file")

    assert checked >= 25, (
        f"only {checked} path-shaped code spans checked — the docs cannot have "
        "shrunk that far; the pattern is probably broken"
    )
    assert not missing, "paths named in docs that do not exist:\n  " + "\n  ".join(missing)


def test_known_absent_paths_are_still_absent():
    """The other half of the gate above: a declared gap that got filled must be re-declared."""
    still_here = []
    for name, reason in KNOWN_ABSENT.items():
        if name == "requirements-dev.txt":
            continue  # declared absent only from site/docs' vantage point
        if list(REPO.rglob(name)):
            still_here.append(f"{name} now exists — drop it from KNOWN_ABSENT ({reason})")
    assert len(KNOWN_ABSENT) == 5, "KNOWN_ABSENT changed size; update the count deliberately"
    assert not still_here, "\n  ".join(still_here)


# ── Scripts and sources ─────────────────────────────────────────────────────


def test_shell_scripts_parse(tracked):
    """`bash -n` every tracked shell script. Cheap, and it fails closed."""
    scripts = [p for p in tracked if p.suffix == ".sh"]
    assert len(scripts) == 3, (
        f"expected 3 shell scripts (two KiKit panel scripts + the WASM build), found "
        f"{len(scripts)}: {[str(p.relative_to(REPO)) for p in scripts]}"
    )
    bad = []
    for s in scripts:
        r = subprocess.run(["bash", "-n", str(s)], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(f"{s.relative_to(REPO)}: {r.stderr.strip()}")
    assert not bad, "shell scripts with syntax errors:\n  " + "\n  ".join(bad)


def test_python_sources_compile(tracked):
    """Every tracked .py compiles — including the simulator prototype CI cannot run."""
    pys = [p for p in tracked if p.suffix == ".py"]
    assert len(pys) >= 8, f"only {len(pys)} python files found: {[p.name for p in pys]}"
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        for p in pys:
            try:
                py_compile.compile(str(p), cfile=os.path.join(tmp, "x.pyc"), doraise=True)
            except py_compile.PyCompileError as exc:
                bad.append(f"{p.relative_to(REPO)}: {exc.msg}")
    assert not bad, "python files that do not compile:\n  " + "\n  ".join(bad)


# ── Leakage ─────────────────────────────────────────────────────────────────


PERSONAL_PATH = re.compile(r"/(?:home|Users)/[A-Za-z][\w.-]*/")


def test_no_personal_absolute_paths_in_tracked_text(tracked):
    """KiCad and slicers happily bake the author's home directory into exports."""
    files = _text_files(tracked)
    hits = []
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for m in PERSONAL_PATH.finditer(text):
            hits.append(f"{p.relative_to(REPO)}: {m.group(0)}")
    assert not hits, "absolute home-directory paths in tracked files:\n  " + "\n  ".join(hits[:20])


def test_no_references_to_the_pre_zana_repo_name(tracked):
    """`botkorp-mono` was where this came from; nothing should still point there."""
    needle = "bot" "korp"  # split so this gate does not match its own source
    stale = []
    for p in _text_files(tracked):
        if p.parent == Path(__file__).parent:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if needle in text:
            stale.append(str(p.relative_to(REPO)))
    assert not stale, "references to the pre-Zana repo remain in:\n  " + "\n  ".join(stale)


def test_the_only_licence_is_the_one_the_readme_claims():
    """If the LICENSE is ever dual-MIT/Apache, the README must say so in the same commit."""
    licence = (REPO / "LICENSE").read_text(encoding="utf-8")
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert licence.lstrip().startswith("MIT License"), (
        "LICENSE is no longer MIT — README.md, site/index.html and "
        "site/docs/overview.md all state MIT and must be updated together"
    )
    assert "[MIT](LICENSE)" in readme
    assert (REPO / "site" / "LICENSE.txt").read_text(encoding="utf-8") == licence, (
        "site/LICENSE.txt has drifted from LICENSE — the site footer would show "
        "terms the repo does not carry"
    )
