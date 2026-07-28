#!/usr/bin/env python3
"""Render the real meshes in mower/ to technical illustrations for the site.

Every part shown on Zana's landing page is drawn from the mesh actually tracked
in this repo — the same `.stl` you would slice — not from stock art or a
marketing render. The dimensions printed beside each one are its real bounding
box in millimetres, measured here at render time, so a part that changes shape
cannot keep an out-of-date caption.

Method: axonometric orthographic projection, back-face culling, and a real
z-buffer rasteriser with flat shading from a fixed light. The obvious cheaper
approach — painter's algorithm through a matplotlib PolyCollection — was tried
first and rejected twice over: it mis-sorts interpenetrating facets on the
31k-triangle shell, and the hairline stroke each polygon needs to avoid seams
bleeds over its neighbours, printing the fan triangulation across every flat
face as visible streaks. A z-buffer has neither problem and needs nothing but
numpy. Output is RGBA with a transparent background, so one render works on
both the graphite and the vellum theme.

    python3 site/gen_renders.py          # → site/assets/renders/*.webp + parts.json

Needs `cwebp` on PATH for the final encode; without it the PNGs are left in
place and the script says so.
"""

from __future__ import annotations

import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "site" / "assets" / "renders"

# The parts worth showing, in the order the landing walks through them.
# (mesh, slug, label, what it is)
PARTS = [
    ("mower/mowbot4-Body.stl", "body", "Chassis body", "Iteration 4 — the shell the drivetrain and boards mount into"),
    ("mower/mowbot4-Plate.stl", "plate", "Base plate", "Deck the motors, castor and coil receiver bolt to"),
    ("mower/mowbot4-Wheel.stl", "wheel", "Drive wheel", "Printed hub and tread; cast from mowbot4-WheelMold"),
    ("mower/mowbot4-MainMotorSupport.stl", "motor-mount", "Motor support", "Bracket for the main drive gearmotor"),
    ("mower/castor_fitting-Body.stl", "castor", "Castor fitting", "Front swivel mount"),
    ("mower/alimunum_coupler-Body.stl", "coupler", "Coupler", "Shaft coupler — printed and aluminium variants"),
    ("mower/mowbot4-WheelMold.stl", "wheel-mold", "Wheel mould", "Two-part mould for casting the tyre"),
    ("mower/mowbot3-Body.stl", "body-3", "Chassis, iteration 3", "The previous shell — kept, because the design history is the documentation"),
]

# Light direction (in view space) and the shading ramp.
#
# The highlight is marigold amber #f2a72c straight off the brand spec, so a lit
# face on a part is the same colour as the accent beside it; the shadowed faces
# fall back to warm grey #8a8378, the spec's muted. A neutral-grey render on a
# warm page reads as a placeholder, and an invented orange would put a tenth
# colour into a nine-colour palette.
LIGHT = np.array([-0.35, 0.45, 0.82])
LIGHT /= np.linalg.norm(LIGHT)
BASE = np.array([0x8a, 0x83, 0x78]) / 255.0   # warm grey — spec, muted
WARM = np.array([0xf2, 0xa7, 0x2c]) / 255.0   # marigold amber — spec, accent
AMBIENT = 0.30

# Axonometric view: yaw about Z, then pitch down. 35.264° is the true isometric
# pitch; a little shallower reads better for wide, flat parts like the deck.
YAW = np.deg2rad(-32.0)
PITCH = np.deg2rad(28.0)


def load_stl(path: Path) -> np.ndarray:
    """Return an (n, 3, 3) array of triangle vertices from a binary or ASCII STL."""
    data = path.read_bytes()
    if len(data) > 84:
        n = struct.unpack("<I", data[80:84])[0]
        if len(data) == 84 + n * 50:
            # Binary: 50 bytes per facet — normal (3f), 3 vertices (9f), attr (H).
            rec = np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")])
            tris = np.frombuffer(data, dtype=rec, count=n, offset=84)
            return tris["v"].reshape(n, 3, 3).astype(np.float64)

    text = data.decode("utf-8", "replace")
    verts = [
        [float(x) for x in line.split()[1:4]]
        for line in text.splitlines()
        if line.strip().startswith("vertex")
    ]
    if len(verts) < 3:
        raise ValueError(f"{path.name}: no triangles found")
    return np.asarray(verts, dtype=np.float64).reshape(-1, 3, 3)


def view_matrix() -> np.ndarray:
    cy, sy = np.cos(YAW), np.sin(YAW)
    cp, sp = np.cos(PITCH), np.sin(PITCH)
    rz = np.array([[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, cp, -sp], [0.0, sp, cp]])
    return rx @ rz


