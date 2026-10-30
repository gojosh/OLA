"""Textura constructions (decisions 0008 and 0011): each plain letter as the strokes of one broad
nib (nib.py), in flattened-plate pixels, y down.

A stroke is a path the nib follows. A minim, the textura's basic stroke, comes down into its head
along the nib's diagonal, turns down the stem, and turns out again into its foot: the nib leaves
the diamond-pointed head and foot by itself, and the turns leave the hollows under the head and
over the foot. Most letters are minims and their variants (a stem with no head, a stroke that
stops without a foot, stems running up to the ascender line or down to the descender line), with
arms, bars, bowls and tails drawn as free paths of the same pen. The measurements every letter
shares (the nib, the head and foot, the lines they sit on) are the family's; each letter adds its
own (where its strokes stand).

A construction returns {"strokes": [...paths], "baseline": y}; each path is a list of cubics. It may
also return "marks": strokes Pugin didn't draw, proposed in the pen's idiom (the stroke over the i),
which are written with the letter but left out of the fit to his; "edges", edges the outline is
trued to where two strokes meet: straight where the pen alone would leave a step (edge_below,
edge_above), curved where the pen, turning, sweeps one (concave_top); and "fit_affine" (a, b, c,
d, e, f), a map from the construction to where Pugin drew the letter, for the letters he squeezed
onto the plate's second line (y, z): the plain letter stands at the full x-height, and only its
comparison with his is squeezed."""
from __future__ import annotations

import numpy as np

import geom as G
from construct import Params, S, arc, cubic, hd, line

FAMILY = {  # name: (start, low, high, meaning)
    "nib_width": (46.8, 30.0, 64.0, "the nib's width (px)"),
    "nib_angle": (45.0, 30.0, 60.0, "the angle of the nib's edge at the heads, at the x-height line and above, rising to the right (degrees)"),
    "nib_angle_foot": (50.0, 30.0, 65.0, "the nib's angle at the feet, at the baseline and below: the pen turns evenly from the one to "
                                         "the other between the two lines, as Pugin's does (degrees)"),
    "nib_thickness": (8.0, 3.0, 14.0, "the nib's thickness: the width of a hairline (px)"),
    "nib_light": (0.8, 0.5, 1.0, "the nib's width in a stroke written with less pressure, as a share of its full width (c's top, "
                                 "e's arm, a's top bowl)"),
    "top_leave": (13.0, 0.0, 40.0, "the angle at which the concave top of c, d, e, g and s leaves the stem's top corner, rising to the "
                                   "right, before it steepens to the nib's own angle at the peak (degrees)"),
    "fork_notch": (13.0, 4.0, 30.0, "the split top of b, d, h, k and l, and the split bottom of q, turned upside down "
                                     "(and of p, until Josh drew it): how deep its notch runs below the tips' tops (px)"),
    "fork_flare": (26.0, 8.0, 100.0, "the split top: how far below the tips' tops the stem begins to widen into it (px)"),
    "fork_out": (4.0, 0.0, 24.0, "the split top: how far each tip stands out beyond the stem's edge (px)"),
    "fork_tip": (3.0, 1.0, 8.0, "the split top: the radius of each horn's rounded tip (px)"),
    "fork_lean": (20.0, 0.0, 45.0, "the split top: how far from upright each horn's outer edge runs into its tip (degrees)"),
    "head": (30.0, 12.0, 50.0, "how far right the head's stroke travels before the stem (px)"),
    "head_angle": (45.0, 25.0, 65.0, "the head stroke's slope, falling to the right (degrees)"),
    "head_turn": (12.0, 1.0, 45.0, "how far down the stem the pen settles out of its turn from the head (px)"),
    "foot": (27.0, 12.0, 50.0, "how far right the foot's stroke travels after the stem (px)"),
    "foot_angle": (45.0, 25.0, 65.0, "the foot stroke's slope, falling to the right (degrees)"),
    "foot_turn": (12.0, 1.0, 45.0, "how far up the stem the pen starts its turn into the foot (px)"),
    "join": (22.0, 8.0, 26.0, "where a foot that runs on into the next minim ends, left of that minim's stem (px; u, w). It was fitted when "
                              "n's and m's heads also started this far right of the stem before; since 2026-10-29 they start clear of it, "
                              "joined by a hairline, and no letter Pugin drew measures it"),
    "top": (3336.0, 3310.0, 3360.0, "where a minim's head stroke starts: the x-height line (px on the plate)"),
    "bottom": (3513.0, 3495.0, 3530.0, "where a minim's foot stroke ends: the baseline (px on the plate)"),
    "ascender": (3230.0, 3190.0, 3270.0, "where an ascender's head stroke starts (px on the plate)"),
    "descender": (3612.0, 3585.0, 3640.0, "where a descender's stroke ends (px on the plate)"),
}


class TParams(Params):
    """Params with the textura's family measurements."""

    def fam(self, name):
        init, lo, hi, _ = FAMILY[name]
        key = f"{self.glyph}:family.{name}" if self.local else f"family.{name}"
        return self._get(key, init, lo, hi)


def pen_of(p):
    """The pen: the family's nib, turning from its angle at the heads to its angle at the feet
    between the x-height line and the baseline."""
    import nib as NB
    return NB.Pen(p.fam("nib_width"), p.fam("nib_thickness"), p.fam("nib_angle"), p.fam("nib_angle_foot"), p.fam("top"), p.fam("bottom"))


def nib_at(p, y):
    """The nib as the pen holds it at height y."""
    return pen_of(p).at(y)


def light(p, stroke):
    """A stroke written with less pressure, so with a narrower nib: lighter than the strokes round it,
    as Pugin's top strokes of c and e and the a's top bowl are (Josh, 2026-10-29: "we need to
    introduce a narrower nib", by about 20% in these)."""
    import nib as NB
    return NB.Stroke(stroke, p.fam("nib_light"))


def tip(p, stroke):
    """A fine stroke drawn with the tip of the nib rather than its edge: a small round point a
    hairline across, so the stroke is a hairline wide whichever way it goes and its edges run on
    smoothly into a pip's (Josh: "crafted with the tip of the nib"; "not a smooth and seamless blend
    into the pip", when the tip was drawn square)."""
    import nib as NB
    return NB.Stroke(stroke, tip=p.fam("nib_thickness") / 2)


def cradle(p, pre, x, y, r, at, clockwise):
    """A pip, a round dot of the nib's tip, and where the fine stroke that ends in it meets it, so
    the pip lies cradled in the stroke's curl (Josh: "properly aligned cradling of the pips"). The
    stroke meets the pip at angle `at` round it (degrees from its right, clockwise on the page),
    heading along its circle (on round it clockwise or not), its centre the tip's radius inside the
    pip's edge and bending as that circle does. There the stroke's outer edge runs on into the pip's
    edge with neither a kink nor a change of bend (Josh: "curve both with tangency and curvature
    scale into the pips"). Returns the pip, the point, the heading, and the bend (curvature, 1/px,
    positive where the heading turns clockwise on the page)."""
    import nib as NB
    c = np.array([p.x(f"{pre}.x", x, 10), p.x(f"{pre}.y", y, 10)])
    r, a = p.length(f"{pre}.pip", r, 4.0, 14.0), p.ang(f"{pre}.at", at, at - 50, at + 50)
    h = a + 90 if clockwise else a - 90
    rho = r - p.fam("nib_thickness") / 2
    return NB.Dot(c, r), c + rho * hd(a), h, (1 if clockwise else -1) / rho


def under(p, q, point, side, reach=0.2):
    """Where a stroke ends under a fine stroke drawn over it with the tip (q, a cubic), as the e's arm
    ends under its crossing member: whatever of the stroke's end would stand out past the fine
    stroke's far edge is trimmed to that edge, so the fine stroke's edge runs on unbroken. `side`
    says which edge is the far one: +1 for the one to the left of the way q runs on the page (its
    normal (dy, -dx)), -1 for the other. Returns the edge to true the outline to: the far edge of
    q, a tip's radius out from it, along `reach` of its length either side of the point nearest
    `point`, and a point of q's ink."""
    import nib as NB
    ts = np.linspace(0, 1, 201)
    t0 = ts[np.argmin(np.linalg.norm(G.bez(q, ts) - point, axis=1))]
    a, b = max(0.0, t0 - reach), min(1.0, t0 + reach)
    piece = G.split(G.split(q, a)[1], (b - a) / (1 - a))[0] if a < 1 else q
    return np.array(NB.offset(piece, side * p.fam("nib_thickness") / 2, tol=0.05)), G.bez(q, np.array([t0]))[0]


def _cross2(u, v):
    return u[0] * v[1] - u[1] * v[0]


def spiral(start, h0, h1, k0, k1, ease=1.0, tight="end", n=4):
    """A spiral from `start` heading h0 (degrees) to heading h1, its bend (curvature, 1/px, positive
    where the heading turns clockwise on the page) going from k0 to k1 along its length, so it eases
    from one bend into the other with no sudden turn anywhere. With `ease` 1 the bend changes evenly
    (an Euler spiral); above 1 it stays near the gentler bend for longer and changes mostly near the
    `tight` end, as a stroke winds into a pip. Its length is what that turn takes. Drawn as n cubics,
    each a short Hermite piece of it. Returns the cubics and where it ends."""
    u = np.linspace(0, 1, 801)
    f = u ** ease if tight == "end" else 1 - (1 - u) ** ease          # 0 to 1: how far the bend has gone from k0 to k1
    F = 1 / (ease + 1) if tight == "end" else ease / (ease + 1)          # its mean
    L = np.radians(h1 - h0) / (k0 + (k1 - k0) * F)
    s_ = u * L
    k = k0 + (k1 - k0) * f
    th = np.radians(h0) + np.concatenate([[0], np.cumsum(np.diff(s_) * (k[1:] + k[:-1]) / 2)])
    c = np.column_stack([np.cos(th), np.sin(th)])
    pts = np.vstack([start, start + np.cumsum(np.diff(s_)[:, None] * (c[1:] + c[:-1]) / 2, axis=0)])
    out = []
    for i in range(n):
        a, b = i * 800 // n, (i + 1) * 800 // n
        l = s_[b] - s_[a]
        out.append(np.array([pts[a], pts[a] + l / 3 * c[a], pts[b] - l / 3 * c[b], pts[b]]))
    return out, pts[-1]


