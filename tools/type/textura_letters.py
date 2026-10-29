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
from construct import Params, S, cubic, hd, line

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
            u = nib_at(p, A[1]).u
            out.append(line(A - (A[0] - after) / u[0] * u, A))
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


def spur_from(p, end):
    """The spur leaving a free foot that ends at `end`: a short hairline up and to the right along the
    nib's own edge, as the pen holds it there, when the letter is written with spurs (p.spur, set by
    the build); otherwise nothing."""
    sp = getattr(p, "spur", None)
    if not sp:
        return []
    return [line(end, end + sp["length"] * nib_at(p, end[1]).u)]


def path(p, pre, nodes, span=15.0, turn=25.0):
    """A free stroke of the pen through named nodes, each (name, x, y, heading): the letter's own
    measurements, within `span` px and `turn` degrees of where they start. Between two nodes whose
    headings are both None the stroke runs straight; otherwise it is a curve leaving and arriving on
    those headings."""
    pts, hds = [], []
    for name, x, y, h in nodes:
        pts.append(np.array([p.x(f"{pre}.{name}.x", x, span), p.x(f"{pre}.{name}.y", y, span)]))
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


def ascender_arm(p, x, pre="arm"):
    """The right branch of a forked ascender: from the stem near its top, a short spur up and to the
    right. On the plate it runs on as a thick arm into a hairline flourish; the plain form keeps only
    its start, since an arm reaching over the next letter is what makes a long s (ſ), not an l."""
    F = np.array([x, p.fam("ascender") + p.length(f"{pre}.from", 30, 5, 70)])
    E = np.array([x + p.length(f"{pre}.reach", 16, 8, 20), p.fam("ascender") + p.length(f"{pre}.end_dy", 0, -30, 20)])
    return [cubic(F, p.ang(f"{pre}.leave", 300, 270, 340), E, p.ang(f"{pre}.arrive", 345, 315, 380), p.t(f"{pre}.t1"), p.t(f"{pre}.t2"))]


def ascender(p, x, spur=True):
    """A minim rising to the ascender line with a forked top (l's), whose foot stands on the baseline."""
    return [minim(p, x, top=p.fam("ascender"), spur=spur), ascender_arm(p, x)]


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
    return NB.pressed(nib_at(p, y), getattr(stroke, "pressure", 1.0))


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

def i_stroke(p, x):
    """The stroke over an i: a short hairline rising to the right above the head, as scribes of the
    period marked an i so it could be told from the minims round it. Pugin's i on plate 9 has none;
    this is a proposal, drawn in the pen's idiom and not fitted."""
    a = np.radians(30.0)                          # a little flatter than the nib, so it has some weight
    c = np.array([x + 4, p.fam("top") - 40])
    h = 13 * np.array([np.cos(a), -np.sin(a)])
    return [line(c - h, c + h)]


def i(p):
    """A single minim, with a hairline stroke above it (proposed: Pugin's i has none)."""
    x = p.x("stem_x", 1190, 15)
    return {"strokes": [minim(p, x)], "marks": [i_stroke(p, x)], "baseline": p.fam("bottom")}


def n(p):
    """Two minims; the second's head starts against the first's stem, so the pair joins at the top."""
    x1, x2 = p.x("stem_1", 1689, 15), p.x("stem_2", 1754, 15)
    return {"strokes": [minim(p, x1, spur=False), minim(p, x2, after=x1)], "baseline": p.fam("bottom")}


def m(p):
    """Three minims, each head starting against the stem before it."""
    x1, x2, x3 = p.x("stem_1", 1478, 15), p.x("stem_2", 1545, 15), p.x("stem_3", 1612, 15)
    return {"strokes": [minim(p, x1, spur=False), minim(p, x2, after=x1, spur=False), minim(p, x3, after=x2)], "baseline": p.fam("bottom")}


