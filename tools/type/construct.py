"""The construction kit for the Pugin fonts (decision 0008).

Primitives are fitted as clean shapes to their averaged instances. Each letter's construction
(letters.py) draws it from the kit's parts; the letters' measurements are fitted to Pugin's drawings
in one solve, sharing the family's stem, curl and trefoil; the outlines are checked, written to the
font source (UFO), and compiled.

Coordinates are plate pixels, y down, until the font is written."""
from __future__ import annotations

import math

import cv2
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
from scipy.spatial import cKDTree

import geom as G


# ── The curl, as a type designer would draw it ────────────────────────────────

def fit_curl(consensus: np.ndarray) -> dict:
    """Fit the averaged curl with four nodes: the stroke's outer edge under the ball, the ball's back
    and crown (all extremes, with flat or upright handles), and the neck, a corner where the ball comes
    back to its stroke. Averaging blurs the notch at the neck, so the neck is put where the ball's side
    and the stroke's edge meet rather than on the blur. Segments run outer → back → crown → neck,
    relative to the outer node, in the template's orientation (ball at the lower left)."""
    pts = G.contours_from_coverage(consensus)[0]
    if G._poly_area(pts) < 0:
        pts = pts[::-1]                       # clockwise on screen: under, back, crown
    n = len(pts)
    iO, iT = int(np.argmax(pts[:, 1])), int(np.argmin(pts[:, 1]))
    iL = int(np.argmin(pts[:, 0]))
    x_cut = pts[:, 0].max() - 3               # the template's straight cut through the stroke
    i = iT
    while not (pts[(i + 1) % n, 1] < pts[i, 1] and pts[i, 0] > pts[iT, 0] + 10):
        i = (i + 1) % n
    iN = i                                    # the bottom of the notch
    run = lambda a, b: np.arange(a, b + 1) % n if b >= a else np.concatenate([np.arange(a, n), np.arange(0, b + 1)])
    ball = pts[run(iO, iN)]
    ball = ball[np.linalg.norm(ball - pts[iN], axis=1) > 3.0]
    k, edge = iN, []
    while pts[k, 0] < x_cut:
        edge.append(k)
        k = (k + 1) % n
    edge = pts[edge]
    edge = edge[np.linalg.norm(edge - pts[iN], axis=1) > 3.0]

    def chain(p):
        ox, oy, lx, ly, tx, ty, nx, ny, phi, _, h1, h2, h3, h4, h5, h6 = p
        O, L, T, N = np.array([ox, oy]), np.array([lx, ly]), np.array([tx, ty]), np.array([nx, ny])
        dn = np.array([math.cos(phi), math.sin(phi)])
        return [np.array([O, O + [-h1, 0], L + [0, h2], L]),
                np.array([L, L + [0, -h3], T + [-h4, 0], T]),
                np.array([T, T + [h5, 0], N - h6 * dn, N])]

    def resid(p):
        dense = G.sample(chain(p), 200)
        N, psi = np.array(p[6:8]), p[9]
        u = np.array([math.cos(psi), -math.sin(psi)])
        v = edge - N
        return np.concatenate([cKDTree(dense).query(ball)[0], v[:, 0] * u[1] - v[:, 1] * u[0],
                               0.5 * cKDTree(ball).query(dense[::4])[0]])

    p0 = [*pts[iO], *pts[iL], *pts[iT], *pts[iN], math.radians(60), math.radians(14), 20, 12, 12, 12, 10, 10]
    lb = [-np.inf] * 8 + [math.radians(10), math.radians(-10)] + [0.5] * 6
    ub = [np.inf] * 8 + [math.radians(90), math.radians(40)] + [80] * 6   # the ball's side may come down upright, no further
    p = least_squares(resid, p0, bounds=(lb, ub), x_scale="jac", loss="soft_l1", f_scale=0.5).x
    segs = chain(p)
    err = cKDTree(G.sample(segs, 300)).query(ball)[0]
    O = segs[0][0].copy()
    rel = [s - O for s in segs]
    return {
        "nodes": {"outer": [0.0, 0.0], "back": _r(rel[1][0]), "crown": _r(rel[2][0]), "neck": _r(rel[2][3])},
        "segments": [[_r(q) for q in s] for s in rel],
        "neck_arrival_deg": round(math.degrees(p[8]), 2),
        "averaged_stroke_angle_at_neck_deg": round(math.degrees(p[9]), 2),
        "outer_node_in_consensus_px": _r(O),
        "fit": {"mean_px": round(float(err.mean()), 3), "max_px": round(float(err.max()), 3),
                "points": int(len(ball)), "excluded": "3 px either side of the averaged notch, and the template's cut"},
    }


def _r(v, nd=3):
    return [round(float(x), nd) for x in v]


def _flat(nested: dict, pre="") -> dict:
    """{"a": {"b": 1}} → {"a.b": 1}, the inverse of _nest."""
    out = {}
    for k, v in nested.items():
        if isinstance(v, dict):
            out.update(_flat(v, f"{pre}{k}."))
        else:
            out[pre + k] = v
    return out


def _nest(flat: dict) -> dict:
    """{"a.b": 1} → {"a": {"b": 1}}, for recipes people read."""
    out = {}
    for k, v in flat.items():
        d = out
        *path, last = k.split(".")
        for q in path:
            d = d.setdefault(q, {})
        d[last] = v
    return out


def curl_parts(curl: dict):
    segs = [np.array(s, float) for s in curl["segments"]]
    return segs, np.array(curl["nodes"]["neck"], float)



# ── The kit: the parts letters are drawn with ─────────────────────────────────
# Headings are compass directions on screen, in degrees: 0 east, 90 south (y runs down), 180 west,
# 270 north. A construction joins parts into contours: clockwise on screen for a letter's outline,
# anticlockwise for its counters, so the ink is always on the right. Each segment carries a label
# (the part it belongs to) and the name of the node it starts from.

