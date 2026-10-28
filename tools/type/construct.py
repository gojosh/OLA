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


def line(A, B):
    A, B = np.asarray(A, float), np.asarray(B, float)
    return np.array([A, A + (B - A) / 3, A + 2 * (B - A) / 3, B])


def arc(c, r, a0, a1):
    """A circular arc from angle a0 to a1 (degrees on screen, either way round), as cubics split at
    each quarter, so the nodes fall on the circle's extremes whichever way the arc is turned."""
    c = np.asarray(c, float)
    up = a1 >= a0
    cuts = [a0]
    q = (math.floor(a0 / 90) + 1) * 90 if up else (math.ceil(a0 / 90) - 1) * 90
    while (q < a1 - 1e-6) if up else (q > a1 + 1e-6):
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
}


class Kit:
    """The primitives a construction places."""

    def __init__(self, curl: dict):
        self.curl_model = curl
        self.curl_segs = [np.array(s, float) for s in curl["segments"]]
        self.curl_nodes = {k: np.array(v, float) for k, v in curl["nodes"].items()}

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
    return segs, names, cs[0] + r * hd(a_in), cs[2] + r * hd(a_out)


# ── Measurements a construction asks for ──────────────────────────────────────

FAMILY = {  # name: (start, low, high, meaning)
    "stem": (39.0, 30.0, 50.0, "half the stem's width (px)"),
    "curl": (1.0, 0.8, 1.25, "the curl's size, as a multiple of the averaged curl"),
    "trefoil_r": (15.0, 9.0, 22.0, "a trefoil lobe's radius (px)"),
    "trefoil_d": (18.0, 9.0, 28.0, "how far each trefoil lobe sits from the trefoil's centre (px)"),
}


class Params:
    """Hands a construction its measurements. Called once with no values to learn what the
    construction asks for (each with a starting value and bounds), then with the fitted values.
    Family measurements are shared by every letter unless `local` is set."""

    def __init__(self, glyph: str, values: dict | None = None, local: bool = False):
        self.glyph, self.values, self.local, self.spec = glyph, values, local, {}

    def _get(self, key, init, lo, hi):
        lo, hi = min(lo, init), max(hi, init)
        self.spec.setdefault(key, (float(init), float(lo), float(hi)))
        return float(init) if self.values is None else float(self.values[key])

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


def fit_letters(letters: dict, refs: dict, kit: Kit, local=False, edge_points=1500):
    """Fit the letters' measurements to Pugin's drawings in one solve. Family measurements (stem,
    curl, trefoil) are shared by every letter, so they settle where the alphabet agrees, unless
    `local` lets each letter have its own. Residuals run both ways: the outline onto his edge, and his
    edge onto the outline. A robust loss keeps his accidents from pulling a whole letter."""
    from scipy.sparse import lil_matrix
    spec = {}
    for g, fn in letters.items():
        p = Params(g, None, local)
        fn(p, kit)
        spec.update(p.spec)
    keys = list(spec)
    x0 = np.array([spec[k][0] for k in keys])
    lb = np.array([spec[k][1] for k in keys])
    ub = np.array([spec[k][2] for k in keys])
    data = {}
    for g in letters:
        e = np.concatenate(reference_edges(refs[g]))
        data[g] = (signed_distance(refs[g]), e[np.linspace(0, len(e) - 1, min(edge_points, len(e))).astype(int)])

    def glyph_res(g, vals):
        built = letters[g](Params(g, vals, local), kit)
        dense = sample_fixed(built)
        sd, edge = data[g]
        return np.concatenate([sd(dense), cKDTree(dense).query(edge)[0], 20 * swelling(built)])

    def resid(x):
        vals = dict(zip(keys, x))
        return np.concatenate([glyph_res(g, vals) for g in letters])

    start = dict(zip(keys, x0))
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
    vals = {k: float(v) for k, v in zip(keys, x)}
    # a free heading within 2° of flat or upright is meant to be flat or upright: the node is an extreme
    for k, v in vals.items():
        if k.endswith("_heading") and abs(v - 90 * round(v / 90)) < 2:
            vals[k] = 90.0 * round(v / 90)
    at_bounds = [k for k, v, lo, hi in zip(keys, x, lb, ub) if min(v - lo, hi - v) < 1e-3 * max(1.0, hi - lo)]
    return vals, at_bounds, {"evaluations": int(nfev), "cost": float(cost)}


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