# ── Strokes ───────────────────────────────────────────────────────────────────

def minim(p, x, top=None, bottom=None, after=None, head=None, foot=True, end=None, before=None, spur=True, lead=0.0, run=None):
    """One minim with its stem at x: down the nib's diagonal into the head, a turn down the stem, and
    a turn out into the foot. top and bottom default to the x-height line and the baseline.
    - after: the stem of a minim this one follows in the same letter. The head is an ordinary head,
      clear of that stem, and the pen comes up to it from that stem along its own edge, leaving a
      hairline that joins the two at the top, as Pugin's n and m do (Josh: "the connection between
      stems is created with the spurs at the top, not simply the angled part of the stems").
    - head: the head stroke's length, if not the family's; 0 for a stem with no head, which starts
      at `top` with the nib's flat cut.
    - lead: how far back along its own diagonal the head stroke starts, above and left of where it
      crosses `top`; the rest of the minim is unchanged (b's bowl, whose head starts in the stem).
    - foot: False for a stroke that stops at `end` with the nib's cut instead of turning out.
    - run: the foot stroke's length, if not the family's (a foot that runs on to meet the stroke on
      its right: foot_to_meet).
    - before: the stem of a minim this one leads into in the same letter; the foot stroke runs on to
      end against it, so the two join at the foot (u, w).
    - spur: whether a free foot carries on into the spur, a short hairline up and to the right, when
      the letter is written with spurs (p.spur, set by the build; the fit to Pugin leaves them out).
      A foot that runs into another stroke of the letter has none, as Pugin's don't."""
    top = p.fam("top") if top is None else top
    bottom = p.fam("bottom") if bottom is None else bottom
    ha, fd, fa = p.fam("head_angle"), p.fam("foot") if run is None else run, p.fam("foot_angle")
    hd = p.fam("head") if head is None else head
    out = []
    if hd > 1.0:
        A = np.array([x - hd, top])
        K1 = np.array([x, top + hd * np.tan(np.radians(ha))])       # where the head's diagonal meets the stem
        B = K1 + [0, p.fam("head_turn")]
        if after is not None:                                       # up from the stem before, along the nib's edge
            out.append(join_from(p, after, A))
        if lead > 0:
            out.append(line(A - lead * np.array([np.cos(np.radians(ha)), np.sin(np.radians(ha))]), A))
        out.append(cubic(A, ha, B, S, 1.0, 1.0))                    # a turn whose handles both reach its corner
    else:
        B = np.array([x, top])
    if not foot:
        return out + [line(B, np.array([x, end]))]
    if before is not None:
        fd = max(4.0, before - x - p.fam("join"))
    D = np.array([x + fd, bottom])
    K2 = np.array([x, bottom - fd * np.tan(np.radians(fa))])        # where the stem meets the foot's diagonal
    C = K2 - [0, p.fam("foot_turn")]
    out += [line(B, C), cubic(C, S, D, fa, 1.0, 1.0)]
    if spur and before is None:
        out += spur_from(p, D)
    return out


def join_from(p, x, start):
    """The hairline that joins a stroke to the stem before it in the same letter: the pen comes up
    from the stem at x along the nib's own edge to where the stroke starts (`start`), as Pugin's n, m,
    h and k are joined at the top (Josh: "the connection between stems is created with the spurs at
    the top")."""
    u = nib_at(p, start[1]).u
    return line(start - (start[0] - x) / u[0] * u, start)


def spur_into(p, start):
    """The spur leading into a head that starts at `start`: a short hairline coming up to it from
    the lower left along the nib's own edge, as the pen enters the stroke. Pugin's first heads
    start with one: i and j have it (Josh: "add the top spur", 2026-10-29), and n, m and r ("add
    the top spur to the first heads of n, m and r, as Pugin's have"). Only when the letter is
    written with spurs (p.spur), so `ss01` leaves it out with the others; and the build leaves it
    out (p.top_spur False) when it spaces the letters, since the hairline tucks into the white
    before its letter rather than pushing the letter before away."""
    sp = getattr(p, "spur", None)
    if not sp or not getattr(p, "top_spur", True):
        return []
    return [line(start - sp["length"] * nib_at(p, start[1]).u, start)]


def entered(p, stroke):
    """A minim (`stroke`) with the top spur leading into its head (spur_into): the first minim of n,
    m and r."""
    return spur_into(p, stroke[0][0]) + stroke


def spur_from(p, end):
    """The spur leaving a free foot that ends at `end`: a short hairline up and to the right along the
    nib's own edge, as the pen holds it there, when the letter is written with spurs (p.spur, set by
    the build); otherwise nothing."""
    sp = getattr(p, "spur", None)
    if not sp:
        return []
    return [line(end, end + sp["length"] * nib_at(p, end[1]).u)]


def path(p, pre, nodes, span=15.0, turn=25.0, at=None):
    """A free stroke of the pen through named nodes, each (name, x, y, heading): the letter's own
    measurements, within `span` px and `turn` degrees of where they start. Between two nodes whose
    headings are both None the stroke runs straight; otherwise it is a curve leaving and arriving on
    those headings. `at` sets some nodes' x outright (name: x), where the stroke must meet another."""
    pts, hds = [], []
    for name, x, y, h in nodes:
        px = at[name] if at and name in at else p.x(f"{pre}.{name}.x", x, span)
        pts.append(np.array([px, p.x(f"{pre}.{name}.y", y, span)]))
        hds.append(None if h is None else p.ang(f"{pre}.{name}.heading", h, h - turn, h + turn))
    out = []
    for k in range(len(nodes) - 1):
        a, b = pts[k], pts[k + 1]
        if hds[k] is None and hds[k + 1] is None:
            out.append(line(a, b))
        else:
            ha = hds[k] if hds[k] is not None else np.degrees(np.arctan2(*(b - a)[::-1]))
            hb = hds[k + 1] if hds[k + 1] is not None else np.degrees(np.arctan2(*(b - a)[::-1]))
            out.append(cubic(a, ha, b, hb, p.t(f"{pre}.{nodes[k][0]}.t1"), p.t(f"{pre}.{nodes[k][0]}.t2")))
    return out


def split_top(p, x):
    """The split top of an ascender, the same on b, d, h, k and l: the stem, as wide as the pen makes
    it, splits into two horns with a notch between them, each horn's outer edge leaving the stem's
    edge and flaring a little outward into a gently rounded tip, its inner edge running straight
    down into the notch. It is the blackletter types' convention (Josh: "a simple, clean split top
    that is consistent between the characters I listed, each split coming to a gentle rounded tip");
    Pugin's flourished tops will be alternates. Its measurements are the family's, held, so every
    ascender has the same top. Its tips' tops stand where the nib's top corner would at the
    ascender line. Returns the filled shape and where the stem below it starts."""
    import nib as NB
    nb = nib_at(p, p.fam("ascender"))
    curves, start = _fork(p, x, nb, p.fam("ascender") + min(c[1] for c in nb.corners))
    return NB.Shape(curves), start


def split_bottom(p, x):
    """The split bottom of a descender, on q (and p, until Josh drew it): the split top (split_top) turned upside
    down at the descender line, with the same five settings, so the stem widens down into two horns
    pointing down, with a notch between them (Josh: "lets do splits on the bottom of p and q, in the
    same manner we did split tops on b, d, h, k, and l"). It is as wide as the pen makes the stem
    there, where the nib has turned to its angle at the feet, and its tips' bottoms stand where the
    nib's bottom corner would at the descender line, as the turned-out foot's did. Pugin's
    descenders run on into swashes, splayed both ways on q; those will be alternates. Returns the
    filled shape and where the stem above it ends."""
    import nib as NB
    nb = nib_at(p, p.fam("descender"))
    bot = p.fam("descender") + max(c[1] for c in nb.corners)
    curves, start = _fork(p, x, nb, bot)
    flip = lambda q: np.array([[px, 2 * bot - py] for px, py in q[::-1]])
    return NB.Shape([flip(q) for q in reversed(curves)]), 2 * bot - start


