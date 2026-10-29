"""Spacing and kerning for the Pugin fonts (the `spacing` settings in a family's source.json).

The white between two capitals is judged a pair at a time. On each line from the baseline to the
cap height, the gap between the left letter's right edge and the right letter's left edge is
measured. The pair's white is the mean of those gaps, each counted no further than `depth` beyond
the pair's closest approach: a deep bay reads about as open as a shallow one, because the eye
fills it. Judging pairs, not single letters, matters here because nearly every Lombardic capital
has curls at its corners: a round side beside a curled one leaves more white than either side
suggests alone.

The side bearings are fitted so that every pair of letters comes as near as it can to one target
white. The fit is robust (Huber): the few pairs far off, which kerning will take care of, don't
drag the rest. How tight the face sets is given by the side bearing a letter carries on average
(`mean_side_bearings`, both sides together). The pairs the side bearings leave more than
`kern_threshold` off the target are kerned to it, and no pair comes closer than `clearance` at its
closest approach, so curls never touch."""
from __future__ import annotations

import numpy as np

import geom as G


def profile(contours, zone, step=5.0):
    """A glyph's two side profiles: on each line across the zone, how far its left edge lies inside
    its leftmost point and its right edge inside its rightmost (inf where the line misses the
    glyph); and its leftmost and rightmost x."""
    polys = [G.sample(c, 30) for c in contours]
    pts = np.concatenate(polys)
    x_min, x_max = float(pts[:, 0].min()), float(pts[:, 0].max())
    ys = np.arange(zone[0] + step / 2, zone[1], step)
    left, right = np.full(len(ys), np.inf), np.full(len(ys), np.inf)
    for P in polys:
        Q = np.roll(P, -1, 0)
        p0, p1, q0, q1 = P[:, None, 0], P[:, None, 1], Q[:, None, 0], Q[:, None, 1]
        hit = ((p1 - ys) * (q1 - ys) <= 0) & (p1 != q1)        # edges × lines
        x = np.where(hit, p0 + (ys - p1) / np.where(hit, q1 - p1, 1) * (q0 - p0), np.nan)
        lo = np.where(hit.any(axis=0), np.nanmin(np.where(hit, x, np.inf), axis=0), np.inf)
        hi = np.where(hit.any(axis=0), np.nanmax(np.where(hit, x, -np.inf), axis=0), -np.inf)
        left = np.fmin(left, lo - x_min)
        right = np.fmin(right, x_max - hi)
    return {"left": left, "right": right, "x_min": x_min, "x_max": x_max}


def pair_white(a, b, depth):
    """Two glyphs' white with no side bearings, and their closest approach: a's right profile set
    against b's left, each line's gap counted no further than `depth` beyond the closest."""
    gap = a["right"] + b["left"]
    ok = np.isfinite(gap)
    closest = float(gap[ok].min())
    return float(np.minimum(np.where(ok, gap, np.inf), closest + depth).mean()), closest


def fit(profiles, letters, symmetric, mean_side_bearings, depth, huber=20.0):
    """Side bearings for the letters, fitted so every pair's white comes as near as it can to one
    target. Symmetric letters keep equal side bearings. Returns the left and right side bearings,
    the target, and each pair's (white with no side bearings, closest approach)."""
    n = len(letters)
    ix = {g: i for i, g in enumerate(letters)}
    white = {(a, b): pair_white(profiles[a], profiles[b], depth) for a in letters for b in letters}
    target = mean_side_bearings + float(np.mean([w for w, _ in white.values()]))
    rows, rhs = [], []
    for (a, b), (w, _) in white.items():          # a's right side bearing + b's left = target − white
        r = np.zeros(2 * n)
        r[n + ix[a]] += 1
        r[ix[b]] += 1
        rows.append(r)
        rhs.append(target - w)
    for g in letters:
        if g in symmetric:
            r = np.zeros(2 * n)
            r[ix[g]], r[n + ix[g]] = 10.0, -10.0
            rows.append(r)
            rhs.append(0.0)
    A, B = np.array(rows), np.array(rhs)
    wt = np.ones(len(B))
    for _ in range(25):
        sol = np.linalg.lstsq(A * wt[:, None], B * wt, rcond=None)[0]
        off = np.abs(A @ sol - B)
        wt = np.sqrt(np.where(off <= huber, 1.0, huber / np.maximum(off, 1e-9)))
    return {g: float(sol[ix[g]]) for g in letters}, {g: float(sol[n + ix[g]]) for g in letters}, target, white


def kern(white, letters, side_bearings, target, threshold, clearance):
    """Kerning for the pairs the side bearings leave more than `threshold` off the target, in steps
    of 5 units, and for any pair that would come closer than `clearance`. side_bearings maps each
    letter to its (left, right) side bearing as spaced."""
    out = {}
    for a in letters:
        for b in letters:
            w, closest = white[(a, b)]
            sb = side_bearings[a][1] + side_bearings[b][0]
            off = target - (sb + w)
            floor = clearance - (sb + closest)        # how much the pair must open to keep clear
            k = 5 * round(off / 5)
            if k < floor:
                k = 5 * int(np.ceil(floor / 5))
            if abs(k) >= threshold or (floor > 0 and k > 0):
                out[(a, b)] = int(k)
    return out


def respace(contours, lsb, rsb, symmetric=False):
    """Move the outline so its left edge sits lsb from the origin; return it with its advance width.
    A symmetric glyph keeps equal side bearings."""
    pts = np.concatenate([G.sample(c, 40) for c in contours])
    x_min, x_max = pts[:, 0].min(), pts[:, 0].max()
    if symmetric:
        lsb = rsb = (lsb + rsb) / 2
    lsb, rsb = int(round(lsb)), int(round(rsb))
    dx = lsb - int(round(x_min))
    moved = [[q + [dx, 0] for q in c] for c in contours]
    width = int(round(x_max)) + dx + rsb
    if symmetric:                       # keep the axis on a whole unit: the same white both sides
        width = 2 * int(round((int(round(x_min)) + int(round(x_max))) / 2 + dx))
    return moved, width, dx