E, S, W, N = 0.0, 90.0, 180.0, 270.0


def hd(deg):
    r = math.radians(deg)
    return np.round(np.array([math.cos(r), math.sin(r)]), 12)   # exactly flat or upright at the compass points


def _unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-12)


def cubic(A, ha, B, hb, ta, tb):
    """A cubic leaving A on heading ha and arriving at B on heading hb (degrees, or vectors). The
    tensions ta and tb (0–1) are fractions of each handle's reach: as far as the point where the two
    tangent lines meet or, for an S-bend where they don't meet ahead, the chord's run along the
    heading, shared between the two handles. Within its reach a curve can't swell past its nodes."""
    A, B = np.asarray(A, float), np.asarray(B, float)
    u = hd(ha) if np.isscalar(ha) else _unit(ha)
    v = hd(hb) if np.isscalar(hb) else _unit(hb)
    d = B - A
    det = u[0] * v[1] - u[1] * v[0]
    s = r = -1.0
    if abs(det) > 1e-9:
        s = (d[0] * v[1] - d[1] * v[0]) / det
        r = (u[0] * d[1] - u[1] * d[0]) / det
    if s > 1e-6 and r > 1e-6:
        a, b = ta * s, tb * r
    else:
        ru, rv = max(abs(float(d @ u)), 1e-3), max(abs(float(d @ v)), 1e-3)
        a = ta * ru
        b = tb * max(rv - a * abs(float(u @ v)), 0.05 * rv)
    return np.array([A, A + a * u, B - b * v, B])


def ends(segs):
    """The first and last points of a run of segments, with the headings there (as vectors)."""
    a, b = segs[0], segs[-1]
    h0 = next(a[k] - a[0] for k in (1, 2, 3) if np.linalg.norm(a[k] - a[0]) > 1e-9)
    h1 = next(b[3] - b[k] for k in (2, 1, 0) if np.linalg.norm(b[3] - b[k]) > 1e-9)
    return a[0], _unit(h0), b[3], _unit(h1)


def line(A, B):
    A, B = np.asarray(A, float), np.asarray(B, float)
    return np.array([A, A + (B - A) / 3, A + 2 * (B - A) / 3, B])


def arc(c, r, a0, a1):
    """A circular arc from angle a0 to a1 (degrees on screen, either way round), as cubics split at
    each quarter, so the nodes fall on the circle's extremes whichever way the arc is turned."""
    c = np.asarray(c, float)
    up = a1 >= a0
    # an extreme within about a pixel of arc from an end becomes that end, rather than leaving a
    # sliver of a segment that rounding to font units would collapse
    snap = max(0.5, math.degrees(1.2 / max(r, 1e-6)))
    cuts = [a0]
    q = (math.floor(a0 / 90) + 1) * 90 if up else (math.ceil(a0 / 90) - 1) * 90
    while (q < a1 + snap) if up else (q > a1 - snap):
        if abs(q - a0) <= snap:
            cuts[0] = q
        elif abs(q - a1) <= snap:
            a1 = q
        elif (q < a1) if up else (q > a1):
            cuts.append(q)
        q += 90 if up else -90
    cuts.append(a1)
    out = []
    for x0, x1 in zip(cuts, cuts[1:]):
        k = 4 / 3 * math.tan(math.radians(x1 - x0) / 4) * r
        p0, p1 = c + r * hd(x0), c + r * hd(x1)
        out.append(np.array([p0, p0 + k * hd(x0 + 90), p1 - k * hd(x1 + 90), p1]))
    return out


# How a curl is turned: the template's ball sits at the lower left of a bar running right.
ORIENT = {
    "bl": np.eye(2),
    "br": np.diag([-1.0, 1.0]),
    "tl": np.diag([1.0, -1.0]),
    "tr": np.diag([-1.0, -1.0]),
    "foot-left": np.array([[0.0, 1.0], [-1.0, 0.0]]),   # at the foot of a stroke coming down, rolling out to the left
    "head-right": np.array([[0.0, -1.0], [1.0, 0.0]]),  # at the head of a stroke going up, rolling out to the right
    "foot-right": np.array([[0.0, -1.0], [-1.0, 0.0]]), # at the foot of a stroke coming down, rolling out to the right
    "head-left": np.array([[0.0, 1.0], [1.0, 0.0]]),    # at the head of a stroke going up, rolling out to the left
}


class Kit:
    """The primitives a construction places."""

    def __init__(self, curl: dict):
        self.curl_model = curl
        self.curl_segs = [np.array(s, float) for s in curl["segments"]]
        self.curl_nodes = {k: np.array(v, float) for k, v in curl["nodes"].items()}
        # the curl's ball as a circle, for curls drawn round (inside O and Q): its back and neck are
        # the ball's left and right extremes
        self.curl_ball_r = float(self.curl_nodes["neck"][0] - self.curl_nodes["back"][0]) / 2

    def curl(self, at, orient, k, theta, anchor="outer", whole=True, place="curl"):
        """The curl with its `anchor` node at `at`, turned by `orient` and scaled by k. Returns its
        segments in the order a clockwise outline meets them, their node names, the neck, and the
        heading of the outline at the neck: leaving it, when the outline goes outer → neck, or arriving,
        when a mirrored curl is met neck → outer. theta is the stroke's angle out of the neck above the
        template's bar, in degrees. whole=False leaves out the outer quarter, for a ball that sits on
        a stroke's corner rather than at the end of a bar."""
        M = ORIENT[orient]
        origin = np.asarray(at, float) - k * (M @ self.curl_nodes[anchor])
        segs = [origin + k * (q @ M.T) for q in self.curl_segs]
        names = [f"{place}: outer", f"{place}: back", f"{place}: crown"]
        if not whole:
            segs, names = segs[1:], names[1:]
        t = math.radians(theta)
        stroke = _unit(M @ np.array([math.cos(t), -math.sin(t)]))
        neck = segs[-1][3]
        if np.linalg.det(M) > 0:
            return segs, names, neck, stroke
        return G.reverse(segs), [f"{place}: neck"] + names[::-1][:-1], neck, -stroke