def _fork(p, x, nb, top):
    """The outline of a split top whose tips' tops stand at `top`, on a stem at x written with the nib
    `nb` (split_top), and where the stem below it starts."""
    w2 = max(c[0] for c in nb.corners)                    # half the stem's width
    notch, flare, out, r, lean = (p.fam(k) for k in ("fork_notch", "fork_flare", "fork_out", "fork_tip", "fork_lean"))
    tip = np.array([x - w2 - out + r, top + r])            # the left tip's centre
    nadir = np.array([x, top + notch])
    start = top + notch + max(-c[1] for c in nb.corners) + 2        # the stem's own flat top cut lies under the shape
    base = start + max(c[1] for c in nb.corners) + 3
    h = 270 - lean                                         # the left horn's outer edge runs into its tip heading so
    meet = tip - r * np.array([-np.sin(np.radians(h)), np.cos(np.radians(h))])
    v = nadir - tip
    t_in = np.degrees(np.arctan2(v[1], v[0]) - np.arccos(r / np.linalg.norm(v)))     # where the inner edge leaves the tip
    a_meet = np.degrees(np.arctan2(*(meet - tip)[::-1]))
    t_in = t_in + 360 if t_in < a_meet else t_in
    left = [line(np.array([x - w2, base]), np.array([x - w2, top + flare])),
            cubic(np.array([x - w2, top + flare]), 270, meet, h, 0.55, 0.55),
            *arc(tip, r, a_meet, t_in),
            line(tip + r * hd(t_in), nadir)]
    mirror = lambda q: np.array([[2 * x - px, py] for px, py in q[::-1]])
    right = [mirror(q) for q in reversed(left)]
    return left + right + [line(np.array([x + w2, base]), np.array([x - w2, base]))], start


def ascender(p, x, spur=True):
    """A minim rising to the ascender line with the split top (split_top), whose foot stands on the
    baseline: the stem, and the top."""
    shape, start = split_top(p, x)
    return [minim(p, x, head=0, top=start, spur=spur), shape]


def _ink_from_left(path, pen, y, n=48):
    """Where the ink of a stroke along `path` begins, from the left, at height y: the least x of the
    nib, set at points along the path, across that height (inf if the stroke doesn't reach it)."""
    best = np.inf
    for q in path:
        at = G.bez(np.asarray(q, float), np.linspace(0, 1, n))
        pts = at[:, None, :] + pen.corners(at[:, 1])                                       # each sample's nib
        a, b = pts, np.roll(pts, -1, axis=1)
        cross = (a[..., 1] - y) * (b[..., 1] - y) <= 0
        dy = np.where(np.abs(b[..., 1] - a[..., 1]) < 1e-9, 1e-9, b[..., 1] - a[..., 1])
        xs = a[..., 0] + (y - a[..., 1]) * (b[..., 0] - a[..., 0]) / dy
        if cross.any():
            best = min(best, float(xs[cross].min()))
    return best


def foot_to_meet(p, x, right):
    """How far the foot of a minim at x runs to meet the stroke on its right (`right`, a path), where
    the family's foot doesn't reach across (d, g; and q and y, since the nib turned to 50° at the
    feet): until the upper corner of its cut is half a hairline inside that stroke's ink, so the two
    join by a hairline's width at a point, as Pugin's do (Josh: "so the left foot meets the stroke
    on its right"). Never shorter than the family's foot."""
    pen = pen_of(p)
    corner = pen.at(p.fam("bottom")).corners[2]     # the upper end of the foot's cut
    reach = _ink_from_left(right, pen, p.fam("bottom") + corner[1])
    return max(p.fam("foot"), reach + pen.thickness / 2 - corner[0] - x)


def edge_below(p, left, right):
    """Where a stroke's foot (`left`) meets, at the bottom of a letter, a stroke that stops with the
    nib's cut (`right`), as in b, o, v and w. Pugin draws the two ends as one straight edge, from
    the foot's point to the right stroke's corner (Josh: "align the angle of each stem seamlessly
    at the bottom"). Measured on the plate, that edge is flatter than the nib's cut there (about 38
    degrees), so the two cuts alone leave a step between them; the outline is trued to the edge
    instead (nib.outline). Returns the edge's two ends and a point inside the ink above it."""
    foot, stop = left[-1][3], right[-1][3]
    cf, cs = nib_at(p, foot[1]).corners, nib_at(p, stop[1]).corners
    return foot + cf[3], stop + cs[2], foot + cf[2]


CONCAVE = 0.6      # how far each handle of a concave top reaches toward the point where its two tangents meet


def nib_for(p, stroke, y):
    """The nib a stroke is written with at height y: the pen's, narrowed if the stroke is light."""
    import nib as NB
    return NB.pressed(nib_at(p, y), NB.pressure_at(stroke))


def concave_top(p, left, right):
    """Where the primary stem (`left`) meets the top stroke (`right`) at the upper left of c, d, e, g
    and s. Pugin's edge there is concave, not straight: it leaves the stem's top corner nearly flat
    (top_leave, measured on the plate) and steepens until it meets the peak of the top stroke along
    the nib's own edge. It is the sweep of the nib's edge as the pen turns from flat to its working
    angle (Josh: "a concave curve on the top left where the primary stem and top line intersect ...
    one of many fine features accomplished by subtle nib rotation"). Returns the curve and a point
    inside the ink below it."""
    top, start = left[0][0], right[0][0]
    corner = top + nib_for(p, left, top[1]).corners[0]
    nb = nib_for(p, right, start[1])
    return cubic(corner, -p.fam("top_leave"), start + nb.corners[1], -nb.angle, CONCAVE, CONCAVE), start + nb.corners[0]


def edge_above(p, left, right):
    """Where the stroke on the left of a bowl (`left`) meets, at the top, the head of the stroke on its
    right (`right`), as in o and q: one straight edge from the left stroke's top corner to the peak
    of the head, as Pugin draws it, in place of the two cuts and the step between them. (In d and g
    the edge is concave: concave_top.) Returns the edge's two ends and a point inside the ink below
    it."""
    top, start = left[0][0], right[0][0]
    ct, cs = nib_at(p, top[1]).corners, nib_at(p, start[1]).corners
    return top + ct[0], start + cs[1], start + cs[0]


def second_line(p):
    """y and z are squeezed onto the plate's second line: there, the letter is the plain letter
    drawn on a lower baseline and shrunk in height about it."""
    k, base = p.length("line2.squeeze", 0.72, 0.5, 1.0), p.x("line2.baseline", 3700, 25)
    b = p.fam("bottom")
    return (1.0, 0.0, 0.0, 0.0, k, base - k * b)


# ── Letters ───────────────────────────────────────────────────────────────────

DOT_ANGLE = 30.0     # the nib turned flatter than at the heads (45°) for the mark over i and j (degrees)
DOT_MOVE = 10.5      # how far the pen moves for it, down the heads' diagonal (px)


def i_stroke(p, x):
    """The mark over an i (and j), as scribes of the period marked an i so it could be told from the
    minims round it. Pugin's i on plate 9 has none, so this is our own, drawn in the pen's idiom and
    not fitted: a short touch of the full nib, turned to 30° and moved a little way down the heads'
    diagonal, so it lies a little flatter than the heads and is about half as thick as it is long.
    It stands over the stem's left part, clear of the head.
    - Josh (2026-10-29): "move it a bit left, and make it slightly thicker"; looking at 15th-century
      textura types for a model, "I'd rather not do the little half circle concept - looks like we
      may have some freedom to invent." The 42-line Bible's marks are fine hairline arcs; his sample
      of a later textura has a short, heavy oblique stroke, about as long as the stem is wide.
    - Until then it was the 45° nib drawn 26 px along a 30° line: a long thin sliver, about 14 px
      across, standing 4 px right of the stem's centre and nearly touching the head.
    Now it is about 17 px across and 4 px left of the stem's centre."""
    import nib as NB
    nb = NB.Nib(p.fam("nib_width"), DOT_ANGLE, p.fam("nib_thickness"))
    ha = np.radians(p.fam("head_angle"))
    d = DOT_MOVE / 2 * np.array([np.cos(ha), np.sin(ha)])
    c = np.array([x - 4, p.fam("top") - 46])
    return NB.dab(nb, c - d, c + d)


def light_head(p, stroke):
    """A minim (`stroke`) whose head is written light (as the c's top stroke is), with the top spur
    leading into it: the head keeps the light nib along its diagonal and comes to full weight as it
    turns down into the stem, so the two meet without a step (i and j; Josh: "the i should use the
    thinner nib on the first angle of the stem, and add the top spur", 2026-10-29). Returns the head
    and the rest of the minim, as two strokes."""
    import nib as NB
    head, *rest = stroke
    spur = spur_into(p, head[0])
    lt, n = p.fam("nib_light"), len(spur)
    return [NB.Stroke(spur + [head], pressure=[(0.0, lt), (n + 0.35, lt), (n + 1.0, 1.0)]), rest]


def i(p):
    """A single minim, its head written light with the top spur leading into it (light_head), and the
    mark above (proposed: Pugin's i has no mark)."""
    x = p.x("stem_x", 1190, 15)
    return {"strokes": light_head(p, minim(p, x)), "marks": [i_stroke(p, x)], "baseline": p.fam("bottom")}


def n(p):
    """Two minims; the second's head starts against the first's stem, so the pair joins at the top.
    The first head has the top spur leading into it (entered)."""
    x1, x2 = p.x("stem_1", 1689, 15), p.x("stem_2", 1754, 15)
    return {"strokes": [entered(p, minim(p, x1, spur=False)), minim(p, x2, after=x1)], "baseline": p.fam("bottom")}


def m(p):
    """Three minims, each head starting against the stem before it. The first head has the top spur
    leading into it (entered)."""
    x1, x2, x3 = p.x("stem_1", 1478, 15), p.x("stem_2", 1545, 15), p.x("stem_3", 1612, 15)
    return {"strokes": [entered(p, minim(p, x1, spur=False)), minim(p, x2, after=x1, spur=False), minim(p, x3, after=x2)], "baseline": p.fam("bottom")}


