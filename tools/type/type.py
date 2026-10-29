# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#   "numpy>=1.26",
#   "scipy>=1.11",
#   "opencv-python-headless>=4.9",
#   "pillow>=10",
#   "scikit-image>=0.22",
#   "ufoLib2>=0.16",
#   "ufo2ft>=3.3",
# ]
# ///
"""Tools for building the Pugin fonts from the flattened plates (decision 0008).

The plates are references, not sources. These tools cut each letter out of a flattened, evened
plate, separate its ink from the paper, measure the alphabet, and find the shapes that repeat, so
the glyphs can be rebuilt from clean construction and checked against Pugin's drawing. The
construction kit is construct.py (primitives, parts, the joint fit, checks, the font source); the
letters' constructions are letters.py; the curve geometry, including fitting with nodes at extremes,
is geom.py.

Usage (from the repository root; uv installs the dependencies):
  uv run tools/type/type.py extract pugin-lombardic     # references/: one image and outline per glyph
  uv run tools/type/type.py measure pugin-lombardic     # measurements.json
  uv run tools/type/type.py curls   pugin-lombardic     # primitives/: the curl terminals, averaged
  uv run tools/type/type.py build   pugin-lombardic     # recipes → source/*.ufo and build/*.otf (--fresh: from scratch)
  uv run tools/type/type.py space   pugin-lombardic     # respace and rekern the built letters and rewrite the font
  uv run tools/type/type.py proof   pugin-lombardic     # proof/index.html
  uv run tools/type/type.py serve   pugin-lombardic     # the proof page with its editor, at localhost:8766
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from skimage import measure

import geom as G

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "fonts"


def family_dir(fam: str) -> Path:
    d = FONTS / fam
    if not (d / "source.json").exists():
        sys.exit(f"No fonts/{fam}/source.json")
    return d


def load_source(fam: str) -> dict:
    return json.loads((family_dir(fam) / "source.json").read_text())


# ── Ink and paper ─────────────────────────────────────────────────────────────

def ink_coverage(img: np.ndarray, region: tuple[int, int, int, int]):
    """How much ink covers each pixel, per ink.

    Each pixel is treated as a mix of the paper and one pure ink: c = paper·(1−a) + ink·a. The coverage
    a comes from projecting the pixel onto the paper→ink line; the pixel is assigned to the ink whose
    line it lies closest to. Edges come out as fractional coverage, which is what lets outlines be
    found to a fraction of a pixel."""
    x0, y0, x1, y1 = region
    f = img[y0:y1, x0:x1].astype(np.float32)
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    sat = f.max(2) - f.min(2)
    lum = f.mean(2)
    paper = np.median(f[(sat < np.percentile(sat, 40)) & (lum > np.percentile(lum, 50))], axis=0)
    inks = {}
    # each ink's pure color: the most saturated of its own pixels (blue is darker and less saturated
    # than red, so it is judged against itself); black only if there is truly dark, neutral ink
    for name, sel in (("red", r > b + 40), ("blue", b > r + 20)):
        if sel.sum() > 2000:
            s = sat[sel]
            inks[name] = np.median(f[sel][s > np.percentile(s, 80)], axis=0)
    dark = (lum < 80) & (sat < 30)
    if dark.sum() > 2000:
        inks["black"] = np.median(f[dark], axis=0)
    cov, resid = {}, {}
    d = paper - f
    for name, ink in inks.items():
        axis = paper - ink
        a = (d @ axis) / float(axis @ axis)
        cov[name] = np.clip(a, 0, 1)
        resid[name] = np.linalg.norm(d - a[..., None] * axis, axis=2)
    names = list(cov)
    best = np.argmin(np.stack([resid[n] for n in names]), 0)
    for i, n in enumerate(names):
        cov[n] = np.where(best == i, cov[n], 0).astype(np.float32)
    return cov, paper, inks


# ── Extraction ────────────────────────────────────────────────────────────────

def row_bands(total: np.ndarray, n_min_rows: int):
    prof = (total > 0.5).mean(1)
    bands, i = [], 0
    while i < len(prof):
        if prof[i] > 0.01:
            j = i
            while j < len(prof) and prof[j:j + 15].max() > 0.01:
                j += 1
            if j - i > 60:
                bands.append((i, j))
            i = j
        else:
            i += 1
    return bands


def glyph_groups(cov: dict, y0: int, y1: int, min_area=30, small=2500, gap_small=45, gap=6):
    """Letters in one row: connected pieces of one ink, joined when they overlap across the row.
    Small pieces (dots, trefoils) may join across a wider gap, so a cluster of dots stays one glyph."""
    pieces = []
    for ink, a in cov.items():
        m = (a[y0:y1] > 0.5).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        for k in range(1, n):
            x, y, w, h, area = (int(v) for v in st[k])
            if area >= min_area:
                pieces.append({"ink": ink, "x0": x, "x1": x + w, "y0": y + y0, "y1": y + h + y0, "area": int(area),
                               "mask": (lab[y:y + h, x:x + w] == k), "ox": x, "oy": y + y0})
    pieces.sort(key=lambda p: p["x0"])
    groups = []
    for p in pieces:
        for g in groups:
            if g["ink"] != p["ink"]:
                continue
            tol = gap_small if (p["area"] < small or g["area"] < small) else gap
            if p["x0"] <= g["x1"] + tol and p["x1"] >= g["x0"] - tol:
                g["pieces"].append(p)
                g["x0"], g["x1"] = min(g["x0"], p["x0"]), max(g["x1"], p["x1"])
                g["y0"], g["y1"] = min(g["y0"], p["y0"]), max(g["y1"], p["y1"])
                g["area"] += p["area"]
                break
        else:
            groups.append({"ink": p["ink"], "x0": p["x0"], "x1": p["x1"], "y0": p["y0"], "y1": p["y1"], "area": p["area"], "pieces": [p]})
    groups = [g for g in groups if g["area"] > 400]
    groups.sort(key=lambda g: g["x0"])
    return groups


def contour_svg(alpha: np.ndarray, level=0.5) -> list[list[tuple[float, float]]]:
    return [[(float(x), float(y)) for y, x in c] for c in measure.find_contours(alpha, level) if len(c) > 8]


def cmd_extract(fam: str):
    d = family_dir(fam)
    src = load_source(fam)
    img = cv2.imread(str(ROOT / src["image"]))
    if img is None:
        sys.exit(f"Missing {src['image']}: run `uv run tools/flatten/flatten.py render {src['plate'][:2]}` first.")
    prm = json.loads((ROOT / src["params"]).read_text())
    fr, pg = prm["frame"], prm["page"]
    region = (int(fr["u0"] - pg["u0"]) + 20, int(fr["y0"] - pg["y0"]) + 20, int(fr["u1"] - pg["u0"]) - 20, int(fr["y1"] - pg["y0"]) - 20)
    cov, paper, inks = ink_coverage(img, region)
    total = sum(cov.values())
    bands = row_bands(total, len(src["rows"]))
    if len(bands) < len(src["rows"]):
        sys.exit(f"Found {len(bands)} rows of ink, expected {len(src['rows'])}")
    out = d / "references"
    out.mkdir(parents=True, exist_ok=True)
    refs = {}
    x0r, y0r = region[:2]
    for ri, labels in enumerate(src["rows"]):
        a, b = bands[ri]
        groups = glyph_groups(cov, max(0, a - 30), min(total.shape[0], b + 30))
        if len(groups) != len(labels):
            print(f"  row {ri + 1}: found {len(groups)} glyphs, expected {len(labels)}:",
                  [(g['ink'], g['x0'], g['x1'], g['area']) for g in groups])
            sys.exit(1)
        heights = [g["y1"] - g["y0"] for g in groups]
        for label, g in zip(labels, groups):
            pad = 24
            gx0, gy0 = max(0, g["x0"] - pad), max(0, g["y0"] - pad)
            gx1, gy1 = min(total.shape[1], g["x1"] + pad), min(total.shape[0], g["y1"] + pad)
            # this glyph's own ink only, within a few pixels of its pieces (keeps neighbours' edges out)
            own = np.zeros((gy1 - gy0, gx1 - gx0), np.uint8)
            for p in g["pieces"]:
                h, w = p["mask"].shape
                own[p["oy"] - gy0:p["oy"] - gy0 + h, p["ox"] - gx0:p["ox"] - gx0 + w] |= p["mask"].astype(np.uint8)
            own = cv2.dilate(own, np.ones((7, 7), np.uint8))
            alpha = cov[g["ink"]][gy0:gy1, gx0:gx1] * own
            name = label.replace(".", "_")
            # ink coverage, 0–255: the reference itself (the ink's color is recorded once, below)
            cv2.imwrite(str(out / f"{name}.png"), np.clip(alpha * 255 + 0.5, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 9])
            contours = [measure.approximate_polygon(np.array(c), 0.12) for c in contour_svg(alpha)]
            H, W = alpha.shape
            paths = " ".join("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in c) + " Z" for c in contours)
            (out / f"{name}.svg").write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
                f'<path d="{paths}" fill="#000" fill-rule="evenodd"/></svg>\n')
            refs[label] = {
                "coverage": f"references/{name}.png", "outline": f"references/{name}.svg", "ink": g["ink"], "row": ri + 1,
                "box_flat_px": [x0r + gx0, y0r + gy0, x0r + gx1, y0r + gy1],
                "ink_box_flat_px": [x0r + g["x0"], y0r + g["y0"], x0r + g["x1"], y0r + g["y1"]],
                "ink_box_page": [round(pg["u0"] + x0r + g["x0"], 1), round(pg["y0"] + y0r + g["y0"], 1),
                                 round(pg["u0"] + x0r + g["x1"], 1), round(pg["y0"] + y0r + g["y1"], 1)],
                "width_px": int(g["x1"] - g["x0"]), "height_px": int(g["y1"] - g["y0"]),
                "ink_area_px": round(float(alpha.sum()), 1), "contours": len(contours),
            }
        print(f"  row {ri + 1}: " + ", ".join(f"{l} ({g['ink']}, {g['x1'] - g['x0']}×{g['y1'] - g['y0']})" for l, g in zip(labels, groups)))
    meta = {"family": src["family"], "plate": src["plate"], "image": src["image"],
            "paper_bgr": [round(float(v), 1) for v in paper],
            "inks_bgr": {k: [round(float(x), 1) for x in v] for k, v in inks.items()},
            "when": time.strftime("%Y-%m-%dT%H:%M:%S"), "glyphs": refs}
    (out / "references.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"  {len(refs)} glyphs → {out.relative_to(ROOT)}  (paper {meta['paper_bgr']}, inks {meta['inks_bgr']})")


# ── Clean curves ──────────────────────────────────────────────────────────────

def fit_outline(alpha: np.ndarray, tol_px=0.35) -> dict:
    """The coverage map's 0.5 contour fitted with cubic Béziers to within tol_px, with nodes at the
    curve's extremes and true corners (geom.fit_with_extrema)."""
    contours, errs = [], []
    for pts in G.contours_from_coverage(alpha):
        segs, _ = G.fit_with_extrema(pts, tol=tol_px)
        contours.append(segs)
        errs.append(G.fit_error(segs, pts))
    errs = np.concatenate(errs) if errs else np.zeros(1)
    H, W = alpha.shape
    d = G.svg_path(contours)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><path d="{d}" fill="#000" fill-rule="evenodd"/></svg>\n'
    n = sum(len(s) for s in contours)
    return {"svg": svg, "path": d, "segments": n, "nodes": n,
            "max_error_px": round(float(errs.max()), 3), "mean_error_px": round(float(errs.mean()), 3)}