def trefoil(C, axis, r, d, enter, leave, place="trefoil"):
    """Three equal round lobes on the arms of a cross: the tip on `axis` (degrees on screen), one at
    each side square to it, every centre d from C. Pugin's trefoils are drawn freehand and vary; this
    one is exact, so it is the same wherever it is placed. A clockwise outline comes in on the first
    side lobe at `enter` degrees from that lobe's outward direction, runs round the three lobes, and
    goes out from the other side lobe at `leave`. The cusps between lobes and the joins are corners;
    the arcs are split at their extremes."""
    C = np.asarray(C, float)
    out_dirs = [axis - 90, axis, axis + 90]
    cs = [C + d * hd(a) for a in out_dirs]

    def cusp(c1, c2):
        m, half = (c1 + c2) / 2, np.linalg.norm(c2 - c1) / 2
        h = math.sqrt(max(r * r - half * half, 0.0))
        perp = _unit([-(c2 - c1)[1], (c2 - c1)[0]])
        a, b = m + h * perp, m - h * perp
        return a if np.linalg.norm(a - C) > np.linalg.norm(b - C) else b

    ang = lambda c, q: math.degrees(math.atan2(q[1] - c[1], q[0] - c[0]))
    k1, k2 = cusp(cs[0], cs[1]), cusp(cs[1], cs[2])
    a_in, a_out = out_dirs[0] + enter, out_dirs[2] + leave
    spans = [(cs[0], a_in, ang(cs[0], k1), "join"), (cs[1], ang(cs[1], k1), ang(cs[1], k2), "cusp"),
             (cs[2], ang(cs[2], k2), a_out, "cusp")]
    segs, names = [], []
    for c, a0, a1, first in spans:
        while a1 <= a0:
            a1 += 360
        while a1 - a0 > 360:
            a1 -= 360
        s = arc(c, r, a0, a1)
        segs += s
        names += [f"{place}: {first}"] + [f"{place}: lobe"] * (len(s) - 1)
    return segs, names, segs[0][0], segs[-1][3]


def two_lobe(c1, r, d, angle, enter, leave, place="two-lobe", r2=None):
    """Two round lobes, the second d from the first along `angle` (degrees on screen), close
    enough to overlap so the cusp between them is crisp. Pugin draws this terminal (a curl with a
    second ball beyond it) with lobes of uneven size and spacing; this one is exact. The lobes are
    equal unless r2 gives the second its own radius (L's tip: a broad crown and a ball). A clockwise
    outline comes in on the first lobe at the screen angle `enter` about its centre, runs over it to
    the cusp and round the second lobe, and leaves it at `leave`. Returns segments, node names, and
    the entry and exit points."""
    c1 = np.asarray(c1, float)
    r2 = r if r2 is None else r2
    u = hd(angle)
    c2 = c1 + d * u
    a = (r * r - r2 * r2 + d * d) / (2 * d)                  # how far along u the cusp lies from c1
    h = math.sqrt(max(r * r - a * a, 0.0))
    cusp = c1 + a * u + h * np.array([u[1], -u[0]])          # on the side a clockwise outline crosses over
    ang = lambda c, q: math.degrees(math.atan2(q[1] - c[1], q[0] - c[0]))
    a1 = ang(c1, cusp)
    while a1 <= enter:
        a1 += 360
    b0 = ang(c2, cusp)
    b1 = leave
    while b1 <= b0:
        b1 += 360
    s1, s2 = arc(c1, r, enter, a1), arc(c2, r2, b0, b1)
    names = [f"{place}: neck"] + [f"{place}: first lobe"] * (len(s1) - 1) + [f"{place}: cusp"] + [f"{place}: second lobe"] * (len(s2) - 1)
    return s1 + s2, names, s1[0][0], s2[-1][3]


# ── Measurements a construction asks for ──────────────────────────────────────

FAMILY = {  # name: (start, low, high, meaning)
    "stem_plain": (39.5, 30.0, 50.0, "half the stem's width in letters that are mostly stem: I, L (px)"),
    "stem_armed": (36.5, 30.0, 50.0, "half the stem's width in letters that carry arms, a shoulder or a wide bar: F, H, K, T (px)"),
    "curl": (1.0, 0.8, 1.25, "the curl's size, as a multiple of the averaged curl"),
    "trefoil_r": (18.0, 9.0, 28.0, "a trefoil lobe's radius (px)"),
    "trefoil_d": (22.0, 9.0, 36.0, "how far each trefoil lobe sits from the trefoil's centre (px)"),
    "ball_r": (21.0, 14.0, 28.0, "the radius of the balls that hang into O's and Q's counters (px)"),
    "two_lobe_r": (19.0, 12.0, 26.0, "the radius of both lobes of the two-lobe terminal (px)"),
    "two_lobe_spread": (1.9, 1.8, 1.97, "how far apart the two-lobe terminal's lobes are, in radii: close to two, so they read as two balls with a deep cusp between"),
}