def render(tris: np.ndarray, out_png: Path, px: int = 1100, ss: int = 2) -> None:
    """Project, cull, z-buffer and flat-shade one mesh onto a transparent PNG.

    `ss` is a supersampling factor: rasterising at ss× and box-filtering down is
    what gives the silhouette a clean edge, since a z-buffer is otherwise hard
    aliased.
    """
    # Centre on the model's own bounding box, so the part sits in frame whatever
    # coordinate system FreeCAD exported it in.
    lo, hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
    tris = tris - (lo + hi) / 2.0

    view = tris @ view_matrix().T
    normals = np.cross(view[:, 1] - view[:, 0], view[:, 2] - view[:, 0])
    lengths = np.linalg.norm(normals, axis=1)

    # Degenerate facets carry no normal and would divide by zero. FreeCAD
    # exports produce a handful of them on filleted surfaces.
    keep = lengths > 1e-12
    view, normals, lengths = view[keep], normals[keep], lengths[keep]
    normals = normals / lengths[:, None]

    # Back-face cull: +Z is toward the viewer after the view rotation.
    front = normals[:, 2] > 0
    view, normals = view[front], normals[front]
    if len(view) == 0:
        raise ValueError("every facet was culled — the view direction is wrong")

    lam = np.clip(normals @ LIGHT, 0.0, 1.0)
    shade = AMBIENT + (1.0 - AMBIENT) * lam ** 0.8
    colours = BASE[None, :] * shade[:, None]
    # Warm only the faces most square to the light, and only part of the way:
    # amber is the accent, so it should catch a rim and a top face, not become
    # the body colour of the part. A high exponent keeps the falloff tight.
    colours += (WARM - BASE)[None, :] * (lam[:, None] ** 3.4) * 0.44
    colours = np.clip(colours, 0.0, 1.0)

    # ── screen mapping ──────────────────────────────────────────────────
    n = px * ss
    xy = view[:, :, :2].reshape(-1, 2)
    mid = (xy.min(axis=0) + xy.max(axis=0)) / 2
    extent = float(np.max(np.ptp(xy, axis=0))) * 1.06 or 1.0
    scale = n / extent
    sx = (view[:, :, 0] - mid[0]) * scale + n / 2
    sy = n / 2 - (view[:, :, 1] - mid[1]) * scale   # screen y grows downward
    sz = view[:, :, 2]

    zbuf = np.full((n, n), -np.inf, dtype=np.float64)
    rgb = np.zeros((n, n, 3), dtype=np.float32)
    hit = np.zeros((n, n), dtype=bool)

    x0 = np.clip(np.floor(sx.min(axis=1)).astype(int), 0, n - 1)
    x1 = np.clip(np.ceil(sx.max(axis=1)).astype(int) + 1, 0, n)
    y0 = np.clip(np.floor(sy.min(axis=1)).astype(int), 0, n - 1)
    y1 = np.clip(np.ceil(sy.max(axis=1)).astype(int) + 1, 0, n)

    ax_, ay_ = sx[:, 0], sy[:, 0]
    bx_, by_ = sx[:, 1], sy[:, 1]
    cx_, cy_ = sx[:, 2], sy[:, 2]
    area = (bx_ - ax_) * (cy_ - ay_) - (cx_ - ax_) * (by_ - ay_)

    for i in range(len(view)):
        if x1[i] <= x0[i] or y1[i] <= y0[i] or area[i] == 0.0:
            continue
        ys, xs = np.mgrid[y0[i]:y1[i], x0[i]:x1[i]]
        px_ = xs + 0.5
        py_ = ys + 0.5
        # Barycentric coordinates; the sign of `area` handles either winding.
        w0 = ((bx_[i] - ax_[i]) * (py_ - ay_[i]) - (px_ - ax_[i]) * (by_[i] - ay_[i])) / area[i]
        w1 = ((px_ - ax_[i]) * (cy_[i] - ay_[i]) - (cx_[i] - ax_[i]) * (py_ - ay_[i])) / area[i]
        inside = (w0 >= 0) & (w1 >= 0) & (w0 + w1 <= 1)
        if not inside.any():
            continue
        z = sz[i, 0] + w1 * (sz[i, 1] - sz[i, 0]) + w0 * (sz[i, 2] - sz[i, 0])
        sub = zbuf[y0[i]:y1[i], x0[i]:x1[i]]
        win = inside & (z > sub)
        if not win.any():
            continue
        sub[win] = z[win]
        rgb[y0[i]:y1[i], x0[i]:x1[i]][win] = colours[i]
        hit[y0[i]:y1[i], x0[i]:x1[i]][win] = True

    # ── downsample (box filter) to the output resolution ────────────────
    a = hit.astype(np.float32).reshape(px, ss, px, ss).mean(axis=(1, 3))
    c = rgb.reshape(px, ss, px, ss, 3).sum(axis=(1, 3))
    cover = (a * ss * ss)[:, :, None]
    with np.errstate(invalid="ignore", divide="ignore"):
        c = np.where(cover > 0, c / np.maximum(cover, 1e-6), 0.0)

    out = np.dstack([np.clip(c, 0, 1), a[:, :, None]])
    plt.imsave(out_png, out)


def to_webp(png: Path) -> Path | None:
    if not shutil.which("cwebp"):
        return None
    webp = png.with_suffix(".webp")
    subprocess.run(
        ["cwebp", "-q", "88", "-alpha_q", "100", "-quiet", str(png), "-o", str(webp)],
        check=True,
    )
    png.unlink()
    return webp


