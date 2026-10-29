"""A broad nib, simulated (decision 0008): the pen a textura is written with.

The nib is a thin rectangle, `width` long and `thickness` thick, its long edge held at `angle`
degrees (rising to the right on the page) and never turned. A stroke is the ground the nib covers
as it moves along a path: the path's Minkowski sum with the nib. Its outline is exact. For each
edge of the nib, the path is cut wherever it runs parallel to that edge; along each piece the edge
sweeps a ribbon between two copies of the piece, shifted to the edge's ends, so the ribbon's sides
are the path's own curves, translated. The ribbons, and the nib at every node of the path, are
joined into one outline (skia-pathops). The outline is then cleaned: straight runs become single
lines, every extreme gets a node, nodes closer than a hair are merged, and outlines run clockwise
with their counters anticlockwise, as the Lombardic letters' do.

Coordinates are page pixels, y down, as in the references."""
from __future__ import annotations

import math

import numpy as np
import pathops
from fontTools.pens.recordingPen import RecordingPen

import geom as G
from construct import is_line, line


class Nib:
    def __init__(self, width, angle, thickness):
        a = math.radians(angle)
        u = np.array([math.cos(a), -math.sin(a)])      # along the edge, rising to the right
        v = np.array([math.sin(a), math.cos(a)])       # across it
        self.width, self.angle, self.thickness = width, angle, thickness
        self.u, self.v = u, v
        h, k = width / 2, thickness / 2
        self.corners = [-h * u - k * v, h * u - k * v, h * u + k * v, -h * u + k * v]


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _parallel_ts(P, e, eps=1e-4):
    """Where a cubic runs parallel to the vector e: the roots of cross(B'(t), e) inside (0, 1)."""
    c0, c1, c2 = _cross(P[1] - P[0], e), _cross(P[2] - P[1], e), _cross(P[3] - P[2], e)
    a, b, c = c0 - 2 * c1 + c2, 2 * (c1 - c0), c0
    if abs(a) < 1e-12:
        roots = [-c / b] if abs(b) > 1e-12 else []
    else:
        disc = b * b - 4 * a * c
        roots = [] if disc < 0 else [(-b + s * math.sqrt(disc)) / (2 * a) for s in (1, -1)]
    return sorted(r for r in roots if eps < r < 1 - eps)


def _pieces(P, ts):
    out, rest, done = [], np.asarray(P, float), 0.0
    for t in ts:
        a, rest = G.split(rest, (t - done) / (1 - done))
        out.append(a)
        done = t
    return out + [rest]


def _add(pen_path, runs):
    """One closed contour from a list of cubics, turned so it runs clockwise on the page."""
    if abs(G.signed_area(runs)) < 1e-6:
        return
    if G.signed_area(runs) < 0:
        runs = G.reverse(runs)
    pen = pen_path.getPen()
    pen.moveTo(tuple(runs[0][0]))
    for q in runs:
        pen.curveTo(tuple(q[1]), tuple(q[2]), tuple(q[3]))
    pen.closePath()


def stroke_region(path, nib: Nib) -> pathops.Path:
    """The region a nib covers moving along `path` (a list of cubics, each ending where the next
    begins), as a pathops Path of overlapping clockwise contours."""
    out = pathops.Path()
    nodes = [path[0][0]] + [q[3] for q in path]
    for n in nodes:
        _add(out, [line(n + a, n + b) for a, b in zip(nib.corners, nib.corners[1:] + nib.corners[:1])])
    for a, b in zip(nib.corners, nib.corners[1:] + nib.corners[:1]):
        e = b - a
        for q in path:
            for piece in _pieces(q, _parallel_ts(q, e)):
                if np.linalg.norm(np.diff(piece, axis=0), axis=1).sum() < 0.05:
                    continue            # a sliver between two cuts adds nothing
                runs = [piece + a, line(piece[3] + a, piece[3] + b), (piece + b)[::-1].copy(), line(piece[0] + b, piece[0] + a)]
                _add(out, runs)
    return out


def outline(strokes, nib: Nib, tol=0.6):
    """The outline of a letter written with `strokes` (each a path, a list of cubics) by one nib:
    the strokes' union, cleaned. Nodes closer than tol (a little over a font unit at the textura's
    scale) are merged, so none collapses when the outline is rounded to units. Returns contours as
    lists of cubics, outer ones clockwise."""
    region = pathops.Path()
    for path in strokes:
        region.addPath(stroke_region(path, nib))
    try:
        region = pathops.simplify(region, fix_winding=True)
    except pathops.PathOpsError:
        # near-coincident geometry can defeat the union: clean each stroke on its own and join them one
        # at a time, on a 1/64 px grid, and failing that with the points nudged by a thousandth of a pixel
        def joined(move):
            acc = None
            for path in strokes:
                sp = pathops.simplify(stroke_region([move(np.asarray(q, float)) for q in path], nib), fix_winding=True)
                acc = sp if acc is None else pathops.op(acc, sp, pathops.PathOp.UNION, fix_winding=True)
            return acc
        try:
            region = joined(lambda q: np.round(q * 64) / 64)
        except pathops.PathOpsError:
            rng = np.random.default_rng(0)
            region = joined(lambda q: q + rng.uniform(-1e-3, 1e-3, q.shape))
    rec = RecordingPen()
    region.draw(rec)
    contours, cur, start = [], [], None
    for op, args in rec.value:
        if op == "moveTo":
            cur, start = [], np.array(args[0], float)
            last = start
        elif op == "lineTo":
            p = np.array(args[0], float)
            cur.append(line(last, p))
            last = p
        elif op == "curveTo":
            pts = [np.array(a, float) for a in args]
            cur.append(np.array([last, *pts]))
            last = pts[-1]
        elif op == "qCurveTo":
            q1, q2 = np.array(args[0], float), np.array(args[-1], float)
            cur.append(np.array([last, last + 2 / 3 * (q1 - last), q2 + 2 / 3 * (q1 - q2), q2]))
            last = q2
        elif op in ("closePath", "endPath"):
            if np.linalg.norm(last - start) > 1e-6:
                cur.append(line(last, start))
            if cur:
                contours.append(cur)
    contours = [c for c in (clean(c, tol) for c in contours) if c and abs(G.signed_area(c)) > 4.0]
    return orient(contours)


