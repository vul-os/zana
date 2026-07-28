"""Shared fixtures. Keeps `mower/coil-study` importable without a package."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
COIL_STUDY = REPO / "mower" / "coil-study"

# physics.py lives beside its siblings and imports them by bare name; the
# study predates this repo and is not going to be repackaged for a test.
if str(COIL_STUDY) not in sys.path:
    sys.path.insert(0, str(COIL_STUDY))


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO


def git_tracked_files() -> list[Path]:
    """Every file git tracks, as absolute paths.

    Fails loudly rather than returning an empty list: a gate that iterates
    over nothing is the failure mode this suite exists to prevent.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "ls-files", "-z"],
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:  # pragma: no cover
        raise AssertionError(
            f"cannot enumerate tracked files with git ({exc}); the repo-integrity "
            "gates verified NOTHING. Run the suite inside a git checkout."
        ) from exc

    files = [REPO / p.decode() for p in out.split(b"\0") if p]
    assert len(files) > 100, (
        f"git ls-files returned only {len(files)} paths — that is not this repo. "
        "Refusing to report a pass over an empty or partial file set."
    )
    return files


@pytest.fixture(scope="session")
def tracked() -> list[Path]:
    return git_tracked_files()