def l(p):
    """A minim rising to the ascender line, its top split into two horns with rounded tips, the same
    split top as b, d, h and k have (split_top). On the plate Pugin's horns run on into hairline
    loops; those will be alternates."""
    return {"strokes": ascender(p, p.x("stem_x", 1399, 15)), "baseline": p.fam("bottom")}


def bowl_pair(p, x1, x2, top1, end2, head2=45.0, bottom2=None, foot2=False, meet=False):
    """The two strokes of a broken bowl, as in o: on the left a stem with no head, cut flat by the
    nib at the top and turning out into the foot; on the right a stroke whose long head starts
    inside the left one (making the bowl's peaked top and its counter's sloping top), coming down
    and stopping with the nib's cut, which lines up with the left stroke's foot. With meet, the
    left stroke's foot runs on to meet the right stroke, for a bowl wider than o's (g)."""
    right = minim(p, x2, head=p.length("right.head", head2, 25, 75), foot=foot2, end=end2, bottom=bottom2)
    left = minim(p, x1, head=0, top=top1, spur=False, run=foot_to_meet(p, x1, right) if meet else None)
    return [left, right]


def o(p):
    """Two strokes round a narrow counter: a flat-topped stem on the left that turns out at the foot,
    and on the right a stroke whose long head starts inside the left one and which stops at the
    bottom with the nib's cut. Where they meet, at the upper left and at the lower right, they make
    one straight edge, as Pugin's do."""
    left, right = bowl_pair(p, p.x("left.x", 1813, 12), p.x("right.x", 1877, 12), p.x("left.top", 3354, 15), p.x("right.end", 3483, 15))
    return {"strokes": [left, right], "edges": [edge_above(p, left, right), edge_below(p, left, right)], "baseline": p.fam("bottom")}


def v(p):
    """A minim on the left, and on the right a stroke with its own head that stops at the bottom with
    the nib's cut, meeting the left one's foot in one straight edge."""
    x1, x2 = p.x("left.x", 2552, 12), p.x("right.x", 2610, 12)
    left, right = minim(p, x1, spur=False), minim(p, x2, foot=False, end=p.x("right.end", 3488, 15))
    return {"strokes": [left, right], "edges": [edge_below(p, left, right)], "baseline": p.fam("bottom")}


def c(p):
    """A stem whose head stroke carries on past it: one wedge across the whole top of the letter, from
    a point at the upper left down to a point well out to the right, as Pugin's c has, written with
    less pressure. That wedge, not an arm added to a head, is what tells c from r. Stem and wedge meet
    in a concave curve at the upper left (concave_top). Pugin's c also hangs a hairline and a ball
    under the wedge; that is left to the flourished form."""
    x, t = p.x("stem_x", 435, 12), p.fam("top")
    top = light(p, path(p, "top", [("from", x + 3, t + 6, None), ("to", x + 55, t + 28, None)], span=14))
    stem = minim(p, x, head=0, top=p.x("stem_top", t + 22, 15))
    return {"strokes": [top, stem], "edges": [concave_top(p, stem, top)], "baseline": p.fam("bottom")}


def e(p):
    """A stem with a flat top, an arm (written with less pressure) leaving its top in a straight wedge
    down to the right, into the crossing member's curl, as the c's top is (Josh: "it should point
    much more directly downward, instead of swooping up"), the two meeting in a concave curve at the
    upper left as in c (concave_top), and the crossing member: a thin cradling stroke drawn with the
    tip of the nib, with a pip at each end (Josh: "for the crossing member, there is a thin cradling
    stem with a pip at each end, crafted with the tip of the nib"). From the top pip it leaves near
    the pip's top and curls over it, down to its rightmost point round the arm's end (Josh: "The top
    pip's cradling should originate a bit more from the top"). Then one gentle S, heading straight
    down at both ends (Josh: "gentle sweeping S curve for the crossmember"), sweeps down to the left
    under the arm's tip to where it touches the stem. Then it turns under the bottom pip and meets it
    from beneath (Josh: "The bottom pip should be cradled from the bottom"). It meets each pip
    cradling it (cradle), so each pip lies in its curl. Where it touches the stem its ink overlaps
    the stem's edge by a quarter of a hairline, closing the eye, as Pugin's does."""
    x, t = p.x("stem_x", 677, 12), p.fam("top")
    arm = light(p, path(p, "arm", [("from", x + 20, t - 3, None), ("to", x + 66, t + 17, None)], span=18))
    import nib as NB
    top, start, leave, k_top = cradle(p, "member.top", x + 75, t - 10, 10.0, -65.0, True)    # from near the pip's top (held: Josh)
    low = np.array([x + nib_at(p, t + 67).corners[2][0] + p.fam("nib_thickness") / 4, p.x("member.low.y", t + 66, 14)])
    # the S runs from the curl's end down to `low`, heading straight down at both ends; its handles
    # (shares of its drop) set how it bends there. The curl and the turn are spirals, easing from the
    # pips' bends into the S's, the bend changing mostly near the pip (Josh: "the outside edge of the
    # s should curve both with tangency and curvature scale into the pips"; "the final turn toward
    # the bottom pip it too sudden"). Where the curl comes out is where the S starts, which sets its
    # bend there: a few rounds settle the two.
    t1, t2 = p.t("member.s.t1"), p.t("member.s.t2")
    k_right = 1 / 45
    for _ in range(12):
        curl, right = spiral(start, leave, 90, k_top, k_right, p.length("member.curl.ease", 2.0, 1.0, 5.0), tight="start")
        sa = t1 * (low[1] - right[1])
        k_new = (2 / 3) * (right[0] - low[0]) / sa ** 2
        if abs(k_new - k_right) < 1e-7:
            break
        k_right = k_new
    sb = t2 * (low[1] - right[1])
    k_low = -(2 / 3) * (right[0] - low[0]) / sb ** 2
    s_curve = np.array([right, right + [0, sa], low - [0, sb], low])
    # the turn under the bottom pip, which meets it from beneath (held: Josh): the pip lies where the
    # turn, bending at last as the pip's edge does, leaves it
    r_end, at_end = p.length("member.end.pip", 10.0, 4.0, 14.0), p.ang("member.end.at", 100.0, 50.0, 150.0)
    rho_end = r_end - p.fam("nib_thickness") / 2
    turn, stop = spiral(low, 90, at_end - 90, k_low, -1 / rho_end, p.length("member.turn.ease", 2.0, 1.0, 5.0), tight="end")
    end = NB.Dot(stop - rho_end * hd(at_end), r_end)
    member = tip(p, curl + [s_curve] + turn)
    stem = minim(p, x, head=0, top=p.x("stem_top", t, 15))
    return {"strokes": [stem, arm, member, top, end], "edges": [concave_top(p, stem, arm), under(p, s_curve, arm[-1][3], 1)],
            "baseline": p.fam("bottom")}


def r(p):
    """A minim, the top spur leading into its head (entered), and off the top right of its head a
    small flag, set apart from the head by a notch, as Pugin's is. Pugin's r hangs a hairline and a
    ball from the flag; that is left to the flourished form.
    Josh has since drawn it himself over the built one (references/hand-drawn-r.svg; decision 0014),
    one shape with its spurs, and the flag with a ball curling under it."""
    if OUTLINES.get("r"):               # drawn by Josh, outline and all
        return {"strokes": drawn(OUTLINES["r"]), "baseline": p.fam("bottom")}
    x, t = p.x("stem_x", 2224, 12), p.fam("top")
    f0 = np.array([x + p.length("flag.from", 38, 32, 50), t + p.length("flag.from_dy", -4, -16, 8)])
    f1 = f0 + [p.length("flag.run", 10, 4, 20), p.length("flag.fall", 10, 2, 22)]
    return {"strokes": [entered(p, minim(p, x)), [line(f0, f1)]], "baseline": p.fam("bottom")}


def t(p):
    """A stem rising a little above the x-height, cut to a point by the nib, turning out at the foot,
    with a short crossbar at the x-height."""
    x, tp = p.x("stem_x", 2482, 12), p.fam("top")
    bar = path(p, "bar", [("left", x - 25, tp + 14, None), ("right", x + 30, tp + 2, None)])
    return {"strokes": [minim(p, x, head=0, top=p.x("stem_top", 3285, 20)), bar], "baseline": p.fam("bottom")}


def b(p):
    """The l's ascender, and on the right a bowl's second stroke, with its own head, stopping at the
    bottom with the nib's cut, which meets the stem's foot in one straight edge. The bowl's head
    starts a little back along its own diagonal, inside the stem, so the bowl closes against the
    stem at the top, as Pugin's does."""
    x1, x2 = p.x("stem_x", 316, 12), p.x("right.x", 380, 12)
    stem, split = ascender(p, x1, spur=False)
    right = minim(p, x2, foot=False, end=p.x("right.end", 3480, 15), lead=p.length("right.lead", 7.5, 0.0, 25.0))
    return {"strokes": [stem, split, right], "edges": [edge_below(p, stem, right)], "baseline": p.fam("bottom")}


def d(p):
    """A bowl's left stroke with a long head, and on the right a stem rising to the ascender line with
    the split top that b, h, k and l have (split_top). Where the bowl's left stroke and its top meet,
    at the upper left, they make one concave curve (concave_top); at the bottom, the left stroke's
    foot runs on to meet the stem. Pugin's stem is upright too, its split top flourished left over
    the bowl and right into a loop; until 2026-10-29 the plain d took his left flourish for an arm
    leaning back over the bowl."""
    x1, x2 = p.x("left.x", 537, 12), p.x("stem_x", 612, 12)
    top = path(p, "bowl_top", [("from", x1 + 6, 3342, 35), ("to", x2 - 6, 3372, 50)])
    stem, split = ascender(p, x2)
    left = minim(p, x1, head=p.length("left.head", 30, 12, 50), spur=False, run=foot_to_meet(p, x1, stem))
    return {"strokes": [left, top, stem, split], "edges": [concave_top(p, left, top)], "baseline": p.fam("bottom")}