class Params:
    """Hands a construction its measurements. Called once with no values to learn what the
    construction asks for (each with a starting value and bounds), then with the fitted values.
    Family measurements are shared by every letter unless `local` is set."""

    def __init__(self, glyph: str, values: dict | None = None, local: bool = False, fill: bool = False):
        self.glyph, self.values, self.local, self.fill, self.spec = glyph, values, local, fill, {}

    def _get(self, key, init, lo, hi):
        lo, hi = min(lo, init), max(hi, init)
        self.spec.setdefault(key, (float(init), float(lo), float(hi)))
        if self.values is None or (self.fill and key not in self.values):
            return float(init)          # `fill`: a glyph built from another's values takes its own starting value for the rest
        return float(self.values[key])

    def x(self, name, init, span=30.0):
        """A position or length in plate pixels."""
        return self._get(f"{self.glyph}:{name}", init, init - span, init + span)

    def length(self, name, init, lo, hi):
        """A length in plate pixels, with explicit bounds."""
        return self._get(f"{self.glyph}:{name}", init, lo, hi)

    def t(self, name, init=0.5):
        """A handle tension. Never shorter than a fifth of its reach: a near-zero handle at a smooth
        node turns the curve so fast that the join reads as a kink."""
        return self._get(f"{self.glyph}:{name}", init, 0.2, 1.0)

    def ang(self, name, init, lo, hi):
        """An angle in degrees."""
        return self._get(f"{self.glyph}:{name}", init, lo, hi)

    def fam(self, name):
        init, lo, hi, _ = FAMILY[name]
        key = f"{self.glyph}:family.{name}" if self.local else f"family.{name}"
        return self._get(key, init, lo, hi)


def mirror_half(half, axis_x, end_name):
    """A symmetric outline from its left half: the half, then its mirror image run backwards.
    end_name names the node on the axis where the half ends."""
    segs = [q for q, _, _ in half]
    right = G.reverse([q * [-1, 1] + [2 * axis_x, 0] for q in segs])
    flip = lambda s: s.replace("left", "\0").replace("right", "left").replace("\0", "right")
    labels = [l for _, l, _ in half]
    names = [nm for _, _, nm in half]
    r_names = [flip(nm) for nm in (names[1:] + [end_name])[::-1]]
    return list(zip(segs, labels, names)) + list(zip(right, [flip(l) for l in labels[::-1]], r_names))


def mirror_copy(run, axis_x):
    """A closed contour's mirror image about x = axis_x, as a contour of its own, run the same way
    round (a counter stays a counter), with left and right swapped in its names."""
    n = len(run)
    segs = G.reverse([q * [-1, 1] + [2 * axis_x, 0] for q, _, _ in run])
    flip = lambda s: s.replace("left", "\0").replace("right", "left").replace("\0", "right")
    # the k-th reversed segment starts where the original's (n - k)-th started
    return [(segs[k], flip(run[n - 1 - k][1]), flip(run[(n - k) % n][2])) for k in range(n)]


def cross_x(P, x):
    """Where a cubic crosses the upright x: its t in [0, 1] (the nearest end if it doesn't)."""
    c = np.array([-P[0][0] + 3 * P[1][0] - 3 * P[2][0] + P[3][0], 3 * P[0][0] - 6 * P[1][0] + 3 * P[2][0],
                  -3 * P[0][0] + 3 * P[1][0], P[0][0] - x])
    roots = [r.real for r in np.roots(c) if abs(r.imag) < 1e-9 and -1e-9 <= r.real <= 1 + 1e-9]
    if roots:
        return float(np.clip(min(roots, key=lambda t: abs(t - 0.5)), 0, 1))
    return 0.0 if abs(P[0][0] - x) < abs(P[3][0] - x) else 1.0


def crossings(A, B, n=48):
    """Where two runs of cubics cross: (i, ta, j, tb, point) for each crossing, A[i] at ta meeting
    B[j] at tb. Found on their polylines and refined by Newton's method."""
    ts = np.linspace(0, 1, n + 1)
    out = []
    for i, qa in enumerate(A):
        pa = G.bez(qa, ts)
        for j, qb in enumerate(B):
            pb = G.bez(qb, ts)
            if (pa.max(0) < pb.min(0)).any() or (pb.max(0) < pa.min(0)).any():
                continue
            q0, e = pb[:-1], pb[1:] - pb[:-1]
            for u in range(n):
                d, w = pa[u + 1] - pa[u], q0 - pa[u]
                den = d[0] * e[:, 1] - d[1] * e[:, 0]
                ok = np.abs(den) > 1e-12
                den = np.where(ok, den, 1.0)
                s = (w[:, 0] * e[:, 1] - w[:, 1] * e[:, 0]) / den
                r = (w[:, 0] * d[1] - w[:, 1] * d[0]) / den
                for v in np.nonzero(ok & (s >= 0) & (s < 1) & (r >= 0) & (r < 1))[0]:
                    t1, t2 = ts[u] + s[v] / n, ts[v] + r[v] / n
                    for _ in range(8):
                        F = G.bez(qa, t1) - G.bez(qb, t2)
                        J = np.column_stack([G.bez_d(qa, t1), -G.bez_d(qb, t2)])
                        if abs(np.linalg.det(J)) < 1e-12:
                            break
                        t1, t2 = np.clip(np.array([t1, t2]) - np.linalg.solve(J, F), 0, 1)
                    pt = G.bez(qa, t1)
                    if all(np.linalg.norm(pt - o[4]) > 0.5 for o in out):
                        out.append((i, float(t1), j, float(t2), pt))
    return out


def cut(run, i, t):
    """A run of (segment, part, name) cut at segment i, t: the run before the cut and after it.
    A cut within a hair of a node falls on the node, so no sliver of a segment is left."""
    q = np.asarray(run[i][0], float)
    if t < 1e-3:
        return run[:i], run[i:]
    if t > 1 - 1e-3:
        return run[:i + 1], run[i + 1:]
    a, b = G.split(q, t)
    return run[:i] + [(a, run[i][1], run[i][2])], [(b, run[i][1], None)] + run[i + 1:]


# ── Fitting letters to Pugin's ────────────────────────────────────────────────