import re  # noqa: E402

# The RAIN board's copper plot, exported from KiCad as an A4 sheet of black
# strokes on a white rectangle. The artwork itself — an interdigitated comb
# electrode — is the most honestly "electronics" thing in the repo, but it is a
# 40 mm drawing adrift on a 210 mm page, in a colour that only works on white.
RAIN_SVG = "mower/PCB/RAIN/output.svg"
PATH_RE = re.compile(r'<path[^>]*\sd="([^"]+)"[^>]*/?>')
XFORM_RE = re.compile(r'transform="matrix\(([-\d.eE]+),[-\d.eE]+,[-\d.eE]+,([-\d.eE]+),'
                      r'([-\d.eE]+),([-\d.eE]+)\)"')
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def rain_electrode(src: Path, dest: Path) -> dict | None:
    """Re-cut the KiCad plot as a tight, theme-coloured SVG.

    Drops the white page rectangle, applies each path's own matrix so the
    output has no transforms left to reason about, crops the viewBox to the
    artwork, and swaps the hard-coded black for `currentColor` so the same file
    reads on graphite and on vellum.
    """
    if not src.is_file():
        return None
    text = src.read_text(encoding="utf-8", errors="replace")

    paths, lo, hi = [], [1e18, 1e18], [-1e18, -1e18]
    for m in PATH_RE.finditer(text):
        tag, d = m.group(0), m.group(1)
        sx, sy, tx, ty = 1.0, 1.0, 0.0, 0.0
        if (t := XFORM_RE.search(tag)):
            sx, sy, tx, ty = (float(g) for g in t.groups())

        # Rewrite the coordinate pairs in place: these plots are straight
        # M/L polylines, so pairwise substitution is exact.
        nums = [float(v) for v in NUM_RE.findall(d)]
        if len(nums) < 4 or len(nums) % 2:
            continue
        pts = []
        for i in range(0, len(nums), 2):
            x, y = nums[i] * sx + tx, nums[i + 1] * sy + ty
            pts.append((x, y))
            lo[0], lo[1] = min(lo[0], x), min(lo[1], y)
            hi[0], hi[1] = max(hi[0], x), max(hi[1], y)

        width = 1.0
        if (w := re.search(r"stroke-width:([\d.]+)", tag)):
            width = float(w.group(1)) * abs(sx)
        cmds = re.findall(r"[MLZmlz]", d)
        seq = "".join(
            f"{c}{pts[i][0]:.3f},{pts[i][1]:.3f}" if c.upper() in "ML" else c
            for i, c in enumerate(cmds[: len(pts)])
        )
        paths.append((seq or "M" + "L".join(f"{x:.3f},{y:.3f}" for x, y in pts), width))

    if not paths:
        return None

    pad = 1.5
    x, y = lo[0] - pad, lo[1] - pad
    w, h = (hi[0] - lo[0]) + 2 * pad, (hi[1] - lo[1]) + 2 * pad
    body = "".join(
        f'<path d="{d}" stroke-width="{lw:.2f}"/>' for d, lw in paths
    )
    dest.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.2f} {y:.2f} {w:.2f} {h:.2f}" '
        f'fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
        f'role="img" aria-label="Interdigitated comb electrode from the RAIN sensor board">'
        f"{body}</svg>\n",
        encoding="utf-8",
    )
    return {"paths": len(paths), "size": [round(w, 1), round(h, 1)]}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    encoded = True

    for rel, slug, label, blurb in PARTS:
        path = REPO / rel
        if not path.is_file():
            print(f"missing mesh, skipping: {rel}", file=sys.stderr)
            continue

        tris = load_stl(path)
        lo, hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
        size = hi - lo

        png = OUT / f"{slug}.png"
        render(tris, png)
        out = to_webp(png)
        if out is None:
            out, encoded = png, False

        manifest.append({
            "slug": slug,
            "label": label,
            "blurb": blurb,
            "source": rel,
            "triangles": int(len(tris)),
            # Millimetres: FreeCAD exports STL in mm, and every part in this
            # repo was modelled that way.
            "size_mm": [round(float(v), 1) for v in size],
            "file": f"./assets/renders/{out.name}",
        })
        print(f"{slug:12s} {len(tris):7d} tris  {size[0]:6.1f} × {size[1]:6.1f} × {size[2]:6.1f} mm  → {out.name}")

    rain = rain_electrode(REPO / RAIN_SVG, OUT / "rain-electrode.svg")
    if rain:
        print(f"{'rain':12s} {rain['paths']:7d} paths {rain['size'][0]:6.1f} × {rain['size'][1]:6.1f} pt  "
              f"→ rain-electrode.svg")
    else:
        print(f"could not re-cut {RAIN_SVG}", file=sys.stderr)

    (OUT / "parts.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {len(manifest)} renders + parts.json to {OUT.relative_to(REPO)}")
    if not encoded:
        print("cwebp not on PATH — PNGs kept. Install it (brew install webp) and re-run;\n"
              "site/index.html references .webp.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