def h(p):
    """The l's ascender, and on the right a leg with its own head that runs down past the baseline
    and turns out at the descender line. The leg's head is joined to the stem by a hairline, as the
    n's second minim is (Josh: "h and k need the same connecting spur we added to m and n"). Pugin's
    leg ends in a hairline loop; plain, it turns out as a minim's foot does."""
    x1, x2 = p.x("stem_x", 1046, 12), p.x("leg.x", 1120, 12)
    return {"strokes": ascender(p, x1) + [minim(p, x2, bottom=p.fam("descender"), after=x1)], "baseline": p.fam("bottom")}


def into_stem(p, stroke, x):
    """A stroke run on, straight along its own heading at its end, until it ends on the stem at x, so
    its end is inside the stem and the two are one (k's bowl: Josh, "the bottom of the k bowl to
    fully connect into the stem"). Nothing if the stroke doesn't end heading toward the stem."""
    end, d = stroke[-1][3], stroke[-1][3] - stroke[-1][2]
    if abs(d[0]) < 1e-9 or (x - end[0]) / d[0] <= 0:
        return []
    return [line(end, end + d * (x - end[0]) / d[0])]


def _corner(nb, f):
    """The corner of a nib that is furthest by f (a function of the corner's offset)."""
    return max(nb.corners, key=f)


def head_to_meet(p, x, top, head, left):
    """How far back along its own diagonal a head stroke starts (minim's `lead`), so that it begins in
    the stroke on its left (`left`, ending in a straight run) instead of beside it: until the lower
    corner of its cut is half a hairline inside that stroke's lower edge. For k's leg, which comes
    out of the bowl's lower stroke as Pugin's does (Josh: "the lower k stem to fully connect with
    the bowl")."""
    a, b = left[-1][0], left[-1][3]                        # the left stroke's straight run
    t = (b - a) / np.linalg.norm(b - a)
    n = np.array([-t[1], t[0]]) if t[0] < 0 else np.array([t[1], -t[0]])
    if n[1] < 0:                                           # the run's normal pointing down, out of its lower edge
        n = -n
    edge = a + _corner(nib_at(p, a[1]), lambda c: float(c @ n))     # a point on that lower edge
    ha = np.radians(p.fam("head_angle"))
    back = -np.array([np.cos(ha), np.sin(ha)])             # up and left, back along the head's diagonal
    A = np.array([x - head, top])
    low = A + _corner(nib_at(p, top), lambda c: float(c[1] - c[0]))   # the cut's lower left corner
    inside = float((edge - low) @ n)                       # how far inside the lower edge it is now
    rate = float(-(back @ n))
    if rate <= 1e-9:
        return 0.0
    return max(0.0, (pen_of(p).thickness / 2 - inside) / rate)


def k(p):
    """The l's ascender, a small closed loop at the x-height against its right side, and a leg with
    its own head coming down from under the loop to a foot on the baseline. As Pugin's, the loop is
    joined to the stem at the top by a hairline, as the n's second minim is, and its lower stroke runs
    on into the stem; the leg's head starts in that lower stroke, so the leg comes out of the bowl
    (Josh: "h and k need the same connecting spur we added to m and n, and k needs the bottom of the
    k bowl to fully connect into the stem, and the lower k stem to fully connect with the bowl")."""
    x1 = p.x("stem_x", 1259, 12)
    loop = path(p, "loop", [("top", 1300, 3345, 20), ("right", 1332, 3372, 90), ("low", 1298, 3402, 160)])
    loop = [join_from(p, x1, loop[0][0])] + loop + into_stem(p, loop, x1)
    x2, top, head = p.x("leg.x", 1330, 12), p.x("leg.top", 3418, 15), p.length("leg.head", 32, 10, 55)
    leg = minim(p, x2, top=top, head=head, lead=head_to_meet(p, x2, top, head, loop))
    return {"strokes": ascender(p, x1) + [loop, leg], "baseline": p.fam("bottom")}


def longs(p):
    """The long s: an arm at the top curving over to the right to a point, the stem coming down from
    it past the baseline, and a tail turning left at the descender line; a short spur on the left at
    the x-height. Pugin's tail is a swash; plain, it stops where it turns."""
    x = p.x("stem_x", 2324, 12)
    stroke = path(p, "stroke", [("arm_end", 2392, 3272, 200), ("arm_top", 2352, 3256, 180), ("stem_top", x, 3292, 90),
                                ("stem_low", x - 6, 3556, 95), ("tail", 2268, 3610, 160)], span=18)
    spur = path(p, "spur", [("from", 2266, 3344, None), ("to", x - 10, 3362, None)])
    return {"strokes": [stroke, spur], "baseline": p.fam("bottom")}


def f(p):
    """As the long s, with a crossbar at the x-height. Pugin's f loops over at the top and its tail
    runs on into a swash; plain, the arm ends in a point and the tail stops where it turns."""
    x = p.x("stem_x", 792, 12)
    stroke = path(p, "stroke", [("arm_end", 858, 3262, 200), ("arm_top", 818, 3246, 180), ("stem_top", x, 3282, 90),
                                ("stem_low", x - 6, 3556, 95), ("tail", 742, 3604, 160)], span=18)
    bar = path(p, "bar", [("left", 742, 3400, None), ("right", 848, 3394, None)])
    return {"strokes": [stroke, bar], "baseline": p.fam("bottom")}


def foot_from(p, x, run=None):
    """A foot leaving a stem at x that runs on past the baseline: the turn out of a minim's foot
    (minim), on its own, starting where a minim's would on the stem, so its first cut lies inside
    the stem. p's bowl is closed by one, as b's is by its stem's foot. run: the foot stroke's
    length, if not the family's."""
    fd, fa = p.fam("foot") if run is None else run, p.fam("foot_angle")
    D = np.array([x + fd, p.fam("bottom")])
    C = np.array([x, p.fam("bottom") - fd * np.tan(np.radians(fa)) - p.fam("foot_turn")])
    return [cubic(C, S, D, fa, 1.0, 1.0)]


def p_(p):
    """A stem with its own head running down past the baseline to the split bottom at the descender
    line (split_bottom), and a bowl on its right. At the top the bowl's head is joined to the stem
    by a hairline, as the n's second minim is (Josh: "The top of the bowl needs the spur to connect
    it, like other contexts"). At the bottom it is closed as b's is: a stroke with its
    own head that stops with the nib's cut, and a foot leaving the stem at the baseline (foot_from),
    the two meeting in one straight edge (edge_below), as Pugin's are on the plate. The bowl is
    wider than b's, so the foot runs on further than the family's, as d's and q's do (its length
    fitted to his). His foot comes into the stem from a curl on its left, and the descender runs
    on into a long swash; plain, neither does.
    - Until 2026-10-29 the descender turned out at the descender line as a minim's foot does.
    - Until then too the bowl was closed by a long diagonal from the right stroke's foot back to the
      stem, whose first cut stood out past the bowl (Josh: "fix the bottom of the bowl - it's pretty
      standard - not sure why it has this weird diagonal stroke for the bottom of the bowl"; "you
      don't need to add the extra flourish on the left side of the p").
    Josh has since drawn it himself over the repaired one (references/hand-drawn-p.svg; decision
    0014), with Pugin's flourishes on the left: a curl off the head, and the bowl's foot sweeping
    across the stem into a curl. Its split bottom is the built one's, as it was when he drew it; it
    no longer moves with the split's settings."""
    if OUTLINES.get("p"):               # drawn by Josh, outline and all
        return {"strokes": drawn(OUTLINES["p"]), "baseline": p.fam("bottom")}
    x1, x2 = p.x("stem_x", 1957, 12), p.x("right.x", 2028, 12)
    split, end = split_bottom(p, x1)
    right = minim(p, x2, foot=False, end=p.x("right.end", 3480, 25), after=x1)
    foot = foot_from(p, x1, p.length("foot.run", 27, 20, 60))
    return {"strokes": [minim(p, x1, foot=False, end=end), split, right, foot], "edges": [edge_below(p, foot, right)],
            "baseline": p.fam("bottom")}


def q(p):
    """o's two strokes, meeting at the upper left in one straight edge, the right one running on past
    the baseline to the split bottom at the descender line (split_bottom); the left stroke's foot
    runs on to meet it. Pugin's descender ends in a swash splayed both ways; plain, it splits as p's
    does. Until 2026-10-29 it turned out as a minim's foot does."""
    x1, x2 = p.x("left.x", 2088, 12), p.x("right.x", 2152, 12)
    split, end = split_bottom(p, x2)
    left, right = bowl_pair(p, x1, x2, p.x("left.top", 3352, 15), end, meet=True)
    return {"strokes": [left, right, split], "edges": [edge_above(p, left, right)], "baseline": p.fam("bottom")}