def signed_distance(alpha: np.ndarray, z=4):
    """Distance to the coverage's 0.5 edge in pixels: positive outside the ink, negative inside."""
    big = cv2.GaussianBlur(cv2.resize(alpha, None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC), (0, 0), z * 0.7)
    ins = (big >= 0.5).astype(np.uint8)
    sdf = (cv2.distanceTransform(1 - ins, cv2.DIST_L2, 5) - cv2.distanceTransform(ins, cv2.DIST_L2, 5)) / z
    return lambda q: map_coordinates(sdf, [(q[:, 1] + 0.5) * z - 0.5, (q[:, 0] + 0.5) * z - 0.5], order=1, mode="nearest")


def reference_edges(alpha: np.ndarray, min_area=400.0):
    """The letter's edges: its outline and counters, without the specks and pinholes of the print."""
    return [c for c in G.contours_from_coverage(alpha) if abs(G._poly_area(c)) > min_area]


def all_segs(built):
    return [q for c in built["contours"] for q, _, _ in c]


def sample_fixed(built, n_outline=900, n_counter=400):
    """Points along each contour, a fixed number per contour, so the fit's residuals keep their
    count when a part (an arc split at its extremes) changes how many segments it has."""
    out = []
    for i, c in enumerate(built["contours"]):
        segs = [q for q, _, _ in c]
        u = np.linspace(0, len(segs), n_outline if i == 0 else n_counter, endpoint=False)
        j = np.minimum(u.astype(int), len(segs) - 1)
        t = (u - j)[:, None]
        P = np.array(segs)[j]
        out.append((1 - t) ** 3 * P[:, 0] + 3 * (1 - t) ** 2 * t * P[:, 1] + 3 * (1 - t) * t ** 2 * P[:, 2] + t ** 3 * P[:, 3])
    return np.concatenate(out)


def fit_letters(letters: dict, refs: dict, kit: Kit, local=False, edge_points=1500, start=None, fixed=None):
    """Fit the letters' measurements to Pugin's drawings in one solve. Family measurements (stem,
    curl, trefoil) are shared by every letter, so they settle where the alphabet agrees, unless
    `local` lets each letter have its own. Residuals run both ways: the outline onto his edge, and his
    edge onto the outline. A robust loss keeps his accidents from pulling a whole letter.
    `start` holds values to begin from (the last build's), in place of each construction's own
    starting values; a measurement it doesn't have starts from the construction's. `fixed` holds
    values that are not fitted at all (the family's, once settled)."""
    fixed = fixed or {}
    from scipy.sparse import lil_matrix
    spec = {}
    for g, fn in letters.items():
        p = Params(g, None, local)
        fn(p, kit)
        spec.update(p.spec)
    keys = [k for k in spec if k not in fixed]
    lb = np.array([spec[k][1] for k in keys])
    ub = np.array([spec[k][2] for k in keys])
    x0 = np.array([(start or {}).get(k, spec[k][0]) for k in keys], float)
    x0 = np.clip(x0, lb, ub)
    data = {}
    for g in letters:
        e = np.concatenate(reference_edges(refs[g]))
        data[g] = (signed_distance(refs[g]), e[np.linspace(0, len(e) - 1, min(edge_points, len(e))).astype(int)], refs[g].shape)

    def glyph_res(g, vals):
        built = letters[g](Params(g, vals, local), kit)
        dense = sample_fixed(built)
        sd, edge, (h, w) = data[g]
        # where the frame of the plate cut a reference (W.1's first curl), the construction runs on past
        # its edge, and there is nothing there to compare it with
        inside = (dense[:, 0] >= 0.5) & (dense[:, 0] <= w - 1.5) & (dense[:, 1] >= 0.5) & (dense[:, 1] <= h - 1.5)
        return np.concatenate([np.where(inside, sd(dense), 0.0), cKDTree(dense).query(edge)[0], 20 * swelling(built)])

    def resid(x):
        vals = {**fixed, **dict(zip(keys, x))}
        return np.concatenate([glyph_res(g, vals) for g in letters])

    start = {**fixed, **dict(zip(keys, x0))}
    sizes = [len(glyph_res(g, start)) for g in letters]
    sparsity = lil_matrix((sum(sizes), len(keys)), dtype=int)
    r0 = 0
    for g, n in zip(letters, sizes):
        cols = [i for i, k in enumerate(keys) if k.startswith(g + ":") or k.startswith("family.")]
        sparsity[r0:r0 + n, cols] = 1
        r0 += n
    # Pugin's edge and the nearest-point distances are a little rough at the pixel scale, so the
    # derivatives are taken over steps of about a tenth of a pixel, and the solve is restarted until
    # it stops improving.
    x, nfev, cost = x0, 0, None
    for _ in range(6):
        r = least_squares(resid, x, bounds=(lb, ub), jac_sparsity=sparsity, x_scale=(ub - lb) / 10, diff_step=5e-4,
                          loss="soft_l1", f_scale=1.0, max_nfev=400)
        x, nfev = r.x, nfev + r.nfev
        if cost is not None and cost - r.cost < 1e-3 * cost:
            cost = r.cost
            break
        cost = r.cost
    vals = {**{k: float(v) for k, v in fixed.items()}, **{k: float(v) for k, v in zip(keys, x)}}
    # a free heading within 2° of flat or upright is meant to be flat or upright: the node is an extreme
    for k, v in vals.items():
        if k.endswith("_heading") and abs(v - 90 * round(v / 90)) < 2:
            vals[k] = 90.0 * round(v / 90)
    at_bounds = [k for k, v, lo, hi in zip(keys, x, lb, ub) if min(v - lo, hi - v) < 1e-3 * max(1.0, hi - lo)]
    return vals, at_bounds, {"evaluations": int(nfev), "cost": float(cost)}