def l(p):
    """A minim rising to the ascender line, its top forked: the head stroke comes in from the upper
    left, and a short spur leaves up and to the right. On the plate the spur runs on as a thick arm
    into a hairline flourish; plain, it stops short, so the l can't be taken for a long s."""
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
    """A stem with a flat top, an arm (written with less pressure) leaving its top to the right, the two
    meeting in a concave curve at the upper left as in c (concave_top), and a hairline from the stem
    up to the arm's end, closing the eye. Pugin's hairline ends in a ball inside the eye; plain, it
    doesn't."""
    x, t = p.x("stem_x", 677, 12), p.fam("top")
    arm = light(p, path(p, "arm", [("from", x + 10, t + 10, 20), ("to", x + 68, t + 30, 40)]))
    hair = path(p, "hairline", [("from", x + 22, t + 88, None), ("to", x + 62, t + 40, None)])
    stem = minim(p, x, head=0, top=p.x("stem_top", t, 15))
    return {"strokes": [stem, arm, hair], "edges": [concave_top(p, stem, arm)], "baseline": p.fam("bottom")}


def r(p):
    """A minim, and off the top right of its head a small flag, set apart from the head by a notch, as
    Pugin's is. Pugin's r hangs a hairline and a ball from the flag; that is left to the flourished
    form."""
    x, t = p.x("stem_x", 2224, 12), p.fam("top")
    f0 = np.array([x + p.length("flag.from", 38, 32, 50), t + p.length("flag.from_dy", -4, -16, 8)])
    f1 = f0 + [p.length("flag.run", 10, 4, 20), p.length("flag.fall", 10, 2, 22)]
    return {"strokes": [minim(p, x), [line(f0, f1)]], "baseline": p.fam("bottom")}


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
    stem, arm = ascender(p, x1, spur=False)
    right = minim(p, x2, foot=False, end=p.x("right.end", 3480, 15), lead=p.length("right.lead", 7.5, 0.0, 25.0))
    return {"strokes": [stem, arm, right], "edges": [edge_below(p, stem, right)], "baseline": p.fam("bottom")}


def d(p):
    """The uncial d: a bowl's left stroke with a long head, and on the right a stem whose top leans
    back over the bowl as a thick arm, cut off by the nib at its left end. Where the bowl's left
    stroke and its top meet, at the upper left, they make one concave curve (concave_top); at the bottom, the left
    stroke's foot runs on to meet the stem. Pugin's arm ends in a small ball and runs on into a
    flourish at the top; plain, it doesn't."""
    x1, x2 = p.x("left.x", 537, 12), p.x("stem_x", 612, 12)
    top = path(p, "bowl_top", [("from", x1 + 6, 3342, 35), ("to", x2 - 6, 3372, 50)])
    arm = path(p, "arm", [("end", 522, 3256, 345), ("over", 590, 3236, 5), ("into", x2, 3280, 90)], span=20)
    stem = minim(p, x2, head=0, top=arm[-1][3][1])
    left = minim(p, x1, head=p.length("left.head", 30, 12, 50), spur=False, run=foot_to_meet(p, x1, stem))
    return {"strokes": [left, top, arm, stem], "edges": [concave_top(p, left, top)], "baseline": p.fam("bottom")}


def h(p):
    """The l's ascender, and on the right a leg with its own head that runs down past the baseline
    and turns out at the descender line. Pugin's leg ends in a hairline loop; plain, it turns out as
    a minim's foot does."""
    x1, x2 = p.x("stem_x", 1046, 12), p.x("leg.x", 1120, 12)
    return {"strokes": ascender(p, x1) + [minim(p, x2, bottom=p.fam("descender"))], "baseline": p.fam("bottom")}


def k(p):
    """The l's ascender, a small closed loop at the x-height against its right side, and a leg with
    its own head coming down from under the loop to a foot on the baseline."""
    x1 = p.x("stem_x", 1259, 12)
    loop = path(p, "loop", [("top", 1300, 3345, 20), ("right", 1332, 3372, 90), ("low", 1298, 3402, 160)])
    leg = minim(p, p.x("leg.x", 1330, 12), top=p.x("leg.top", 3418, 15), head=p.length("leg.head", 32, 10, 55))
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


def p_(p):
    """A stem with its own head running down past the baseline to turn out at the descender line,
    and a bowl on its right: a stroke with a head, coming down and turning back in to the stem at
    the baseline. Pugin's bowl sweeps on across the stem into a curl, and the descender into a long
    swash; plain, neither does."""
    x1, x2 = p.x("stem_x", 1957, 12), p.x("right.x", 2028, 12)
    right = minim(p, x2, foot=False, end=p.x("right.end", 3470, 15))
    close = path(p, "bowl_foot", [("from", x2, 3468, 120), ("to", x1 + 10, 3508, 165)])
    return {"strokes": [minim(p, x1, bottom=p.fam("descender")), right, close], "baseline": p.fam("bottom")}