def g(p):
    """o's two strokes, meeting at the upper left in one concave curve (concave_top), the right one running on past
    the baseline and sweeping round to the left under the letter, and a small ear to the right at
    the top. The bowl is wider than o's, so the left stroke's foot runs on to meet the right one.
    Pugin's tail ends in a hairline curl; plain, it stops with the nib's cut.
    Josh has since drawn it himself over Pugin's (references/hand-drawn-g.svg; decision 0014): the
    left stroke with the arm and ear, and the right stroke with the tail, two shapes kept apart by
    the hairlines of white Pugin leaves where they meet."""
    if OUTLINES.get("g"):               # drawn by Josh, outline and all
        return {"strokes": drawn(OUTLINES["g"]), "baseline": p.fam("bottom")}
    x1, x2 = p.x("left.x", 900, 12), p.x("right.x", 973, 12)
    left, right = bowl_pair(p, x1, x2, p.x("left.top", 3352, 15), 3520, meet=True)
    tail = path(p, "tail", [("from", x2, 3518, 90), ("turn", x2 + 10, 3568, 120), ("end", 900, 3592, 185)], span=18)
    ear = path(p, "ear", [("from", x2 + 8, 3340, None), ("to", 1004, 3332, None)])
    return {"strokes": [left, right, tail, ear], "edges": [concave_top(p, left, right)], "baseline": p.fam("bottom")}


def y(p):
    """v's two strokes, the right one running on past the baseline and sweeping round to the left; the
    left one's foot runs on to meet it. Pugin's tail ends in a ball; plain, it stops with the nib's
    cut. Pugin drew it on the plate's second line, squeezed; the plain y stands at the full x-height.
    Josh's own y, drawn by hand, stands beside it as an alternate (y.alt, under ss03; decision 0014)."""
    x1, x2 = p.x("left.x", 1342, 12), p.x("right.x", 1405, 12)
    right = minim(p, x2, foot=False, end=p.fam("bottom"))
    tail = path(p, "tail", [("from", x2, p.fam("bottom") - 2, 90), ("end", x2 - 105, p.fam("descender"), 175)], span=18)
    left = minim(p, x1, spur=False, run=foot_to_meet(p, x1, right))
    return {"strokes": [left, right, tail], "baseline": p.fam("bottom"), "fit_affine": second_line(p)}


def x(p):
    """A stem with its own head running down past the baseline and turning left at the descender
    line, a short flag to the right at the top, and a short stroke down to the right from the
    middle of the stem to the baseline. Pugin's tail ends in a ball and his strokes in hairlines;
    plain, they stop with the nib's cut."""
    xs = p.x("stem_x", 2677, 12)
    stem = path(p, "stem", [("top", xs, 3360, 90), ("low", xs - 8, 3570, 95), ("tail", 2630, 3622, 165)], span=15)
    head = minim(p, xs, foot=False, end=3362)
    flag = path(p, "flag", [("from", xs + 10, 3346, None), ("to", 2740, 3344, None)])
    leg = path(p, "leg", [("from", xs + 8, 3462, 50), ("to", 2722, 3520, 45)])
    return {"strokes": [head, stem, flag, leg], "baseline": p.fam("bottom")}


def a(p):
    """The two-storey a, drawn as Pugin's pen drew it, in three strokes (Josh):
    - the stem, from the top of the letter, its upper part bowing slightly in down to the waist, then
      straight on down to its foot;
    - the bottom bowl, leaving the waist, coming down the left and turning out into a foot that ends
      in a spur reaching up toward the stem (its measurements held: "It was correct before");
    - the top bowl, one smooth curve: from the stem's top, rising to the left to make the sloped top,
      over and down the left side, and back to end exactly where the bottom bowl begins.
    Each stroke flows; where they meet they meet at a point, so the outline keeps the sharp corners
    there that give the letter its edge. The top bowl is written with less pressure, lighter than the
    stem (Josh: "Same with the e and top bowl on the a")."""
    xs = p.x("stem_x", 238, 12)
    bowl = path(p, "bowl", [("waist", 222, 3438, 160), ("left", 180, 3466, 90), ("low", 180, 3494, 90), ("foot", 206, 3520, 40)], span=15)
    bowl += spur_from(p, bowl[-1][3])
    w0 = bowl[0][0]
    s0 = np.array([xs, p.x("stem.top_y", 3366, 22)])           # where the stem and the top bowl both start
    wy = p.x("stem.waist_y", 3432, 25)
    stem = [cubic(s0, p.ang("stem.top_heading", 90, 70, 110), np.array([xs, wy]), S, p.t("stem.t1"), p.t("stem.t2"))]
    stem += minim(p, xs, head=0, top=wy)                        # on down from the waist, the same stroke
    top = np.array([p.x("bowl_top.top.x", 205, 14), p.x("bowl_top.top.y", 3338, 14)])
    left = np.array([p.x("bowl_top.left.x", 174, 14), p.x("bowl_top.left.y", 3392, 18)])
    leave, down = p.ang("bowl_top.start_heading", 215, 190, 245), p.ang("stem.top_heading", 90, 70, 110)
    upper = light(p, [cubic(s0, leave, top, 180, p.t("bowl_top.t1"), p.t("bowl_top.t2")),
                      cubic(top, 180, left, S, p.t("bowl_top.t3"), p.t("bowl_top.t4")),
                      cubic(left, S, w0, p.ang("bowl_top.end_heading", 40, 10, 70), p.t("bowl_top.t5"), p.t("bowl_top.t6"))])
    # the top bowl is lighter than the stem, so at the stem's top the stem's full cut would stand proud
    # of the sloped top: the sloped top runs straight on until it meets the stem's right edge instead
    full = nib_at(p, s0[1])
    proud = (1 - upper.pressure) * full.width / 2                                       # how far the stem's corner stands out
    slope = s0 + full.corners[1] - proud * full.u                                       # the lighter nib's upper corner
    along, edge = -hd(leave), s0 + full.corners[2]                                      # the sloped top; the stem's right edge
    k = np.linalg.solve(np.column_stack([along, -hd(down)]), edge - slope)[0]
    return {"strokes": [stem, bowl, upper], "edges": [(slope - proud * along, slope + k * along, s0)], "baseline": p.fam("bottom")}


def turned(p, stroke, pre, angles, pressures=None):
    """A stroke the scribe turns the pen along, and presses on as he goes: the nib held at each of
    `angles` ((s along the stroke, name, starting angle) each, a measurement of its own,
    `pre`.<name>.angle), turned smoothly between them; and, with `pressures` ((s, name, starting
    pressure) each, `pre`.<name>.pressure), narrowed or spread to that share of its width there,
    changing smoothly between. The nib's
    corners sweep curves as it turns, which make the concave edges a nib held at one angle can't
    (Josh, of the s: "notice the concave curves created by the sweep of the nib during rotation"),
    and the pressure varies the stroke's width along its length (Josh: "create a pressure dimension
    along the length of the entire line, which varies the width")."""
    import nib as NB
    angle = [(at, p.ang(f"{pre}.{name}.angle", a, a - 35, a + 35)) for at, name, a in angles]
    pressure = [(at, p.length(f"{pre}.{name}.pressure", v, 0.15, 1.25)) for at, name, v in pressures] if pressures else 1.0
    return NB.Stroke(stroke, pressure=pressure, angle=angle)


def steadiness(stroke, n=60, w_angle=1.5, w_pressure=150.0):
    """How sharply the pen turns and presses along a stroke, as residuals the fit adds to its own:
    the bend of the nib's angle and of its pressure at n even steps of the stroke's length (second
    differences), weighted so that a turn or a press made over a few pixels costs as much as a few
    pixels off Pugin's edge, and one eased over a stroke's length next to nothing. So the fit turns
    and presses the pen no more sharply than his letter asks (Josh: "both pressure and angle should
    probably be smoother in the transitions")."""
    import nib as NB
    m = len(stroke)
    sg = np.linspace(0, m, 40 * m + 1)
    L = stroke.length_at(sg)
    su = np.interp(np.linspace(0, L[-1], n), L, sg)
    a = NB._turned(stroke, su) if getattr(stroke, "angle", None) is not None else np.zeros(n)
    pr = np.zeros(n) if np.isscalar(stroke.pressure) or not w_pressure else np.atleast_1d(NB.pressure_at(stroke, su))
    return np.concatenate([w_angle * np.diff(a, 2), w_pressure * np.diff(pr, 2)])


def pip_on(p, pre, start, h0, drop, r, at, clockwise, ease=2.5):
    """A fine stroke of the nib's tip leaving a stroke at `start`, heading h0, and winding into a
    pip that it meets as the e's member meets its bottom pip (cradle): its bend easing from nothing
    into the pip's, mostly near the pip, so its edge runs on into the pip's with neither kink nor
    change of bend. First it runs straight on for a fitted length, then it turns. Returns the stroke
    (drawn with the tip) and the pip."""
    import nib as NB
    r, at = p.length(f"{pre}.pip", r, 6.0, 14.0), p.ang(f"{pre}.at", at, at - 60, at + 60)
    rho = r - p.fam("nib_thickness") / 2
    drop = p.length(f"{pre}.drop", drop, 0.0, 30.0)
    a = start + drop * hd(h0)
    sign = 1 if clockwise else -1
    h1 = at + 90 if clockwise else at - 90
    while sign * (h1 - h0) <= 0:            # the way round it winds
        h1 += sign * 360
    turn, stop = spiral(a, h0, h1, 0.0, sign / rho, p.length(f"{pre}.ease", ease, 1.0, 5.0), tight="end")
    return tip(p, [line(start, a)] + turn), NB.Dot(stop - rho * hd(at), r)


# ── Strokes drawn by hand ─────────────────────────────────────────────────────

# Letters Josh draws himself, point by point, on the proof page's pen editor (Josh: "can create for me
# an editor, where I can define, at any point I create, the position, angle, and pressure? I'm pretty
# sure I can draw it myself"). A letter's recipe holds its drawing ("drawn"); the build and the
# editor load it here, and the letter is drawn from it, not from its construction's measurements.
PENNABLE = set()          # the s was, until Josh drew its outline himself (OUTLINES)
DRAWN = {}

