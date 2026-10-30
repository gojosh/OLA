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
#   "skia-pathops>=0.8",
# ]
# ///
"""Tools for the Pugin textura (decisions 0008 and 0011): the small alphabet of plate 9.

A textura is written with a broad nib, so its letters are rebuilt as strokes of one simulated pen
(nib.py), fitted to Pugin's letters and checked against them. Each letter has a plain form, the
default, built from its strokes; Pugin's flourished forms are alternates that add hairlines and
swashes to the same strokes.

Usage (from the repository root; uv installs the dependencies):
  uv run tools/type/textura.py extract pugin-textura   # references/: each letter's ink, with its hairlines
  uv run tools/type/textura.py measure pugin-textura   # measurements.json: the nib, the x-height, the stems
  uv run tools/type/textura.py build   pugin-textura   # fit the letters, write source/*.ufo and build/*.otf
  uv run tools/type/textura.py build   pugin-textura --fit b,o   # fit only b and o; the rest as they stand ('none': fit nothing;
                                                                 #   b:right.lead: only that measurement of b; c:top.*: all c's top.*;
                                                                 #   family: the shared measurements, the letters as they stand)
  uv run tools/type/textura.py proof   pugin-textura   # proof/index.html (served by `type.py serve` at /pugin-textura/proof/)
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import json
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from skimage import measure, segmentation

import geom as G
import type as T

ROOT = T.ROOT


def _flat_region(src: dict):
    """The plate's frame on the flattened image, inset as the Lombardic references are."""
    prm = json.loads((ROOT / src["params"]).read_text())
    fr, pg = prm["frame"], prm["page"]
    return (int(fr["u0"] - pg["u0"]) + 20, int(fr["y0"] - pg["y0"]) + 20, int(fr["u1"] - pg["u0"]) - 20, int(fr["y1"] - pg["y0"]) - 20)


def cmd_extract(fam: str):
    """Cut each letter out of the lowercase rows. Ink is separated from paper as for the capitals.
    The letters run into each other through their flourishes, so they are separated by weight: an
    opening as wide as the hairlines leaves the nib's strokes, whose larger pieces seed the letters
    (one box per letter in source.json); every other piece of ink goes to the letter it is joined
    to by the shortest way along the ink."""
    d = T.family_dir(fam)
    src = T.load_source(fam)
    img = cv2.imread(str(ROOT / src["image"]))
    if img is None:
        sys.exit(f"Missing {src['image']}: run `uv run tools/flatten/flatten.py render {src['plate'][:2]}` first.")
    region = _flat_region(src)
    cov, paper, inks = T.ink_coverage(img, region)
    red = cov["red"]
    zx0, zy0, zx1, zy1 = src["zone_flat_px"]
    rx, ry = region[:2]
    a = red[zy0 - ry:zy1 - ry, zx0 - rx:zx1 - rx]
    ink = (a > 0.5).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (src["body_opening_px"],) * 2)
    body = cv2.morphologyEx(ink, cv2.MORPH_OPEN, k)
    n, lab, st, cen = cv2.connectedComponentsWithStats(body, connectivity=8)
    markers = np.zeros(ink.shape, np.int32)
    glyphs = src["glyphs"]
    inside = lambda g, x, y: g["box"][0] <= x < g["box"][2] and g["box"][1] <= y < g["box"][3]
    for i in range(1, n):
        if st[i, 4] < src["seed_min_area_px"]:
            continue
        cx, cy = cen[i][0] + zx0, cen[i][1] + zy0
        hits = [j for j, g in enumerate(glyphs) if inside(g, cx, cy)]
        if len(hits) == 1:
            markers[lab == i] = hits[0] + 1
    for j, g in enumerate(glyphs):
        if g.get("hairline_only"):
            x0, y0, x1, y1 = (v - o for v, o in zip(g["box"], (zx0, zy0, zx0, zy0)))
            cx, cy, hw, hh = (x0 + x1) // 2, (y0 + y1) // 2, (x1 - x0) // 5, (y1 - y0) // 5
            sub = ink[cy - hh:cy + hh, cx - hw:cx + hw] > 0
            markers[cy - hh:cy + hh, cx - hw:cx + hw][sub & (markers[cy - hh:cy + hh, cx - hw:cx + hw] == 0)] = j + 1
    # the rest of the ink, flooded from the seeds along the ink
    owner = segmentation.watershed(np.zeros(ink.shape), markers, mask=ink > 0)
    out = d / "references"
    out.mkdir(parents=True, exist_ok=True)
    refs = {}
    pad = 24
    for j, g in enumerate(glyphs):
        mine = (owner == j + 1).astype(np.uint8)
        if not mine.any():
            print(f"  {g['glyph']}: no ink found")
            continue
        others = ((owner > 0) & (owner != j + 1)).astype(np.uint8)
        # this letter's own ink, with the soft edge around it but none of its neighbours'
        keep = cv2.dilate(mine, np.ones((5, 5), np.uint8)) & (1 - cv2.dilate(others, np.ones((3, 3), np.uint8)) | mine)
        ys, xs = np.nonzero(mine)
        bx0, by0, bx1, by1 = max(0, xs.min() - pad), max(0, ys.min() - pad), min(a.shape[1], xs.max() + 1 + pad), min(a.shape[0], ys.max() + 1 + pad)
        alpha = a[by0:by1, bx0:bx1] * keep[by0:by1, bx0:bx1]
        bod = body[by0:by1, bx0:bx1] & mine[by0:by1, bx0:bx1]
        name = g["glyph"]
        cv2.imwrite(str(out / f"{name}.png"), np.clip(alpha * 255 + 0.5, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 9])
        cv2.imwrite(str(out / f"{name}.body.png"), (bod * 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 9])
        flat = [int(v) for v in (bx0 + zx0, by0 + zy0, bx1 + zx0, by1 + zy0)]
        refs[name] = {"char": g.get("char", name), "coverage": f"references/{name}.png", "body": f"references/{name}.body.png",
                      "box_flat_px": flat, "ink_box_flat_px": [int(xs.min()) + zx0, int(ys.min()) + zy0, int(xs.max()) + 1 + zx0, int(ys.max()) + 1 + zy0],
                      "ink_area_px": round(float(alpha.sum()), 1), "body_area_px": int(bod.sum())}
    # an overview: each letter's ink in its own colour over the plate's zone
    pal = np.array([[60, 60, 200], [200, 90, 40], [40, 150, 60], [160, 60, 160], [30, 140, 190]], np.uint8)
    over = np.full(ink.shape + (3,), 245, np.uint8)
    for j in range(len(glyphs)):
        over[owner == j + 1] = pal[j % len(pal)]
    over[(body > 0) & (owner > 0)] = (over[(body > 0) & (owner > 0)] * 0.6).astype(np.uint8)
    cv2.imwrite(str(out / "overview.jpg"), cv2.resize(over, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 85])
    meta = {"family": src["family"], "plate": src["plate"], "image": src["image"], "zone_flat_px": src["zone_flat_px"],
            "paper_bgr": [round(float(v), 1) for v in paper], "ink_bgr": [round(float(v), 1) for v in inks["red"]],
            "when": time.strftime("%Y-%m-%dT%H:%M:%S"), "glyphs": refs}
    (out / "references.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(f"  {len(refs)} letters → {out.relative_to(ROOT)}: " + ", ".join(f"{k} ({v['ink_box_flat_px'][2] - v['ink_box_flat_px'][0]}×"
                                                                       f"{v['ink_box_flat_px'][3] - v['ink_box_flat_px'][1]})" for k, v in refs.items()))


def _edges(alpha: np.ndarray, origin, tol=1.6, min_len=12.0):
    """Straight edges of a letter's outline: (angle mod 180 in degrees on the page, length), from a
    polygon fitted to its 0.5 contour on a 4× smoothed copy."""
    big = cv2.GaussianBlur(cv2.resize(alpha.astype(np.float32), None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC), (0, 0), 2)
    out = []
    for c in measure.find_contours(big, 0.5):
        if len(c) < 60:
            continue
        P = (c[:, ::-1] / 4 + origin).astype(np.float32)
        ap = cv2.approxPolyDP(P.reshape(-1, 1, 2), tol, True).reshape(-1, 2)
        for p, q in zip(ap, np.roll(ap, -1, 0)):
            dx, dy = q - p
            L = float(math.hypot(dx, dy))
            if L >= min_len:
                out.append((math.degrees(math.atan2(dy, dx)) % 180, L))
    return out