def q(p):
    """o's two strokes, meeting at the upper left in one straight edge, the right one running on past
    the baseline to turn out at the descender line; the left stroke's foot runs on to meet it. Pugin's
    descender ends in a swash splayed both ways; plain, it turns out as a minim's foot does."""
    x1, x2 = p.x("left.x", 2088, 12), p.x("right.x", 2152, 12)
    left, right = bowl_pair(p, x1, x2, p.x("left.top", 3352, 15), None, bottom2=p.fam("descender"), foot2=True, meet=True)
    return {"strokes": [left, right], "edges": [edge_above(p, left, right)], "baseline": p.fam("bottom")}


def g(p):
    """o's two strokes, meeting at the upper left in one concave curve (concave_top), the right one running on past
    the baseline and sweeping round to the left under the letter, and a small ear to the right at
    the top. The bowl is wider than o's, so the left stroke's foot runs on to meet the right one.
    Pugin's tail ends in a hairline curl; plain, it stops with the nib's cut."""
    x1, x2 = p.x("left.x", 900, 12), p.x("right.x", 973, 12)
    left, right = bowl_pair(p, x1, x2, p.x("left.top", 3352, 15), 3520, meet=True)
    tail = path(p, "tail", [("from", x2, 3518, 90), ("turn", x2 + 10, 3568, 120), ("end", 900, 3592, 185)], span=18)
    ear = path(p, "ear", [("from", x2 + 8, 3340, None), ("to", 1004, 3332, None)])
    return {"strokes": [left, right, tail, ear], "edges": [concave_top(p, left, right)], "baseline": p.fam("bottom")}


def y(p):
    """v's two strokes, the right one running on past the baseline and sweeping round to the left; the
    left one's foot runs on to meet it. Pugin's tail ends in a ball; plain, it stops with the nib's
    cut. Pugin drew it on the plate's second line, squeezed; the plain y stands at the full x-height."""
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


def s(p):
    """The textura s: an upper stroke with a flat top, coming down the left, and an arm running from
    its top to the right, the two meeting in a concave curve at the upper left (concave_top); a spine
    down to the right; a lower stroke down the right, cut off by the nib; and a foot stroke under the
    left. Pugin's s hangs a hairline and ball from the arm and another under the spine; plain, it
    doesn't."""
    x1, x2 = p.x("upper.x", 2367, 12), p.x("lower.x", 2428, 12)
    upper = minim(p, x1, head=0, top=p.x("upper.top", 3346, 15), foot=False, end=p.x("upper.end", 3438, 15))
    arm = path(p, "arm", [("from", x1 + 8, 3346, 15), ("to", 2438, 3356, 25)])
    spine = path(p, "spine", [("from", x1, 3436, 30), ("to", x2, 3468, 60)])
    lower = minim(p, x2, head=0, top=3462, foot=False, end=p.x("lower.end", 3490, 15))
    foot = path(p, "foot", [("from", x2, 3488, 135), ("bottom", 2398, 3526, 180), ("end", 2356, 3502, 225)], span=15)
    return {"strokes": [upper, arm, spine, lower, foot], "edges": [concave_top(p, upper, arm)], "baseline": p.fam("bottom")}


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
    stopped by the nib; with i's hairline stroke above. Modelled on i."""
    x0 = p.x("stem_x", 1190, 15)
    bt, ds = p.fam("bottom"), p.fam("descender")
    stem = minim(p, x0, foot=False, end=bt - 30)
    tail = [cubic(np.array([x0, bt - 30]), S, np.array([x0 - 52, ds]), 172, 0.6, 0.6)]
    return {"strokes": [stem, tail], "marks": [i_stroke(p, x0)], "baseline": bt}


LETTERS = {"i": i, "n": n, "m": m, "l": l, "o": o, "v": v, "c": c, "e": e, "r": r, "t": t, "b": b, "d": d, "h": h, "k": k,
           "longs": longs, "f": f, "p": p_, "q": q, "g": g, "y": y, "x": x, "a": a, "s": s, "z": z,
           "u": u, "w": w, "j": j}
DERIVED = {"u": "n", "w": "v", "j": "i"}      # a letter Pugin didn't draw: the letter whose fitted measurements it takes