# Letters whose whole outline Josh has drawn himself, in a drawing program, over Pugin's (decision 0014;
# Josh: "I drew it myself, and dropped it as an SVG in the references folder"): references/hand-drawn-<g>.svg,
# placed on the plate by the .json beside it. The build takes the outline as it stands. A letter Pugin
# drew on the plate's second line, shorter, stands at full height here, and OUTLINE_ON_PLATE maps it
# back onto his for comparison (the y). A drawing may stand beside a letter rather than for it: an
# alternate (ALTERNATES: y.alt, Josh's y beside the one built from Pugin's), reached through a
# stylistic set and spaced and kerned in its own right.
OUTLINES = {}
OUTLINE_ON_PLATE = {}
ALTERNATES = {}


def _inside(pt, poly):
    """Whether a point lies inside a polygon (an array of its points), by the even-odd rule."""
    xs, ys = poly[:, 0], poly[:, 1]
    x2, y2 = np.roll(xs, -1), np.roll(ys, -1)
    cross = (ys > pt[1]) != (y2 > pt[1])
    xi = xs + (pt[1] - ys) * (x2 - xs) / np.where(y2 == ys, 1e-12, y2 - ys)
    return bool(np.sum(cross & (pt[0] < xi)) % 2)


def drawn(contours):
    """Josh's drawing (OUTLINES[g]) as filled shapes, filled as his drawing program fills it
    (even-odd): a path lying inside another is a hole in it, cut from the shape round it (nib.Shape's
    `holes`): a bowl's counter. A path inside a hole is a shape again. A path only touching another,
    as the p's curls touch its stem, is a shape of its own, joined to it: inside is by most of a
    path's points, not one of them."""
    import nib as NB
    pts = [G.sample([np.asarray(q, float) for q in c], 12) for c in contours]
    within = lambda i, j: i != j and np.mean([_inside(q, pts[j]) for q in pts[i]]) > 0.5
    depth = [sum(within(i, j) for j in range(len(contours))) for i in range(len(contours))]
    shapes = []
    for i, c in enumerate(contours):
        if depth[i] % 2 == 0:
            s = NB.Shape(c)
            s.holes = [contours[j] for j in range(len(contours)) if depth[j] == depth[i] + 1 and within(j, i)]
            shapes.append(s)
    return shapes


def hand_drawn(name):
    """The letter drawn from Josh's outline as it stands (OUTLINES[name])."""
    def letter(p):
        return {"strokes": drawn(OUTLINES[name]), "baseline": p.fam("bottom"), "fit_affine": OUTLINE_ON_PLATE.get(name)}
    letter.__doc__ = ALTERNATES.get(name, {}).get("description")
    return letter


def through(points):
    """The pen's path through drawn points (each {"x", "y", "corner"}), as cubics: at a smooth point it
    passes on a tangent between the directions to its neighbours, each handle a third of the way to
    the next point; at a corner point it turns sharply, each side heading straight for its neighbour."""
    P = [np.array([q["x"], q["y"]], float) for q in points]
    unit = lambda v: v / max(np.linalg.norm(v), 1e-9)
    n = len(P)
    t_in, t_out = [], []
    for i in range(n):
        back = unit(P[i] - P[i - 1]) if i > 0 else None
        ahead = unit(P[i + 1] - P[i]) if i < n - 1 else None
        if back is None or ahead is None:
            t = back if ahead is None else ahead
            t_in.append(t), t_out.append(t)
        elif points[i].get("corner"):
            t_in.append(back), t_out.append(ahead)
        else:
            d0, d1 = np.linalg.norm(P[i] - P[i - 1]), np.linalg.norm(P[i + 1] - P[i])
            t = unit((P[i] - P[i - 1]) / max(d0, 1e-9) ** 2 * d1 + (P[i + 1] - P[i]) / max(d1, 1e-9) ** 2 * d0)
            t_in.append(t), t_out.append(t)
    out = []
    for i in range(n - 1):
        d = np.linalg.norm(P[i + 1] - P[i])
        out.append(np.array([P[i], P[i] + d / 3 * t_out[i], P[i + 1] - d / 3 * t_in[i + 1], P[i + 1]]))
    return out


def drawn_stroke(points):
    """A stroke drawn by hand: the pen's path through the points, the nib held at each point's angle
    and pressed by its pressure there, both changing smoothly between, by the length of the path."""
    import nib as NB
    return NB.Stroke(through(points), angle=[(i, float(q["angle"])) for i, q in enumerate(points)],
                     pressure=[(i, float(q["pressure"])) for i, q in enumerate(points)])