def check_contour(segs, names, smooth_deg=0.5) -> dict:
    """The rules a type designer's outline keeps: no curve swells past its end nodes (so every node
    sits at an extreme), handles at an extreme lie flat or upright, and every join is smooth unless
    it's meant to be a corner."""
    swells = [names[i] for i, P in enumerate(segs) if G.extrema_ts(P)]
    corners, skew = [], []
    for i, P in enumerate(segs):
        prev = segs[i - 1]
        tin = next((prev[3] - prev[k] for k in (2, 1, 0) if np.linalg.norm(prev[3] - prev[k]) > 1e-9), None)
        tout = next((P[k] - P[0] for k in (1, 2, 3) if np.linalg.norm(P[k] - P[0]) > 1e-9), None)
        ang = math.degrees(math.acos(np.clip(np.dot(tin, tout) / (np.linalg.norm(tin) * np.linalg.norm(tout)), -1, 1)))
        if ang > smooth_deg:
            corners.append({"node": names[i], "turn_deg": round(ang, 1)})
            continue
        for h in (tin, tout):
            a = math.degrees(math.atan2(abs(h[1]), abs(h[0])))
            if 1e-6 < a < 2 or 88 < a < 90 - 1e-6:
                skew.append(names[i])
    return {"segments": len(segs), "curves_swelling_past_nodes": swells, "corners": corners,
            "nearly_flat_handles": sorted(set(skew))}


def check_outline(contours, names, smooth_deg=0.5) -> dict:
    """check_contour over every contour of a glyph. In whole font units a smooth join on a slant can
    kink by a degree or two when a short handle is rounded, so the font's check allows up to 2°."""
    parts = [check_contour(c, n, smooth_deg) for c, n in zip(contours, names)]
    out = {"contours": len(parts), "segments": sum(p["segments"] for p in parts),
           "curves_swelling_past_nodes": [x for p in parts for x in p["curves_swelling_past_nodes"]],
           "corners": [x for p in parts for x in p["corners"]],
           "nearly_flat_handles": sorted({x for p in parts for x in p["nearly_flat_handles"]})}
    out["ok"] = not out["curves_swelling_past_nodes"] and not out["nearly_flat_handles"]
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
    if built.get("half"):
        ax = built["axis"]
        axis_u = int(round(lsb + (ax - x_min) * scale))
        left = [conv(q, ax, axis_u) for q, _, _ in built["half"]]
        right = G.reverse([q * [-1, 1] + [2 * axis_u, 0] for q in left])
        return [left + right], 2 * axis_u, ax - axis_u / scale
    contours = [[conv(q, x_min, lsb) for q, _, _ in c] for c in built["contours"]]
    return contours, int(round((x_max - x_min) * scale + 2 * lsb)), x_min - lsb / scale


def is_line(P):
    a, b = P[0], P[3]
    if np.linalg.norm(b - a) < 1e-9:
        return False
    u = (b - a) / np.linalg.norm(b - a)
    off = [abs((P[k] - a)[0] * u[1] - (P[k] - a)[1] * u[0]) for k in (1, 2)]
    return max(off) < 1e-6


def write_ufo(path, info: dict, glyphs: dict):
    """glyphs: name → {"unicode": int | None, "width": int, "contours": [[4×2 segments]]}"""
    import ufoLib2
    font = ufoLib2.Font()
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