# ── Primitive mining: find every instance of a repeated shape and average them ──

ORIENTS = {"bottom-left": (False, False), "bottom-right": (True, False), "top-left": (False, True), "top-right": (True, True)}


def _orient(img: np.ndarray, flip_x: bool, flip_y: bool) -> np.ndarray:
    if flip_x:
        img = img[:, ::-1]
    if flip_y:
        img = img[::-1, :]
    return np.ascontiguousarray(img)


def _warp(img, angle, scale, center, size):
    M = cv2.getRotationMatrix2D(center, angle, scale)
    return cv2.warpAffine(img, M, size, flags=cv2.INTER_CUBIC, borderValue=0)


def mine(fam: str, prim: str, thr=0.7, nms=30):
    """Search every glyph for the primitive in four orientations, a few rotations and sizes; then bring
    each instance back to the template's orientation, refine its alignment, and average."""
    d = family_dir(fam)
    src = load_source(fam)
    meta = json.loads((d / "references" / "references.json").read_text())
    spec = src["primitives"][prim]["template"]
    cov = {n: cv2.imread(str(d / g["coverage"]), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255 for n, g in meta["glyphs"].items()}
    x0, y0, x1, y1 = spec["box"]
    T = cov[spec["glyph"]][y0:y1, x0:x1]
    fx0, fy0 = ORIENTS[spec["orientation"]]
    T = _orient(T, fx0, fy0)  # canonical: bottom-left
    ys, xs = np.nonzero(T > 0.05)  # trim to the ink, so every centre below refers to the same box
    T = T[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    th, tw = T.shape
    hits = []
    for name, A in cov.items():
        if name.startswith("ornament"):
            continue
        P = np.pad(A, 60)
        cands = []
        for oname, (fx, fy) in ORIENTS.items():
            for scale in (0.85, 1.0, 1.15):
                for ang in (-36, -24, -12, 0, 12, 24, 36):
                    big = np.pad(T, 30)
                    Tw = _warp(big, ang, scale, (big.shape[1] / 2, big.shape[0] / 2), (big.shape[1], big.shape[0]))
                    Tw = _orient(Tw, fx, fy)
                    ys, xs = np.nonzero(Tw > 0.05)
                    Tw = Tw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
                    R = cv2.matchTemplate(P, Tw, cv2.TM_CCOEFF_NORMED)
                    while True:
                        _, v, _, (px, py) = cv2.minMaxLoc(R)
                        if v < thr:
                            break
                        cands.append((float(v), px + Tw.shape[1] / 2 - 60, py + Tw.shape[0] / 2 - 60, oname, scale, ang))
                        R[max(0, py - nms):py + nms, max(0, px - nms):px + nms] = -1
        cands.sort(reverse=True)
        kept = []
        for c in cands:
            if all(math.hypot(c[1] - k[1], c[2] - k[2]) > nms for k in kept):
                kept.append(c)
        for v, cx, cy, oname, scale, ang in kept:
            hits.append({"glyph": name, "x": round(cx, 1), "y": round(cy, 1), "orientation": oname, "scale": scale, "angle": ang, "score": round(v, 3)})
    # canonicalise each instance: cut it out, undo flips, rotation and size, then refine by ECC
    S = 2 * max(th, tw)
    aligned, kept_hits = [], []
    Tc = np.zeros((S, S), np.float32)
    Tc[(S - th) // 2:(S - th) // 2 + th, (S - tw) // 2:(S - tw) // 2 + tw] = T
    region = cv2.dilate((Tc > 0.02).astype(np.uint8), np.ones((9, 9), np.uint8))  # align on the terminal only
    fails = 0
    for h in hits:
        A = np.pad(cov[h["glyph"]], S)
        cx, cy = h["x"] + S, h["y"] + S
        patch = A[int(cy - S / 2):int(cy - S / 2) + S, int(cx - S / 2):int(cx - S / 2) + S]
        fx, fy = ORIENTS[h["orientation"]]
        patch = _orient(patch, fx, fy)
        # the candidate was flip(rotate(T)), so undo the flip first, then the rotation and size
        patch = _warp(patch, -h["angle"], 1 / h["scale"], (S / 2, S / 2), (S, S))
        warp = np.eye(2, 3, dtype=np.float32)
        try:
            _, warp = cv2.findTransformECC(Tc, patch, warp, cv2.MOTION_AFFINE,
                                           (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), region, 5)
        except cv2.error:
            fails += 1
            continue
        al = cv2.warpAffine(patch, warp, (S, S), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP) * (region > 0)
        m = region > 0
        if np.corrcoef(al[m], Tc[m])[0, 1] < 0.8:
            fails += 1
            continue
        aligned.append(al)
        h["affine"] = [[round(float(v), 4) for v in r] for r in warp]
        kept_hits.append(h)
    if not aligned:
        sys.exit(f"  {prim}: {len(hits)} candidates, none aligned ({fails} failed)")
    # lithographic ink density varies from letter to letter: scale each instance so its solid ink reads 1
    aligned = [np.clip(al / max(np.percentile(al[al > 0.15], 90), 0.3), 0, 1) if (al > 0.15).any() else al for al in aligned]
    stack = np.stack(aligned)
    mean = stack.mean(0)
    for _ in range(2):  # re-register against the average itself, so the template's quirks don't win
        new = []
        for al in aligned:
            warp = np.eye(2, 3, dtype=np.float32)
            try:
                _, warp = cv2.findTransformECC(mean, al, warp, cv2.MOTION_AFFINE,
                                               (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), region, 5)
                new.append(cv2.warpAffine(al, warp, (S, S), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP) * (region > 0))
            except cv2.error:
                new.append(al)
        aligned = new
        mean = np.stack(aligned).mean(0)
    median = np.median(np.stack(aligned), 0)
    dev = [float(np.sqrt(((al - median) ** 2)[median > 0.02].mean())) for al in aligned]
    # drop instances that are not really this primitive (a cut corner, a different terminal), then re-average
    cut = 2.0 * float(np.median(dev))
    keep = [i for i, dv in enumerate(dev) if dv <= cut]
    dropped = [kept_hits[i] for i in range(len(kept_hits)) if i not in keep]
    aligned = [aligned[i] for i in keep]
    kept_hits = [kept_hits[i] for i in keep]
    median = np.median(np.stack(aligned), 0)
    dev = [float(np.sqrt(((al - median) ** 2)[median > 0.02].mean())) for al in aligned]
    for h, dv in zip(kept_hits, dev):
        h["rms_from_consensus"] = round(dv, 4)
    out = d / "primitives"
    out.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out / f"{prim}.consensus.png"), np.clip(median * 255 + 0.5, 0, 255).astype(np.uint8))
    cv2.imwrite(str(out / f"{prim}.template.png"), np.clip(Tc * 255 + 0.5, 0, 255).astype(np.uint8))
    # every instance, aligned, in a strip (for review), and the spread across them
    tiles = [np.clip(al * 255, 0, 255).astype(np.uint8) for al in aligned]
    cols = 12
    rows = [np.hstack(tiles[i:i + cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[i:i + cols]))) for i in range(0, len(tiles), cols)]
    cv2.imwrite(str(out / f"{prim}.instances.png"), 255 - np.vstack(rows))
    spread = np.stack(aligned).std(0)
    cv2.imwrite(str(out / f"{prim}.spread.png"), np.clip(spread / max(spread.max(), 1e-6) * 255, 0, 255).astype(np.uint8))
    contours = [measure.approximate_polygon(np.array(c), 0.1) for c in measure.find_contours(median, 0.5) if len(c) > 8]
    paths = " ".join("M" + " L".join(f"{x:.2f} {y:.2f}" for y, x in c) + " Z" for c in contours)
    (out / f"{prim}.consensus.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}"><path d="{paths}" fill="#000" fill-rule="evenodd"/></svg>\n')
    fitted = fit_outline(median)
    (out / f"{prim}.fitted.svg").write_text(fitted["svg"])
    report = {"primitive": prim, "template": spec, "threshold": thr, "instances": len(kept_hits), "candidates": len(hits),
              "dropped_as_outliers": [{k: h[k] for k in ("glyph", "orientation", "x", "y")} for h in dropped],
              "fitted": {k: fitted[k] for k in ("segments", "nodes", "max_error_px", "mean_error_px")},
              "size_px": S, "by_glyph": {}, "hits": kept_hits, "when": time.strftime("%Y-%m-%dT%H:%M:%S")}
    for h in kept_hits:
        report["by_glyph"][h["glyph"]] = report["by_glyph"].get(h["glyph"], 0) + 1
    (out / f"{prim}.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"  {prim}: {len(kept_hits)} instances in {len(report['by_glyph'])} glyphs (of {len(hits)} candidates, {len(dropped)} dropped "
          f"as outliers); median deviation from the consensus {np.median(dev):.3f} coverage")
    print(f"  fitted outline: {fitted['segments']} Bézier segments, {fitted['nodes']} on-curve points; "
          f"max error {fitted['max_error_px']} px, mean {fitted['mean_error_px']} px from the consensus")
    return report


def cmd_curls(fam: str):
    mine(fam, "curl")


# ── Construction: primitives → recipes → font ─────────────────────────────────

def _saved_measurements(d: Path, recipes: dict) -> dict:
    """Where the last build left off: each letter's measurements from its recipe and the family's
    from family.json, keyed as the fit keys them. Recorded corrections are taken back off, since
    the build applies them again after fitting."""
    import construct as K
    start = {}
    fj = d / "family.json"
    if fj.exists():
        start.update({f"family.{k}": v for k, v in json.loads(fj.read_text())["shared"].items()})
    for g, (_, r) in recipes.items():
        m = {k: v for k, v in r.get("measured", {}).items() if k not in ("units", "family", "from", "when")}
        start.update({f"{g}:{k}": v for k, v in K._flat(m).items()})
        for c in r.get("corrections", []):
            if f"{g}:{c['measure']}" in start:
                start[f"{g}:{c['measure']}"] -= c["add"]
    return start


def _fingerprint(g: str, coverage: Path, curl: dict) -> str:
    """What fitting a letter alone depends on: its construction, the shared parts and the kit, its
    reference, and the curl. When none of these has changed, the last result still stands."""
    import hashlib
    import inspect
    import construct as K
    import letters as LT
    helpers = [f for _, f in inspect.getmembers(LT, inspect.isfunction)
               if f.__module__ == LT.__name__ and f not in LT.LETTERS.values()]
    h = hashlib.sha256()
    for src in [inspect.getsource(LT.LETTERS[g]), *map(inspect.getsource, helpers), inspect.getsource(K), inspect.getsource(G)]:
        h.update(src.encode())
    h.update(coverage.read_bytes())
    h.update(json.dumps({k: v for k, v in curl.items() if k != "when"}, sort_keys=True).encode())
    return h.hexdigest()[:16]


def cmd_build(fam: str, fresh: bool = False):
    """Fit the clean curl to its consensus; fit each recipe's measurements to Pugin's letter; check
    the outlines; write the UFO source and compile it."""
    import construct as K
    d = family_dir(fam)
    src = load_source(fam)
    P = d / "primitives"
    cons = cv2.imread(str(P / "curl.consensus.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    curl = K.fit_curl(cons)
    curl["when"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    (P / "curl.model.json").write_text(json.dumps(curl, indent=1) + "\n")
    segs = [np.array(s) + curl["outer_node_in_consensus_px"] for s in curl["segments"]]
    S = cons.shape[1]
    (P / "curl.model.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}"><path d="{G.svg_path([segs])}" '
                                      f'fill="none" stroke="#000" stroke-width=".5"/>{G.svg_nodes([segs], 1.2)}</svg>\n')
    print(f"  curl model: 4 nodes (outer, back, crown, neck), {curl['fit']['mean_px']} px mean, "
          f"{curl['fit']['max_px']} px worst from the consensus; neck arrival {curl['neck_arrival_deg']}°")
    # the averaged outline, refitted with nodes at extremes
    rep = json.loads((P / "curl.json").read_text())
    fitted = fit_outline(cons)
    (P / "curl.fitted.svg").write_text(fitted["svg"])
    rep["fitted"] = {k: fitted[k] for k in ("segments", "nodes", "max_error_px", "mean_error_px")}
    (P / "curl.json").write_text(json.dumps(rep, indent=1) + "\n")

    import letters as LT
    kit = K.Kit(curl)
    fc = src["font"]
    meas = json.loads((d / "measurements.json").read_text())
    scale = fc["cap_height"] / meas["summary"]["height"]["median_px"]
    refs = json.loads((d / "references" / "references.json").read_text())["glyphs"]
    out = d / "build"
    out.mkdir(exist_ok=True)
    recipes = {}
    for rp in sorted((d / "recipes").glob("*.json")):
        r = json.loads(rp.read_text())
        recipes[r["glyph"]] = (rp, r)
    # Glyphs Pugin drew are fitted to his letters. A glyph he didn't draw (a modern Y) is built from
    # the fitted measurements of the letter it is modelled on (`derived_from`) and is not fitted.
    everything = {g: LT.LETTERS[g] for g in recipes}
    derived = {g: r["derived_from"] for g, (_, r) in recipes.items() if r.get("derived_from")}
    letters = {g: fn for g, fn in everything.items() if g not in derived}
    alphas = {g: cv2.imread(str(d / refs[g]["coverage"]), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255 for g in letters}
    fam_of = lambda v: {k.split("family.")[1]: round(x, 3) for k, x in v.items() if "family." in k}
    # Every fit starts where the last build left off, so letters that haven't changed settle at once.
    # --fresh starts from the constructions' own starting values instead.
    start = {} if fresh else _saved_measurements(d, recipes)
    # each letter alone, with its own stem, curl and trefoil: how far Pugin's letters disagree. A
    # letter whose construction, reference and kit are unchanged keeps its last result; the rest
    # are fitted in parallel.
    t0 = time.time()
    cache_p = out / "alone.json"
    cache = json.loads(cache_p.read_text()) if cache_p.exists() and not fresh else {}
    alone, todo = {}, []
    for g in letters:
        fp = _fingerprint(g, d / refs[g]["coverage"], curl)
        if cache.get(g, {}).get("fingerprint") == fp and "values" in cache[g]:
            alone[g] = cache[g]
        else:
            todo.append((g, fp))
    if todo:
        import os
        from concurrent.futures import ProcessPoolExecutor
        jobs = []
        for g, _ in todo:
            own = {k: v for k, v in start.items() if k.startswith(g + ":")}
            own.update({f"{g}:{k}": v for k, v in start.items() if k.startswith("family.")})
            jobs.append((g, alphas[g], curl, own))
        with ProcessPoolExecutor(max_workers=min(len(jobs), max(1, (os.cpu_count() or 2) - 1))) as ex:
            for (g, fp), res in zip(todo, ex.map(K.alone_fit, jobs)):
                alone[g] = {**res, "fingerprint": fp}
    cache_p.write_text(json.dumps(alone, indent=1) + "\n")
    print(f"  letters alone: {len(todo)} fitted, {len(letters) - len(todo)} unchanged ({time.time() - t0:.0f} s)")
    # The family's measurements settle where Pugin's letters agree: each is the median of what the
    # letters that use it want on their own. Then every letter is fitted again with those held fixed,
    # in parallel, starting from its own fit alone. A letter whose construction and the family's
    # values are unchanged keeps its last result.
    t0 = time.time()
    wants = {}
    for g in letters:
        for k, v in alone[g]["family"].items():
            wants.setdefault(k, []).append(v)
    shared = {k: round(float(np.median(v)), 3) for k, v in sorted(wants.items())}
    fixed = {f"family.{k}": v for k, v in shared.items()}
    ref_p = out / "refined.json"
    ref_cache = json.loads(ref_p.read_text()) if ref_p.exists() and not fresh else {}
    refined, todo2 = {}, []
    for g in letters:
        key = {"fingerprint": alone[g]["fingerprint"], "family": {k: v for k, v in shared.items() if k in alone[g]["family"]}}
        if all(ref_cache.get(g, {}).get(k) == v for k, v in key.items()):
            refined[g] = ref_cache[g]
        else:
            todo2.append((g, key))
    if todo2:
        import os
        from concurrent.futures import ProcessPoolExecutor
        jobs = [(g, alphas[g], curl, alone[g]["values"], {k: v for k, v in fixed.items() if k.split("family.")[1] in alone[g]["family"]})
                for g, _ in todo2]
        with ProcessPoolExecutor(max_workers=min(len(jobs), max(1, (os.cpu_count() or 2) - 1))) as ex:
            for (g, key), res in zip(todo2, ex.map(K.refine_fit, jobs)):
                refined[g] = {**key, **res}
    ref_p.write_text(json.dumps(refined, indent=1) + "\n")
    vals = dict(fixed)
    at_bounds = []
    for g in letters:
        vals.update(refined[g]["values"])
        at_bounds += refined[g]["at_bounds"]
    info = {"method": "family = median of the letters' own fits; each letter refitted with it fixed",
            "refitted": len(todo2), "unchanged": len(letters) - len(todo2)}
    print(f"  together: {len(todo2)} refitted, {len(letters) - len(todo2)} unchanged ({time.time() - t0:.0f} s); shared {shared}")
    for g, (rp, r) in recipes.items():
        for c in r.get("corrections", []):
            vals[f"{g}:{c['measure']}"] += c["add"]
    for g, srcg in derived.items():
        vals.update({f"{g}:{k[len(srcg) + 1:]}": v for k, v in vals.items() if k.startswith(srcg + ":")})
    glyphs = {}
    when = time.strftime("%Y-%m-%dT%H:%M:%S")
    for g, fn in everything.items():
        rp, r = recipes[g]
        built = fn(K.Params(g, vals, fill=g in derived), kit)
        # adjustments made by hand on the proof page, recorded as moves from the construction
        base_px = [[q.tolist() for q, _, _ in c] for c in built["contours"]]
        base_names = [[nm for _, _, nm in c] for c in built["contours"]]
        adj_p = d / "adjustments" / f"{g.replace('.', '_')}.json"
        adj_points = json.loads(adj_p.read_text())["points"] if adj_p.exists() else []
        applied, stale = K.adjust(built, adj_points)
        added = K.add_extremes(built) if applied else []
        dropped = K.drop_redundant(built) if added else []
        dev = K.deviation(built, alphas[g]) if g in alphas else None
        names = [[nm for _, _, nm in c] for c in built["contours"]]
        chk = K.check_outline([[q for q, _, _ in c] for c in built["contours"]], names, swell_tol=0.2)
        units, width, origin = K.to_units(built, scale, fc["sidebearing"])
        chk_u = K.check_outline(units, names, smooth_deg=3.0, swell_tol=0.5)
        mine = {k[len(g) + 1:]: round(v, 3) for k, v in vals.items() if k.startswith(g + ":")}
        uni = int(r["unicode"][2:], 16) if r.get("unicode") else None
        base = recipes.get(r.get("alternate_of", ""), (None, {}))[1]
        char = chr(uni) if uni else chr(int(base["unicode"][2:], 16)) if base.get("unicode") else g
        if dev:
            r["measured"] = {**K._nest(mine), "units": "plate pixels, y down; tensions 0–1; angles in degrees",
                             "family": "shared with the other letters: see family.json", "from": refs[g]["coverage"], "when": when}
            r["fit"] = {"mean_px": dev["overall"]["mean_px"], "p95_px": dev["overall"]["p95_px"], "max_px": dev["overall"]["max_px"],
                        "mean_px_fitted_alone": alone[g]["mean_px"], "wobble_of_pugins_edge_mean_px": dev["wobble_of_pugins_edge"]["mean_px"],
                        "segments": chk_u["segments"], "outline_checks_pass": chk_u["ok"]}
        else:
            r["measured"] = {**K._nest(mine), "units": "plate pixels, y down; tensions 0–1; angles in degrees",
                             "from": f"{derived[g]}'s fitted measurements; the rest are the construction's own", "when": when}
            r["fit"] = {"segments": chk_u["segments"], "outline_checks_pass": chk_u["ok"]}
        rp.write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
        trace = sum(len(G.fit_with_extrema(c, tol=0.5)[0]) for c in K.reference_edges(alphas[g])) if dev else None
        report = {"glyph": g, "char": char, "feature": r.get("feature"), "alternate_of": r.get("alternate_of"),
                  "construction": r["construction"], "description": r["description"],
                  "symmetric": bool(built.get("half") or built.get("halves")),
                  "measured": mine, "family": shared, "alone": alone.get(g), "derived_from": derived.get(g),
                  "at_bounds": [k for k in at_bounds if k.startswith(g + ":") or k.startswith("family.")],
                  "direct_trace_segments": trace, "deviation": dev, "checks_px": chk, "checks_units": chk_u,
                  "contours_px": [[q.tolist() for q, _, _ in c] for c in built["contours"]],
                  "contours_px_base": base_px, "mirrored": K.mirrored_counts(built), "axis_px": built.get("axis"),
                  "adjustments": {"points": adj_points, "applied": applied, "stale": stale, "extremes_added": added, "nodes_moved_to_extremes": dropped},
                  "node_names_base": base_names,
                  "labels": [[l for _, l, _ in c] for c in built["contours"]], "node_names": names,
                  "units": {"scale_per_px": scale, "baseline_px": built["baseline"], "origin_px": origin, "advance": width,
                            "cap_units": float(max(q[:, 1].max() for c in units for q in c)),
                            "outline": [[q.tolist() for q in c] for c in units]}}
        (out / f"{g.replace('.', '_')}.json").write_text(json.dumps(report) + "\n")
        glyphs[g] = {"unicode": uni, "width": width, "contours": units}
        print(f"  {g}: {chk_u['segments']} segments in {chk_u['contours']} contour(s), {len(chk_u['corners'])} corners; "
              f"checks {'pass' if chk_u['ok'] else 'FAIL ' + json.dumps(chk_u)}")
        if adj_points:
            print(f"     adjusted by hand: {applied} point(s)" + (f"; {len(dropped)} node(s) moved to the extremes the moves made"
                  if dropped else "") + (f"; {len(added) - len(dropped)} node(s) added at them" if len(added) > len(dropped) else "") + (f"; {len(stale)} STALE, skipped (the construction has changed): "
                  + ", ".join(e['node'] for e in stale) if stale else ""))
        if dev:
            o = dev["overall"]
            print(f"     Pugin's edge from the construction: mean {o['mean_px']} px (alone {alone[g]['mean_px']}), "
                  f"95% within {o['p95_px']} px, worst {o['max_px']} px")
        else:
            print(f"     built from {derived[g]}'s measurements; Pugin drew no {g}")
    (d / "family.json").write_text(json.dumps({
        "shared": shared, "meaning": {k: v[3] for k, v in K.FAMILY.items()},
        "fitted_alone": {g: a["family"] for g, a in alone.items()},
        "mean_px": {g: {"shared": json.loads((out / f"{g.replace('.', '_')}.json").read_text())["deviation"]["overall"]["mean_px"],
                        "alone": a["mean_px"]} for g, a in alone.items()},
        "at_bounds": at_bounds, "fit": info, "when": when}, indent=1) + "\n")
    write_font(d, src, list(glyphs))


def write_font(d: Path, src: dict, names: list[str]):
    """Space and kern the built glyphs (spacing.py), write the UFO source and compile it. Reads
    each glyph's outline in font units from build/<glyph>.json and records its spacing there. The
    letters are spaced and kerned against each other; other glyphs (the cross, the ornament) take
    the letters' median side bearing and no kerning."""
    import unicodedata

    import construct as K
    import spacing as SP
    import ufo2ft
    fc, sp = src["font"], src["spacing"]
    out = d / "build"
    cap = fc["cap_height"]
    builds, contours, profiles = {}, {}, {}
    for g in names:
        bp = out / f"{g.replace('.', '_')}.json"
        builds[g] = (bp, json.loads(bp.read_text()))
        contours[g] = [[np.array(q, float) for q in c] for c in builds[g][1]["units"]["outline"]]
        profiles[g] = SP.profile(contours[g], (0, cap))
    letters = [g for g in names if unicodedata.category(builds[g][1]["char"][0]).startswith("L")]
    symmetric = {g for g in names if builds[g][1].get("symmetric")}
    lsb, rsb, target, white = SP.fit(profiles, letters, symmetric, sp["mean_side_bearings"], sp["depth"])
    median = float(np.median(list(lsb.values()) + list(rsb.values())))
    glyphs, table, features, spaced = {}, {}, {}, {}
    for g in names:
        bp, b = builds[g]
        u = b["units"]
        moved, width, dx = SP.respace(contours[g], lsb.get(g, median), rsb.get(g, median), g in symmetric)
        pts = np.concatenate([G.sample(c, 40) for c in moved])
        lsb_u, rsb_u = int(round(pts[:, 0].min())), int(round(width - pts[:, 0].max()))
        spaced[g] = (lsb_u, rsb_u)
        u.pop("profile_depth", None)
        u.update({"spaced_outline": [[q.tolist() for q in c] for c in moved], "advance": width, "lsb": lsb_u, "rsb": rsb_u,
                  "spaced_origin_px": u["origin_px"] - dx / u["scale_per_px"]})
        bp.write_text(json.dumps(b) + "\n")
        glyphs[g] = {"unicode": ord(b["char"]) if len(b["char"]) == 1 and not b.get("feature") else None, "width": width, "contours": moved}
        if b.get("feature"):
            features.setdefault(b["feature"], []).append((b["alternate_of"], g))
        table[g] = {"left": lsb_u, "right": rsb_u, "advance": width}
    kerning = SP.kern(white, letters, spaced, target, sp["kern_threshold"], sp["clearance"])
    (d / "spacing.json").write_text(json.dumps({"method": sp, "target_white": round(target, 1), "glyphs": table,
                                                "kerning": {f"{a} {b}": k for (a, b), k in sorted(kerning.items())}},
                                               indent=1, ensure_ascii=False) + "\n")
    glyphs[".notdef"] = {"unicode": None, "width": 500, "contours": K.notdef(500, cap)}
    glyphs["space"] = {"unicode": 0x20, "width": sp["word_space"], "contours": []}
    info = {"familyName": fc["name"], "styleName": "Regular", "unitsPerEm": fc["units_per_em"], "capHeight": cap,
            "ascender": fc["ascender"], "descender": fc["descender"], "versionMajor": 0, "versionMinor": 1,
            "postscriptFontName": fc["postscript_name"],
            "openTypeNameDescription": "Working draft, not for release. A revival of the Lombardic capitals in A. W. N. Pugin's "
                                       "Glossary of Ecclesiastical Ornament (1844), plate 9, rebuilt from measured primitives."}
    ufo = d / "source" / f"{fc['postscript_name']}.ufo"
    ufo.parent.mkdir(exist_ok=True)
    # stylistic sets: each alternate replaces its base letter when its feature is on
    fea = "".join(f"feature {tag} {{\n" + "".join(f"    sub {a} by {b};\n" for a, b in pairs) + f"}} {tag};\n"
                  for tag, pairs in sorted(features.items()))
    font = K.write_ufo(ufo, info, glyphs, fea, kerning)
    otf_path = out / f"{fc['postscript_name']}.otf"
    ufo2ft.compileOTF(font).save(otf_path)
    print("  spacing: " + ", ".join(f"{g} {v['left']}|{v['right']}" for g, v in table.items()))
    big = sorted(kerning.items(), key=lambda kv: kv[1])
    print(f"  kerning: {len(kerning)} pairs; most closed " + ", ".join(f"{a}{b} {k}" for (a, b), k in big[:6])
          + "; most opened " + ", ".join(f"{a}{b} {k}" for (a, b), k in big[::-1][:3]))
    print(f"  wrote {ufo.relative_to(ROOT)} and {otf_path.relative_to(ROOT)} ({otf_path.stat().st_size} bytes)")


def cmd_space(fam: str):
    """Respace the built letters and rewrite the font, without fitting again."""
    d = family_dir(fam)
    reports = [json.loads(p.read_text()) for p in sorted((d / "build").glob("*.json"))]
    write_font(d, load_source(fam), [r["glyph"] for r in reports if "glyph" in r])     # not the fit caches


# ── Measurements ──────────────────────────────────────────────────────────────

def _runs(row: np.ndarray, thr=0.5):
    """Ink runs along a scanline, each with its width by summed coverage (sub-pixel)."""
    on = row > thr
    out, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]:
                j += 1
            a, b = max(0, i - 2), min(len(row), j + 2)
            out.append(float(row[a:b].sum()))
            i = j
        else:
            i += 1
    return out


def cmd_measure(fam: str):
    """Heights of each glyph, and the widths of its strokes across the middle (40–60% of its height).
    Strokes are sorted into hairlines, stems, and bowls by width; the medians are the regularized
    values the construction starts from."""
    d = family_dir(fam)
    meta = json.loads((d / "references" / "references.json").read_text())
    per, allruns = {}, []
    for name, g in meta["glyphs"].items():
        a = cv2.imread(str(d / g["coverage"]), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
        ys, xs = np.nonzero(a > 0.5)
        top, bot = int(ys.min()), int(ys.max())
        H = bot - top
        runs = []
        for fy in np.linspace(0.4, 0.6, 9):
            runs += _runs(a[int(top + fy * H)])
        per[name] = {"height_px": H, "width_px": int(xs.max() - xs.min()), "mid_runs_px": [round(r, 1) for r in runs]}
        if not name.startswith("ornament") and name != "cross":
            allruns += [r for r in runs if r < 140]  # wider runs are bars and diagonals seen along their length
    r = np.array(allruns)
    groups = {"hairline": r[r < 45], "stem": r[(r >= 45) & (r < 86)], "bowl": r[(r >= 86) & (r < 140)]}
    heights = np.array([v["height_px"] for k, v in per.items() if not k.startswith("ornament") and k != "cross"])
    summary = {k: {"median_px": round(float(np.median(v)), 1), "p25_px": round(float(np.percentile(v, 25)), 1),
                   "p75_px": round(float(np.percentile(v, 75)), 1), "n": int(len(v))} for k, v in groups.items()}
    summary["height"] = {"median_px": round(float(np.median(heights)), 1), "p25_px": round(float(np.percentile(heights, 25)), 1),
                         "p75_px": round(float(np.percentile(heights, 75)), 1), "n": int(len(heights))}
    st, h = summary["stem"]["median_px"], summary["height"]["median_px"]
    summary["ratios"] = {"stem_to_height": round(st / h, 4), "bowl_to_stem": round(summary["bowl"]["median_px"] / st, 3),
                         "hairline_to_stem": round(summary["hairline"]["median_px"] / st, 3)}
    out = {"family": meta["family"], "note": "Pixels of the flattened plate (about the photograph's own scale). Heights include the curl terminals.",
           "summary": summary, "glyphs": per, "when": time.strftime("%Y-%m-%dT%H:%M:%S")}
    (d / "measurements.json").write_text(json.dumps(out, indent=1) + "\n")
    for k in ("height", "stem", "bowl", "hairline"):
        v = summary[k]
        print(f"  {k:9s} median {v['median_px']:6.1f} px  (middle half {v['p25_px']}–{v['p75_px']}, n={v['n']})")
    print(f"  ratios: {summary['ratios']}")


# ── Proof page ────────────────────────────────────────────────────────────────

def _png_uri(img: np.ndarray, ext=".png", q=None) -> str:
    import base64
    params = [cv2.IMWRITE_JPEG_QUALITY, q] if ext == ".jpg" and q else []
    ok, buf = cv2.imencode(ext, img, params)
    return f"data:image/{'jpeg' if ext == '.jpg' else 'png'};base64," + base64.b64encode(buf.tobytes()).decode()


def _constructed_html(d: Path, meta: dict) -> tuple[str, str]:
    """The constructed glyphs, each laid over Pugin's letter on the flattened plate: the outline with
    its nodes and handles, the compiled font in place, and where the two differ."""
    import base64
    import html as H
    bdir = d / "build"
    reports = [json.loads(p.read_text()) for p in sorted(bdir.glob("*.json"))] if bdir.exists() else []
    reports = [r for r in reports if "contours_px" in r]
    if not reports:
        return "", ""
    otf = next(bdir.glob("*.otf"), None)
    css = (f"@font-face{{font-family:'Draft';src:url(data:font/otf;base64,{base64.b64encode(otf.read_bytes()).decode()}) format('opentype')}}"
           if otf else "")
    plate_p = ROOT / meta["image"]
    plate = cv2.imread(str(plate_p)) if plate_p.exists() else None
    paper = np.array(meta["paper_bgr"], np.float32)
    inks = {k: np.array(v, np.float32) for k, v in meta["inks_bgr"].items()}
    hexc = lambda bgr: "#%02x%02x%02x" % tuple(int(v) for v in bgr[::-1])
    out = []
    for b in reports:
        name = b["glyph"]
        model = b.get("derived_from")              # a glyph Pugin didn't draw is shown over the letter it is modelled on
        g = meta["glyphs"][model or name]
        a = cv2.imread(str(d / g["coverage"]), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
        Hh, Ww = a.shape
        if plate is not None:
            x0, y0, x1, y1 = g["box_flat_px"]
            crop = plate[y0:y1, x0:x1]
        else:
            crop = (paper * (1 - a[..., None]) + inks[g["ink"]] * a[..., None]).astype(np.uint8)
        contours = [[np.array(q) for q in c] for c in b["contours_px"]]
        segs = [q for c in contours for q in c]
        node_names = [nm for c in b["node_names"] for nm in c]
        c = G.rasterize(contours, a.shape)
        # compare shapes, not ink: Pugin's letter as the region inside his 0.5 edge, so the thin and
        # speckled ink inside the letter doesn't read as a difference
        import construct as K
        gy, gx = np.mgrid[0:Hh, 0:Ww]
        shape = np.clip(0.5 - K.signed_distance(a)(np.column_stack([gx.ravel(), gy.ravel()]).astype(float)), 0, 1).reshape(Hh, Ww)
        diff = shape - c if not model else np.zeros_like(c)
        rgba = np.zeros((Hh, Ww, 4), np.uint8)
        rgba[diff > 0, :3] = (12, 89, 232)     # orange: Pugin's ink the construction leaves out
        rgba[diff <= 0, :3] = (120, 166, 12)   # green: the construction where Pugin has no ink
        rgba[..., 3] = np.clip(np.abs(diff) * 1.6 * 255, 0, 255).astype(np.uint8)
        diff_paper = paper * (1 - rgba[..., 3:] / 255) + rgba[..., :3] * (rgba[..., 3:] / 255)
        corners = {c["node"] for c in b["checks_px"]["corners"]}
        nodes = []
        for P, nm in zip(segs, node_names):
            for s_, e_ in ((P[0], P[1]), (P[3], P[2])):
                if np.linalg.norm(s_ - e_) > 0.5 and not construct_is_line(P):
                    nodes.append(f'<line class="hl" x1="{s_[0]:.2f}" y1="{s_[1]:.2f}" x2="{e_[0]:.2f}" y2="{e_[1]:.2f}"/>'
                                 f'<circle class="hp" cx="{e_[0]:.2f}" cy="{e_[1]:.2f}" r="1.6"/>')
        for P, nm in zip(segs, node_names):
            x, y = P[0]
            t = f"<title>{H.escape(nm)}</title>"
            nodes.append(f'<rect class="nd corner" x="{x - 2.6:.2f}" y="{y - 2.6:.2f}" width="5.2" height="5.2">{t}</rect>' if nm in corners
                         else f'<circle class="nd" cx="{x:.2f}" cy="{y:.2f}" r="2.6">{t}</circle>')
        u = b["units"]
        em = 1000 / u["scale_per_px"]
        fx = u.get("spaced_origin_px", u["origin_px"])
        ch = H.escape(b["char"])
        ffs = f' style="font-feature-settings:\'{b["feature"]}\'"' if b.get("feature") else ""
        font_text = f'<text class="L-font" x="{fx:.2f}" y="{u["baseline_px"]:.2f}" font-size="{em:.2f}"{ffs}>{ch}</text>'
        path = G.svg_path(contours)
        dv = b["deviation"] or {"overall": {"mean_px": "—", "p95_px": "—", "max_px": "—"}, "by_part": {},
                                "wobble_of_pugins_edge": {"mean_px": "—"}}
        o = dv["overall"]
        parts = "".join(f"<tr><th>{H.escape(k)}</th><td>{v['mean_px']}</td><td>{v['p95_px']}</td><td>{v['max_px']}</td></tr>"
                        for k, v in dv["by_part"].items())
        meas_rows = "".join(f"<tr><th>{H.escape(k)}</th><td>{v}</td></tr>" for k, v in b["measured"].items())
        ck = b["checks_units"]
        ink = hexc(inks[g["ink"]])
        other = hexc(inks["red" if g["ink"] == "blue" else "blue"])
        fs = f";font-feature-settings:'{b['feature']}'" if b.get("feature") else ""
        spec = "".join(f'<span style="font-size:{s_}px;color:{col}{fs}">{ch}</span>'
                       for s_, col in ((24, ink), (48, other), (96, ink), (192, other)))
        vb = f"0 0 {Ww} {Hh}"
        out.append(f"""
<section class="built"><h2>Constructed: {H.escape(name)}</h2>
<p class="lede">{H.escape(b['description'])} {_provenance(name, model)} Hover a node for its name.</p>
<div class="ov-grid">
<figure class="ov off-diff off-font off-fill" id="ov-{H.escape(name)}">
  <div class="ov-wrap"><img class="L-plate" src="{_png_uri(crop, '.jpg', 92)}" alt="Pugin's {H.escape(name)}, plate 9">
  <svg viewBox="{vb}"><image class="L-diff" href="{_png_uri(rgba)}" width="{Ww}" height="{Hh}"/>{font_text}
  <path class="L-outline" d="{path}"/><g class="L-nodes">{''.join(nodes)}</g></svg></div>
  <fieldset class="layers"><legend>Show</legend>
    <label><input type="checkbox" data-l="plate" checked> Pugin's plate</label>
    <label><input type="checkbox" data-l="outline" checked> Outline</label>
    <label><input type="checkbox" data-l="nodes" checked> Nodes and handles</label>
    <label><input type="checkbox" data-l="font"> The compiled font, in place</label>
    <label><input type="checkbox" data-l="diff"> Difference</label>
    <label><input type="checkbox" data-l="fill"> Filled</label>
  </fieldset>
  <div class="edit-bar"><label><input type="checkbox" data-act="edit"> Edit points</label>
    <button type="button" data-act="undo">Undo</button><button type="button" data-act="reset">Remove all moves</button>
    <button type="button" data-act="save">Save</button><button type="button" data-act="rebuild" class="api-only">Save and rebuild</button>
    <span class="edit-status"></span></div>
  <div class="edit-info"></div>
  <script type="application/json" class="edit-data">{_edit_data(b)}</script>
  <figcaption>Circles are smooth nodes, squares are corners. Difference: <b style="color:#e8590c">orange</b> is Pugin's ink the construction leaves out;
  <b style="color:#0ca678">green</b> is the construction where he has none.</figcaption>
</figure>
<div class="facts">
  <table>
  <tr><th>Outline</th><td>{ck['segments']} segments. A direct trace of the same edge needs {b.get('direct_trace_segments') or '—'}.</td></tr>
  <tr><th>Nodes at extremes</th><td>{'Yes: no curve swells past its nodes, and every handle at an extreme lies flat or upright.' if ck['ok'] else 'No: ' + H.escape(json.dumps(ck))}</td></tr>
  <tr><th>Corners</th><td>{len(ck['corners'])}, each on purpose: {H.escape('; '.join(dict.fromkeys(c['node'].split(':')[0] for c in ck['corners'])))}</td></tr>
  <tr><th>Pugin's edge from the construction</th><td>mean {o['mean_px']} px; 95% within {o['p95_px']} px; worst {o['max_px']} px</td></tr>
  <tr><th>Sharing the family's parts</th><td>{o['mean_px']} px mean; with its own stem, curl and trefoil it would be {(b.get('alone') or {}).get('mean_px', '—')} px</td></tr>
  <tr><th>Pugin's edge about itself</th><td>{dv['wobble_of_pugins_edge']['mean_px']} px mean wobble about its own smoothed course</td></tr>
  {_lean_row(dv)}
  <tr><th>In the font</th><td>{u['advance']} units wide, side bearings {u.get('lsb', '—')} and {u.get('rsb', '—')}; {u['cap_units']:.0f} high; 1 plate pixel = {u['scale_per_px']:.3f} units</td></tr>
  </table>
  <h3>By part (px)</h3>
  <table class="num"><thead><tr><th></th><th>mean</th><th>95%</th><th>worst</th></tr></thead><tbody>{parts}</tbody></table>
</div>
</div>
<div class="tri">
  <figure><img src="{_png_uri(crop, '.jpg', 92)}" alt=""><figcaption>Pugin</figcaption></figure>
  <figure><svg viewBox="{vb}" style="background:{hexc(paper)}"><text x="{fx:.2f}" y="{u['baseline_px']:.2f}" font-size="{em:.2f}" fill="{ink}" font-family="Draft"{ffs}>{ch}</text></svg><figcaption>The font</figcaption></figure>
  <figure><img src="{_png_uri(diff_paper.astype(np.uint8))}" alt=""><figcaption>Where they differ</figcaption></figure>
</div>
<p class="spec">{spec}</p>
<details><summary>The measurements, fitted to Pugin's letter (plate pixels; tensions 0–1)</summary>
<table class="num">{meas_rows}</table>
<p class="lede">At the end of their allowed range: {H.escape(', '.join(f"{k.split(':', 1)[-1]} = {b['measured'].get(k.split(':', 1)[-1], b['family'].get(k.split('family.')[-1]))}" for k in b['at_bounds']) or 'none')}.
A neck angle of 0° means the bar leaves the neck flat; it can't dip lower without adding an extreme.</p></details>
</section>""")
    css += """
.ov-grid{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:24px;align-items:start}
.ov{margin:0} .ov-wrap{position:relative;background:#fff;border:1px solid var(--rule)} .ov-wrap img{display:block;width:100%;height:auto}
.ov-wrap svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.L-outline{fill:rgba(30,26,22,.55);stroke:#ff5a1f;stroke-width:1.4px;vector-effect:non-scaling-stroke} .off-fill .L-outline{fill:none}
.edit-bar{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;font-size:.85rem;padding:6px 0;border-top:1px solid var(--rule)}
.edit-bar button{font:inherit;padding:2px 10px;border:1px solid var(--rule);background:#fff8;border-radius:3px;cursor:pointer}
.edit-bar .api-only{display:none} .has-api .edit-bar .api-only{display:inline-block}
.edit-bar.dirty .edit-status{color:#a8382a} .edit-bar.busy button{opacity:.5;pointer-events:none}
.edit-status{color:var(--muted)} .edit-info{font-size:.8rem;color:var(--muted);min-height:1.2em;white-space:pre-wrap}
.editing .ov-wrap svg{touch-action:none} .editing .nd,.editing .hp{cursor:grab}
.nd.sel,.hp.sel{fill:#ff5a1f;stroke:#1e1a16}
.bulge{fill:none;stroke:#d6336c;stroke-width:3px;stroke-opacity:.55;vector-effect:non-scaling-stroke;pointer-events:none}
.xtr{fill:#d6336c;stroke:#fff;stroke-width:1px;vector-effect:non-scaling-stroke;pointer-events:none}
.L-font{fill:rgba(255,90,31,.35);font-family:'Draft'}
.hl{stroke:#1e1a16;stroke-width:.8px;vector-effect:non-scaling-stroke} .hp{fill:#fff;stroke:#1e1a16;stroke-width:.8px;vector-effect:non-scaling-stroke}
.nd{fill:#fff;stroke:#1e1a16;stroke-width:1.2px;vector-effect:non-scaling-stroke} .nd.corner{fill:#ff5a1f}
.off-plate .L-plate{opacity:.12} .off-outline .L-outline,.off-nodes .L-nodes,.off-font .L-font,.off-diff .L-diff{display:none}
.layers{border:0;padding:8px 0;display:flex;flex-wrap:wrap;gap:4px 16px;font-size:.9rem} .layers legend{float:left;color:var(--muted);padding:0 4px 0 0}
.facts table{width:100%} .facts th{width:38%;vertical-align:top;font-weight:400;color:var(--muted)} .facts h3{font-weight:400;margin:20px 0 6px}
.num td{text-align:right}
.tri{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:24px} .tri figure{margin:0} .tri img,.tri svg{display:block;width:100%;height:auto;border:1px solid var(--rule)}
.spec{font-family:'Draft';line-height:1;display:flex;align-items:baseline;gap:28px;margin:28px 0;flex-wrap:wrap}
details{margin-top:12px} summary{cursor:pointer;color:var(--muted)}
.fam .sh th,.fam .sh td{font-weight:700;border-top:2px solid var(--ink)}
.words{font-family:'Draft';font-size:72px;line-height:1.25;margin:24px 0;font-kerning:normal}
@media (max-width:860px){.ov-grid{grid-template-columns:1fr} .tri{grid-template-columns:1fr 1fr}}
"""
    return "".join(out), css


def _lean_row(dv: dict) -> str:
    if "pugins_stem_lean_deg" not in dv:
        return ""
    deg, px = dv["pugins_stem_lean_deg"], abs(dv["pugins_stem_lean_px"])
    if abs(deg) < 0.2:
        txt = f"stands upright, as the construction does: its midline moves {px} px across the straight"
    else:
        txt = (f"leans {abs(deg)}° {'clockwise' if deg > 0 else 'anticlockwise'}: its midline moves {px} px across the straight. "
               f"The construction stands upright.")
    return f"<tr><th>Pugin's stem</th><td>{txt}</td></tr>"


def _family_html(d: Path, meta: dict) -> str:
    """The measurements every letter shares, beside what each letter would have on its own, and a
    specimen of the letters built so far."""
    import html as H
    fp = d / "family.json"
    if not fp.exists():
        return ""
    f = json.loads(fp.read_text())
    sh = f["shared"]
    cell = lambda fam, k, fmt: fmt(fam[k]) if k in fam else "—"
    stem = lambda v: f"{2 * v:.1f}"
    stem_cell = lambda fam: (f"{stem(fam['stem_plain'])} (plain)" if "stem_plain" in fam
                             else f"{stem(fam['stem_armed'])} (armed)" if "stem_armed" in fam else "—")
    rows = "".join(
        f"<tr><th>{H.escape(g)}</th><td>{stem_cell(a)}</td><td>{cell(a, 'curl', lambda v: f'{v:.3f}')}</td>"
        f"<td>{cell(a, 'trefoil_r', lambda v: f'{v:.1f}')}</td><td>{cell(a, 'two_lobe_r', lambda v: f'{v:.1f}')}</td>"
        f"<td>{f['mean_px'][g]['alone']}</td><td>{f['mean_px'][g]['shared']}</td></tr>"
        for g, a in f["fitted_alone"].items())
    rows += (f"<tr class='sh'><th>Shared</th><td>{stem(sh['stem_plain'])} plain, {stem(sh['stem_armed'])} armed</td><td>{sh['curl']:.3f}</td><td>{sh['trefoil_r']:.1f}</td>"
             f"<td>{sh['two_lobe_r']:.1f}</td><td></td><td></td></tr>")
    inks = {k: "#%02x%02x%02x" % tuple(int(v) for v in c[::-1]) for k, c in meta["inks_bgr"].items()}
    words = ["✠ KYRIE", "GLORIA", "CREDO", "ALLELUIA", "VENI CREATOR", "MAGNIFICAT", "LAUDATE", "BENEDICTE", "MISERERE",
             "WHITSUN", "AVE", "AMEN ⁙"]
    spec = " ".join(f'<span style="color:{inks["red" if i % 2 else "blue"]}">{w}</span>' for i, w in enumerate(words))
    sp_p = d / "spacing.json"
    n_kern = len(json.loads(sp_p.read_text()).get("kerning", {})) if sp_p.exists() else 0
    return f"""
<section class="family"><h2>The letters together</h2>
<p class="lede">The letters were fitted to Pugin's in one solve, sharing two stem weights, one curl, one ball, one trefoil and one two-lobe terminal, so those
parts settle where his letters agree. Fitted alone, each letter would take the values in its row. The trefoil is three equal round lobes on the
arms of a cross, and the two-lobe terminal two equal overlapping lobes: each is the same wherever it is placed, where Pugin's are freehand and vary.</p>
<table class="num fam"><thead><tr><th></th><th>stem width (px)</th><th>curl size</th><th>trefoil lobe radius (px)</th><th>two-lobe radius (px)</th>
<th>mean from Pugin, alone (px)</th><th>sharing (px)</th></tr></thead><tbody>{rows}</tbody></table>
<p class="words">{spec}</p>
<p class="lede">With the stylistic sets on: <code>ss01</code> gives the uncial forms of T, M and W, <code>ss02</code> the modern Y (drawn on Pugin's V).</p>
<p class="words" style="font-feature-settings:'ss01','ss02'">{spec}</p>
<p class="lede">Spacing and kerning are judged a pair at a time: the side bearings are fitted so every pair of letters leaves as nearly as it can
the same white between them, and the {n_kern} pairs still off are kerned (see the README). The same words without kerning:</p>
<p class="words" style="font-kerning:none">{spec}</p>
</section>"""


def _edit_data(b: dict) -> str:
    """What the proof page's editor needs for one glyph: its construction's outline before any moves
    by hand, the moves saved for it, its node names, and which contours are mirrored."""
    adj = b.get("adjustments") or {}
    ck = b.get("checks_units") or {}
    problems = ck.get("curves_swelling_past_nodes", []) + ck.get("nearly_flat_handles", []) + ck.get("degenerate_segments", [])
    data = {"glyph": b["glyph"], "base": b.get("contours_px_base") or b["contours_px"],
            "names": b.get("node_names_base") or b["node_names"], "check": problems, "moved": len(adj.get("nodes_moved_to_extremes", [])),
            "added": len(adj.get("extremes_added", [])) - len(adj.get("nodes_moved_to_extremes", [])),
            "mirrored": b.get("mirrored") or [None] * len(b["contours_px"]), "axis": b.get("axis_px"),
            "scale": b["units"]["scale_per_px"], "points": adj.get("points", []), "stale": len(adj.get("stale", []))}
    return json.dumps(data, separators=(",", ":")).replace("</", "<\\/")


def _provenance(name: str, model: str | None) -> str:
    import html as H
    if model:
        return (f"Built from the kit's parts and {H.escape(model)}'s fitted measurements; Pugin drew no {H.escape(name)}, so it "
                f"is not fitted. The outline below is drawn over his {H.escape(model)} on the flattened plate, for comparison.")
    return ("Built from the kit's parts, not traced; its measurements were fitted to Pugin's letter together with the other "
            "letters, sharing the family's measurements (two stem weights, the curl, the balls, the trefoil and the two-lobe "
            f"terminal). The outline below is drawn over his {H.escape(name)} on the flattened plate.")


def construct_is_line(P) -> bool:
    import construct as K
    return K.is_line(np.asarray(P))


def cmd_proof(fam: str):
    """A self-contained proof page: the references in their inks with every found curl marked,
    the measurements, and each primitive's instances, consensus, and fitted outline."""
    import html as H
    d = family_dir(fam)
    meta = json.loads((d / "references" / "references.json").read_text())
    meas = json.loads((d / "measurements.json").read_text()) if (d / "measurements.json").exists() else None
    paper = np.array(meta["paper_bgr"], np.float32)
    inks = {k: np.array(v, np.float32) for k, v in meta["inks_bgr"].items()}
    prims = {p.stem: json.loads(p.read_text()) for p in sorted((d / "primitives").glob("*.json")) if p.name.count(".") == 1}
    hits_by = {}
    for pn, rep in prims.items():
        for h in rep["hits"]:
            hits_by.setdefault(h["glyph"], []).append((pn, h))
    tiles = []
    for name, g in meta["glyphs"].items():
        a = cv2.imread(str(d / g["coverage"]), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
        img = (paper * (1 - a[..., None]) + inks[g["ink"]] * a[..., None]).astype(np.uint8)
        Hh, Ww = a.shape
        marks = "".join(
            f'<g class="hit"><circle cx="{h["x"]:.1f}" cy="{h["y"]:.1f}" r="26"/><text x="{h["x"]:.1f}" y="{h["y"] + 4:.1f}">'
            f'{"↙↘↖↗"[["bottom-left", "bottom-right", "top-left", "top-right"].index(h["orientation"])]}</text></g>'
            for pn, h in hits_by.get(name, []))
        m = (meas or {}).get("glyphs", {}).get(name, {})
        tiles.append(f'<figure class="g"><div class="art"><img src="{_png_uri(img, ".jpg", 90)}" alt="{H.escape(name)}">'
                     f'<svg viewBox="0 0 {Ww} {Hh}">{marks}</svg></div><figcaption><b>{H.escape(name)}</b> '
                     f'<span>{g["ink"]} · {m.get("width_px", g["width_px"])}×{m.get("height_px", g["height_px"])} · '
                     f'{len(hits_by.get(name, []))} curls</span></figcaption></figure>')
    prim_html = []
    for pn, rep in prims.items():
        P = d / "primitives"
        cons = cv2.imread(str(P / f"{pn}.consensus.png"), cv2.IMREAD_GRAYSCALE)
        S = cons.shape[1]
        model_p = P / f"{pn}.model.json"
        if model_p.exists():
            model = json.loads(model_p.read_text())
            segs = [np.array(q) + model["outer_node_in_consensus_px"] for q in model["segments"]]
            path, node_svg = G.svg_path([segs]), G.svg_nodes([segs], 1.3)
            fit_caption = (f"Consensus of {rep['instances']} (gray) and the clean {H.escape(pn)}: four nodes, at the stroke's outer edge, "
                           f"the ball's back and crown, and the neck, a corner. Mean {model['fit']['mean_px']} px, worst {model['fit']['max_px']} px "
                           f"from the consensus. A free fit needs {rep['fitted']['segments']} segments for {rep['fitted']['mean_error_px']} px.")
        else:
            fitted = (P / f"{pn}.fitted.svg").read_text()
            path, node_svg = fitted.split('d="')[1].split('"')[0], ""
            fit_caption = (f"Consensus of {rep['instances']} (gray) and the fitted outline (red): {rep['fitted']['segments']} cubic segments, "
                           f"mean {rep['fitted']['mean_error_px']} px, worst {rep['fitted']['max_error_px']} px from the consensus")
        inst = cv2.imread(str(P / f"{pn}.instances.png"))
        spread = cv2.imread(str(P / f"{pn}.spread.png"), cv2.IMREAD_GRAYSCALE)
        bg = cv2.cvtColor(255 - cons, cv2.COLOR_GRAY2BGR)
        by = ", ".join(f"{k} {v}" for k, v in sorted(rep["by_glyph"].items()))
        prim_html.append(f"""
<section class="prim"><h2>Primitive: {H.escape(pn)}</h2>
<p class="lede">{H.escape(json.loads((d / 'source.json').read_text())['primitives'][pn]['note'])}</p>
<div class="three">
  <figure><img class="px" src="{_png_uri(cv2.cvtColor(255 - cv2.imread(str(P / f'{pn}.template.png'), 0), cv2.COLOR_GRAY2BGR))}"><figcaption>Template, from {H.escape(rep['template']['glyph'])}</figcaption></figure>
  <figure class="fit"><img class="px" src="{_png_uri(bg)}"><svg class="ed" viewBox="0 0 {S} {S}"><path d="{path}" class="outline"/>{node_svg}</svg>
    <figcaption>{fit_caption}</figcaption></figure>
  <figure><img class="px" src="{_png_uri(cv2.applyColorMap(spread, cv2.COLORMAP_INFERNO))}"><figcaption>Where the instances disagree (bright = more)</figcaption></figure>
</div>
<figure><img class="wide" src="{_png_uri(inst, '.jpg', 88)}"><figcaption>All {rep['instances']} instances, turned to one orientation and aligned. Found in: {H.escape(by)}.</figcaption></figure>
</section>""")
    s = meas["summary"] if meas else None
    meas_html = ""
    if s:
        rows = "".join(f"<tr><th>{k}</th><td>{s[k]['median_px']}</td><td>{s[k]['p25_px']}–{s[k]['p75_px']}</td><td>{s[k]['n']}</td></tr>"
                       for k in ("height", "stem", "bowl", "hairline"))
        meas_html = f"""<section><h2>Proportions</h2>
<table><thead><tr><th></th><th>median px</th><th>middle half</th><th>samples</th></tr></thead><tbody>{rows}</tbody></table>
<p class="lede">Stem ÷ height {s['ratios']['stem_to_height']} · bowl ÷ stem {s['ratios']['bowl_to_stem']} · hairline ÷ stem {s['ratios']['hairline_to_stem']}.
The spread within each group is Pugin's hand; the revival settles each to one value.</p></section>"""
    built_html, built_css = _constructed_html(d, meta)
    built_html = _family_html(d, meta) + built_html
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{H.escape(meta['family'])} · proof</title>
<style>
:root{{--paper:#F4EFE3;--ink:#1E1A16;--muted:#6b6258;--rule:#d8cfbf;--red:#A8382A}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 Georgia,serif}}
main{{max-width:1240px;margin:0 auto;padding:32px 20px 80px}}
h1{{font-weight:400;font-size:2rem;margin:0 0 4px}} h2{{font-weight:400;font-size:1.4rem;margin:40px 0 8px;border-top:1px solid var(--rule);padding-top:20px}}
.lede{{color:var(--muted);max-width:52rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px}}
.g{{margin:0;background:#fff8;border:1px solid var(--rule);padding:8px}}
.art{{position:relative}} .art img{{display:block;width:100%;height:auto}} .art svg{{position:absolute;inset:0;width:100%;height:100%}}
.hit circle{{fill:none;stroke:#0a8f6a;stroke-width:3}} .hit text{{font:bold 22px system-ui;fill:#0a8f6a;text-anchor:middle}}
.g figcaption{{font-size:.8rem;color:var(--muted)}} .g figcaption b{{color:var(--ink);font-size:1rem;margin-right:4px}}
table{{border-collapse:collapse;font-variant-numeric:tabular-nums}} td,th{{padding:4px 14px;border-bottom:1px solid var(--rule);text-align:left}}
.three{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}} .three figure{{margin:0;position:relative}}
.px{{width:100%;image-rendering:auto;background:#fff;border:1px solid var(--rule)}} .fit svg{{position:absolute;left:0;top:0;width:100%;aspect-ratio:1}}
.outline{{fill:rgba(168,56,42,.12);stroke:var(--red);stroke-width:.6}} .fit circle{{fill:var(--red)}}
.wide{{width:100%;border:1px solid var(--rule);background:#fff}} figcaption{{font-size:.85rem;color:var(--muted);margin-top:4px}}
@media (max-width:760px){{.three{{grid-template-columns:1fr}}}}
.ed .n{{fill:#fff;stroke:var(--red);stroke-width:.4}} .ed .h{{stroke:var(--red);stroke-width:.3}} .ed .hc{{fill:#fff;stroke:var(--red);stroke-width:.3}}
{built_css}
</style></head><body><main>
<h1>{H.escape(meta['family'])}</h1>
<p class="lede">The working proof of the Lombardic revival: first the glyphs built so far, each over Pugin's letter;
then the references from plate 9, cut from the flattened, evened plate and separated from the paper by ink, with a green circle
on every curl terminal the primitive search found; then the alphabet's proportions and its primitives. Generated by <code>tools/type/type.py</code> on {time.strftime('%Y-%m-%d %H:%M')}.</p>
{built_html}
<section><h2>References ({len(meta['glyphs'])})</h2><div class="grid">{''.join(tiles)}</div></section>
{meas_html}
{''.join(prim_html)}
</main>
<script>
const FAMILY = {json.dumps(fam)};
{(Path(__file__).parent / "editor.js").read_text()}
document.querySelectorAll('.layers input').forEach(i => i.addEventListener('change', () =>
  i.closest('figure').classList.toggle('off-' + i.dataset.l, !i.checked)));
</script></body></html>"""
    (d / "proof").mkdir(exist_ok=True)
    (d / "proof" / "index.html").write_text(page)
    print(f"  wrote {(d / 'proof' / 'index.html').relative_to(ROOT)} ({len(page) // 1024} KB)")


def cmd_serve(fam: str, port: int = 8766):
    """Serve the proof pages (fonts/) on localhost, with a small API behind the proof page's editor:
    POST /api/<family>/adjustments/<glyph> saves that glyph's adjustments; POST /api/<family>/rebuild
    runs the build and the proof in the background; GET /api/<family>/status reports on it."""
    import http.server
    import subprocess
    import threading
    d = family_dir(fam)
    glyph_names = {json.loads(p.read_text())["glyph"] for p in (d / "recipes").glob("*.json")}
    state = {"running": False, "ok": None, "log": "", "finished": None}
    me = str(Path(__file__).resolve())

    def rebuild():
        state.update(running=True, ok=None, log="")
        out, ok = [], True
        for cmd in ([sys.executable, me, "build", fam], [sys.executable, me, "proof", fam]):
            p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
            out.append(p.stdout + p.stderr)
            if p.returncode:
                ok = False
                break
        log = "".join(out)
        state.update(running=False, ok=ok, failures=[l.strip() for l in log.splitlines() if "FAIL" in l or "STALE" in l],
                     log=log[-6000:], finished=time.time())

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(FONTS), **k)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def _json(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path.split("?")[0] == f"/api/{fam}/status":
                return self._json(200, state)
            return super().do_GET()

        def do_POST(self):
            parts = self.path.split("?")[0].strip("/").split("/")
            if parts[:2] != ["api", fam]:
                return self._json(404, {"error": "not found"})
            if parts[2:3] == ["adjustments"] and len(parts) == 4 and parts[3] in glyph_names:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                pts = [{"contour": int(e["contour"]), "segment": int(e["segment"]), "point": int(e["point"]), "node": str(e["node"]),
                        "dx": round(float(e["dx"]), 3), "dy": round(float(e["dy"]), 3)} for e in body.get("points", [])]
                p = d / "adjustments" / f"{parts[3].replace('.', '_')}.json"
                if pts:
                    p.parent.mkdir(exist_ok=True)
                    p.write_text(json.dumps({"glyph": parts[3], "units": "plate pixels, y down; each a move of one control point "
                                             "from the construction, made by hand on the proof page", "points": pts,
                                             "when": time.strftime("%Y-%m-%dT%H:%M:%S")}, indent=1) + "\n")
                elif p.exists():
                    p.unlink()
                return self._json(200, {"saved": len(pts)})
            if parts[2:] == ["rebuild"]:
                if state["running"]:
                    return self._json(409, {"error": "a build is already running"})
                threading.Thread(target=rebuild, daemon=True).start()
                return self._json(202, {"started": True})
            return self._json(404, {"error": "not found"})

        def log_message(self, fmt, *args):
            if "/api/" in (args[0] if args else ""):
                super().log_message(fmt, *args)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"  serving fonts/ at http://localhost:{port}/{fam}/proof/ (saves to fonts/{fam}/adjustments/)")
    srv.serve_forever()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["extract", "measure", "curls", "build", "space", "proof", "serve"])
    ap.add_argument("family")
    ap.add_argument("--fresh", action="store_true",
                    help="build: start every fit from the constructions' starting values, not the last build's, and refit every letter alone")
    ap.add_argument("--port", type=int, default=8766, help="serve: the port")
    a = ap.parse_args()
    if a.cmd == "serve":
        cmd_serve(a.family, a.port)
        return
    if a.cmd == "build":
        cmd_build(a.family, fresh=a.fresh)
        return
    {"extract": cmd_extract, "measure": cmd_measure, "curls": cmd_curls, "space": cmd_space, "proof": cmd_proof}[a.cmd](a.family)


if __name__ == "__main__":
    main()