def alone_fit(job):
    """One letter fitted alone, with its own family measurements. A top-level function so the
    build can run several in separate processes."""
    import letters as LT
    g, alpha, curl, start = job
    kit = Kit(curl)
    v, _, _ = fit_letters({g: LT.LETTERS[g]}, {g: alpha}, kit, local=True, start=start)
    built = LT.LETTERS[g](Params(g, v, local=True), kit)
    return {"family": {k.split("family.")[1]: round(x, 3) for k, x in v.items() if "family." in k},
            "values": {k: x for k, x in v.items() if "family." not in k},
            "mean_px": deviation(built, alpha)["overall"]["mean_px"]}


def refine_fit(job):
    """One letter fitted with the family's measurements held at their settled values, starting from
    its own fit alone. A top-level function so the build can run several in separate processes."""
    import letters as LT
    g, alpha, curl, start, fixed = job
    kit = Kit(curl)
    v, at_bounds, info = fit_letters({g: LT.LETTERS[g]}, {g: alpha}, kit, start=start, fixed=fixed)
    return {"values": {k: x for k, x in v.items() if not k.startswith("family.")},
            "at_bounds": at_bounds, "evaluations": info["evaluations"]}


def swelling(built):
    """For each contour, how far its curves swell past their own end nodes (pixels): zero when
    every node sits at an extreme."""
    out = []
    for c in built["contours"]:
        total = 0.0
        for q, _, _ in c:
            pts = G.bez(q, np.linspace(0, 1, 24))
            lo, hi = np.minimum(q[0], q[3]), np.maximum(q[0], q[3])
            total += float(np.clip(lo - pts, 0, None).max() + np.clip(pts - hi, 0, None).max())
        out.append(total)
    return np.array(out)


def deviation(built, alpha: np.ndarray) -> dict:
    """How far Pugin's edge lies from the construction, overall and part by part, beside how far his
    edge wobbles about its own smoothed course (the floor no clean curve can go below)."""
    refs = reference_edges(alpha)
    ref = np.concatenate(refs)
    per = 200
    segs = all_segs(built)
    labels = [l for c in built["contours"] for _, l, _ in c]
    dense = np.concatenate([G.bez(P, np.linspace(0, 1, per)) for P in segs])
    lab = np.repeat(np.array(labels), per)
    dd, ii = cKDTree(dense).query(ref)
    stats = lambda v: {"mean_px": round(float(v.mean()), 2), "p95_px": round(float(np.percentile(v, 95)), 2),
                       "max_px": round(float(v.max()), 2)}
    parts = {}
    for part in dict.fromkeys(labels):
        sel = lab[ii] == part
        if sel.any():
            parts[part] = stats(dd[sel])
    wob = []
    for c in refs:
        step = np.median(np.linalg.norm(np.diff(c, axis=0), axis=1))
        k = max(1, int(round(6 / step)))
        w = np.exp(-0.5 * (np.arange(-3 * k, 3 * k + 1) / k) ** 2)
        w /= w.sum()
        sm = sum(np.roll(c, o, 0) * wi for o, wi in zip(range(-3 * k, 3 * k + 1), w))
        wob.append(cKDTree(sm).query(c)[0])
    sd = signed_distance(alpha)(G.sample(segs, 60))
    return {"overall": stats(dd), "by_part": parts, "wobble_of_pugins_edge": stats(np.concatenate(wob)),
            "construction_outside_ink_max_px": round(float(sd.max()), 2),
            "construction_inside_ink_max_px": round(float(-sd.min()), 2), "edge_points": int(len(ref))}


# ── Checks ────────────────────────────────────────────────────────────────────

def _swell(P):
    pts = G.bez(P, np.linspace(0, 1, 64))
    lo, hi = np.minimum(P[0], P[3]), np.maximum(P[0], P[3])
    return float(max(np.clip(lo - pts, 0, None).max(), np.clip(pts - hi, 0, None).max()))


def check_contour(segs, names, smooth_deg=0.5, swell_tol=0.0) -> dict:
    """The rules a type designer's outline keeps: no curve swells past its end nodes (so every node
    sits at an extreme), handles at an extreme lie flat or upright, and every join is smooth unless
    it's meant to be a corner."""
    swells = [names[i] for i, P in enumerate(segs) if G.extrema_ts(P) and (swell_tol <= 0 or _swell(P) > swell_tol)]
    corners, skew, degenerate = [], [], []
    for i, P in enumerate(segs):
        prev = segs[i - 1]
        tin = next((prev[3] - prev[k] for k in (2, 1, 0) if np.linalg.norm(prev[3] - prev[k]) > 1e-9), None)
        tout = next((P[k] - P[0] for k in (1, 2, 3) if np.linalg.norm(P[k] - P[0]) > 1e-9), None)
        if tin is None or tout is None:
            degenerate.append(names[i])
            continue
        ang = math.degrees(math.acos(np.clip(np.dot(tin, tout) / (np.linalg.norm(tin) * np.linalg.norm(tout)), -1, 1)))
        if ang > smooth_deg:
            corners.append({"node": names[i], "turn_deg": round(ang, 1)})
            continue
        for h in (tin, tout):
            a = math.degrees(math.atan2(abs(h[1]), abs(h[0])))
            if 1e-6 < a < 2 or 88 < a < 90 - 1e-6:
                skew.append(names[i])
    return {"segments": len(segs), "curves_swelling_past_nodes": swells, "corners": corners,
            "nearly_flat_handles": sorted(set(skew)), "degenerate_segments": degenerate}


def check_outline(contours, names, smooth_deg=0.5, swell_tol=0.0) -> dict:
    """check_contour over every contour of a glyph. In whole font units a smooth join on a slant can
    kink by a few degrees where a handle is only ten or so units long, and a curve can poke a
    fraction of a unit past its node, so the font's check allows up to 3° and half a unit."""
    parts = [check_contour(c, n, smooth_deg, swell_tol) for c, n in zip(contours, names)]
    out = {"contours": len(parts), "segments": sum(p["segments"] for p in parts),
           "curves_swelling_past_nodes": [x for p in parts for x in p["curves_swelling_past_nodes"]],
           "corners": [x for p in parts for x in p["corners"]],
           "nearly_flat_handles": sorted({x for p in parts for x in p["nearly_flat_handles"]}),
           "degenerate_segments": [x for p in parts for x in p["degenerate_segments"]]}
    out["ok"] = not out["curves_swelling_past_nodes"] and not out["nearly_flat_handles"] and not out["degenerate_segments"]
    return out