def cmd_measure(fam: str):
    """The hand's measurements, from the references: the x-height band (heads and feet of the
    letters that stay within it), ascenders and descenders, the width of upright stems, the nib's
    angle (the edges that rise to the right on the heads and feet, which the nib's edge cut), the
    nib's width (an upright stem is the nib's width times the cosine of its angle), and the
    hairline's width."""
    d = T.family_dir(fam)
    refs = json.loads((d / "references" / "references.json").read_text())["glyphs"]
    load = lambda g, k: cv2.imread(str(d / refs[g][k]), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    top = lambda g: refs[g]["box_flat_px"][1] + int(np.nonzero(load(g, "body").any(1))[0].min())
    bottom = lambda g: refs[g]["box_flat_px"][1] + int(np.nonzero(load(g, "body").any(1))[0].max()) + 1
    short = [g for g in "acimnorsuv" if g in refs]
    x_top, base = float(np.median([top(g) for g in short])), float(np.median([bottom(g) for g in short]))
    asc = float(np.median([top(g) for g in "bdhkl" if g in refs]))
    desc = float(np.median([bottom(g) for g in "pq" if g in refs]))
    # upright stems: ink runs across the middle of the x-height band
    widths = []
    for g in "ilmn":
        b, (x0, y0) = load(g, "body"), refs[g]["box_flat_px"][:2]
        for y in range(int(x_top + 0.35 * (base - x_top)) - y0, int(x_top + 0.65 * (base - x_top)) - y0, 4):
            row = load(g, "coverage")[y]
            on = row > 0.5
            i = 0
            while i < len(on):
                if on[i]:
                    j = i
                    while j < len(on) and on[j]:
                        j += 1
                    if j - i > 20:
                        widths.append(float(row[max(0, i - 2):j + 2].sum()))
                    i = j
                else:
                    i += 1
    stem = float(np.median(widths))
    # the nib's angle: edges rising to the right on the heads and feet of the minims
    rising, falling = [], []
    for g in "ilmnr":
        for ang, L in _edges(load(g, "coverage"), np.array(refs[g]["box_flat_px"][:2])):
            if 120 <= ang <= 160 and L < 60:
                rising.append((180 - ang, L))
            elif 20 <= ang <= 60 and L < 60:
                falling.append((ang, L))
    wmed = lambda v: float(np.average([a for a, _ in v], weights=[L for _, L in v]))
    nib_angle = wmed(rising)
    nib_width = stem / math.cos(math.radians(nib_angle))
    # the hairline: twice the distance to the paper along the middle of the thin strokes
    hair = []
    for g in refs:
        ink = (load(g, "coverage") > 0.5).astype(np.uint8)
        thin = ink & (1 - cv2.dilate(load(g, "body").astype(np.uint8), np.ones((7, 7), np.uint8)))
        dt = cv2.distanceTransform(ink, cv2.DIST_L2, 5)
        ridge = (dt == cv2.dilate(dt, np.ones((3, 3)))) & (thin > 0) & (dt > 1)
        hair += list(2 * dt[ridge])
    hairline = float(np.median(hair))
    xh = base - x_top
    m = {"units": "flattened-plate pixels, y down",
         "x_height_band_px": [round(x_top, 1), round(base, 1)], "x_height_px": round(xh, 1),
         "ascender_px": round(base - asc, 1), "descender_px": round(desc - base, 1),
         "ascender_over_x_height": round((base - asc) / xh, 3), "descender_over_x_height": round((desc - base) / xh, 3),
         "stem_px": round(stem, 1), "stem_samples": len(widths),
         "nib_angle_deg": round(nib_angle, 1), "nib_angle_edges": len(rising),
         "head_and_foot_stroke_deg": round(wmed(falling), 1),
         "nib_width_px": round(nib_width, 1), "hairline_px": round(hairline, 1),
         "note": "The x-height band runs from the points of the minims' heads to the points of their feet. The nib's angle is the mean of the head and foot "
                 "edges that rise to the right (weighted by length); the nib's width follows from it and the upright stem.",
         "when": time.strftime("%Y-%m-%dT%H:%M:%S")}
    (d / "measurements.json").write_text(json.dumps(m, indent=1) + "\n")
    print("  " + ", ".join(f"{k} {v}" for k, v in m.items() if k not in ("note", "when", "units")))


# ── Fitting the letters to Pugin's ─────────────────────────────────────────────

def _resample(contours, n=700):
    """n points spread evenly along all of a letter's contours together, so the fit's residuals keep
    their count whatever the outline's topology."""
    segs = []
    for c in contours:
        P = G.sample(c, 30)
        segs += list(zip(P, np.roll(P, -1, 0)))
    a = np.array([s[0] for s in segs])
    b = np.array([s[1] for s in segs])
    L = np.linalg.norm(b - a, axis=1)
    cum = np.concatenate([[0], np.cumsum(L)])
    s = (np.arange(n) + 0.5) * cum[-1] / n
    k = np.clip(np.searchsorted(cum, s, side="right") - 1, 0, len(L) - 1)
    t = ((s - cum[k]) / np.maximum(L[k], 1e-9))[:, None]
    return a[k] + t * (b[k] - a[k])


class Ref:
    """A letter's reference, ready for fitting: its coverage, where it sits on the plate, the signed
    distance to Pugin's edge, and the edges of his letter's body (his edge within a few pixels of
    the nib's strokes, which leaves out the hairline flourishes the plain form doesn't have)."""

    def __init__(self, d, r, near=5, keep=None):
        import construct as K
        self.alpha = cv2.imread(str(d / r["coverage"]), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
        body = cv2.imread(str(d / r["body"]), cv2.IMREAD_GRAYSCALE)
        hand = d / "references" / "hand" / f"{Path(r['coverage']).stem}-main.png"
        if keep == "main" and hand.exists():
            # the main stroke as Josh drew it over Pugin's, where his ink can't show it: the s's ends
            # run on in his ink into the fine stems that grow out of them (Josh: "Do you need me to use
            # a brush tool and show you the correct terminal shapes?"). On its own canvas (scale and
            # origin in the .json beside it), brought back to the plate.
            m = json.loads(hand.with_suffix(".json").read_text())
            paint = 1 - cv2.imread(str(hand), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
            z, (hx, hy) = m["scale"], m["origin"]
            small = cv2.resize(paint, (paint.shape[1] // z, paint.shape[0] // z), interpolation=cv2.INTER_AREA)
            ox, oy = int(round(hx - r["box_flat_px"][0])), int(round(hy - r["box_flat_px"][1]))
            self.alpha = np.zeros_like(self.alpha)
            h_, w_ = min(small.shape[0], self.alpha.shape[0] - oy), min(small.shape[1], self.alpha.shape[1] - ox)
            self.alpha[oy:oy + h_, ox:ox + w_] = small[:h_, :w_]
            body = (self.alpha > 0.5).astype(np.uint8) * 255
        elif keep == "main":
            # the letter's main stroke alone: his ink within a few pixels of his body's largest piece,
            # without the hairlines and pips drawn apart from it (Josh: "You need to drop the stems
            # and nibs to do this analysis"). The few pixels give back what the body's opening rounded
            # off his corners; his ink opened by a 5 px disc leaves out the first few pixels of each
            # hairline where it leaves the body, which those few pixels would keep (Josh: "Why am I
            # still seeing part of the stem for the pip?").
            n, lab, stats, _ = cv2.connectedComponentsWithStats((body > 0).astype(np.uint8))
            main = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
            ink = (self.alpha > 0.5).astype(np.uint8)
            opened = cv2.morphologyEx(ink, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
            keep = cv2.dilate(main, np.ones((9, 9), np.uint8)) & (opened | main)
            self.alpha = self.alpha * keep.astype(np.float32)
            body = main * 255
        self.origin = np.array(r["box_flat_px"][:2], float)
        self.sd = K.signed_distance(self.alpha)
        near_body = cv2.dilate((body > 0).astype(np.uint8), np.ones((2 * near + 1,) * 2, np.uint8))
        e = np.concatenate(K.reference_edges(self.alpha))
        xi, yi = np.clip(np.round(e).astype(int), 0, [self.alpha.shape[1] - 1, self.alpha.shape[0] - 1]).T
        e = e[near_body[yi, xi] > 0]
        self.edges = e[np.linspace(0, len(e) - 1, min(1500, len(e))).astype(int)]


def _load_drawn(d):
    """The letters Josh has drawn by hand, for the constructions to draw from: whole outlines drawn
    in a drawing program (references/hand-drawn-<g>.svg, placed on the plate by the .json beside it;
    textura_letters.OUTLINES; or, if the .json says "alternate", beside its letter rather than for it,
    textura_letters.ALTERNATES, with the alternates built as letters are, BUILT_ALTERNATES), and strokes drawn point by point in the pen editor (a recipe's
    "drawn" points; textura_letters.DRAWN)."""
    import textura_letters as TL
    TL.DRAWN.clear()
    TL.OUTLINES.clear()
    TL.ALTERNATES.clear()
    for f in sorted((d / "recipes").glob("*.json")):
        r = json.loads(f.read_text())
        if r.get("drawn"):
            TL.DRAWN[f.stem] = r["drawn"]["points"]
    TL.OUTLINE_ON_PLATE.clear()
    for f in sorted((d / "references").glob("hand-drawn-*.svg")):
        if not f.with_suffix(".json").exists():        # a drawing not in use (an earlier one, kept)
            continue
        m = json.loads(f.with_suffix(".json").read_text())
        scale = np.broadcast_to(np.asarray(m["scale"], float), (2,))         # one scale, or one for x and one for y
        cs = [[np.asarray(q) * scale + m["offset"] for q in c] for c in G.read_svg(f)]
        if m.get("warp_y"):        # heights mapped to heights, evenly between: some bands lengthened, the rest kept as drawn
            ins, outs = (np.asarray(v, float) for v in zip(*m["warp_y"]))
            cs = [[np.column_stack([q[:, 0], np.interp(q[:, 1], ins, outs)]) for q in c] for c in cs]
        TL.OUTLINES[m["glyph"]] = cs
        if m.get("alternate"):
            TL.ALTERNATES[m["glyph"]] = {**m["alternate"], "of": m["glyph"].split(".")[0], "description": m.get("description", "")}
        if m.get("on_plate"):
            TL.OUTLINE_ON_PLATE[m["glyph"]] = tuple(m["on_plate"])
    # letters built as the others are that stand beside another (Pugin's archaic x)
    for a, alt in TL.BUILT_ALTERNATES.items():
        TL.ALTERNATES[a] = {**alt, "of": a.split(".")[0], "description": (TL.LETTERS[a].__doc__ or "").strip()}


class Workbench:
    """What the proof page's stroke editor needs (served by `type.py serve`; decision 0012). A letter
    is the strokes of the pen through its own named measurements: the nodes of its strokes (a pair
    of measurements, name.x and name.y, in plate pixels) and their settings (handle lengths,
    headings, a pip's size, how a spiral tightens). The editor moves those, and the letter is drawn
    again here, by the same code as the build, as they move. What Josh sets is saved as the letter's
    own held measurements in its recipe (`held`, which every fit keeps as it is), and listed in
    `held_by_hand`, so it can be told from what he asked for in words."""

    def __init__(self, fam):
        self.fam, self.d = fam, T.family_dir(fam)
        self.refs_meta = json.loads((self.d / "references" / "references.json").read_text())["glyphs"]
        self._refs = {}
        _load_drawn(self.d)

    def _family(self):
        import textura_letters as TL
        src = T.load_source(self.fam)
        shared = json.loads((self.d / "family.json").read_text())["shared"]
        held = {k: float(v) for k, v in src.get("held", {}).items() if not k.endswith("_note")}
        spur = {k: float(v) for k, v in src["spur"].items() if not k.endswith("note")}
        return {f"family.{k}": v for k, v in {**shared, **held}.items() if k in TL.FAMILY}, spur

    def _recipe(self, g):
        return json.loads((self.d / "recipes" / f"{g}.json").read_text())

    def editable(self):
        import textura_letters as TL
        return [g for g in TL.LETTERS if g not in TL.DERIVED and g in self.refs_meta and (self.d / "recipes" / f"{g}.json").exists()]

    # ── The pen editor: a letter drawn by hand, point by point (decision 0013) ──

    def _params(self, g):
        import textura_letters as TL
        fam, spur = self._family()
        r = self._recipe(g)
        import construct as K
        mine = {f"{g}:{k}": v for k, v in K._flat({k: v for k, v in r.get("measured", {}).items() if k not in ("units", "from", "when", "family")}).items()}
        return TL.TParams(g, {**fam, **mine}, False, True)

    def pen(self, g):
        """A letter's drawing: its points (as saved, or, before any is, taken from its construction:
        a point every 10 px along its pen's path, with the nib's angle and pressure there, and a
        corner where the path turns sharply), the nib's size, and where Pugin's letter and Josh's
        drawing of it are."""
        import nib as NB
        import textura_letters as TL
        r, ref = self._recipe(g), self.refs_meta[g]
        if r.get("drawn"):
            points = r["drawn"]["points"]
        else:
            saved = TL.DRAWN.pop(g, None)
            try:
                b = TL.LETTERS[g](self._params(g))
            finally:
                if saved is not None:
                    TL.DRAWN[g] = saved
            st = b["strokes"][0]
            n = len(st)
            corners = set()                         # where the construction's path turns sharply
            for i in range(1, n):
                v1 = np.asarray(st[i - 1], float)[3] - np.asarray(st[i - 1], float)[2]
                v2 = np.asarray(st[i], float)[1] - np.asarray(st[i], float)[0]
                if np.linalg.norm(v1) > 1e-9 and np.linalg.norm(v2) > 1e-9 and \
                        np.degrees(np.arccos(np.clip(v1 @ v2 / np.linalg.norm(v1) / np.linalg.norm(v2), -1, 1))) > 15:
                    corners.add(i)
            # a point every 10 px along it, and at each corner: close enough to the construction to start from
            sg = np.linspace(0, n, 40 * n + 1)
            ls = st.length_at(sg)
            at = sorted({round(float(v), 4) for v in np.interp(np.arange(0, ls[-1], 10.0), ls, sg)} | {float(n)} | {float(i) for i in corners})
            points = []
            for v in at:
                i = min(int(v), n - 1)
                pt = G.bez(np.asarray(st[i], float), np.array([v - i]))[0]
                points.append({"x": round(float(pt[0]), 2), "y": round(float(pt[1]), 2), "angle": round(NB.turned_angle(st, v), 2),
                               "pressure": round(NB.pressure_at(st, v), 3), "corner": v in corners})
        p = self._params(g)
        hand = self.d / "references" / "hand" / f"{g}-main.png"
        out = {"glyph": g, "char": ref["char"], "box": ref["box_flat_px"], "ink": ref.get("ink_box_flat_px", ref["box_flat_px"]),
               "reference": ref["coverage"], "points": points, "drawn": bool(r.get("drawn")),
               "nib": {"width": p.fam("nib_width"), "thickness": p.fam("nib_thickness")}}
        if hand.exists():
            m = json.loads(hand.with_suffix(".json").read_text())
            img = cv2.imread(str(hand), cv2.IMREAD_GRAYSCALE)
            out["hand"] = {"src": f"references/hand/{hand.name}", "x": m["origin"][0], "y": m["origin"][1],
                           "w": img.shape[1] / m["scale"], "h": img.shape[0] / m["scale"]}
        return out

    def pen_outline(self, g, points):
        """The letter drawn from these points by the build's own pen: its outline, the pen's path, how
        far Josh's drawing of its main stroke (or Pugin's main stroke) lies from it, and whether the
        outline passes the checks in font units."""
        import construct as K
        import nib as NB
        import textura_letters as TL
        p = self._params(g)
        st = TL.drawn_stroke(points)
        cs = NB.outline([st], TL.pen_of(p))
        key = (g, "main")
        if key not in self._refs:
            self._refs[key] = Ref(self.d, self.refs_meta[g], keep="main")
        dev = _deviation(cs, self._refs[key]) if cs else {"mean_px": None, "p95_px": None, "max_px": None}
        meas = json.loads((self.d / "measurements.json").read_text())
        built = {"contours": [[(q, "stroke", f"stroke: node {k}") for k, q in enumerate(c)] for c in cs], "baseline": TL.baseline(p)}
        units = NB.tidy_units(K.to_units(built, T.load_source(self.fam)["font"]["x_height"] / meas["x_height_px"], 0)[0])
        chk = K.check_outline(units, [[f"stroke: node {k}" for k in range(len(c))] for c in units], smooth_deg=3.0, swell_tol=0.5)
        return {"contours": [[np.round(np.asarray(q), 3).tolist() for q in c] for c in cs], "path": [np.round(q, 3).tolist() for q in st],
                "mean_px": dev["mean_px"], "p95_px": dev["p95_px"], "max_px": dev["max_px"], "ok": bool(chk["ok"]), "contour_count": len(cs)}

    def pen_save(self, g, points):
        """The drawing saved in the letter's recipe ("drawn"), which the build draws the letter from."""
        import textura_letters as TL
        keep = ("x", "y", "angle", "pressure", "corner")
        pts = [{k: (bool(q.get(k)) if k == "corner" else round(float(q[k]), 3)) for k in keep} for q in points]
        r = self._recipe(g)
        r["drawn"] = {"points": pts, "units": "plate pixels, y down; the nib's angle in degrees; pressure as a share of the nib's width",
                      "note": "drawn by Josh, point by point, on the proof page's pen editor (decision 0013); the build draws the letter from it",
                      "when": time.strftime("%Y-%m-%d %H:%M")}
        (self.d / "recipes" / f"{g}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
        TL.DRAWN[g] = pts
        return {"saved": len(pts)}

    def letter(self, g):
        """The letter's measurements: each with its bounds, its value as it stands (held, or as last
        fitted), and which are held; the nodes, as pairs of measurements; where Pugin's letter is."""
        import construct as K
        import textura_letters as TL
        p0 = TL.TParams(g, None, False)
        TL.LETTERS[g](p0)
        TL.pen_of(p0)
        r = self._recipe(g)
        measured = {f"{g}:{k}": v for k, v in K._flat({k: v for k, v in r.get("measured", {}).items()
                                                        if k not in ("units", "from", "when", "family")}).items()}
        held = {f"{g}:{k}": float(v) for k, v in r.get("held", {}).items()}
        spec = {k: v for k, v in p0.spec.items() if k.startswith(g + ":")}
        values = {k: float(held.get(k, measured.get(k, v[0]))) for k, v in spec.items()}
        names = [k[len(g) + 1:] for k in spec]
        nodes = sorted({n[:-2] for n in names if n.endswith(".x") and n[:-2] + ".y" in names})
        ref = self.refs_meta[g]
        return {"glyph": g, "char": ref["char"], "box": ref["box_flat_px"], "ink": ref.get("ink_box_flat_px", ref["box_flat_px"]), "reference": ref["coverage"],
                "spec": {k[len(g) + 1:]: {"lo": v[1], "hi": v[2]} for k, v in spec.items()},
                "values": {k[len(g) + 1:]: round(v, 3) for k, v in values.items()},
                "held": sorted(k[len(g) + 1:] for k in held if k in spec), "by_hand": sorted(r.get("held_by_hand", [])),
                "nodes": nodes, "description": (TL.LETTERS[g].__doc__ or "").strip()}

    GROUPS = {"split_top": {"title": "the split top and bottom", "prefix": "fork_", "letters": ["b", "d", "h", "k", "l", "q"],
                            "below": ["q"]}}     # the letters whose split stands at the bottom, turned upside down

    def outline(self, g, values, family=None):
        """The letter drawn from these measurements (its own, by name; the family's as they stand, or
        as `family` sets some of them), with its spurs, as the font has it: its outline, the pen's
        paths, how far Pugin's body edge lies from it, and whether the outline passes the checks."""
        import construct as K
        import textura_letters as TL
        fam, spur = self._family()
        fam.update({f"family.{k}": float(v) for k, v in (family or {}).items()})
        vals = {**fam, **{f"{g}:{k}": float(v) for k, v in values.items()}}
        p = TL.TParams(g, vals, False, True)        # `fill`: anything not sent takes its starting value
        p.spur = spur
        cs, b = _outline(TL.LETTERS[g], p, marks=True)
        if g not in self._refs:
            self._refs[g] = Ref(self.d, self.refs_meta[g])
        dev = _deviation(cs, self._refs[g], b.get("fit_affine"))
        # checked as the build checks it: in font units, rounded and tidied
        import nib as NB
        meas = json.loads((self.d / "measurements.json").read_text())
        built = {"contours": [[(q, "stroke", f"stroke: node {k}") for k, q in enumerate(c)] for c in cs], "baseline": b["baseline"]}
        units = NB.tidy_units(K.to_units(built, T.load_source(self.fam)["font"]["x_height"] / meas["x_height_px"], 0)[0])
        chk = K.check_outline(units, [[f"stroke: node {k}" for k in range(len(c))] for c in units], smooth_deg=3.0, swell_tol=0.5)
        return {"contours": [[np.round(q, 3).tolist() for q in c] for c in cs],
                "strokes": [[np.round(np.asarray(q), 3).tolist() for q in s] for s in b["strokes"] + b.get("marks", [])],
                "affine": list(b["fit_affine"]) if b.get("fit_affine") else None,
                "mean_px": dev["mean_px"], "ok": bool(chk["ok"]), "contour_count": len(cs)}

    def group(self, name):
        """A group of the family's held settings, such as the split top's, shared by several letters:
        each setting with its bounds, meaning and value, which were set by hand, and its letters with
        where Pugin's are."""
        import textura_letters as TL
        grp = self.GROUPS[name]
        src = T.load_source(self.fam)
        held = src.get("held", {})
        keys = [k for k in TL.FAMILY if k.startswith(grp["prefix"])]
        refs = {g: {"box": self.refs_meta[g]["box_flat_px"], "ink": self.refs_meta[g].get("ink_box_flat_px", self.refs_meta[g]["box_flat_px"]),
                    "reference": self.refs_meta[g]["coverage"], "char": self.refs_meta[g]["char"]} for g in grp["letters"]}
        return {"group": name, "title": grp["title"], "letters": grp["letters"], "below": grp.get("below", []), "refs": refs,
                "spec": {k: {"lo": TL.FAMILY[k][1], "hi": TL.FAMILY[k][2], "meaning": TL.FAMILY[k][3]} for k in keys},
                "values": {k: float(held.get(k, TL.FAMILY[k][0])) for k in keys},
                "by_hand": sorted(k for k in src.get("held_by_hand", []) if k in keys)}

    def group_outlines(self, name, values):
        """Every letter of the group drawn with its settings as sent, each with its own measurements as
        they stand."""
        return {g: self.outline(g, self.letter(g)["values"], family=values) for g in self.GROUPS[name]["letters"]}

    def save_group(self, name, set_):
        """Hold the group's settings at these values in source.json, as set by hand."""
        grp = self.group(name)
        bad = [k for k in set_ if k not in grp["spec"]]
        if bad:
            raise ValueError(f"no such settings of {grp['title']}: {', '.join(bad)}")
        path = self.d / "source.json"
        src = json.loads(path.read_text())
        held = src.setdefault("held", {})
        for k, v in set_.items():
            held[k] = round(min(max(float(v), grp["spec"][k]["lo"]), grp["spec"][k]["hi"]), 3)
        hand = set(src.get("held_by_hand", [])) | set(set_)
        if hand:
            src["held_by_hand"] = sorted(hand)
            src["held_by_hand_note"] = ("family settings set by hand in the stroke editor on the proof page (decision 0012); last saved "
                                        + time.strftime("%Y-%m-%d %H:%M"))
        path.write_text(json.dumps(src, indent=1, ensure_ascii=False) + "\n")
        return {"by_hand": sorted(k for k in hand if k in grp["spec"])}

    def save(self, g, set_, release):
        """Hold these measurements at these values in the letter's recipe, as set by hand, and let
        the released ones go back to the fit."""
        spec = self.letter(g)["spec"]
        bad = [k for k in [*set_, *release] if k not in spec]
        if bad:
            raise ValueError(f"no such measurements of {g}: {', '.join(bad)}")
        path = self.d / "recipes" / f"{g}.json"
        r = json.loads(path.read_text())
        held, hand = r.get("held", {}), set(r.get("held_by_hand", []))
        for k, v in set_.items():
            held[k] = round(min(max(float(v), spec[k]["lo"]), spec[k]["hi"]), 3)
            hand.add(k)
        for k in release:
            held.pop(k, None)
            hand.discard(k)
        r["held"] = held
        if hand:
            r["held_by_hand"] = sorted(hand)
            r["held_by_hand_note"] = ("measurements set by hand in the stroke editor on the proof page (decision 0012), and held so every "
                                      "fit keeps them; last saved " + time.strftime("%Y-%m-%d %H:%M"))
        else:
            r.pop("held_by_hand", None)
            r.pop("held_by_hand_note", None)
        if not held:
            r.pop("held", None)
        path.write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
        return {"held": sorted(held), "by_hand": sorted(hand)}


def _affine(A, pts):
    """Points mapped by a construction's fit_affine (a, b, c, d, e, f), if it has one."""
    if not A:
        return pts
    a, b, c, d, e, f = A
    return np.column_stack([a * pts[:, 0] + b * pts[:, 1] + c, d * pts[:, 0] + e * pts[:, 1] + f])


def _outline(fn, p, marks=False, only=None):
    """A letter's outline: its strokes, and with `marks` the strokes Pugin didn't draw (left out of
    the fit); with `only`, just those of its strokes (by index)."""
    import nib as NB
    import textura_letters as TL
    b = fn(p)
    strokes = b["strokes"] if only is None else [b["strokes"][i] for i in only]
    return NB.outline(strokes + (b.get("marks", []) if marks else []), TL.pen_of(p), edges=b.get("edges", ()) if only is None else ()), b


def fit_glyph(job):
    """One letter's measurements fitted to Pugin's: the outline onto his edge, and his body's edge
    onto the outline, with a robust loss so the hairlines joining his strokes don't pull. A
    top-level function, so the build can fit letters in parallel. job: (glyph, (family folder,
    reference entry), start, fixed, local)."""
    from scipy.optimize import least_squares
    from scipy.spatial import cKDTree
    import pathops
    import textura_letters as TL
    g, (d, r), start, fixed, local = job
    _load_drawn(d)
    ref = Ref(d, r)
    fn = TL.LETTERS[g]
    p0 = TL.TParams(g, None, local)
    b0 = fn(p0)
    TL.pen_of(p0)
    spec = p0.spec
    keys = [k for k in spec if k not in fixed]
    lb_all, ub_all = {k: spec[k][1] for k in keys}, {k: spec[k][2] for k in keys}
    cur = {**fixed, **{k: float(np.clip(start.get(k, spec[k][0]), lb_all[k], ub_all[k])) for k in keys}}
    # A letter may be fitted in stages (b["fit_stages"]): some of its measurements at a time, against
    # some of its strokes and a reference to suit (the s: its main stroke against his main stroke
    # alone, then its stems and pips against his whole letter, the main stroke held). And it may add
    # residuals of its own (b["smooth"]: how sharply its pen turns and presses, so it does so no more
    # than his letter asks).
    def wanted(k, names):
        return any(k == f"{g}:{n}" or k.startswith(f"{g}:{n}.") for n in names)
    for st in b0.get("fit_stages") or [{}]:
        ks = [k for k in keys if ("keys" not in st or wanted(k, st["keys"])) and not wanted(k, st.get("exclude", ()))]
        if not ks:
            continue
        rf = ref if st.get("ref") is None else Ref(d, r, keep=st["ref"])
        only, smooth = st.get("strokes"), st.get("smooth", True)
        lb, ub = np.array([lb_all[k] for k in ks]), np.array([ub_all[k] for k in ks])

        def resid(x):
            vals = {**cur, **dict(zip(ks, x))}
            try:
                cs, b = _outline(fn, TL.TParams(g, vals, local), only=only)
            except pathops.PathOpsError:
                cs = []                   # geometry the union can't settle counts as a bad fit, which steers the search away
            if not cs:
                return np.full(700 + len(rf.edges) + len(b0.get("smooth", [])), 50.0)
            pts = _affine(b.get("fit_affine"), _resample(cs)) - rf.origin
            extra = np.asarray(b.get("smooth", []), float) if smooth else np.zeros(0)
            return np.concatenate([rf.sd(pts), cKDTree(pts).query(rf.edges)[0], extra])

        x, cost = np.array([cur[k] for k in ks], float), None
        for _ in range(4):
            # each measurement stepped by half a percent of its range to find the slopes: a step
            # relative to its value (least_squares' own) is lost in the outline's rounding for one near
            # zero (a slide of a few pixels), and needlessly coarse for one far from it (a position)
            step = 0.005 * (ub - lb) / np.maximum(1.0, np.abs(x))
            res = least_squares(resid, x, bounds=(lb, ub), x_scale=(ub - lb) / 10, diff_step=step, loss="soft_l1", f_scale=1.5, max_nfev=300)
            x = res.x
            if cost is not None and cost - res.cost < 1e-3 * cost:
                break
            cost = res.cost
        cur.update(zip(ks, map(float, x)))
    vals = {**fixed, **{k: cur[k] for k in keys}}
    at_bounds = [k for k in keys if min(cur[k] - lb_all[k], ub_all[k] - cur[k]) < 1e-3 * max(1.0, ub_all[k] - lb_all[k])]
    return g, vals, at_bounds


def _deviation(cs, ref, aff=None):
    """How far Pugin's body edge lies from the outline (px), mapped onto his letter by `aff` if the
    construction has a fit_affine."""
    from scipy.spatial import cKDTree
    dense = _affine(aff, np.concatenate([G.sample(c, 120) for c in cs])) - ref.origin
    dd = cKDTree(dense).query(ref.edges)[0]
    return {"mean_px": round(float(dd.mean()), 2), "p95_px": round(float(np.percentile(dd, 95)), 2), "max_px": round(float(dd.max()), 2)}


def cmd_build(fam: str, fit_only: list[str] | None = None):
    """Fit each letter alone; set each shared measurement to the median of what the letters want
    alone; fit each letter again with those held; check the outlines; space; write the UFO source
    and compile it.

    With fit_only, a list of letters (perhaps empty), the shared measurements stay as family.json
    has them, every other letter keeps its own as its recipe has them, and only the letters named
    are fitted again: for a correction to some letters that shouldn't move the rest. An item
    letter:name (b:right.lead) fits just that measurement of the letter, the rest as they stand; the
    name may end in * (c:top.*) for every measurement that begins so. The
    item "family" fits the shared measurements again, as a full build does, while the letters keep
    their own: for a change to the pen. (A full build
    moves every letter a little: the medians drift, since each letter's fit alone starts from the
    last family, and a fit restarted where it stopped wanders where Pugin's letter gives it little
    to hold on to.) An empty list fits nothing, rebuilding each letter as it is now drawn from its
    measurements as they stand. What each letter wants alone is left as the last full build found it."""
    import construct as K
    import nib as NB
    import spacing as SP
    import textura_letters as TL
    import ufo2ft
    from concurrent.futures import ProcessPoolExecutor
    d = T.family_dir(fam)
    _load_drawn(d)
    src = T.load_source(fam)
    refs_meta = json.loads((d / "references" / "references.json").read_text())["glyphs"]
    meas = json.loads((d / "measurements.json").read_text())
    names = [g for g in TL.LETTERS if g in refs_meta]
    refs = {g: Ref(d, refs_meta[g]) for g in names}
    rec_dir = d / "recipes"
    rec_dir.mkdir(exist_ok=True)
    recipes = {g: json.loads((rec_dir / f"{g}.json").read_text()) for g in names if (rec_dir / f"{g}.json").exists()}
    start = {}
    for g, r in recipes.items():
        start.update({f"{g}:{k}": v for k, v in K._flat({k: v for k, v in r.get("measured", {}).items() if k not in ("units", "from", "when", "family")}).items()})
    famp = d / "family.json"
    fam_before = json.loads(famp.read_text()) if famp.exists() else {}
    shared_before = fam_before.get("shared", {})
    refit_family = fit_only is None or "family" in fit_only or not shared_before
    keep = fit_only is not None         # letters not named keep their measurements as their recipes have them
    t0 = time.time()
    # family values held at a set value rather than fitted (Josh's corrections; source.json)
    held = {k: float(v) for k, v in src.get("held", {}).items() if not k.endswith("_note")}
    # a letter's own measurements held at a set value (a recipe's "held": what Josh has said is right)
    held_own = {g: {f"{g}:{k}": float(v) for k, v in r.get("held", {}).items()} for g, r in recipes.items()}
    own = {g: {k: v for k, v in start.items() if k.startswith(g + ":")} for g in names}
    if not refit_family:
        alone = own
        shared = {**shared_before, **held}
    else:
        jobs = [(g, (d, refs_meta[g]), {**{k: v for k, v in start.items() if k.startswith(g + ":")},
                              **{f"{g}:family.{k}": v for k, v in shared_before.items() if k not in held}},
                 {**{f"{g}:family.{k}": v for k, v in held.items()}, **held_own.get(g, {})}, True) for g in names]
        with ProcessPoolExecutor(max_workers=min(len(jobs), max(1, (os.cpu_count() or 2) - 1))) as ex:
            alone = {g: v for g, v, _ in ex.map(fit_glyph, jobs)}
        wants = {}
        for g in names:
            for k, v in alone[g].items():
                if ":family." in k:
                    wants.setdefault(k.split(":family.")[1], []).append(v)
        shared = {k: round(float(np.median(v)), 3) for k, v in sorted(wants.items())}
        shared.update({k: v for k, v in shared_before.items() if k not in shared})     # what no letter Pugin drew measures (join)
        shared.update(held)
    fixed = {f"family.{k}": v for k, v in shared.items()}
    fit_keys = {}                       # letter: the measurements to fit, or None for all of them
    for item in fit_only or []:
        g, _, k = item.partition(":")
        if g == "family":
            continue
        if not k:
            fit_keys[g] = None
        elif fit_keys.get(g, set()) is not None:
            fit_keys.setdefault(g, set()).add(f"{g}:{k}")
    todo = [g for g in names if not keep or g in fit_keys]

    def fixed_of(g):
        f = dict(fixed)
        if keep and fit_keys.get(g):    # just some of the letter's measurements: the rest as its recipe has them
            f.update({k: v for k, v in own[g].items() if not any(fnmatch.fnmatchcase(k, pat) for pat in fit_keys[g])})
        return {**f, **held_own.get(g, {})}

    jobs = [(g, (d, refs_meta[g]), {k: v for k, v in (own if keep else alone)[g].items() if ":family." not in k}, fixed_of(g), False)
            for g in todo]
    refined = {}
    if jobs:
        with ProcessPoolExecutor(max_workers=min(len(jobs), max(1, (os.cpu_count() or 2) - 1))) as ex:
            refined = {g: (v, ab) for g, v, ab in ex.map(fit_glyph, jobs)}
    for g in names:
        if g not in refined:            # kept as its recipe has it
            p0 = TL.TParams(g, None, False)
            TL.LETTERS[g](p0)
            missing = [k for k in p0.spec if k.startswith(g + ":") and k not in own[g]]
            if missing:
                raise SystemExit(f"{g} is now drawn with measurements its recipe hasn't got ({', '.join(missing)}): fit it (--fit {g})")
            refined[g] = ({**fixed, **own[g], **held_own.get(g, {})}, recipes.get(g, {}).get("fit", {}).get("at_bounds", []))
    print(("  fitted " + ("the family's shared measurements, then " if refit_family else "")
           + (", ".join(", ".join(sorted(fit_keys[g])) if fit_keys.get(g) else g for g in todo) or "no letters")
           + ("; the other letters" if refit_family else "; the family and the rest") + " as they stand" if keep else
           f"  fitted {len(names)} letters alone and together") + f" ({time.time() - t0:.0f} s); shared {shared}")
    fc = src["font"]
    scale = fc["x_height"] / meas["x_height_px"]
    out = d / "build"
    out.mkdir(exist_ok=True)
    when = time.strftime("%Y-%m-%dT%H:%M:%S")
    glyphs, units_all = {}, {}
    # letters Pugin didn't draw take the fitted measurements of the letter each is modelled on
    derived = {g: m for g, m in TL.DERIVED.items() if m in refined}
    chars = {g: refs_meta[g]["char"] if g in refs_meta else g.split(".")[0] for g in [*names, *derived]}
    spur = {k: float(v) for k, v in src["spur"].items() if not k.endswith("note")}
    plain_units = {}
    nopip_units = {}        # letters with their fine stems and pips left off (ss02)

    def params(g, vals, spurs, top_spur=True):
        pp = TL.TParams(g, vals, False, g in derived)
        pp.spur = spur if spurs else None
        pp.top_spur = top_spur
        return pp
    space_units = {}        # the letters as they are spaced: without the top spurs leading into first heads

    for g in [*names, *derived]:
        if g in derived:
            m = derived[g]
            vals = {**fixed, **{f"{g}:{k[len(m) + 1:]}": v for k, v in refined[m][0].items() if k.startswith(m + ":")}}
            at_bounds = []
        else:
            vals, at_bounds = refined[g]
        # the letter as the font has it, with spurs; and without, for the stylistic set that drops them
        cs, b = _outline(TL.LETTERS[g], params(g, vals, True), marks=True)
        cs_plain, b_plain = _outline(TL.LETTERS[g], params(g, vals, False), marks=True)
        built = {"contours": [[(q, "stroke", f"stroke: node {k}") for k, q in enumerate(c)] for c in cs], "baseline": b["baseline"]}
        names_ = [[nm for _, _, nm in c] for c in built["contours"]]
        chk = K.check_outline([[q for q, _, _ in c] for c in built["contours"]], names_, swell_tol=0.2)
        units, width, origin = K.to_units(built, scale, 0)
        units = NB.tidy_units(units)
        names_ = [[f"stroke: node {k}" for k in range(len(c))] for c in units]
        chk_u = K.check_outline(units, names_, smooth_deg=3.0, swell_tol=0.5)
        band_from = (b["baseline"] - params(g, vals, True).fam("bottom")) * scale       # the same for every letter
        mine = {k[len(g) + 1:]: round(v, 3) for k, v in vals.items() if k.startswith(g + ":")}
        r = recipes.get(g, {"glyph": g, "unicode": f"U+{ord(chars[g]):04X}", "construction": f"textura_letters.py: {g}"})
        r["description"] = (TL.LETTERS[g].__doc__ or "").strip()
        if g in derived:
            dev = dev_alone = None
            r["derived_from"] = derived[g]
            r["proposal"] = "Pugin drew no " + TL.DERIVED_FORM.get(g, g) + ": drafted in his idiom for Josh's judgment (decision 0008), not fitted to the plate."
            r["measured"] = {**K._nest(mine), "units": "plate pixels, y down; angles in degrees",
                             "from": f"{derived[g]}'s fitted measurements; the rest are the construction's own", "when": when}
            r["fit"] = {"segments": chk_u["segments"], "outline_checks_pass": chk_u["ok"]}
        else:
            dev = _deviation(cs, refs[g], b.get("fit_affine"))
            if not refit_family:        # not fitted alone this time: as the last full build found it
                dev_alone = {"mean_px": r.get("fit", {}).get("mean_px_fitted_alone")}
            else:
                cs_alone, b_alone = _outline(TL.LETTERS[g], TL.TParams(g, alone[g], True))
                dev_alone = _deviation(cs_alone, refs[g], b_alone.get("fit_affine"))
            r["measured"] = {**K._nest(mine), "units": "plate pixels, y down; angles in degrees", "family": "shared with the other letters: see family.json",
                             "from": refs_meta[g]["coverage"], "when": when}
            r["fit"] = {"mean_px": dev["mean_px"], "p95_px": dev["p95_px"], "max_px": dev["max_px"], "mean_px_fitted_alone": dev_alone["mean_px"],
                        "segments": chk_u["segments"], "outline_checks_pass": chk_u["ok"], "at_bounds": at_bounds}
        (rec_dir / f"{g}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
        report = {"glyph": g, "char": chars[g], "description": r["description"], "measured": mine, "family": shared,
                  "derived_from": derived.get(g), "deviation": dev, "deviation_alone": dev_alone, "checks_px": chk, "checks_units": chk_u,
                  **({"alternate_of": TL.ALTERNATES[g]["of"], "feature": TL.ALTERNATES[g]["feature"]} if g in TL.ALTERNATES else {}),
                  "fit_affine": list(b["fit_affine"]) if b.get("fit_affine") else None,
                  "contours_px": [[q.tolist() for q in c] for c in cs], "strokes_px": [[q.tolist() for q in s] for s in b["strokes"] + b.get("marks", [])],
                  "units": {"scale_per_px": scale, "baseline_px": b["baseline"], "origin_px": origin, "outline": [[q.tolist() for q in c] for c in units]}}
        (out / f"{g}.json").write_text(json.dumps(report) + "\n")
        units_all[g] = units
        if sum(map(len, b_plain["strokes"])) != sum(map(len, b["strokes"])):       # it has a spur
            bp = {"contours": [[(q, "stroke", f"stroke: node {k}") for k, q in enumerate(c)] for c in cs_plain], "baseline": b_plain["baseline"]}
            pu = NB.tidy_units(K.to_units(bp, scale, 0)[0])
            ck = K.check_outline(pu, [[f"stroke: node {k}" for k in range(len(c))] for c in pu], smooth_deg=3.0, swell_tol=0.5)
            if not ck["ok"]:
                print(f"  {g} without spurs: checks FAIL {json.dumps(ck)}")
            plain_units[g] = pu
        if b.get("pips"):                                                           # its stems and pips can be left off
            keep = [i for i in range(len(b["strokes"])) if i not in b["pips"]]
            cs_np, _ = _outline(TL.LETTERS[g], params(g, vals, True), only=keep)
            # in the same frame as the whole letter: from its leftmost point, its baseline
            x_min = float(G.sample([np.asarray(q, float) for c in cs for q in c], 40)[:, 0].min())        # as to_units finds it
            conv = lambda q: np.round(np.column_stack([(np.asarray(q)[:, 0] - x_min) * scale, (b["baseline"] - np.asarray(q)[:, 1]) * scale]))
            npu = NB.tidy_units([[conv(q) for q in c] for c in cs_np])
            ck = K.check_outline(npu, [[f"stroke: node {k}" for k in range(len(c))] for c in npu], smooth_deg=3.0, swell_tol=0.5)
            if not ck["ok"]:
                print(f"  {g} without stems and pips: checks FAIL {json.dumps(ck)}")
            nopip_units[g] = npu
        cs_sp, b_sp = _outline(TL.LETTERS[g], params(g, vals, True, top_spur=False), marks=True)
        if sum(map(len, b_sp["strokes"])) != sum(map(len, b["strokes"])):          # it has a top spur
            bs = {"contours": [[(q, "stroke", f"stroke: node {k}") for k, q in enumerate(c)] for c in cs_sp], "baseline": b_sp["baseline"]}
            su = NB.tidy_units(K.to_units(bs, scale, 0)[0])
            # each is put into units from its own leftmost point: line them up by the right, which the top spur leaves alone
            right = lambda us: max(float(np.asarray(q)[:, 0].max()) for c in us for q in c)
            space_units[g] = [[np.asarray(q, float) + [right(units) - right(su), 0] for q in c] for c in su]
        print(f"  {g}: {chk_u['segments']} segments in {chk_u['contours']} contour(s); checks {'pass' if chk_u['ok'] else 'FAIL ' + json.dumps(chk_u)}; "
              + (f"built from {derived[g]}'s measurements; Pugin drew no {TL.DERIVED_FORM.get(g, g)}" if g in derived else
                 f"Pugin's body edge from it: mean {dev['mean_px']} px (alone {dev_alone['mean_px']}), 95% within {dev['p95_px']} px")
              + (f"; at bounds: {at_bounds}" if at_bounds else ""))
    # Josh's drawings that stand beside their letters (y.alt): drawn as they stand, in their letter's frame
    for a, alt in TL.ALTERNATES.items():
        if a in TL.LETTERS:             # built above, as letters are (Pugin's archaic x)
            continue
        g = alt["of"]
        cs, b = _outline(TL.hand_drawn(a), params(g, refined[g][0], True), marks=True)
        built = {"contours": [[(q, "stroke", f"stroke: node {k}") for k, q in enumerate(c)] for c in cs], "baseline": b["baseline"]}
        chk = K.check_outline([[q for q, _, _ in c] for c in built["contours"]], [[nm for _, _, nm in c] for c in built["contours"]], swell_tol=0.2)
        units, width, origin = K.to_units(built, scale, 0)
        units = NB.tidy_units(units)
        chk_u = K.check_outline(units, [[f"stroke: node {k}" for k in range(len(c))] for c in units], smooth_deg=3.0, swell_tol=0.5)
        dev = _deviation(cs, refs[g], b.get("fit_affine")) if g in refs else None
        report = {"glyph": a, "char": chars[g], "alternate_of": g, "feature": alt["feature"], "description": TL.hand_drawn(a).__doc__,
                  "deviation": dev, "deviation_alone": dev, "checks_px": chk, "checks_units": chk_u,
                  "fit_affine": list(b["fit_affine"]) if b.get("fit_affine") else None,
                  "contours_px": [[q.tolist() for q in c] for c in cs], "strokes_px": [[q.tolist() for q in s] for s in b["strokes"]],
                  "units": {"scale_per_px": scale, "baseline_px": b["baseline"], "origin_px": origin, "outline": [[q.tolist() for q in c] for c in units]}}
        (out / f"{a}.json").write_text(json.dumps(report) + "\n")
        units_all[a] = units
        chars[a] = chars[g]
        print(f"  {a}: {chk_u['segments']} segments in {chk_u['contours']} contour(s); checks {'pass' if chk_u['ok'] else 'FAIL ' + json.dumps(chk_u)}; "
              f"Josh's drawing, beside {g} under {alt['feature']}" + (f"; Pugin's body edge from it: mean {dev['mean_px']} px, 95% within {dev['p95_px']} px" if dev else ""))
    for f in out.glob("*.*.json"):          # an alternate no longer drawn
        if f.stem not in TL.ALTERNATES:
            f.unlink()
    famp.write_text(json.dumps({"shared": shared, "meaning": {k: v[3] for k, v in TL.FAMILY.items()},
                                "fitted_alone": fam_before.get("fitted_alone", {}) if not refit_family else
                                {g: {k.split(':family.')[1]: round(v, 3) for k, v in alone[g].items() if ':family.' in k} for g in names},
                                "when": fam_before.get("when", when) if not refit_family else when}, indent=1) + "\n")
    pitch = None
    if "n" in refined:
        v = refined["n"][0]
        pitch = (v["n:stem_2"] - v["n:stem_1"]) * scale      # the minims' pitch inside a letter, in units
    print(f"  spurs on {len(plain_units)} letters ({', '.join(plain_units)}); without them under ss01; "
          f"spaced without the top spurs of {', '.join(space_units)}")
    if nopip_units:
        print(f"  without stems and pips under ss02: {', '.join(nopip_units)}")
    if TL.ALTERNATES:
        print("  alternates: " + ", ".join(f"{a} under {alt['feature']} (\"{alt['name']}\")" for a, alt in TL.ALTERNATES.items()))
    write_font(d, src, units_all, chars, pitch, plain_units, space_units, nopip_units, TL.ALTERNATES, band_from)


def write_font(d, src, units_all, chars, pitch_units=None, plain_units=None, space_units=None, nopip_units=None, alternates=None,
               band_from=0.0):
    """Space the letters (spacing.py, over the x-height), write the UFO source and compile it. The
    x-height band the letters are spaced over runs from band_from, the height of the line the foot
    strokes end on (`bottom`), up by the x-height: so it was measured when the textura was spaced,
    when that line was the baseline, and so it stays since the baseline moved down to the points of
    the feet (textura_letters.baseline), so the spacing doesn't change with it. A
    letter in space_units is spaced and kerned as drawn there (without the top spur that leads into
    its first head, a hairline that tucks into the white before it), and set as units_all has it.
    An alternate (a glyph in alternates, which says its letter and the stylistic set that reaches
    it) is spaced after the letters, which keep their side bearings, each alternate on its own, and
    kerned in its own right."""
    import construct as K
    import spacing as SP
    import ufo2ft
    fc, sp = src["font"], src["spacing"]
    alternates = alternates or {}
    names = list(units_all)
    letters = [g for g in names if g not in alternates]
    drawn = {g: [[np.array(q, float) for q in c] for c in units_all[g]] for g in names}
    contours = {g: [[np.array(q, float) for q in c] for c in (space_units or {}).get(g, units_all[g])] for g in names}
    lo, hi = band_from, band_from + fc["x_height"]          # the x-height band, as the letters are spaced over it
    print(f"  spaced over the x-height band from {lo:.1f} to {hi:.1f} units")
    profiles = {g: SP.profile(contours[g], (lo, hi)) for g in names}
    # a textura is spaced like a fence: the white between two letters is the white between a
    # letter's own minims, so two i's stand one minim's pitch apart
    target = sp.get("target_white")
    if target is None and pitch_units and "i" in names:
        xs = np.concatenate([G.sample(c, 40)[:, 0] for c in contours["i"]])
        target = pitch_units - (xs.max() - xs.min()) + SP.pair_white(profiles["i"], profiles["i"], sp["depth"])[0]
    lsb, rsb, target, white = SP.fit(profiles, letters, set(), sp.get("mean_side_bearings", 0), sp["depth"], target=target)
    if alternates:              # each against the letters and itself, so one alternate's spacing doesn't move another's
        for a in alternates:
            lsb, rsb, _ = SP.fit_more(profiles, letters, lsb, rsb, [a], sp["depth"], target)
        white = {(a, b): SP.pair_white(profiles[a], profiles[b], sp["depth"]) for a in names for b in names}
    glyphs, table, spaced = {}, {}, {}
    dxs = {}
    for g in names:
        moved, width, dx = SP.respace(contours[g], lsb[g], rsb[g])
        dxs[g] = dx
        pts = np.concatenate([G.sample(c, 40) for c in moved])
        spaced[g] = (int(round(pts[:, 0].min())), int(round(width - pts[:, 0].max())))
        glyphs[g] = {"unicode": None if g in alternates else ord(chars[g]), "width": width,
                     "contours": [[np.array(q, float) + [dx, 0] for q in c] for c in drawn[g]]}
        table[g] = {"left": spaced[g][0], "right": spaced[g][1], "advance": width}
    # above the x-height (ascenders, arms) and below the baseline (descenders, tails) parts need more air
    # than heads and feet, which in a textura this tight all but touch
    def closest_outside(a, b):
        out = []
        for zone in ((hi, fc["ascender"] + lo), (fc["descender"] + lo, lo)):
            pa, pb = SP.profile(contours[a], zone), SP.profile(contours[b], zone)
            # profiles are measured from each glyph's own extremes; refer them to the x-height ones
            gap = (profiles[a]["x_max"] - pa["x_max"] + pa["right"]) + (pb["x_min"] - profiles[b]["x_min"] + pb["left"])
            if np.isfinite(gap).any():
                out.append(float(gap[np.isfinite(gap)].min()))
        return min(out) if out else np.inf
    closest = {(a, b): closest_outside(a, b) for a in names for b in names}
    kerning = SP.kern(white, names, spaced, target, sp["kern_threshold"], sp["clearance"], closest, sp.get("clearance_outside"))
    # a last check on the parts above the x-height and below the baseline, by true distance: two
    # parts can be clear row by row and still almost meet on a slant (d's arm over a preceding l's spur)
    from scipy.spatial import cKDTree
    outer = {}
    for g in names:
        pts = np.concatenate([G.sample(c, 30) for c in glyphs[g]["contours"]])
        outer[g] = pts[(pts[:, 1] > hi) | (pts[:, 1] < lo)]
    need = sp.get("clearance_outside", sp["clearance"])
    opened = 0
    for a in names:
        if not len(outer[a]):
            continue
        tree = cKDTree(outer[a])
        for b in names:
            if not len(outer[b]):
                continue
            k = kerning.get((a, b), 0)
            dist = lambda kk: tree.query(outer[b] + [glyphs[a]["width"] + kk, 0])[0].min()
            if dist(k) >= need:
                continue
            while dist(k) < need and k < 300:
                k += 5
            kerning[(a, b)] = k
            opened += 1
    print(f"  opened {opened} pair(s) whose parts above or below the x-height came within {need} units on a slant")
    # a top spur is left out of the spacing, so it tucks into the white before its letter; but it
    # mustn't touch the letter before: where it comes within the clearance, that pair opens until it doesn't
    whole = {g: np.concatenate([G.sample(c, 30) for c in glyphs[g]["contours"]]) for g in names}
    need, tucked = sp.get("clearance_top_spur", sp["clearance"]), 0
    for b in (space_units or {}):
        body = cKDTree(np.concatenate([G.sample(c, 30) for c in contours[b]]) + [dxs[b], 0])
        spur = whole[b][body.query(whole[b])[0] > 2.0]          # what the letter has that it is spaced without
        if not len(spur):
            continue
        for a in names:
            tree = cKDTree(whole[a])
            k = kerning.get((a, b), 0)
            dist = lambda kk: tree.query(spur + [glyphs[a]["width"] + kk, 0])[0].min()
            if dist(k) >= need:
                continue
            while dist(k) < need and k < 300:
                k += 5
            kerning[(a, b)] = k
            tucked += 1
    if space_units:
        print(f"  opened {tucked} pair(s) where a top spur came within {need} units of the letter before")
    (d / "spacing.json").write_text(json.dumps({"method": sp, "target_white": round(target, 1), "glyphs": table,
                                                "kerning": {f"{a} {b}": k for (a, b), k in sorted(kerning.items())}}, indent=1) + "\n")
    glyphs[".notdef"] = {"unicode": None, "width": 500, "contours": K.notdef(500, fc["x_height"])}
    glyphs["space"] = {"unicode": 0x20, "width": sp["word_space"], "contours": []}
    info = {"familyName": fc["name"], "styleName": "Regular", "unitsPerEm": fc["units_per_em"], "xHeight": fc["x_height"],
            "ascender": fc["ascender"], "descender": fc["descender"], "capHeight": fc["ascender"], "versionMajor": 0, "versionMinor": 1,
            "postscriptFontName": fc["postscript_name"],
            "openTypeNameDescription": "Working draft, not for release. A revival of the textura minuscule on plate 9 of A. W. N. Pugin's "
                                       "Glossary of Ecclesiastical Ornament (1844), written again with a simulated broad nib."}
    ufo = d / "source" / f"{fc['postscript_name']}.ufo"
    ufo.parent.mkdir(exist_ok=True)
    # the letters without their spurs: in the same place and width, reached through ss01, kerned as
    # their letters are (each letter and its alternate share a kerning group)
    plain_units = plain_units or {}
    for g, pu in plain_units.items():
        glyphs[f"{g}.nospur"] = {"unicode": None, "width": glyphs[g]["width"],
                                 "contours": [[np.array(q, float) + [dxs[g], 0] for q in c] for c in pu]}
    fea = ""
    if plain_units:
        fea = ("feature ss01 {\n    featureNames { name \"Without spurs\"; };\n"
               + "".join(f"    sub {g} by {g}.nospur;\n" for g in plain_units if g not in alternates) + "} ss01;\n")
    # the letters without their fine stems and pips (the s): likewise in the same place and width,
    # reached through ss02, kerned as their letters are
    nopip_units = nopip_units or {}
    for g, pu in nopip_units.items():
        glyphs[f"{g}.nopips"] = {"unicode": None, "width": glyphs[g]["width"],
                                 "contours": [[np.array(q, float) + [dxs[g], 0] for q in c] for c in pu]}
    if nopip_units:
        fea += ("feature ss02 {\n    featureNames { name \"Without stems and pips\"; };\n"
                + "".join(f"    sub {g} by {g}.nopips;\n" for g in nopip_units) + "} ss02;\n")
    # Josh's drawings beside their letters (y.alt): each reached through its own stylistic set, from its
    # letter or from what an earlier set has made of it
    for a, alt in alternates.items():
        g = alt["of"]
        fea += (f"feature {alt['feature']} {{\n    featureNames {{ name \"{alt['name']}\"; }};\n"
                + "".join(f"    sub {h} by {a};\n" for h in [g] + ([f"{g}.nospur"] if g in plain_units else []) + ([f"{g}.nopips"] if g in nopip_units else []))
                + f"}} {alt['feature']};\n")
    # an alternate with spurs of its own drops them under ss01 too: after the alternates' sets,
    # whose lookups come first, so it does whichever sets are on
    spurred = [a for a in alternates if a in plain_units]
    if spurred:
        fea += "feature ss01 {\n" + "".join(f"    sub {a} by {a}.nospur;\n" for a in spurred) + "} ss01;\n"
    groups = {}
    for g in names:
        members = [g] + ([f"{g}.nospur"] if g in plain_units else []) + ([f"{g}.nopips"] if g in nopip_units else [])
        groups[f"public.kern1.{g}"] = members
        groups[f"public.kern2.{g}"] = members
    grouped = {(f"public.kern1.{a}", f"public.kern2.{b}"): k for (a, b), k in kerning.items()}
    font = K.write_ufo(ufo, info, glyphs, fea, grouped)
    font.groups.update(groups)
    # the script it's for, said outright: with no capitals or figures, macOS can't tell, and its
    # previews (Finder, Quick Look, Font Book) show only the first two letters instead of the alphabet
    font.lib["public.openTypeMeta"] = {"dlng": ["Latn"], "slng": ["Latn"]}
    font.save(ufo, overwrite=True)
    otf = d / "build" / f"{fc['postscript_name']}.otf"
    ufo2ft.compileOTF(font).save(otf)
    print("  spacing: " + ", ".join(f"{g} {v['left']}|{v['right']}" for g, v in table.items()) + f"; kerning: {len(kerning)} pairs")
    print(f"  wrote {ufo.relative_to(ROOT)} and {otf.relative_to(ROOT)} ({otf.stat().st_size} bytes)")


def cmd_proof(fam: str):
    """proof/index.html: the letters built so far set as text under Lombardic initials, and each
    letter over Pugin's, with the nib's path, the outline, its nodes, and the fit's numbers."""
    import base64
    import html as H
    import textura_letters as TL
    d = T.family_dir(fam)
    src = T.load_source(fam)
    refs = json.loads((d / "references" / "references.json").read_text())["glyphs"]
    _load_drawn(d)
    meas = json.loads((d / "measurements.json").read_text())
    fam_j = json.loads((d / "family.json").read_text())
    otf = d / "build" / f"{src['font']['postscript_name']}.otf"
    lomb = T.FONTS / "pugin-lombardic" / "build" / "PuginLombardicDraft-Regular.otf"
    font_face = lambda name, p: f"@font-face{{font-family:'{name}';src:url(data:font/otf;base64,{base64.b64encode(p.read_bytes()).decode()}) format('opentype')}}"
    # each letter, then any alternate beside it (y, y.alt)
    built = [json.loads(p.read_text()) for p in sorted((d / "build").glob("*.json"), key=lambda p: (p.stem.split(".")[0], p.stem))]
    cards = []
    for b in built:
        g = b["glyph"]
        if b.get("alternate_of") in refs:       # Josh's drawing beside a letter: over Pugin's letter
            g = b["alternate_of"]
        if g not in refs:          # a letter Pugin didn't draw: shown on its own
            pts = np.concatenate([G.sample([np.array(q) for q in c], 20) for c in b["contours_px"]])
            o = pts.min(0) - 24
            a = np.zeros((int(pts[:, 1].max() - o[1] + 24), int(pts[:, 0].max() - o[0] + 24)), np.float32)
        else:
            r = refs[g]
            o = np.array(r["box_flat_px"][:2], float)
            a = cv2.imread(str(d / r["coverage"]), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
            # room for anything of ours outside his box (the mark over the i stands above it)
            pts = _affine(b.get("fit_affine"), np.concatenate([G.sample([np.array(q) for q in c], 20) for c in b["contours_px"]]))
            lo = np.minimum(0, np.floor(pts.min(0) - o - 8)).astype(int)
            hi = np.maximum(0, np.ceil(pts.max(0) - o + 8 - a.shape[::-1])).astype(int)
            a = np.pad(a, ((-lo[1], hi[1]), (-lo[0], hi[0])))
            o = o + lo
        z = 2.0 if max(a.shape) < 300 else 1.4
        aff = b.get("fit_affine")      # a letter Pugin squeezed onto the second line is drawn squeezed over his
        img = cv2.cvtColor(cv2.resize((255 - a * 90).astype(np.uint8), None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC), cv2.COLOR_GRAY2BGR)
        for s in b["strokes_px"]:
            for q in s:
                pts = np.round((_affine(aff, G.bez(np.array(q), np.linspace(0, 1, 24))) - o + .5) * z).astype(np.int32)
                cv2.polylines(img, [pts], False, (0, 150, 230), 1, cv2.LINE_AA)
        for c in b["contours_px"]:
            for q in c:
                q = np.array(q)
                pts = np.round((_affine(aff, G.bez(q, np.linspace(0, 1, 30))) - o + .5) * z).astype(np.int32)
                cv2.polylines(img, [pts], False, (170, 50, 20), 2, cv2.LINE_AA)
                cv2.circle(img, tuple(int(v) for v in (_affine(aff, q[:1])[0] - o + .5) * z), 3, (40, 130, 40), -1)
        dv, ck = b["deviation"], b["checks_units"]
        fit = (f"<b>A proposal:</b> Pugin drew no {H.escape(TL.DERIVED_FORM.get(b['glyph'], b['char']))}; built from {H.escape(b['derived_from'])}'s fitted measurements." if b.get("derived_from")
               else f"<b>An alternate</b> (<code>{H.escape(b['glyph'])}</code>, under <code>{H.escape(b['feature'])}</code>). Pugin's body edge from the outline: mean {dv['mean_px']} px, 95% within {dv['p95_px']} px." if b.get("alternate_of")
               else f"Pugin's body edge from the outline: mean {dv['mean_px']} px (fitted alone {b['deviation_alone']['mean_px']}), 95% within {dv['p95_px']} px.")
        edit = "" if b.get("derived_from") or b.get("alternate_of") or g in TL.DRAWN or g in TL.OUTLINES else f' <button class="edit" data-edit="{H.escape(g)}">Edit strokes</button>'
        if g in TL.PENNABLE:
            edit += f' <button class="edit" data-pen="{H.escape(g)}">Draw the stroke</button>'
        cards.append(f"""<figure class="card" id="g-{H.escape(b['glyph'])}"><img src="{T._png_uri(img)}" alt="{H.escape(b['char'])}{'' if b.get('derived_from') else " over Pugin's"}">
<figcaption><b>{H.escape(b['char'])}</b> {H.escape(b['description'])}<br>
{fit} {ck['segments']} segments in {ck['contours']} contour(s); outline checks {'pass' if ck['ok'] else 'FAIL'}.{edit}</figcaption></figure>""")
    # phrases set with a Lombardic initial; only those whose letters are all built (Pugin drew no u, j or w)
    have = {b["char"] for b in built}
    phrases = [w for w in ("Kyrie eleison", "Gloria in excelsis deo", "Agnus dei", "Dominus vobiscum", "Te deum laudamus", "Ave maris stella",
                           "Ecce ancilla domini", "Salve regina", "World without end", "Jubilate deo", "Pater noster")
               if set(w[1:].replace(" ", "")) <= have]
    lines = " ".join(f'<span><span class="init">{w[0]}</span>{w[1:]}</span>' for w in phrases[:9])
    plain = " ".join(w.lower() for w in phrases[:9])
    xwords = "gloria in excelsis deo pax rex lux crux exsultet"
    fam_rows = "".join(f"<tr><th>{H.escape(fam_j['meaning'][k])}</th><td>{v}</td></tr>" for k, v in fam_j["shared"].items())
    plate = cv2.imread(str(ROOT / src["image"]))
    zx0, zy0, zx1, zy1 = src["zone_flat_px"]
    row = cv2.resize(plate[zy0:zy1, zx0:zx1], None, fx=0.45, fy=0.45, interpolation=cv2.INTER_AREA)
    # our letters where his stand, at the same scale, to set under his (Josh: "put our alphabet below the
    # image of pugin's alphabet, in such a way that we can compare"). Those on his first line are in his
    # plate's own pixels already; y and z, which he squeezed onto the second line, stand at full height
    # with their heads level with his there, as Josh's y was first placed. His x is the archaic one.
    on_plate = [b for b in built if b["glyph"] in refs]
    top1 = min(q[1] for b in built if b["glyph"] == "n" for c in b["contours_px"] for s_ in c for q in s_)
    drop = refs["y"]["ink_box_flat_px"][1] - top1 if "y" in refs else 0.0
    place = [(b, drop if b.get("fit_affine") else 0.0) for b in on_plate]
    low = max(q[1] + dy for b, dy in place for c in b["contours_px"] for s_ in c for q in s_)
    cover = np.zeros((max(zy1, int(math.ceil(low)) + 12) - zy0, zx1 - zx0), np.float32)
    for b, dy in place:
        cover = np.maximum(cover, G.rasterize([[np.array(q) - [zx0, zy0 - dy] for q in c] for c in b["contours_px"]], cover.shape))
    paper, ink = np.array([231, 241, 246], np.float32), np.array([34, 38, 42], np.float32)     # the page's paper and ink (BGR)
    ours = (paper + cover[..., None] * (ink - paper)).astype(np.uint8)
    ours = cv2.resize(ours, (row.shape[1], int(round(ours.shape[0] * row.shape[1] / ours.shape[1]))), interpolation=cv2.INTER_AREA)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pugin Textura · proof</title><style>
{font_face('Textura', otf)}
{font_face('Lombardic', lomb)}
:root{{--ink:#2a2622;--paper:#f6f1e7;--red:#b8442f;--blue:#2f5596;--rule:#d8cfbf}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 Georgia,serif}}
main{{max-width:1100px;margin:0 auto;padding:120px 56px 128px}}
@media (max-width:640px){{main{{padding:56px 16px 80px}}}}
h1{{font-weight:normal;margin:0 0 16px}} h2{{font-weight:normal;margin:72px 0 20px;padding-bottom:4px;border-bottom:1px solid var(--rule)}}
main p{{margin:0 0 1.4em}} .lede{{max-width:62em}}
.set{{font-family:'Textura';font-size:80px;line-height:1.1;color:var(--ink);margin:32px 0;font-kerning:normal}}
.set .init{{font-family:'Lombardic';color:var(--red);font-size:1.12em;line-height:0}}
.set span:nth-child(even) .init{{color:var(--blue)}}
.small{{font-size:40px}}
.cards{{display:flex;flex-wrap:wrap;gap:16px}} .card{{margin:0;background:#fff;border:1px solid var(--rule);padding:8px;max-width:520px}}
.card img{{max-width:100%;height:auto;display:block}} figcaption{{font-size:14px;margin-top:6px}}
table{{border-collapse:collapse}} th,td{{text-align:left;padding:3px 10px;border-bottom:1px solid var(--rule);font-weight:normal}} td{{font-variant-numeric:tabular-nums}}
img.plate{{max-width:100%;height:auto;display:block}} img.plate.ours{{margin-top:10px}}
button.edit{{display:none;margin-left:6px;font:inherit;font-size:13px}} .has-api button.edit{{display:inline}}
#se{{position:fixed;inset:0;background:var(--paper);z-index:10;display:flex;flex-direction:column}} #se[hidden]{{display:none}}
body.se-open{{overflow:hidden}}
#se header{{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 14px;padding:10px 16px;border-bottom:1px solid var(--rule)}}
#se header h3{{margin:0;font-weight:normal;font-size:22px}} #se header .sp{{flex:1}}
#se header button{{font:inherit;font-size:14px}}
#se-status{{font-size:14px;padding:6px 16px;border-bottom:1px solid var(--rule)}} #se-status .bad{{color:var(--red)}} #se-status pre{{white-space:pre-wrap;font-size:12px}}
#se.busy header button{{opacity:.4;pointer-events:none}}
#se .body{{flex:1;display:flex;min-height:0}}
#se-svg{{flex:1;min-width:0;height:100%;background:#fff;touch-action:none;user-select:none}}
#se aside{{width:360px;overflow:auto;padding:8px 12px;border-left:1px solid var(--rule);font-size:13px}}
#se aside h4{{margin:12px 0 2px;font-weight:normal;font-style:italic;color:#6b6157}}
#se-desc{{font-size:13px;color:#6b6157;margin:4px 0 6px}} #se summary{{cursor:pointer;color:#6b6157}} .se-help{{font-size:12px;color:#6b6157;margin:6px 0}}
.se-row{{display:grid;grid-template-columns:96px 1fr 64px;gap:2px 6px;align-items:center}}
.se-row label{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}} .se-row input[type=number]{{width:64px;font:inherit}}
.se-row .se-held{{grid-column:2/4;font-size:11px;color:var(--blue)}} .se-row .se-held:empty{{display:none}}
.se-row .se-held button{{font:inherit;font-size:11px;padding:0 4px}}
.se-row.moved label{{color:var(--red);font-weight:bold}}
.se-ref{{filter:invert(1);opacity:.28}}
.se-outline{{fill:rgba(184,68,47,.22);stroke:var(--red);stroke-width:1;vector-effect:non-scaling-stroke}}
.se-pens path{{fill:none;stroke:#e09a2b;stroke-width:1;vector-effect:non-scaling-stroke}}
.se-node{{fill:#fff;stroke:#2c7a3a;stroke-width:1.5;vector-effect:non-scaling-stroke;cursor:grab}}
.se-node.held{{stroke:var(--blue)}} .se-node.moved{{fill:var(--red)}} .se-node.sel{{stroke-width:3}}
.se-tag{{font-family:Georgia,serif;fill:#2c7a3a;pointer-events:none}}
#se-many{{display:none;flex:1;min-width:0;background:#fff;gap:6px;padding:8px;overflow:auto;grid-template-columns:repeat(5,minmax(0,1fr));align-content:start}}
#se.group #se-many{{display:grid}} #se.group #se-svg{{display:none}}
#se-many figure{{margin:0}} #se-many svg{{width:100%;height:auto;display:block}} #se.group .se-help{{display:none}} #se-many figcaption{{text-align:center;font-size:14px}}
.se-row.se-wide{{grid-template-columns:1fr 64px;margin-bottom:8px}} .se-row.se-wide label{{grid-column:1/3;white-space:normal}} .se-row.se-wide input[type=range]{{grid-column:1/2}}
#pe{{position:fixed;inset:0;background:var(--paper);z-index:11;display:flex;flex-direction:column}} #pe[hidden]{{display:none}}
#pe header{{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 14px;padding:10px 16px;border-bottom:1px solid var(--rule)}}
#pe header h3{{margin:0;font-weight:normal;font-size:22px}} #pe header .sp{{flex:1}} #pe header button,#pe header label{{font:inherit;font-size:14px}}
#pe-status{{font-size:14px;padding:6px 16px;border-bottom:1px solid var(--rule)}} #pe-status .bad{{color:var(--red)}}
#pe.busy header button{{opacity:.4;pointer-events:none}}
#pe .body{{flex:1;display:flex;min-height:0}}
#pe-svg{{flex:1;min-width:0;height:100%;background:#fff;touch-action:none;user-select:none}}
#pe aside{{width:380px;overflow:auto;padding:8px 12px;border-left:1px solid var(--rule);font-size:13px}}
.pe-hand{{opacity:.22}} .pe-outline{{fill:rgba(184,68,47,.2);stroke:var(--red);stroke-width:1;vector-effect:non-scaling-stroke}}
.pe-path{{fill:none;stroke:#e09a2b;stroke-width:1;vector-effect:non-scaling-stroke;cursor:copy}}
.pe-nib{{stroke:#2a6fb0;stroke-width:2;vector-effect:non-scaling-stroke;opacity:.7}} .pe-nib.sel{{opacity:1;stroke-width:3}}
.pe-turn{{fill:#2a6fb0;stroke:#fff;stroke-width:1;vector-effect:non-scaling-stroke;cursor:alias}}
.pe-pt{{fill:#fff;stroke:#2c7a3a;stroke-width:1.5;vector-effect:non-scaling-stroke;cursor:grab}} .pe-pt.sel{{fill:#2c7a3a}}
.pe-row{{display:grid;grid-template-columns:22px repeat(4,1fr) 22px;gap:2px 4px;align-items:center;padding:1px 2px}}
.pe-row input[type=number]{{width:100%;font:inherit;font-size:12px}} .pe-row.sel{{background:#e9efe2}} .pe-row.head{{color:#6b6157;font-size:11px}}
#pe.no-ref .se-ref,#pe.no-hand .pe-hand,#pe.no-nibs .pe-nibs{{display:none}}
@media (max-width:800px){{#se .body{{flex-direction:column}} #se aside{{width:auto;height:40%;border-left:0;border-top:1px solid var(--rule)}}}}
</style></head><body><main>
<h1>Pugin Textura <small>(working name)</small></h1>
<p class="lede">The small alphabet of plate 9, which Pugin dates to the latter part of the fifteenth century, written again with a simulated broad nib
(decisions 0008 and 0011). Each letter is the strokes of one pen, fitted to his. These are the <b>plain forms</b>, the defaults; his flourished forms will be
alternates on the same strokes. Built so far: <b>{H.escape(' '.join(sorted({b["char"] for b in built})))}</b> (u, w, j and the modern x are proposals: Pugin drew none of them). Capitals are Lombardic initials for now.</p>
<p class="set">{lines}</p>
<p class="set small">{plain}</p>
<p class="lede">Free feet carry on into a <b>spur</b>, a short hairline up and to the right, as Pugin's do. They are on by default; the stylistic set
<code>ss01</code> ("Without spurs") drops them, keeping each letter's width and kerning. The same words without spurs:</p>
<p class="set small" style="font-feature-settings:'ss01'">{plain}</p>
<p class="lede">The s's fine stems and pips are on by default; the stylistic set <code>ss02</code> ("Without stems and pips") leaves them off, keeping its
width and kerning. The same words with <code>ss02</code>:</p>
<p class="set small" style="font-feature-settings:'ss02'">{plain}</p>
<p class="lede">Josh's own y, drawn by hand, stands beside the y built from Pugin's: the stylistic set <code>ss03</code> ("Alternate y")
sets it, spaced and kerned in its own right. The same words with <code>ss03</code>:</p>
<p class="set small" style="font-feature-settings:'ss03'">{plain}</p>
<p class="lede">The x is a modern x, a proposal in Pugin's idiom (decision 0015). The x he drew is the archaic form, here as Josh drew it over his:
the stylistic set <code>ss04</code> ("Archaic x") sets it, spaced and kerned in its own right. Some words with an x, as they are and with <code>ss04</code>:</p>
<p class="set small">{xwords}</p>
<p class="set small" style="font-feature-settings:'ss04'">{xwords}</p>
<h2>Pugin's alphabet</h2>
<img class="plate" src="{T._png_uri(row, '.jpg', 82)}" alt="The textura minuscule on plate 9">
<img class="plate ours" src="{T._png_uri(ours, '.png')}" alt="The textura as built, each letter under Pugin's">
<p class="lede">Above, the plate; below, ours, each letter where his stands, at the same scale. On the first line they are in his plate's own
pixels; y and z, which he squeezed onto the second line, stand at full height, their heads level with his. Under his x is ours of his form
(<code>x.archaic</code>); the modern x, u, w and j, which he didn't draw, are set in the text above, and his ampersand isn't built yet.</p>
<h2>The pen</h2>
<p class="lede">Measured from the references: x-height {meas['x_height_px']} px; ascenders {meas['ascender_px']} px above the baseline, descenders {meas['descender_px']} px below;
upright stems {meas['stem_px']} px; the nib's edge at {meas['nib_angle_deg']}°, so the nib is about {meas['nib_width_px']} px wide; hairlines {meas['hairline_px']} px.
Settled by the fit, shared by every letter:</p>
<table>{fam_rows}</table>
<h2>The letters over Pugin's</h2>
<p class="lede">Orange: the path the nib follows. Red: the outline it leaves. Green dots: its nodes. Grey: Pugin's letter, flourishes included; the fit
leaves out his hairlines, which the plain forms don't have.</p>
<p class="lede">With the local proof server running (<code>font-proofs</code>: <code>tools/type/type.py serve</code>), each letter Pugin drew has
<b>Edit strokes</b>: drag a stroke's nodes, or set its settings, and the letter is drawn again as you go. Saving holds what you changed in the letter's
recipe, so every build keeps it (decision 0012). <button class="edit" data-edit-group="split_top">Edit the split top</button> tunes the
split top that b, d, h, k and l share, and the split bottom of q, which is the same turned upside down, on all six at once (p's is Josh's drawing).</p>
<div class="cards">{''.join(cards)}</div>
</main>
<div id="se" hidden>
<header><h3 id="se-title"></h3><span class="sp"></span>
<button data-act="undo">Undo</button><button data-act="reset">Back to saved</button><button data-act="save">Save</button>
<button data-act="rebuild">Save and rebuild</button><button data-act="close">Close</button></header>
<div id="se-status"></div>
<div class="body"><svg id="se-svg" xmlns="http://www.w3.org/2000/svg"></svg><div id="se-many"></div>
<aside><details><summary>How this letter is drawn</summary><p id="se-desc"></p></details>
<p class="se-help">Drag a node; arrow keys nudge it (Shift for more). Set the rest with their sliders. Blue: held. Red: changed, not yet saved.</p>
<div id="se-list"></div></aside></div>
</div>
<div id="pe" hidden>
<header><h3 id="pe-title"></h3><span class="sp"></span>
<label><input type="checkbox" data-show="ref" checked> Pugin</label><label><input type="checkbox" data-show="hand" checked> drawing</label>
<label><input type="checkbox" data-show="nibs" checked> nibs</label>
<button data-act="undo">Undo</button><button data-act="reset">Back to saved</button><button data-act="save">Save</button>
<button data-act="rebuild">Save and rebuild</button><button data-act="close">Close</button></header>
<div id="pe-status"></div>
<div class="body"><svg id="pe-svg" xmlns="http://www.w3.org/2000/svg"></svg>
<aside><p class="se-help">Each point: where the pen is, the nib's angle and how hard it's pressed. Drag a point to move it, the round end of
its nib to turn it. Double-click the path to add a point; Delete removes one; C makes it a corner. Arrow keys move it (Shift for more),
[ and ] turn the nib, &minus; and = change the pressure.</p>
<div id="pe-list"></div></aside></div>
</div>
<script>{(Path(__file__).parent / "textura_editor.js").read_text()}</script>
<script>{(Path(__file__).parent / "textura_pen.js").read_text()}</script>
</body></html>"""
    (d / "proof").mkdir(exist_ok=True)
    (d / "proof" / "index.html").write_text(page)
    print(f"  wrote {(d / 'proof' / 'index.html').relative_to(ROOT)} ({len(page) // 1024} KB)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["extract", "measure", "build", "proof"])
    ap.add_argument("family")
    ap.add_argument("--fit", metavar="LETTERS", help="build: fit only these letters (comma-separated glyph names, or letter:measurement "
                                                     "for one measurement; 'family' for the shared measurements; 'none' for none), leaving the rest as they stand")
    a = ap.parse_args()
    if a.command == "build":
        only = None if a.fit is None else [g for g in a.fit.split(",") if g and g != "none"]
        import textura_letters as TL
        unknown = {g.partition(":")[0] for g in only or []} - set(TL.LETTERS) - {"family"}
        if unknown:
            ap.error(f"no such letters: {', '.join(sorted(unknown))}")
        cmd_build(a.family, only)
    else:
        {"extract": cmd_extract, "measure": cmd_measure, "proof": cmd_proof}[a.command](a.family)


if __name__ == "__main__":
    main()