def s(p):
    """The textura s: a single stroke of the pen (Josh: "The s is a single stroke of the pen"), the
    scribe turning the nib as it goes (Josh: "Reproducing it accurately will require thoughtful nib
    rotation. notice the concave curves created by the sweep of the nib during rotation"). From the
    horn at the top right the pen goes left along the top to the peak, the nib turning flatter, which
    scoops the top edge; at the peak it turns down to the left stem, the nib's sweep leaving the
    concave edge at the upper left, and the scribe pressing harder round the shoulder, which spreads
    the nib and pushes out the point there (Josh: "I suspect a bit of pressure pushes the nib of the
    pen out at the points"); down the stem, across the spine (the nib flatter, so the spine is
    thinner than the stems) and down the right stem, the turns' sweeps leaving the concave corners of
    the counters; then down to the foot, the bottom point, and left along the bottom to the tail,
    the nib turning steeper again, as at the horn. Nearly the same turned half round. At each end,
    a fine stem of the nib's tip winds into a pip (Josh: "the s also has two pips off of stems at
    each terminal"): from under the top down and round under its pip, and from the bottom up and
    round over its pip."""
    if OUTLINES.get("s"):               # drawn by Josh, outline and all
        import nib as NB
        import geom as G
        # its largest path is the main stroke; the others, each fine stem with its pip, can be left
        # off (the stylistic set ss02, "Without stems and pips"; Josh: "And you have the stems able to
        # enabled and disabled")
        paths = sorted(OUTLINES["s"], key=lambda c: -abs(G.signed_area(c)))
        return {"strokes": [NB.Shape(c) for c in paths], "pips": list(range(1, len(paths))), "baseline": p.fam("bottom")}
    if DRAWN.get("s"):                  # drawn by Josh, point by point
        return {"strokes": [drawn_stroke(DRAWN["s"])], "baseline": p.fam("bottom")}
    import nib as NB
    peak = np.array([p.x("peak.x", 2393, 15), p.x("peak.y", 3348, 15)])
    foot = np.array([p.x("foot.x", 2411, 15), p.x("foot.y", 3512, 15)])
    xl, xr = p.x("left.x", 2370, 12), p.x("right.x", 2425, 12)
    l0, l1 = np.array([xl, p.x("left.top", 3386, 20)]), np.array([xl, p.x("left.low", 3413, 15)])
    r1, r2 = p.length("turn1", 12.7, 4, 30), p.length("turn2", 12.9, 4, 30)
    m0 = l1 + [r1, r1]
    q0 = np.array([xr, p.x("right.top", 3444, 15)])
    m1 = q0 - [r2, r2]
    q1 = np.array([xr, p.x("right.low", 3492, 20)])
    hs = np.degrees(np.arctan2(*(m1 - m0)[::-1]))                     # the spine's own heading
    tt = 0.55                                                          # a turn's handles: near a circle's
    level = p.length("nib.level", 0.79, 0.6, 1.3)
    # At each end the scribe twists the pen: the nib pivots on one of its ends while the other sweeps
    # round a quarter circle as wide as the nib, so the stroke ends in a round swish between two points,
    # the nib's ends swapping places as it turns (Josh: "the terminal of the stroke at both ends (top
    # and bottom) swish a curve to a rounded point, so that the what otherwise would be the bottom of the
    # nib makes top point, and the top of the nib makes the bottom point"; his drawing of the s's main
    # stroke, references/hand/s-main.png, has round ends just the nib's width across). At the top the
    # pen sets the nib down from the pivot to the horn's point, and turns it on the pivot until it
    # stands upright below it, then goes on left along the top; at the tail, the same turned half
    # round. The nib's middle goes round the pivot at half its width; its pressure is the stroke's
    # level there. And the pivot slides a little as the nib turns, along a path that may bow, so the
    # edge it leaves between the pivot and the point is the concave scoop of Josh's drawing, not the
    # straight print of the nib (Josh: "let each pivot slide a little as the nib turns").
    R = p.fam("nib_width") * level / 2
    def pivot(pre, c, a0, a1, side):
        """The nib's middle, going round the pivot as the nib turns from a0 to a1 (degrees), on the
        side `side` (1: along the nib's angle from the pivot, -1: against it), the pivot sliding from c
        by `pre`.slide and bowing by `pre`.bow at the middle of the turn; as three cubics, each a
        Hermite piece of it. Returns them and the heading it leaves and arrives on."""
        slide = np.array([p.length(f"{pre}.slide.x", 0.0, -15, 15), p.length(f"{pre}.slide.y", 0.0, -15, 15)])
        bow = np.array([p.length(f"{pre}.bow.x", 0.0, -10, 10), p.length(f"{pre}.bow.y", 0.0, -10, 10)])
        u = lambda a: np.array([np.cos(np.radians(a)), -np.sin(np.radians(a))])
        du = lambda a: np.radians(1) * np.array([-np.sin(np.radians(a)), -np.cos(np.radians(a))])      # per degree
        f = lambda a: (a - a0) / (a1 - a0)
        mid = lambda a: c + f(a) * slide + 4 * f(a) * (1 - f(a)) * bow + side * R * u(a)
        d = lambda a: (slide + 4 * (1 - 2 * f(a)) * bow) / (a1 - a0) + side * R * du(a)               # per degree of a
        out, edges = [], np.linspace(a0, a1, 4)
        for t0, t1 in zip(edges, edges[1:]):
            out.append(np.array([mid(t0), mid(t0) + (t1 - t0) / 3 * d(t0), mid(t1) - (t1 - t0) / 3 * d(t1), mid(t1)]))
        way = np.sign(a1 - a0)
        h = lambda a: np.degrees(np.arctan2(*(way * d(a))[::-1]))
        return out, h(a0), h(a1)
    piv_top = np.array([p.x("pivot.top.x", 2410, 15), p.x("pivot.top.y", 3340, 15)])
    a_top = (p.ang("pivot.top.from", 196, 150, 240), p.ang("pivot.top.to", 90, 50, 130))
    piv_bot = np.array([p.x("pivot.bottom.x", 2392, 15), p.x("pivot.bottom.y", 3521, 15)])
    a_bot = (p.ang("pivot.bottom.from", 118, 70, 160), p.ang("pivot.bottom.to", 188, 150, 230))
    top_twist, _, h_horn = pivot("pivot.top", piv_top, *a_top, -1)
    bot_twist, h_tail, _ = pivot("pivot.bottom", piv_bot, *a_bot, 1)
    horn, tail = top_twist[-1][3], bot_twist[0][0]
    path_ = top_twist + [
             cubic(horn, h_horn, peak, p.ang("peak.in", 201, 160, 240), p.t("top.t1", 0.27), p.t("top.t2", 0.85)),
             cubic(peak, p.ang("peak.out", 160, 100, 200), l0, 90, p.t("shoulder.t1"), p.t("shoulder.t2")),
             line(l0, l1), cubic(l1, 90, m0, hs, tt, tt), line(m0, m1), cubic(m1, hs, q0, 90, tt, tt), line(q0, q1),
             cubic(q1, 90, foot, p.ang("foot.in", 93, 60, 160), p.t("haunch.t1"), p.t("haunch.t2")),
             cubic(foot, p.ang("foot.out", 204, 160, 240), tail, h_tail, p.t("bottom.t1", 0.59), p.t("bottom.t2", 0.48))] + bot_twist
    # the nib's angle through the twist at the top, along the top, at the peak, round the shoulder,
    # down the left stem, at the spine's middle, down the right stem, round the haunch, at the foot,
    # along the bottom, and through the twist at the tail, turning smoothly between them by the length
    # of the stroke; one angle down each stem. The turning makes the shape (Josh: "The rest here is
    # handled by nib rotation"): its sweeps scoop the top and the bottom, leave the concave edge from
    # the shoulder's point to the peak and the concave corners of the counters, and round the two
    # ends. The fit is charged for sharp turns of it (steadiness; Josh: "both pressure and angle should
    # probably be smoother in the transitions").
    ang = lambda name, a: p.ang(f"nib.{name}.angle", a, a - 35, a + 35)
    lerp = lambda a, k: a[0] + (a[1] - a[0]) * k / 3
    angles = [(k, lerp(a_top, k)) for k in range(4)] + [
              (3.3, ang("horn", 70.8)), (4, ang("peak", 50.6)),
              (4.5, ang("shoulder", 18.2)), (5, ang("stem", 36.5)), (6, ang("stem", 36.5)), (7.5, ang("spine", 14.7)),
              (9, ang("right", 30.6)), (10, ang("right", 30.6)), (10.5, ang("haunch", 20.8)), (11, ang("foot", 72.1)),
              (11.7, ang("tail", 78.9))] + [(12 + k, lerp(a_bot, k)) for k in range(4)]
    # The pressure: one steady level along the whole stroke, with a little bump of more at each turn,
    # which spreads the nib there and pushes out the point at the corner of the turn (Josh: "Pressure
    # seems to vary too much in this context. It should be a straight line, with little pressure
    # bumps at each turn, to produce the horns at the corners of the turns"): at the peak, round the
    # shoulder, the turns into and out of the spine, round the haunch, and at the foot.
    turns = [(4, "peak"), (4.5, "shoulder"), (6.5, "turn1"), (8.5, "turn2"), (10.5, "haunch"), (11, "foot")]
    stroke = NB.Stroke(path_, angle=angles, pressure=NB.Bumps(level, [(at, p.length(f"bump.{name}.height", 0.1, 0.0, 0.5),
                                                                       p.length(f"bump.{name}.reach", 8.0, 2.0, 30.0)) for at, name in turns]))
    strokes = [stroke]
    if PIPS:
        up_start = np.array([p.x("top_hair.x", 2434, 10), p.x("top_hair.y", 3368, 10)])
        lo_start = np.array([p.x("low_hair.x", 2376, 10), p.x("low_hair.y", 3488, 10)])
        up_hair, up_pip = pip_on(p, "top_hair", up_start, 90, 1.3, 10.6, 118, False, ease=3.0)
        lo_hair, lo_pip = pip_on(p, "low_hair", lo_start, -90, 12.9, 10.0, 291, False, ease=2.5)
        strokes += [up_hair, up_pip, lo_hair, lo_pip]
    # fitted against his main stroke alone, his stems and pips dropped (Josh: "You need to drop the
    # stems and nibs to do this analysis"); with the stems and pips, they're fitted after, the main
    # stroke held
    stages = [{"strokes": [0], "ref": "main", "exclude": ["top_hair", "low_hair"]}]
    if PIPS:
        stages.append({"keys": ["top_hair", "low_hair"], "smooth": False})
    return {"strokes": strokes, "baseline": p.fam("bottom"), "smooth": steadiness(stroke, w_pressure=0.0), "fit_stages": stages}


# The s's stems and pips are left off while its main stroke's shape is worked out (Josh: "I want the
# stems and pips disabled while we do this work. We need to focus on nailing the shape").
PIPS = False


def z(p):
    """The textura z: a bar along the top rising to the right, a diagonal down to the left, and a
    lower stroke turning back along the baseline and away to the left. Pugin's tail is a hairline
    swash; plain, it stops. Pugin drew it on the plate's second line, squeezed; the plain z stands
    at the full x-height."""
    tp, bt = p.fam("top"), p.fam("bottom")
    top = path(p, "top", [("left", 1442, tp + 14, None), ("right", 1512, tp + 6, None)])
    diag = path(p, "diagonal", [("from", 1510, tp + 14, None), ("to", 1460, tp + 96, None)])
    lower = path(p, "lower", [("from", 1452, tp + 100, 20), ("right", 1520, tp + 140, 90), ("bottom", 1490, bt, 170), ("end", 1440, bt + 4, 185)], span=18)
    return {"strokes": [top, diag, lower], "baseline": bt, "fit_affine": second_line(p)}


# ── Letters Pugin didn't draw ─────────────────────────────────────────────────
# Proposals in his idiom (decision 0008), built from the fitted measurements of the letter each is
# modelled on (DERIVED), not fitted to anything of his.

def u(p):
    """n turned over: two minims, the first's foot running on to end against the second's stem, so
    the pair joins at the foot as n's joins at the head. Each has its own head. Modelled on n."""
    x1, x2 = p.x("stem_1", 1689, 15), p.x("stem_2", 1754, 15)
    return {"strokes": [minim(p, x1, before=x2), minim(p, x2)], "baseline": p.fam("bottom")}


def w(p):
    """u followed by v's second stroke: two minims joined at the foot, and a third stroke with its own
    head that stops with the nib's cut, meeting the second's foot in one straight edge, as v's does.
    Modelled on v, whose two strokes set the pitch."""
    x1 = p.x("left.x", 2552, 12)
    pitch = p.x("right.x", 2610, 12) - x1
    x2, x3 = x1 + pitch, x1 + 2 * pitch
    second, third = minim(p, x2, spur=False), minim(p, x3, foot=False, end=p.x("right.end", 3488, 15))
    return {"strokes": [minim(p, x1, before=x2), second, third], "edges": [edge_below(p, second, third)], "baseline": p.fam("bottom")}


def j(p):
    """i running on past the baseline and turning left at the descender line, as ſ's tail does,
    stopped by the nib; with i's light head, top spur and mark (Josh: "give the j the same light
    head and top spur as the i", 2026-10-29). Modelled on i."""
    x0 = p.x("stem_x", 1190, 15)
    bt, ds = p.fam("bottom"), p.fam("descender")
    stem = minim(p, x0, foot=False, end=bt - 30)
    tail = [cubic(np.array([x0, bt - 30]), S, np.array([x0 - 52, ds]), 172, 0.6, 0.6)]
    return {"strokes": light_head(p, stem) + [tail], "marks": [i_stroke(p, x0)], "baseline": bt}


LETTERS = {"i": i, "n": n, "m": m, "l": l, "o": o, "v": v, "c": c, "e": e, "r": r, "t": t, "b": b, "d": d, "h": h, "k": k,
           "longs": longs, "f": f, "p": p_, "q": q, "g": g, "y": y, "x": x, "a": a, "s": s, "z": z,
           "u": u, "w": w, "j": j}
DERIVED = {"u": "n", "w": "v", "j": "i"}      # a letter Pugin didn't draw: the letter whose fitted measurements it takes