# ── Font source ───────────────────────────────────────────────────────────────

def to_units(built, scale, lsb):
    """The outline in font units: y up, the baseline at the bottom curls' outer edge, rounded to
    whole units. A symmetric letter is rounded on its left half and mirrored about an axis on a whole
    unit, so it stays exactly symmetric. Returns contours, advance width, and where the font's x = 0
    falls on the plate."""
    base = built["baseline"]
    pts = G.sample(all_segs(built), 40)
    x_min, x_max = pts[:, 0].min(), pts[:, 0].max()
    conv = lambda q, x0, u0: np.round(np.column_stack([(q[:, 0] - x0) * scale + u0, (base - q[:, 1]) * scale]))
    halves = built.get("halves") or ([built["half"]] if built.get("half") else None)
    if halves:
        # contours given as halves are mirrored on a whole unit; a None takes the contour as built
        ax = built["axis"]
        axis_u = int(round(lsb + (ax - x_min) * scale))
        out = []
        for i, half in enumerate(halves):
            if half is None:
                out.append([conv(q, ax, axis_u) for q, _, _ in built["contours"][i]])
                continue
            left = [conv(q, ax, axis_u) for q, _, _ in half]
            out.append(left + G.reverse([q * [-1, 1] + [2 * axis_u, 0] for q in left]))
        return out, 2 * axis_u, ax - axis_u / scale
    contours = [[conv(q, x_min, lsb) for q, _, _ in c] for c in built["contours"]]
    return contours, int(round((x_max - x_min) * scale + 2 * lsb)), x_min - lsb / scale


# ── Adjustments by hand ───────────────────────────────────────────────────────

def mirrored_counts(built):
    """For each contour, how many segments its left half has if it is mirrored, else None."""
    halves = built.get("halves") or ([built["half"]] if built.get("half") else None)
    if not halves:
        return [None] * len(built["contours"])
    return [len(h) if h is not None else None for h in halves]


def adjust(built, points):
    """Apply recorded adjustments (moves of single control points, in plate pixels, made by hand on
    the proof page) to a built glyph, after its fit. Each names the node of the segment it belongs
    to; one whose node no longer matches (the construction has changed since) is skipped and
    reported. Lines stay lines. In a mirrored contour only the left half is adjusted; the nodes on
    the axis stay on it, their handles stay flat, and the right half is mirrored again from the left.
    Returns (applied, stale)."""
    if not points:
        return 0, []
    conts, counts, axis = built["contours"], mirrored_counts(built), built.get("axis")
    lines = {(c, s) for c, cont in enumerate(conts) for s, (q, _, _) in enumerate(cont) if is_line(q)}
    applied, stale = 0, []
    for e in points:
        c, s, k = e["contour"], e["segment"], e["point"]
        if not (c < len(conts) and s < len(conts[c]) and conts[c][s][2] == e["node"] and (counts[c] is None or s < counts[c])):
            stale.append(e)
            continue
        q, label, name = conts[c][s]
        q = np.array(q, float)
        q[k] += (e["dx"], e["dy"])
        conts[c][s] = (q, label, name)
        applied += 1
    for c, cont in enumerate(conts):
        for s, (q, label, name) in enumerate(cont):
            if (c, s) in lines:
                q = np.array(q, float)
                q[1], q[2] = q[0] + (q[3] - q[0]) / 3, q[0] + 2 * (q[3] - q[0]) / 3
                cont[s] = (q, label, name)
        n = counts[c]
        if n is None:
            continue
        q0, qn = np.array(cont[0][0], float), np.array(cont[n - 1][0], float)
        q0[0][0], q0[1][1] = axis, q0[0][1]
        qn[3][0], qn[2][1] = axis, qn[3][1]
        cont[0], cont[n - 1] = (q0, cont[0][1], cont[0][2]), (qn, cont[n - 1][1], cont[n - 1][2])
        for i in range(n):
            j = 2 * n - 1 - i
            cont[j] = ((cont[i][0] * [-1, 1] + [2 * axis, 0])[::-1].copy(), cont[j][1], cont[j][2])
        half = built["halves"][c] if built.get("halves") else built["half"]
        for i in range(n):
            half[i] = (cont[i][0], half[i][1], half[i][2])
    return applied, stale


def add_extremes(built, tol=0.2):
    """After moves by hand: where a curve now bulges past its nodes by more than tol pixels, split it
    at the extremes inside it, so every extreme is a node again. The shape is unchanged; the new
    node's handles are set exactly flat or upright. A mirrored contour is split on its left half and
    mirrored again. Returns the names of the nodes added."""
    added = []

    def split_run(run):
        out = []
        for q, label, name in run:
            q = np.array(q, float)
            ts = [t for t in G.extrema_ts(q) if 0.02 < t < 0.98]
            if not ts or _swell(q) <= tol:
                out.append((q, label, name))
                continue
            rest, done = q, 0.0
            pieces = []
            for t in sorted(ts):
                a, rest = G.split(rest, (t - done) / (1 - done))
                d = G.bez_d(q, t)
                k = 0 if abs(d[0]) < abs(d[1]) else 1      # an x extreme is upright, a y extreme flat
                a[2][k] = a[3][k]
                rest[1][k] = rest[0][k]
                pieces.append(a)
                done = t
            pieces.append(rest)
            out.append((pieces[0], label, name))
            for p in pieces[1:]:
                out.append((p, label, f"{name}: {ADDED}"))
                added.append(f"{name}: {ADDED}")
        return out

    counts = mirrored_counts(built)
    for c, n in enumerate(counts):
        cont = built["contours"][c]
        if n is None:
            built["contours"][c] = split_run(cont)
            continue
        end_name = cont[n][2]
        left = split_run(cont[:n])
        if len(left) == n:
            continue
        built["contours"][c] = mirror_half(left, built["axis"], end_name)
        if built.get("halves"):
            built["halves"][c] = left
        else:
            built["half"] = left
    return added