def _straighten(q, tol):
    """A cubic within tol of the straight line between its ends becomes that line."""
    a, b = q[0], q[3]
    L = np.linalg.norm(b - a)
    if L < 1e-9:
        return q
    u = (b - a) / L
    off = max(abs(_cross(q[k] - a, u)) for k in (1, 2))
    inside = all(-tol <= np.dot(q[k] - a, u) <= L + tol for k in (1, 2))
    return line(a, b) if off < tol and inside else q


def clean(c, tol=0.3):
    """Merge nodes closer than tol, make near-straight curves lines, join a straight run into one
    line, and put a node at every extreme with its handle flat or upright."""
    reach = lambda q: float(np.linalg.norm(np.diff(np.asarray(q, float), axis=0), axis=1).sum())
    segs = [_straighten(np.asarray(q, float), tol / 3) for q in c if reach(q) > tol]
    if not segs:
        return []
    for i in range(len(segs)):            # close any gap a dropped sliver left
        segs[i] = segs[i].copy()
        nxt = segs[(i + 1) % len(segs)]
        if np.linalg.norm(segs[i][3] - nxt[0]) > 1e-9:
            m = (segs[i][3] + nxt[0]) / 2
            segs[i][2] += m - segs[i][3]
            segs[i][3] = m
            segs[(i + 1) % len(segs)] = nxt.copy()
            segs[(i + 1) % len(segs)][1] += m - nxt[0]
            segs[(i + 1) % len(segs)][0] = m
    merged = []
    for q in segs:
        if merged and is_line(q) and is_line(merged[-1]):
            p = merged[-1]
            d1, d2 = p[3] - p[0], q[3] - q[0]
            if abs(_cross(d1, d2)) < 1e-3 * np.linalg.norm(d1) * np.linalg.norm(d2) and np.dot(d1, d2) > 0:
                merged[-1] = line(p[0], q[3])
                continue
        merged.append(q)
    if len(merged) > 1 and is_line(merged[0]) and is_line(merged[-1]):
        d1, d2 = merged[-1][3] - merged[-1][0], merged[0][3] - merged[0][0]
        if abs(_cross(d1, d2)) < 1e-3 * np.linalg.norm(d1) * np.linalg.norm(d2) and np.dot(d1, d2) > 0:
            merged = [line(merged[-1][0], merged[0][3])] + merged[1:-1]
    out = []
    for q in merged:
        if is_line(q):
            out.append(q)
            continue
        rest, done = q, 0.0
        for t in G.extrema_ts(q, eps=0.02):
            a, rest = G.split(rest, (t - done) / (1 - done))
            d = G.bez_d(q, t)
            k = 0 if abs(d[0]) < abs(d[1]) else 1        # an x extreme is upright, a y extreme flat
            a[2][k] = a[3][k]
            rest[1][k] = rest[0][k]
            out.append(a)
            done = t
        out.append(rest)
    return out


def _inside(pt, c):
    poly = G.sample(c, 16)
    x, y = pt
    inside = False
    for (x0, y0), (x1, y1) in zip(poly, np.roll(poly, -1, 0)):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def orient(contours):
    """Outer contours clockwise on the page, counters (inside an odd number of others) anticlockwise."""
    out = []
    for i, c in enumerate(contours):
        depth = sum(_inside(G.sample(c, 4)[0], o) for j, o in enumerate(contours) if j != i)
        cw = G.signed_area(c) > 0
        out.append(c if cw == (depth % 2 == 0) else G.reverse(c))
    out.sort(key=lambda c: -abs(G.signed_area(c)))
    return out


def tidy_units(contours, flat_deg=2.0):
    """An outline after rounding to whole font units: segments that rounding collapsed to a point are
    dropped, and a handle within flat_deg of flat or upright is made exactly so (it was meant to be:
    the node is an extreme)."""
    out = []
    for c in contours:
        segs = [np.array(q, float) for q in c if np.abs(np.diff(np.asarray(q, float), axis=0)).sum() >= 1.0]
        for q in segs:
            for node, handle in ((0, 1), (3, 2)):
                d = q[handle] - q[node]
                if np.abs(d).sum() < 1e-9:
                    continue
                ang = np.degrees(np.arctan2(abs(d[1]), abs(d[0])))
                if 0 < ang < flat_deg:
                    q[handle][1] = q[node][1]
                elif 90 - flat_deg < ang < 90:
                    q[handle][0] = q[node][0]
        for i in range(len(segs)):                 # keep the contour closed
            segs[i][3] = segs[(i + 1) % len(segs)][0]
        if segs:
            out.append(segs)
    return out
