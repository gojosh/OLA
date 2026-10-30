"""A broad nib, simulated (decision 0008): the pen a textura is written with.

The nib is a thin rectangle, `width` long and `thickness` thick, its long edge held at `angle`
degrees (rising to the right on the page). A stroke is the ground the nib covers as it moves along
a path: the path's Minkowski sum with the nib. Its outline is exact. For each
edge of the nib, the path is cut wherever it runs parallel to that edge; along each piece the edge
sweeps a ribbon between two copies of the piece, shifted to the edge's ends, so the ribbon's sides
are the path's own curves, translated. The ribbons, and the nib at every node of the path, are
joined into one outline (skia-pathops). Where two strokes meet in a straight edge that their cuts
alone would leave stepped, the outline is trued to it (true_to). The outline is then cleaned: straight runs become single
lines, every extreme gets a node, nodes closer than a hair are merged, and outlines run clockwise
with their counters anticlockwise, as the Lombardic letters' do.

A Pen is a nib that turns as it goes down the page, as Pugin's does: held at one angle at the
heads and another at the feet, turned evenly between. Where a stroke's angle hardly changes along a
segment, the segment is drawn as above at its mean angle; along a straight segment that turns
further (a stem), the ground covered is the hull of the nib at its two ends; and a curve that turns
further is cut into pieces that don't. The nib at every node is set at that node's own angle, so
the cuts at a stroke's ends are exact.

A Stroke is a path written with less pressure (`pressure` below 1): the nib's width is that share of
its full width, its hairline unchanged, so the stroke is lighter all along. A stroke may instead be
written with the nib's tip alone (tip_region): a small round point a hairline across, so a fine
stroke is a hairline wide whichever way it goes, its edges true parallels of its path. A Dot is a pip, a round dot such as the tip leaves at
the end of a fine stroke; a Shape, any filled shape the outline takes as it is (the split top of an
ascender).

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


class Bumps:
    """A pressure along a stroke that is one steady level, with short bumps of more pressure at given
    places: at each, (s along the stroke, how much more, how far either side it reaches, px), the
    bump a bell by the length of path covered (Josh: "Pressure ... should be a straight line, with
    little pressure bumps at each turn, to produce the horns at the corners of the turns")."""

    def __init__(self, level, bumps):
        self.level, self.bumps = float(level), list(bumps)

    def at(self, stroke, s):
        l = stroke.length_at(s)
        out = np.full(l.shape, self.level)
        for at, height, reach in self.bumps:
            out += height * np.exp(-0.5 * ((l - stroke.length_at(at)[0]) / max(reach, 1e-6)) ** 2)
        return out


class Stroke(list):
    """A path (a list of cubics) written with less pressure: the nib narrowed to `pressure` of its
    width, its thickness, the hairline, unchanged (above 1, pressed harder, it spreads). The pressure
    may change along the path: then it is a list of (s, pressure), s running from 0 at the path's
    start to k at the end of its k-th cubic, and changes smoothly between, by the length of path
    covered (along, ramped_region). With `angle`, a list of (s, degrees), the
    scribe turns the pen along the stroke: the nib is held at those angles there and turned smoothly
    between, by the length of path covered (turned_angle), instead of at the pen's own angle for its
    height. Or, with `tip` (a
    radius), written with the nib's tip alone: a small round point (tip_region)."""

    def __init__(self, path, pressure=1.0, tip=None, angle=None):
        super().__init__(path)
        self.pressure, self.tip, self.angle = pressure, tip, angle
        self._lengths = None

    def length_at(self, s):
        """How far along the path s is (px): s runs from 0 at the start to k at the end of the k-th
        cubic. A nib turned or pressed along the stroke changes by the length covered, not by the
        cubic it is on, so it changes as evenly across a node as either side of it."""
        if self._lengths is None:
            u = np.linspace(0, 1, 65)
            tables = []
            for q in self:
                d = np.linalg.norm(np.diff(G.bez(np.asarray(q, float), u), axis=0), axis=1)
                tables.append(np.concatenate([[0], np.cumsum(d)]))
            starts = np.concatenate([[0], np.cumsum([t[-1] for t in tables])])
            self._lengths = (u, tables, starts)
        u, tables, starts = self._lengths
        s = np.atleast_1d(np.asarray(s, float))
        i = np.clip(np.floor(s).astype(int), 0, len(tables) - 1)
        out = np.empty(s.shape)
        for k in np.unique(i):
            m = i == k
            out[m] = starts[k] + np.interp(s[m] - k, u, tables[k])
        return out


def _by_length(stroke, knots, s):
    """A value set at points along a stroke ((s, value) each), at s (a number or an array), changing
    by the length covered."""
    if not hasattr(stroke, "length_at"):
        return along(knots, s)
    cache = stroke.__dict__.setdefault("_knots_by_length", {})
    key = id(knots)
    if key not in cache:                                    # where the knots fall, by length, worked out once
        cache[key] = _prepared(list(zip(stroke.length_at([k for k, _ in knots]), [v for _, v in knots])))
    out = _along(cache[key], stroke.length_at(s))
    return float(out[0]) if np.ndim(s) == 0 else out


def pressure_at(stroke, s=0.0):
    """A stroke's pressure at s along its path (see Stroke); 1.0 for a plain path."""
    pr = getattr(stroke, "pressure", 1.0)
    if np.isscalar(pr):
        return float(pr)
    if isinstance(pr, Bumps):
        out = pr.at(stroke, s)
        return float(out[0]) if np.ndim(s) == 0 else out
    return _by_length(stroke, pr, s)


def along(knots, s):
    """A value set at points along a stroke ((s, value) each), at s (a number, or an array): through
    each in turn, changing smoothly between them (a monotone cubic, so it never runs past one and
    back), and as fast on either side of each."""
    return _along(_prepared(knots), s)


def _prepared(knots):
    """The knots of `along`, with the slope at each (Fritsch-Carlson), ready to evaluate."""
    ss, vv = (np.asarray(v, float) for v in zip(*knots))
    if len(ss) == 1:
        return ss, vv, None, None
    h, d = np.diff(ss), np.diff(vv) / np.diff(ss)
    m = np.zeros_like(vv)
    m[0], m[-1] = d[0], d[-1]
    for k in range(1, len(vv) - 1):
        if d[k - 1] * d[k] > 0:
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
    return ss, vv, h, m


def _along(prep, s):
    ss, vv, h, m = prep
    x = np.asarray(s, float)
    if h is None:
        out = np.full(x.shape, vv[0])
    else:
        k = np.clip(np.searchsorted(ss, x) - 1, 0, len(ss) - 2)
        t = np.clip((x - ss[k]) / h[k], 0.0, 1.0)
        out = ((2 * t ** 3 - 3 * t ** 2 + 1) * vv[k] + (t ** 3 - 2 * t ** 2 + t) * h[k] * m[k]
               + (-2 * t ** 3 + 3 * t ** 2) * vv[k + 1] + (t ** 3 - t ** 2) * h[k] * m[k + 1])
    return float(out) if out.ndim == 0 else out


def turned_angle(stroke, s):
    """The nib's angle at s along a stroke the pen turns along (see Stroke): through each of its
    angles in turn, turning smoothly between them by the length covered (along)."""
    return _by_length(stroke, stroke.angle, s)


def ramped(stroke):
    """Whether a stroke's nib changes along it: its pressure, or its angle as the pen turns."""
    return not np.isscalar(getattr(stroke, "pressure", 1.0)) or getattr(stroke, "angle", None) is not None


def _unit_normal(v):
    n = np.array([v[1], -v[0]])
    return n / np.linalg.norm(n)


def offset(q, d, tol=0.1, depth=0):
    """The cubic q offset by d to one side (its normal, (dy, -dx)), as cubics: each control-polygon
    edge's line moved over by d and the new control points where those lines meet (Tiller and
    Hanson), the cubic halved until the result is within `tol` px of the true offset (a tenth of a
    pixel is a quarter of a font unit at the textura's scale)."""
    q = np.asarray(q, float)
    e = [q[1] - q[0], q[2] - q[1], q[3] - q[2]]
    tangent = G.bez_d(q, np.array([0.0, 1.0]))
    e[0] = e[0] if np.linalg.norm(e[0]) > 1e-9 else tangent[0]
    e[2] = e[2] if np.linalg.norm(e[2]) > 1e-9 else tangent[1]
    e[1] = e[1] if np.linalg.norm(e[1]) > 1e-9 else (e[0] + e[2]) / 2
    n = [_unit_normal(v) for v in e]
    base = [q[0] + d * n[0], q[1] + d * n[1], q[2] + d * n[2]]

    def meet(i, j, fallback):
        den = _cross(e[i], e[j])
        if abs(den) < 1e-9 * np.linalg.norm(e[i]) * np.linalg.norm(e[j]):
            return fallback
        return base[i] + e[i] * (_cross(base[j] - base[i], e[j]) / den)
    o = np.array([q[0] + d * n[0], meet(0, 1, q[1] + d * n[0]), meet(1, 2, q[2] + d * n[2]), q[3] + d * n[2]])
    ts = np.linspace(0, 1, 9)
    true = G.bez(q, ts) + d * np.array([_unit_normal(v) for v in G.bez_d(q, ts)])
    dense = G.bez(o, np.linspace(0, 1, 64))
    err = max(np.min(np.linalg.norm(dense - pt, axis=1)) for pt in true)
    if err <= tol or depth >= 5:
        return [o]
    a, b = G.split(q, 0.5)
    return offset(a, d, tol, depth + 1) + offset(b, d, tol, depth + 1)


def _arc(c, r, a0, a1):
    """A circular arc about c from angle a0 to a1 (radians, at most a quarter turn), as one cubic."""
    k = 4 / 3 * np.tan((a1 - a0) / 4) * r
    p0, p3 = c + r * np.array([np.cos(a0), np.sin(a0)]), c + r * np.array([np.cos(a1), np.sin(a1)])
    return np.array([p0, p0 + k * np.array([-np.sin(a0), np.cos(a0)]), p3 - k * np.array([-np.sin(a1), np.cos(a1)]), p3])


def tip_region(path, radius) -> pathops.Path:
    """The ground the nib's tip covers along `path` (a list of cubics, each running on smoothly into
    the next): a small round point of the given radius, so the stroke is the path offset by the
    radius to either side (offset), with round ends. Its edges are true parallels of its path,
    so they run on into a pip's round edge without a break."""
    qs = [np.asarray(q, float) for q in path]
    d0, d1 = G.bez_d(qs[0], np.array([0.0]))[0], G.bez_d(qs[-1], np.array([1.0]))[0]
    a_start, a_end = np.arctan2(d0[1], d0[0]), np.arctan2(d1[1], d1[0])
    left = [o for q in qs for o in offset(q, radius)]
    right = [o[::-1].copy() for q in reversed(qs) for o in reversed(offset(q, -radius))]
    # (dy, -dx) is a quarter turn back from the way the stroke goes: the end cap runs from there round
    # through the way it goes to the other side, and the start cap likewise round its back
    end = [_arc(qs[-1][3], radius, a_end - np.pi / 2, a_end), _arc(qs[-1][3], radius, a_end, a_end + np.pi / 2)]
    start = [_arc(qs[0][0], radius, a_start + np.pi / 2, a_start + np.pi), _arc(qs[0][0], radius, a_start + np.pi, a_start + 3 * np.pi / 2)]
    out = pathops.Path()
    _add(out, left + end + right + start)
    return out


class Shape(list):
    """A filled shape: a closed path of cubics that the outline takes as it is, rather than as ground
    a nib covers. It is listed and drawn like any stroke. It may have holes (`holes`: closed paths
    cut from it, such as the counter of a letter Josh has drawn)."""


class Dot(Shape):
    """A pip: a round dot of radius r about c, filled, such as the nib's tip leaves at the end of a
    fine stroke: a Shape, its own circle (four cubics)."""

    def __init__(self, c, r):
        c, k = np.asarray(c, float), 0.5523 * r
        p = [c + [r, 0], c + [0, r], c + [-r, 0], c + [0, -r]]
        t = [np.array([0, k]), np.array([-k, 0]), np.array([0, -k]), np.array([k, 0])]
        super().__init__([np.array([p[i], p[i] + t[i], p[(i + 1) % 4] - t[(i + 1) % 4], p[(i + 1) % 4]]) for i in range(4)])
        self.c, self.r = c, r


def pressed(nib, pressure):
    """The nib (a Nib or a Pen) under less pressure: narrower, as thick."""
    if pressure == 1.0:
        return nib
    if isinstance(nib, Nib):
        return Nib(nib.width * pressure, nib.angle, nib.thickness)
    return Pen(nib.width * pressure, nib.thickness, nib.top_angle, nib.bottom_angle, nib.y_top, nib.y_bottom)


class Pen:
    """A nib that turns as it goes down the page: at `top_angle` at or above y_top, at `bottom_angle`
    at or below y_bottom, and turned evenly between (y down)."""

    STEP = 1.0          # the most a piece of a stroke drawn at one angle may turn along its length (degrees)

    def __init__(self, width, thickness, top_angle, bottom_angle, y_top, y_bottom):
        self.width, self.thickness = width, thickness
        self.top_angle, self.bottom_angle, self.y_top, self.y_bottom = top_angle, bottom_angle, y_top, y_bottom

    def angle(self, y):
        f = np.clip((np.asarray(y, float) - self.y_top) / (self.y_bottom - self.y_top), 0.0, 1.0)
        return self.top_angle + f * (self.bottom_angle - self.top_angle)

    def at(self, y) -> Nib:
        return Nib(self.width, float(self.angle(y)), self.thickness)

    def corners(self, ys):
        """The nib's corners at each height in ys, as an array (len(ys), 4, 2)."""
        a = np.radians(self.angle(ys))
        u = np.stack([np.cos(a), -np.sin(a)], -1)
        v = np.stack([np.sin(a), np.cos(a)], -1)
        h, k = self.width / 2, self.thickness / 2
        return np.stack([-h * u - k * v, h * u - k * v, h * u + k * v, -h * u + k * v], 1)


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


def _footprint(out, n, nib: Nib):
    _add(out, [line(n + a, n + b) for a, b in zip(nib.corners, nib.corners[1:] + nib.corners[:1])])


def _ribbons(out, q, nib: Nib):
    """The ground each edge of a nib held at one angle sweeps along the cubic q."""
    for a, b in zip(nib.corners, nib.corners[1:] + nib.corners[:1]):
        e = b - a
        for piece in _pieces(q, _parallel_ts(q, e)):
            if np.linalg.norm(np.diff(piece, axis=0), axis=1).sum() < 0.05:
                continue            # a sliver between two cuts adds nothing
            runs = [piece + a, line(piece[3] + a, piece[3] + b), (piece + b)[::-1].copy(), line(piece[0] + b, piece[0] + a)]
            _add(out, runs)


def _hull(pts):
    """The convex hull of points, anticlockwise (monotone chain)."""
    pts = sorted(map(tuple, np.round(pts, 9)))
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and _cross(np.subtract(h[-1], h[-2]), np.subtract(p, h[-2])) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, hi = half(pts), half(pts[::-1])
    return [np.array(p) for p in lo[:-1] + hi[:-1]]


def stroke_region(path, nib) -> pathops.Path:
    """The region a nib (a Nib, or a turning Pen) covers moving along `path` (a list of cubics, each
    ending where the next begins), as a pathops Path of overlapping clockwise contours."""
    out = pathops.Path()
    nodes = [path[0][0]] + [q[3] for q in path]
    if not isinstance(nib, Pen):        # a Nib held at one angle
        for n in nodes:
            _footprint(out, n, nib)
        for q in path:
            _ribbons(out, q, nib)
        return out
    pen = nib
    for n in nodes:
        _footprint(out, n, pen.at(n[1]))
    for q in path:
        q = np.asarray(q, float)
        angles = pen.angle(G.bez(q, np.linspace(0, 1, 17))[:, 1])
        turn = float(angles.max() - angles.min())
        if turn <= pen.STEP:
            _ribbons(out, q, Nib(pen.width, float(angles.mean()), pen.thickness))
        elif is_line(q):                # a stem turning on the way down: the hull of the nib at its two ends
            cs = pen.corners([q[0][1], q[3][1]])
            hull = _hull(np.concatenate([q[0] + cs[0], q[3] + cs[1]]))
            _add(out, [line(a, b) for a, b in zip(hull, hull[1:] + hull[:1])])
        else:                           # a curve turning further: in pieces that don't
            k = int(math.ceil(turn / pen.STEP))
            for piece in _pieces(q, [i / k for i in range(1, k)]):
                _footprint(out, piece[3], pen.at(piece[3][1]))
                _ribbons(out, piece, Nib(pen.width, float(pen.angle(G.bez(piece, np.array([0.5]))[0, 1])), pen.thickness))
    return out


def _turned(stroke, s):
    """turned_angle at each of the positions s (an array)."""
    return np.atleast_1d(_by_length(stroke, stroke.angle, np.atleast_1d(s)))


def _corners_along(nib, stroke, q, i, t):
    """The corners (len(t), 4, 2) of the nib a stroke is written with, at parameters t of its i-th
    cubic q: its angle the pen's for the height, or as the scribe turns it (Stroke.angle); its width
    narrowed by the pressure there."""
    t = np.atleast_1d(np.asarray(t, float))
    pts = G.bez(q, t)
    if getattr(stroke, "angle", None) is not None:
        a = _turned(stroke, i + t)
    elif isinstance(nib, Pen):
        a = np.broadcast_to(nib.angle(pts[:, 1]), t.shape).astype(float)
    else:
        a = np.full(t.shape, nib.angle)
    pr = getattr(stroke, "pressure", 1.0)
    w = nib.width * (np.full(t.shape, float(pr)) if np.isscalar(pr) else np.atleast_1d(pressure_at(stroke, i + t)))
    r = np.radians(a)
    u = np.stack([np.cos(r), -np.sin(r)], -1)
    v = np.stack([np.sin(r), np.cos(r)], -1)
    h, k = (w / 2)[:, None], nib.thickness / 2
    return np.stack([-h * u - k * v, h * u - k * v, h * u + k * v, -h * u + k * v], 1)


def _trace(q, corner, t0, t1, tol=0.05, depth=0):
    """The path of one corner of the nib (corner: t -> its offsets) along the cubic q, from t0 to
    t1, as cubics within tol pixels of it: each a Hermite piece from the path's own ends and
    tangents, split where it strays."""
    eps = 1e-5
    f = lambda t: G.bez(q, t) + corner(t)
    ends = f(np.array([t0, t1]))
    dt = t1 - t0
    d = (f(np.array([t0 + eps, t1])) - f(np.array([t0, t1 - eps]))) / eps
    P = np.array([ends[0], ends[0] + d[0] * dt / 3, ends[1] - d[1] * dt / 3, ends[1]])
    us = np.array([0.25, 0.5, 0.75])
    if depth >= 7 or np.linalg.norm(G.bez(P, us) - f(t0 + us * dt), axis=1).max() <= tol:
        return [P]
    m = (t0 + t1) / 2
    return _trace(q, corner, t0, m, tol, depth + 1) + _trace(q, corner, m, t1, tol, depth + 1)


def ramped_region(path, nib, stroke) -> pathops.Path:
    """The region a nib (a Nib, or a turning Pen) covers moving along `path` while it changes
    along it: its pressure, or its angle as the scribe turns the pen (`stroke`'s, see Stroke). So
    the stroke widens or narrows evenly, without a step where the pressure changes (an i's light
    head running into its full stem), and a turning nib sweeps the curves it sweeps. As for a nib
    held at one angle and width (_ribbons), each edge of the nib sweeps the ground between the
    paths of its two corners; here those paths are traced as the nib changes and fitted with
    cubics, so the outline keeps the nib's corners and few nodes. Each piece is simplified on its
    own and the pieces joined one at a time: as the nib turns, an edge's ribbon can twist, and its
    far lobe, wound the other way, would cancel what it overlaps if all were simplified together."""
    out = None
    def add(runs):
        nonlocal out
        if abs(G.signed_area(runs)) < 0.05:     # a sliver where two of the paths meet: nothing to add
            return
        piece = pathops.Path()
        _add(piece, runs)
        try:
            piece = pathops.simplify(piece, fix_winding=True)
        except pathops.PathOpsError:            # nearly coincident curves: as a fine polygon instead
            pts = np.concatenate([G.bez(np.asarray(q, float), np.linspace(0, 1, 12)[:-1]) for q in runs])
            piece = pathops.Path()
            _add(piece, [line(m, n) for m, n in zip(pts, np.roll(pts, -1, 0))])
            piece = pathops.simplify(piece, fix_winding=True)
        out = piece if out is None else pathops.op(out, piece, pathops.PathOp.UNION, fix_winding=True)
    pr = stroke.pressure
    ks = ([] if np.isscalar(pr) else [b[0] for b in pr.bumps] if isinstance(pr, Bumps) else [s for s, _ in pr]) + [s for s, _ in (getattr(stroke, "angle", None) or [])]
    grid = np.linspace(0, 1, 65)
    for i, q in enumerate(path):
        q = np.asarray(q, float)
        cs = _corners_along(nib, stroke, q, i, np.array([0.0, 1.0]))
        for pt, c in zip(q[[0, 3]], cs):
            add([line(pt + a, pt + b) for a, b in zip(c, np.roll(c, -1, 0))])
        knots = {float(s - i) for s in ks if i < s < i + 1}                       # where a corner's path may turn sharply
        cg, dg = _corners_along(nib, stroke, q, i, grid), G.bez_d(q, grid)
        for a, b in zip(range(4), (1, 2, 3, 0)):
            # where the path runs along this edge of the nib, as the nib changes: there the ribbon would fold
            e = cg[:, b] - cg[:, a]
            cr = dg[:, 0] * e[:, 1] - dg[:, 1] * e[:, 0]
            folds = set()
            for j in np.nonzero(cr[:-1] * cr[1:] < 0)[0]:
                lo, hi, c_lo = grid[j], grid[j + 1], cr[j]
                for _ in range(30):
                    m = (lo + hi) / 2
                    cm = _corners_along(nib, stroke, q, i, m)[0]
                    dm = G.bez_d(q, np.array([m]))[0]
                    em = cm[b] - cm[a]
                    c_m = dm[0] * em[1] - dm[1] * em[0]
                    lo, hi, c_lo = (lo, m, c_lo) if c_m * c_lo < 0 else (m, hi, c_m)
                if 1e-4 < (lo + hi) / 2 < 1 - 1e-4:
                    folds.add((lo + hi) / 2)
            ts = sorted(knots | folds)
            for t0, t1 in zip([0.0] + ts, ts + [1.0]):
                if t1 - t0 < 1e-4:
                    continue
                ra = _trace(q, lambda t, a=a: _corners_along(nib, stroke, q, i, t)[:, a], t0, t1)
                rb = _trace(q, lambda t, b=b: _corners_along(nib, stroke, q, i, t)[:, b], t0, t1)
                add(ra + [line(ra[-1][3], rb[-1][3])] + G.reverse(rb) + [line(rb[0][0], ra[0][0])])
    return out


def dab(nib: Nib, a, b) -> "Shape":
    """The ground a nib held at one angle covers moving straight from a to b, as a filled shape: a
    short touch of the pen (the mark over i and j)."""
    hull = _hull(np.concatenate([np.asarray(a, float) + nib.corners, np.asarray(b, float) + nib.corners]))
    return Shape([line(m, n) for m, n in zip(hull, hull[1:] + hull[:1])])


def true_to(region, q, inside, depth=40.0):
    """The region trued to the edge q, a cubic (a straight one, or a curve) or a run of cubics, from
    one point to another: the ground between the edge and `inside` (a point of the ink on the edge's
    near side) filled, and the band beyond the edge, between its ends, cut away. Where two strokes
    meet in an edge that their cuts alone would leave stepped, or that the pen, turning, sweeps into
    a curve, or where one stroke's end lies under another."""
    qs, inside = np.asarray(q, float), np.asarray(inside, float)
    qs = list(qs) if qs.ndim == 3 else [qs]
    a, b = qs[0][0], qs[-1][3]
    out = np.array([b[1] - a[1], a[0] - b[0]]) / np.linalg.norm(b - a)
    if np.dot(inside - a, out) > 0:
        out = -out
    fill, band = pathops.Path(), pathops.Path()
    _add(fill, qs + [line(b, inside), line(inside, a)])
    _add(band, qs + [line(b, b + depth * out), line(b + depth * out, a + depth * out), line(a + depth * out, a)])
    region = pathops.op(region, fill, pathops.PathOp.UNION, fix_winding=True)
    return pathops.op(region, band, pathops.PathOp.DIFFERENCE, fix_winding=True)


def outline(strokes, nib, tol=0.6, edges=()):
    """The outline of a letter written with `strokes` (each a path, a list of cubics) by one nib (a
    Nib, or a turning Pen): the strokes' union, trued to any `edges` (each a straight edge's two
    ends, or a curved edge, and a point of the ink on its near side; true_to), and cleaned. Nodes
    closer than tol (a little over a font unit at the textura's scale) are merged, so none
    collapses when the outline is rounded to units.
    Returns contours as lists of cubics, outer ones clockwise."""
    # each stroke cleaned on its own, then the strokes joined one at a time. (Simplifying every stroke's
    # pieces together in one pass can silently drop a stroke: at a 50° nib it lost most of h's stem.)
    def joined(move):
        acc = None
        for path in strokes:
            qs = [move(np.asarray(q, float)) for q in path]
            if isinstance(path, Shape):
                sp = pathops.Path()
                _add(sp, qs)
                for h in getattr(path, "holes", ()):
                    hp = pathops.Path()
                    _add(hp, [move(np.asarray(q, float)) for q in h])
                    sp = pathops.op(sp, hp, pathops.PathOp.DIFFERENCE, fix_winding=True)
            elif getattr(path, "tip", None):
                sp = pathops.simplify(tip_region(qs, path.tip), fix_winding=True)
            elif ramped(path):
                sp = ramped_region(qs, nib, path)
            else:
                sp = pathops.simplify(stroke_region(qs, pressed(nib, getattr(path, "pressure", 1.0))), fix_winding=True)
            acc = sp if acc is None else pathops.op(acc, sp, pathops.PathOp.UNION, fix_winding=True)
        return acc
    try:
        region = joined(lambda q: q)
    except pathops.PathOpsError:
        # near-coincident geometry can defeat the union: try again on a 1/64 px grid, and failing that
        # with the points nudged by a thousandth of a pixel
        try:
            region = joined(lambda q: np.round(q * 64) / 64)
        except pathops.PathOpsError:
            rng = np.random.default_rng(0)
            region = joined(lambda q: q + rng.uniform(-1e-3, 1e-3, q.shape))
    for e in edges:         # (a, b, inside) for a straight edge, (q, inside) for a curved one
        region = true_to(region, line(e[0], e[1]) if len(e) == 3 else e[0], e[-1])
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
    return harmonize(out)


def harmonize(c, smooth_deg=10.0):
    """A contour whose nodes meet at a slight angle (under smooth_deg) made smooth: both handles at
    such a node turned onto one tangent, the average of the two, keeping their lengths and the node
    where it is; where one side is straight (a line, or a curve within a quarter pixel of one, like
    a stem's edge), only the other side's handle is turned, onto it; and likewise where one side's
    handle is flat or upright (the node is an extreme, and must stay one). A node whose turn would
    give either curve an extreme between its nodes is left as it is. Pieces of the
    outline from different strokes and corners meet at such angles, which read as an unsteady hand
    (Josh: "Why are we not ending up with a smooth outline? It looks like someone with a shaky hand
    tried to do it"). A larger angle is a corner of the letter or of the nib, and is kept."""
    segs = [np.array(q, float) for q in c]
    n = len(segs)
    if n < 2:
        return segs
    for j in range(n):
        a, b = segs[j - 1], segs[j]
        P = b[0]
        hin = a[2] if np.linalg.norm(a[3] - a[2]) > 1e-9 else a[0]
        hout = b[1] if np.linalg.norm(b[1] - b[0]) > 1e-9 else b[3]
        din, dout = P - hin, hout - P
        li, lo = np.linalg.norm(din), np.linalg.norm(dout)
        if li < 1e-9 or lo < 1e-9:
            continue
        ang = np.degrees(np.arccos(np.clip(np.dot(din, dout) / (li * lo), -1, 1)))
        if not 1e-3 < ang < smooth_deg:
            continue
        straight = lambda q: is_line(q) or _straighten(q, 0.25) is not q or np.linalg.norm(q[3] - q[0]) < 1e-9
        la, lb = straight(a), straight(b)
        if la and lb:
            continue
        axis = lambda v: min(abs(v[0]), abs(v[1])) < 1e-9
        la, lb = la or axis(din), lb or axis(dout)
        if la and lb:
            continue
        d = din / li if la else dout / lo if lb else (din / li + dout / lo) / np.linalg.norm(din / li + dout / lo)
        na, nb = a.copy(), b.copy()
        if not la:
            na[2] = P - d * np.linalg.norm(P - a[2])
        if not lb:
            nb[1] = P + d * np.linalg.norm(b[1] - P)
        if any(len(G.extrema_ts(new, eps=0.02)) > len(G.extrema_ts(old, eps=0.02)) for new, old in ((na, a), (nb, b))):
            continue
        segs[j - 1][:], segs[j][:] = na, nb
    return segs

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