ADDED = "extreme added after moves by hand"


def drop_redundant(built, tol=0.35):
    """After add_extremes: a smooth node beside an added extreme that is no longer an extreme itself
    (a move by hand tilted its handles) is redundant. It is removed, its two curves merged into one
    that keeps the moved shape within tol pixels (0.35 px is about half a font unit) and doesn't bulge; the added extreme takes its name.
    So a tilted handle at an extreme comes out as the node moved to where the extreme now is.
    Returns the names of the nodes removed."""
    removed = []

    def unit(v):
        return v / (np.linalg.norm(v) + 1e-12)

    def flat_or_upright(v):
        a = abs(math.degrees(math.atan2(v[1], v[0]))) % 90
        return min(a, 90 - a) < 0.5

    def pass_(run, closed):
        m = len(run)
        for i in range(m):
            if not run[i][2].endswith(ADDED):
                continue
            for k in (i - 1, i + 1):
                if not closed and (k <= 0 or k >= m):
                    continue
                a, b = (k - 1) % m, k % m
                A, B = np.array(run[a][0], float), np.array(run[b][0], float)
                if run[b][2].endswith(ADDED) or is_line(A) or is_line(B):
                    continue
                tin, tout = A[3] - A[2], B[1] - B[0]
                if np.linalg.norm(tin) < 1e-9 or np.linalg.norm(tout) < 1e-9:
                    continue
                turn = math.degrees(math.acos(np.clip(np.dot(unit(tin), unit(tout)), -1, 1)))
                if turn > 1.0 or flat_or_upright(tin):
                    continue
                pts = np.concatenate([G.bez(A, np.linspace(0, 1, 40)), G.bez(B, np.linspace(0, 1, 41)[1:])])
                t1 = unit(A[1] - A[0]) if np.linalg.norm(A[1] - A[0]) > 1e-9 else unit(A[2] - A[0])
                t2 = unit(B[2] - B[3]) if np.linalg.norm(B[2] - B[3]) > 1e-9 else unit(B[1] - B[3])
                P, err = G.fit_span(pts, t1, t2)
                if err.max() > tol or _swell(P) > 0.2:
                    continue
                name_b = run[b][2]
                merged = (P, run[a][1], run[a][2])
                new = list(run)
                new[a] = merged
                del new[b]
                j = i if i < b else i - 1                     # the added extreme's index after the merge
                new[j] = (new[j][0], new[j][1], name_b)
                removed.append(name_b)
                return new, True
        return run, False

    def clean(run, closed):
        changed = True
        while changed:
            run, changed = pass_(run, closed)
        return run

    counts = mirrored_counts(built)
    for c, n in enumerate(counts):
        cont = built["contours"][c]
        if n is None:
            built["contours"][c] = clean(cont, True)
            continue
        end_name = cont[n][2]
        left = clean(cont[:n], False)
        if len(left) == n:
            continue
        built["contours"][c] = mirror_half(left, built["axis"], end_name)
        if built.get("halves"):
            built["halves"][c] = left
        else:
            built["half"] = left
    return removed


def is_line(P):
    a, b = P[0], P[3]
    if np.linalg.norm(b - a) < 1e-9:
        return False
    u = (b - a) / np.linalg.norm(b - a)
    off = [abs((P[k] - a)[0] * u[1] - (P[k] - a)[1] * u[0]) for k in (1, 2)]
    return max(off) < 1e-6


def write_ufo(path, info: dict, glyphs: dict, features: str = "", kerning: dict | None = None):
    """glyphs: name → {"unicode": int | None, "width": int, "contours": [[4×2 segments]]}; features
    is OpenType feature code (the stylistic sets); kerning maps (left, right) glyph names to units."""
    import ufoLib2
    font = ufoLib2.Font()
    font.features.text = features
    font.kerning.update(kerning or {})
    for k, v in info.items():
        setattr(font.info, k, v)
    for name, g in glyphs.items():
        gl = font.newGlyph(name)
        gl.width = g["width"]
        if g.get("unicode") is not None:
            gl.unicodes = [g["unicode"]]
        pen = gl.getPen()
        contours = g["contours"]
        # PostScript direction (y up): the outline runs counter-clockwise, counters clockwise
        if contours:
            areas = [G.signed_area(c) for c in contours]
            outer = int(np.argmax(np.abs(areas)))
            contours = [G.reverse(c) if (a < 0) == (i == outer) else c for i, (c, a) in enumerate(zip(contours, areas))]
        for segs in contours:
            pen.moveTo(tuple(int(v) for v in segs[0][0]))
            for P in segs:
                if is_line(P):
                    pen.lineTo(tuple(int(v) for v in P[3]))
                else:
                    pen.curveTo(*(tuple(int(v) for v in q) for q in P[1:]))
            pen.closePath()
    font.save(path, overwrite=True)
    return font


def notdef(width, cap):
    m = 50
    outer = [(m, 0), (width - m, 0), (width - m, cap), (m, cap)]
    inner = [(m + 60, 60), (m + 60, cap - 60), (width - m - 60, cap - 60), (width - m - 60, 60)]
    seg = lambda a, b: np.array([a, a, b, b], float)
    return [[seg(o[i], o[(i + 1) % 4]) for i in range(4)] for o in (outer, inner)]
