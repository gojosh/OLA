"""Lombardic letter constructions (decision 0008).

Each construction draws one letter from the kit's parts (construct.py): the stem, its flares, the
bars, the curl, the trefoil, and curves fitted where a letter has a stroke of its own (an arm, a
bowl). It asks for its measurements through `p`, each with a starting value read off Pugin's
letter and the bounds the fit may move it within; `p.fam` asks for one shared by the whole alphabet.
Stems come in two weights (decision 0009): `stem_plain` for letters that are mostly stem (I, L) and
`stem_armed` for letters that carry arms, a shoulder or a wide bar (F, H, K, T).

A construction returns its contours (lists of (segment, part, node name)), the baseline (the outer
edge of the bottom curls), and, for a symmetric letter, the left half and the axis. Coordinates are
the letter's reference image, in plate pixels, y down."""
from __future__ import annotations

import math

import numpy as np

import geom as G
from construct import (E, N, ORIENT, S, W, arc, cross_x, crossings, cubic, cut, ends, line, mirror_copy, mirror_half,
                       trefoil, two_lobe)

CAP_PX = 427.0     # the plate's median letter height (measurements.json), for glyphs that sit by it rather than on the baseline


# ── Shared parts ──────────────────────────────────────────────────────────────

def foot(p, K, ax, w, i):
    """From the bottom bar's centre on the axis: out along its edge to the curl, round the curl, and
    up the flare to the foot of the stem's left side."""
    C = np.array([ax, p.x("bottom.centre_y", i["centre_y"])])
    O = np.array([ax - p.x("bottom.half_width", i["half_width"]), p.x("bottom.outer_y", i["outer_y"], 15)])
    out = [(cubic(C, W, O, W, p.t("bottom.edge_t1"), p.t("bottom.edge_t2")), "bottom bar", "bottom bar: centre")]
    segs, names, neck, leave = K.curl(O, "bl", p.fam("curl"), p.ang("bottom.neck_deg", 0, 0, 40), place="curl, bottom-left")
    out += [(s, "curl", nm) for s, nm in zip(segs, names)]
    S1 = np.array([ax - w, p.x("stem.foot_y", i["foot_y"], 60)])
    out.append((cubic(neck, leave, S1, N, p.t("bottom.flare_t1"), p.t("bottom.flare_t2")), "flare", "curl, bottom-left: neck"))
    return out, S1, O


def head(p, K, ax, w, S2, i, side="left", pre=None):
    """From the head of the stem's straight: up the flare into the top curl. On the left the outline
    meets the curl neck first and ends at its outer node; on the right it starts at the outer node
    (the end of the top bar) and ends at the head of the straight. Both sides asking for the same
    `pre` makes the top symmetric about the stem."""
    pre = pre or ("top" if side == "left" else "top_right")
    sgn = -1 if side == "left" else 1
    O = np.array([ax + sgn * p.x(f"{pre}.half_width", i["half_width"]), p.x("top.outer_y", i["outer_y"], 15)])
    segs, names, neck, h = K.curl(O, "tl" if side == "left" else "tr", p.fam("curl"), p.ang(f"{pre}.neck_deg", 0, 0, 40),
                                  place=f"curl, top-{side}")
    if side == "left":
        flare = (cubic(S2, N, neck, h, p.t(f"{pre}.flare_t1"), p.t(f"{pre}.flare_t2")), "flare", "stem: head of straight")
        return [flare] + [(s, "curl", nm) for s, nm in zip(segs, names)], O
    flare = (cubic(neck, h, S2, S, p.t(f"{pre}.flare_t2"), p.t(f"{pre}.flare_t1")), "flare", "curl, top-right: neck")
    return [(s, "curl", nm) for s, nm in zip(segs, names)] + [flare], O


def top_edge(p, O, ax, i, side="left", pre=None, inflect=False):
    """The top bar's edge between the curl's outer node and the bar's centre on the axis, as a list
    of segments. With `inflect`, the edge has a node where it is steepest, for a bar that drops
    quickly from the ball: one curve would need a stub of a handle at the ball, which reads as a kink."""
    C = np.array([ax, p.x("top.centre_y", i["centre_y"])])
    pre = pre or ("top" if side == "left" else "top_right")
    left = side == "left"
    if not inflect:
        if left:
            return [(cubic(O, E, C, E, p.t(f"{pre}.edge_t2"), p.t(f"{pre}.edge_t1")), "top bar", "curl, top-left: outer")]
        return [(cubic(C, E, O, E, p.t(f"{pre}.edge_t1"), p.t(f"{pre}.edge_t2")), "top bar", "top bar: centre")]
    dx, y = p.x(f"{pre}.inflect_dx", i["half_width"] / 2, 40), p.x(f"{pre}.inflect_y", i["inflect_y"], 12)
    h = p.ang(f"{pre}.inflect_deg", 20, 2, 70)
    t1, t2, t3, t4 = (p.t(f"{pre}.edge_t{n}") for n in (1, 2, 3, 4))
    if left:
        Ti = np.array([ax - dx, y])
        return [(cubic(O, E, Ti, h, t2, t3), "top bar", "curl, top-left: outer"),
                (cubic(Ti, h, C, E, t4, t1), "top bar", "top bar: steepest, left")]
    Ti = np.array([ax + dx, y])
    return [(cubic(C, E, Ti, -h, t1, t4), "top bar", "top bar: centre"),
            (cubic(Ti, -h, O, E, t3, t2), "top bar", "top bar: steepest, right")]


def lobed_foot(p, Pl, i):
    """The two-lobe terminal at the foot of a stroke that sweeps right (H, K): two balls of one size
    and spacing for the alphabet, the second set off in the direction the letter needs. The stroke's outside
    comes down to the pocket's leftmost point Pl, runs along the pocket's floor into a sharp neck
    under the first lobe, goes over both lobes, and leaves the second at a corner onto the
    stroke's underside. Returns the segments and that last corner."""
    r = p.fam("two_lobe_r")
    c1 = np.array([p.x("terminal.x", i["x"], 20), p.x("terminal.y", i["y"], 20)])
    segs, names, neck, J = two_lobe(c1, r, r * p.fam("two_lobe_spread"), p.ang("terminal.lobe_angle", i["angle"], 0, 75),
                                    p.ang("terminal.neck_at", 95, 60, 150), p.ang("terminal.join_at", 145, 100, 175),
                                    place="two-lobe terminal")
    # the pocket's floor dips below both its leftmost point and the neck, then rises into the neck
    f = 0.85 * p.t("pocket.f", 0.5)
    Pb = np.array([Pl[0] + f * (neck[0] - Pl[0]), max(Pl[1], neck[1]) + p.length("pocket.dip", 8, 1, 30)])
    out = [(cubic(Pl, S, Pb, E, p.t("pocket.t1"), p.t("pocket.t2")), "stroke", "pocket: leftmost"),
           (cubic(Pb, E, neck, p.ang("terminal.neck_rise", 310, 260, 355), p.t("pocket.t3"), p.t("pocket.t4")), "stroke", "pocket: lowest")]
    return out + [(s, "two-lobe", nm) for s, nm in zip(segs, names)], J


def bottom_right(p, K, k, S4, O_bl, i):
    """From the foot of the stem's right side, along the bottom bar's top into the bottom-right
    curl, then back along the bar's underside, over its high point, to the bottom-left curl."""
    O_br = np.array([p.x("bottom.right_x", i["right_x"], 20), p.x("bottom.right_y", i["right_y"], 12)])
    segs, names, bneck, arrive = K.curl(O_br, "br", k, p.ang("bottom_right.neck_deg", 0, 0, 40), place="curl, bottom-right")
    out = [(cubic(S4, S, bneck, arrive, p.t("bottom.fillet_t1"), p.t("bottom.fillet_t2")), "bottom bar", "stem: right, foot of straight")]
    out += [(s, "curl", nm) for s, nm in zip(segs, names)]
    Bc = np.array([p.x("bottom.high_x", i["high_x"], 50), p.x("bottom.high_y", i["high_y"], 12)])
    out.append((cubic(O_br, W, Bc, W, p.t("bottom.edge_t1"), p.t("bottom.edge_t2")), "bottom bar", "curl, bottom-right: outer"))
    out.append((cubic(Bc, W, O_bl, W, p.t("bottom.edge_t3"), p.t("bottom.edge_t4")), "bottom bar", "bottom bar: high point"))
    return out


def left_side(p, K, ax, w, k, i):
    """The stem's left side, as in the I: from the bottom-left curl up to the top-left curl's outer
    node. Returns the segments, the bottom-left curl's outer node, and the top-left one's."""
    O_bl = np.array([ax - p.x("bottom.half_width", i["bottom_half_width"]), p.x("bottom.outer_y", i["bottom_y"], 15)])
    segs, names, neck, leave = K.curl(O_bl, "bl", k, p.ang("bottom.neck_deg", 0, 0, 40), place="curl, bottom-left")
    run = [(s, "curl", nm) for s, nm in zip(segs, names)]
    S1 = np.array([ax - w, p.x("stem.foot_y", i["foot_y"], 50)])
    run.append((cubic(neck, leave, S1, N, p.t("bottom.flare_t1"), p.t("bottom.flare_t2")), "flare", "curl, bottom-left: neck"))
    S2 = np.array([ax - w, p.x("stem.head_y", i["head_y"], 50)])
    run.append((line(S1, S2), "stem", "stem: foot of straight, left"))
    h, Otl = head(p, K, ax, w, S2, {"half_width": i["top_half_width"], "outer_y": i["top_y"]})
    return run + h, O_bl, Otl


def rounded_corner(p, pre, c, r, a_from, a_to, label, name):
    """A corner rounded by a small arc, run clockwise from a_from to a_to (degrees about its centre;
    each given as (start, low, high)). The edges on either side meet it along its tangents. Returns
    the arc's segments, its first and last points, and the headings there."""
    ctr = np.array([p.x(f"{pre}.x", c[0], 15), p.x(f"{pre}.y", c[1], 15)])
    a0, a1 = p.ang(f"{pre}.from", *a_from), p.ang(f"{pre}.to", *a_to)
    segs = arc(ctr, p.length(f"{pre}.r", r, 3, 15), a0, a1)
    run = [(s, label, name if j == 0 else f"{name}, extreme") for j, s in enumerate(segs)]
    return (run, *ends(segs))


def cap_top(p, K, k, pre, Ls, hL, Rs, hR, i, at=None, neck_l=(0, 0, 40), neck_r=(0, 0, 40)):
    """The head of a stroke at any slant: a short bar along the top line with a curl at each end,
    flaring down into the stroke's two edges, as the I's top does into its stem. Clockwise: from Ls
    on the stroke's left edge (leaving it on heading hL, up the edge), up the flare into the top-left
    curl, along the bar's top (dipping to a low point between the curls) to the top-right curl, and
    down its flare to Rs on the right edge (arriving on heading hR, down the edge). `at` gives the
    curls' outer nodes (left x, right x, y) where the construction has worked them out; the low point
    then sits a fraction of the way between them. `neck_l` and `neck_r` give the range of each flare's
    angle out of its curl's neck (start, low, high), for a curl that sits over its stroke's edge."""
    if at:
        y = at[2]
        O_l, O_r = np.array([at[0], y]), np.array([at[1], y])
        D = np.array([at[0] + p.length(f"{pre}.low_at", 0.5, 0.2, 0.8) * (at[1] - at[0]), y + p.length(f"{pre}.low_dy", 8, 0, 25)])
    else:
        y = p.x(f"{pre}.y", i["y"], 15)
        O_l = np.array([p.x(f"{pre}.left_x", i["left"], 20), y])
        O_r = np.array([p.x(f"{pre}.right_x", i["right"], 20), y])
        D = np.array([p.x(f"{pre}.low_x", (i["left"] + i["right"]) / 2, 40), y + p.length(f"{pre}.low_dy", 8, 0, 25)])
    segs_l, names_l, nk_l, arrive_l = K.curl(O_l, "tl", k, p.ang(f"{pre}.neck_l", *neck_l), place=f"curl, {pre}, left")
    segs_r, names_r, nk_r, leave_r = K.curl(O_r, "tr", k, p.ang(f"{pre}.neck_r", *neck_r), place=f"curl, {pre}, right")
    run = [(cubic(Ls, hL, nk_l, arrive_l, p.t(f"{pre}.flare_l1"), p.t(f"{pre}.flare_l2")), "flare", f"{pre}: left edge, top")]
    run += [(s, "curl", nm) for s, nm in zip(segs_l, names_l)]
    run += [(cubic(O_l, E, D, E, p.t(f"{pre}.edge_t1"), p.t(f"{pre}.edge_t2")), "bar", f"curl, {pre}, left: outer"),
            (cubic(D, E, O_r, E, p.t(f"{pre}.edge_t3"), p.t(f"{pre}.edge_t4")), "bar", f"{pre}: low point")]
    run += [(s, "curl", nm) for s, nm in zip(segs_r, names_r)]
    run.append((cubic(nk_r, leave_r, Rs, hR, p.t(f"{pre}.flare_r1"), p.t(f"{pre}.flare_r2")), "flare", f"curl, {pre}, right: neck"))
    return run


def cap_bottom(p, K, k, pre, Rs, hR, Ls, hL, i):
    """The foot of a stroke at any slant, the cap turned over: clockwise from Rs on the stroke's
    right edge (heading hR, down it), down the flare into the bottom-right curl, back along the bar's
    underside (rising to a high point between the curls) to the bottom-left curl, and up its flare
    to Ls on the left edge (arriving on heading hL, up it)."""
    y = p.x(f"{pre}.y", i["y"], 15)
    O_l = np.array([p.x(f"{pre}.left_x", i["left"], 20), y])
    O_r = np.array([p.x(f"{pre}.right_x", i["right"], 20), y])
    D = np.array([p.x(f"{pre}.high_x", (i["left"] + i["right"]) / 2, 40), y - p.length(f"{pre}.high_dy", 8, 0, 25)])
    segs_r, names_r, neck_r, arrive_r = K.curl(O_r, "br", k, p.ang(f"{pre}.neck_r", 0, 0, 40), place=f"curl, {pre}, right")
    segs_l, names_l, neck_l, leave_l = K.curl(O_l, "bl", k, p.ang(f"{pre}.neck_l", 0, 0, 40), place=f"curl, {pre}, left")
    run = [(cubic(Rs, hR, neck_r, arrive_r, p.t(f"{pre}.flare_r1"), p.t(f"{pre}.flare_r2")), "flare", f"{pre}: right edge, foot")]
    run += [(s, "curl", nm) for s, nm in zip(segs_r, names_r)]
    run += [(cubic(O_r, W, D, W, p.t(f"{pre}.edge_t1"), p.t(f"{pre}.edge_t2")), "bar", f"curl, {pre}, right: outer"),
            (cubic(D, W, O_l, W, p.t(f"{pre}.edge_t3"), p.t(f"{pre}.edge_t4")), "bar", f"{pre}: high point")]
    run += [(s, "curl", nm) for s, nm in zip(segs_l, names_l)]
    run.append((cubic(neck_l, leave_l, Ls, hL, p.t(f"{pre}.flare_l1"), p.t(f"{pre}.flare_l2")), "flare", f"curl, {pre}, left: neck"))
    return run


def edge_point(p, name, xy, heading, span=30, turn=20, upright=False):
    """A point on a stroke's edge where a cap's flare meets it, and the edge's heading there. Where
    the flare turns against the stroke's slant (the inside of V's arms), the edge runs upright for a
    moment before leaning with the stroke, so the point is an extreme: `upright` fixes the heading
    to straight up or down (whichever `heading` is nearer) and leaves the lean to the edge below."""
    xy = np.array([p.x(f"{name}.x", xy[0], span), p.x(f"{name}.y", xy[1], span)])
    if upright:
        return xy, N if 180 <= heading % 360 < 360 else S
    return xy, p.ang(f"{name}.heading", heading, heading - turn, heading + turn)


def symmetric(half, ax, end_name, baseline):
    return {"contours": [mirror_half(half, ax, end_name)], "half": half, "axis": ax, "baseline": baseline}


# ── Letters ───────────────────────────────────────────────────────────────────

def I(p, K):
    """A straight stem that flares into a top and a bottom bar, each ending in a curl at both sides."""
    ax, w = p.x("axis_x", 178.5, 20), p.fam("stem_plain")
    run, S1, O = foot(p, K, ax, w, {"centre_y": 432.3, "half_width": 111.1, "outer_y": 445.6, "foot_y": 305})
    S2 = np.array([ax - w, p.x("stem.head_y", 148, 60)])
    run.append((line(S1, S2), "stem", "stem: foot of straight"))
    h, Ot = head(p, K, ax, w, S2, {"half_width": 100.5, "outer_y": 23.2})
    run += h + top_edge(p, Ot, ax, {"centre_y": 38.7})
    return symmetric(run, ax, "top bar: centre", O[1])


def T_1(p, K):
    """The straight T. Below, the I's stem, bottom bar and curls. Above, a bar arched up to the axis,
    whose ends turn down into two tapering arms. Each arm has a ball at its outer top corner and ends
    in a curl rolling outward."""
    ax, w, k = p.x("axis_x", 235, 20), p.fam("stem_armed"), p.fam("curl")
    run, S1, O = foot(p, K, ax, w, {"centre_y": 444, "half_width": 154, "outer_y": 451, "foot_y": 330})
    # the stem's left side runs straight up to the point of the counter's arch
    S2 = np.array([ax - w, p.x("stem.head_y", 63, 25)])
    run.append((line(S1, S2), "stem", "stem: foot of straight"))
    # the arch: from that corner down the inside of the arm to the curl at its foot
    M1 = np.array([p.x("arm.inner_x", 95), p.x("arm.inner_y", 200, 50)])
    hm = p.ang("arm.inner_heading", 100, 75, 135)
    # The curl at the arm's foot sits above the bottom bar's curl with clear space between them,
    # which keeps the letter legible small. Pugin leaves 16.3 px (his left arm); the construction
    # keeps at least that.
    crown_y = O[1] + k * K.curl_nodes["crown"][1]
    drop = k * (ORIENT["foot-left"] @ K.curl_nodes["back"])[1]
    Oa = np.array([p.x("arm.curl_x", 79, 20), crown_y - p.length("arm.gap", 16.3, 16.3, 40) - drop])
    run.append((cubic(S2, p.ang("arch.spring_heading", 160, 95, 180), M1, hm, p.t("arch.t1"), p.t("arch.t2")), "arch", "counter: point of the arch"))
    run.append((cubic(M1, hm, Oa, S, p.t("arm.inner_t1"), p.t("arm.inner_t2")), "arm", "arm: inside"))
    segs, names, neck, leave = K.curl(Oa, "foot-left", k, p.ang("arm.neck_deg", -5, -30, 0), place="curl, foot of left arm")
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    # up the outside of the arm, past its narrowest point, to the round knob on its corner. The
    # narrowest point is never left of the neck, and the edge leaves the neck upright or leaning
    # toward it, so the edge can't swing out and back on the way.
    Aw = np.array([neck[0] + p.length("arm.waist_dx", 2, 0, 20), p.x("arm.waist_y", 300, 50)])
    run.append((cubic(neck, leave, Aw, N, p.t("arm.outer_t1"), p.t("arm.outer_t2")), "arm", "curl, foot of left arm: neck"))
    kc = np.array([p.x("knob.x", 43, 15), p.x("knob.y", 40, 15)])
    kr = p.x("knob.r", 18, 7)
    run.append((cubic(Aw, N, kc + [-kr, 0], N, p.t("arm.outer_t3"), p.t("arm.outer_t4")), "arm", "arm: outside, narrowest"))
    knob = arc(kc, kr, 180, 360 + p.ang("knob.neck_at", 50, 0, 89))
    run += [(s, "knob", nm) for s, nm in zip(knob, ["knob, top-left: back", "knob, top-left: crown", "knob, top-left: side"])]
    # the bar's top, from the knob up to the axis
    C = np.array([ax, p.x("top.centre_y", 28, 15)])
    run.append((cubic(knob[-1][3], p.ang("top.neck_out", -5, -60, 0), C, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "knob, top-left: neck"))
    return symmetric(run, ax, "top bar: centre", O[1])


def L(p, K):
    """The I's top and stem with its bottom-left curl. The base runs right into an arm that tapers
    as it rises and ends in two lobes close together: the arm runs up into the upper one, which
    rolls over to the second just below it. The base comes to a rounded point under the arm."""
    ax, w, k = p.x("axis_x", 137.5, 20), p.fam("stem_plain"), p.fam("curl")
    O_bl = np.array([ax - p.x("bottom.half_width", 66), p.x("bottom.outer_y", 450, 15)])
    segs, names, neck, leave = K.curl(O_bl, "bl", k, p.ang("bottom.neck_deg", 0, 0, 40), place="curl, bottom-left")
    run = [(s, "curl", nm) for s, nm in zip(segs, names)]
    S1 = np.array([ax - w, p.x("stem.foot_y", 375, 50)])
    run.append((cubic(neck, leave, S1, N, p.t("bottom.flare_t1"), p.t("bottom.flare_t2")), "flare", "curl, bottom-left: neck"))
    yh = p.x("stem.head_y", 140, 50)
    S2 = np.array([ax - w, yh])
    run.append((line(S1, S2), "stem", "stem: foot of straight, left"))
    # the top is the I's, symmetric about the stem: both sides share their measurements
    top = {"half_width": 66.5, "outer_y": 27, "centre_y": 38, "inflect_y": 30}
    h, Otl = head(p, K, ax, w, S2, top)
    run += h + top_edge(p, Otl, ax, top, inflect=True)
    S3 = np.array([ax + w, yh])
    hr, Otr = head(p, K, ax, w, S3, top, side="right", pre="top")
    run += top_edge(p, Otr, ax, top, "right", pre="top", inflect=True) + hr
    # down the stem's right side, round into the base and up the inside of the arm
    S4 = np.array([ax + w, p.x("stem.foot_y_right", 340, 90)])
    run.append((line(S3, S4), "stem", "stem: head of straight, right"))
    B1 = np.array([p.x("base.inside_x", 230), p.x("base.inside_y", 417, 20)])
    run.append((cubic(S4, S, B1, E, p.t("base.fillet_t1"), p.t("base.fillet_t2")), "base", "stem: foot of straight, right"))
    A1 = np.array([p.x("arm.inner_x", 338, 25), p.x("arm.inner_y", 230, 60)])
    ha = p.ang("arm.inner_heading", 275, 250, 300)
    run.append((cubic(B1, E, A1, ha, p.t("base.rise_t1"), p.t("base.rise_t2")), "arm", "base: inside"))
    # the arm's tip: a broad round crown, which the arm runs smoothly up into, and on its lower right
    # a ball the size of the two-lobe terminal's, meeting the crown in a shallow waist; the arm's
    # outside meets the ball at a notch
    rb = p.fam("two_lobe_r")
    c1 = np.array([p.x("arm_tip.x", 392, 15), p.x("arm_tip.y", 86, 15)])
    rcr = p.length("arm_tip.crown_r", 34, 22, 45)
    dist = abs(rcr - rb) + p.length("arm_tip.overhang", 6, 1, 25)
    segs, names, e0, e1 = two_lobe(c1, rcr, dist, p.ang("arm_tip.lobe_angle", 45, 10, 85),
                                   p.ang("arm_tip.enter", 190, 165, 215), p.ang("arm_tip.leave", 205, 170, 250), place="two-lobe tip", r2=rb)
    names[0] = "two-lobe tip: the arm runs in"
    _, h0, _, _ = ends(segs)
    run.append((cubic(A1, ha, e0, h0, p.t("arm.inner_t1"), p.t("arm.inner_t2")), "arm", "arm: inside"))
    run += [(s, "two-lobe", nm) for s, nm in zip(segs, names)]
    A2 = np.array([p.x("arm.outer_x", 365, 20), p.x("arm.outer_y", 210, 60)])
    run.append((cubic(e1, p.ang("arm_tip.out", 100, 75, 125), A2, S, p.t("arm.under_t1"), p.t("arm.under_t2")), "arm", "two-lobe tip: notch"))
    # the foot of the arm comes to a rounded point: a small arc, met tangentially by the arm's
    # outside and left the same way by the base's underside
    tc = np.array([p.x("tip.x", 393, 15), p.x("tip.y", 446, 15)])
    tr = p.x("tip.r", 6, 4)
    a0, a1 = p.ang("tip.from", -15, -60, 0), p.ang("tip.to", 105, 90, 160)
    tip = arc(tc, tr, a0, a1)
    t0, th0, t1, th1 = ends(tip)
    run.append((cubic(A2, S, t0, th0, p.t("arm.outer_t1"), p.t("arm.outer_t2")), "arm", "arm: outside"))
    run += [(s, "arm", nm) for s, nm in zip(tip, ["arm: rounded point"] + ["arm: rounded point, extreme"] * (len(tip) - 1))]
    Bc = np.array([p.x("base.under_x", 245), p.x("base.under_y", 432, 15)])
    run.append((cubic(t1, th1, Bc, W, p.t("base.under_t1"), p.t("base.under_t2")), "base", "base: foot of the arm"))
    run.append((cubic(Bc, W, O_bl, W, p.t("base.edge_t1"), p.t("base.edge_t2")), "base", "base: underside"))
    return {"contours": [run], "baseline": O_bl[1]}


def F(p, K):
    """The I's left side, top-left and bottom-left curls on a stem. The top bar ends square and drops
    as a stroke that closes the upper counter, crosses the middle bar and ends in a trefoil. The foot
    runs right into a bottom-right curl."""
    ax, w, k = p.x("axis_x", 119, 20), p.fam("stem_armed"), p.fam("curl")
    O_bl = np.array([ax - p.x("bottom.half_width", 67), p.x("bottom.outer_y", 440, 15)])
    segs, names, neck, leave = K.curl(O_bl, "bl", k, p.ang("bottom.neck_deg", 0, 0, 40), place="curl, bottom-left")
    run = [(s, "curl", nm) for s, nm in zip(segs, names)]
    S1 = np.array([ax - w, p.x("stem.foot_y", 370, 50)])
    run.append((cubic(neck, leave, S1, N, p.t("bottom.flare_t1"), p.t("bottom.flare_t2")), "flare", "curl, bottom-left: neck"))
    S2 = np.array([ax - w, p.x("stem.head_y", 110, 50)])
    run.append((line(S1, S2), "stem", "stem: foot of straight, left"))
    h, Otl = head(p, K, ax, w, S2, {"half_width": 64, "outer_y": 26})
    run += h
    # the top bar to its square end, and the stroke down to the trefoil
    # the top bar to its end, a corner rounded a little, and the stroke down to the trefoil
    Tlow = np.array([p.x("top.low_x", 220, 90), p.x("top.low_y", 32, 15)])
    corner, c0, h0, c1, h1 = rounded_corner(p, "top.corner", (390, 31), 7, (265, 245, 290), (380, 360, 400), "top bar", "top bar: rounded corner")
    run.append((cubic(Otl, E, Tlow, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "curl, top-left: outer"))
    run.append((cubic(Tlow, E, c0, h0, p.t("top.edge_t3"), p.t("top.edge_t4")), "top bar", "top bar: low point"))
    run += corner
    # the stroke's inside leaves the trefoil's inner lobe as far round as its top, so the lobe curls in
    # toward the counter and the stroke reads as sweeping outward
    axis = p.ang("trefoil.axis", 45, 0, 90)
    tsegs, tnames, J1, J2 = trefoil(np.array([p.x("trefoil.x", 388, 20), p.x("trefoil.y", 330, 20)]), axis,
                                    p.fam("trefoil_r"), p.fam("trefoil_d"), p.ang("trefoil.enter", -100, -175, -5),
                                    p.ang("trefoil.leave_at", 230, 150, 285) - (axis + 90))
    Sw = np.array([p.x("stroke.waist_x", 368, 15), p.x("stroke.waist_y", 270, 40)])
    run.append((cubic(c1, h1, Sw, S, p.t("stroke.t1"), p.t("stroke.t2")), "right stroke", "top bar: rounded corner, end"))
    run.append((cubic(Sw, S, J1, p.ang("stroke.foot_heading", 60, 0, 90), p.t("stroke.t3"), p.t("stroke.t4")), "right stroke", "right stroke: narrowest"))
    run += [(s, "trefoil", nm) for s, nm in zip(tsegs, tnames)]
    # up the stroke's inside (leaving the last lobe along its tangent) to a sharp point under the
    # middle bar, then along under the bar to the lower counter's top, and round into the stem
    LC = np.array([p.x("lower.point_x", 336, 15), p.x("lower.point_y", 240, 15)])
    Si = np.array([p.x("stroke.inside_x", 338, 15), p.x("stroke.inside_y", 290, 35)])
    run.append((cubic(J2, tsegs[-1][3] - tsegs[-1][2], Si, N, p.t("lower.t1"), p.t("lower.t2")), "right stroke", "trefoil: join, left"))
    run.append((cubic(Si, N, LC, p.ang("lower.point_in", 262, 240, 270), p.t("lower.t7"), p.t("lower.t8")), "right stroke",
                "right stroke: inside, narrowest"))
    LCt = np.array([p.x("lower.top_x", 220, 60), p.x("lower.top_y", 230, 15)])
    run.append((cubic(LC, p.ang("lower.point_out", 185, 178, 220), LCt, W, p.t("lower.t5"), p.t("lower.t6")), "middle bar", "lower counter: point"))
    S3 = np.array([ax + w, p.x("stem.counter_top_y", 268, 25)])
    run.append((cubic(LCt, W, S3, S, p.t("lower.t3"), p.t("lower.t4")), "middle bar", "lower counter: top"))
    S4 = np.array([ax + w, p.x("stem.counter_foot_y", 340, 40)])
    run.append((line(S3, S4), "stem", "stem: right, below the middle bar"))
    O_br = np.array([p.x("foot.curl_x", 338, 20), p.x("foot.curl_y", 445, 15)])
    segs, names, bneck, arrive = K.curl(O_br, "br", k, p.ang("foot.neck_deg", 0, 0, 40), place="curl, bottom-right")
    run.append((cubic(S4, S, bneck, arrive, p.t("foot.fillet_t1"), p.t("foot.fillet_t2")), "foot", "stem: right, foot of straight"))
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    Bc = np.array([p.x("foot.under_x", 200, 60), p.x("foot.under_y", 437, 15)])
    run.append((cubic(O_br, W, Bc, W, p.t("foot.under_t1"), p.t("foot.under_t2")), "foot", "curl, bottom-right: outer"))
    run.append((cubic(Bc, W, O_bl, W, p.t("foot.edge_t1"), p.t("foot.edge_t2")), "foot", "foot: underside"))
    # the upper counter, anticlockwise: down the stem, along the middle bar, up the stroke, back along the top
    U1 = np.array([ax + w, p.x("counter.left_top_y", 95, 25)])
    U2 = np.array([ax + w, p.x("counter.left_foot_y", 180, 20)])
    Ub = np.array([p.x("counter.bottom_x", 230, 40), p.x("counter.bottom_y", 201, 12)])
    Ubr = np.array([p.x("counter.corner_x", 326, 15), p.x("counter.corner_y", 182, 15)])
    Ut = np.array([p.x("counter.top_x", 230, 40), p.x("counter.top_y", 57, 12)])
    hb = p.ang("counter.corner_in", 340, 300, 380)
    counter = [(line(U1, U2), "upper counter", "upper counter: stem, top"),
               (cubic(U2, S, Ub, E, p.t("counter.t1"), p.t("counter.t2")), "upper counter", "upper counter: stem, foot"),
               (cubic(Ub, E, Ubr, hb, p.t("counter.t3"), p.t("counter.t4")), "upper counter", "upper counter: bottom"),
               (cubic(Ubr, p.ang("counter.corner_out", 250, 215, 285), Ut, W, p.t("counter.t5"), p.t("counter.t6")), "upper counter",
                "upper counter: corner"),
               (cubic(Ut, W, U1, S, p.t("counter.t7"), p.t("counter.t8")), "upper counter", "upper counter: top")]
    return {"contours": [run, counter], "baseline": O_bl[1]}


def bowl_and_stroke(p, K, i):
    """The outline of the uncial E and C: a round bowl closed on the right by a straight stroke that
    ends in a top-right and a bottom-right curl, with a notch where bowl and stroke meet, top and
    bottom. Returns the run and the bottom-right curl's outer node."""
    k = p.fam("curl")
    E0 = np.array([p.x("bowl.left_x", i["left"][0], 15), p.x("bowl.left_y", i["left"][1], 40)])
    Et = np.array([p.x("bowl.top_x", i["top"][0], 40), p.x("bowl.top_y", i["top"][1], 12)])
    Eb = np.array([p.x("bowl.bottom_x", i["bottom"][0], 40), p.x("bowl.bottom_y", i["bottom"][1], 12)])
    Nt = np.array([p.x("notch.x", i["notch"][0], 15), p.x("notch.y", i["notch"][1], 15)])
    xr = p.x("stroke.right_x", i["stroke_right"], 15)
    run = [(cubic(E0, N, Et, E, p.t("bowl.t1"), p.t("bowl.t2")), "bowl", "bowl: left"),
           (cubic(Et, E, Nt, p.ang("notch.in", 25, 0, 60), p.t("bowl.t3"), p.t("bowl.t4")), "bowl", "bowl: top")]
    O_tr = np.array([p.x("top.curl_x", i["top_curl"][0], 15), p.x("top.curl_y", i["top_curl"][1], 12)])
    run.append((cubic(Nt, p.ang("notch.out", 330, 290, 360), O_tr, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "notch, top"))
    segs, names, neck, leave = K.curl(O_tr, "tr", k, p.ang("top.neck_deg", 15, -20, 60), place="curl, top-right")
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    R1 = np.array([xr, p.x("stroke.top_y", i["stroke_top"], 90)])
    R2 = np.array([xr, p.x("stroke.foot_y", i["stroke_foot"], 60)])
    run.append((cubic(neck, leave, R1, S, p.t("top.flare_t1"), p.t("top.flare_t2")), "flare", "curl, top-right: neck"))
    run.append((line(R1, R2), "right stroke", "right stroke: top of straight"))
    O_br = np.array([p.x("bottom.curl_x", i["bottom_curl"][0], 15), p.x("bottom.curl_y", i["bottom_curl"][1], 12)])
    segs, names, bneck, arrive = K.curl(O_br, "br", k, p.ang("bottom.neck_deg", 0, 0, 40), place="curl, bottom-right")
    run.append((cubic(R2, S, bneck, arrive, p.t("bottom.flare_t1"), p.t("bottom.flare_t2")), "flare", "right stroke: foot of straight"))
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    Nb = np.array([p.x("notch_b.x", i["notch_b"][0], 15), p.x("notch_b.y", i["notch_b"][1], 15)])
    run.append((cubic(O_br, W, Nb, p.ang("notch_b.in", 200, 180, 250), p.t("bottom.edge_t1"), p.t("bottom.edge_t2")), "bottom bar", "curl, bottom-right: outer"))
    run.append((cubic(Nb, p.ang("notch_b.out", 150, 110, 180), Eb, W, p.t("bowl.t7"), p.t("bowl.t8")), "bowl", "notch, bottom"))
    run.append((cubic(Eb, W, E0, N, p.t("bowl.t5"), p.t("bowl.t6")), "bowl", "bowl: bottom"))
    return run, O_br


def E_(p, K):
    """The uncial E: a round bowl, closed on the right by a stroke that ends in a top-right and a
    bottom-right curl, with a bar across the middle. Two counters."""
    run, O_br = bowl_and_stroke(p, K, {"left": (25, 237), "top": (231, 26), "bottom": (231, 455), "notch": (322, 59),
                                       "stroke_right": 355, "top_curl": (376, 27), "stroke_top": 140, "stroke_foot": 380,
                                       "bottom_curl": (376, 452), "notch_b": (330, 422)})
    xl = p.x("stroke.left_x", 310, 15)
    # upper counter, anticlockwise
    Ut = np.array([p.x("upper.top_x", 237, 40), p.x("upper.top_y", 50, 12)])
    Ul = np.array([p.x("upper.left_x", 128, 15), p.x("upper.left_y", 165, 30)])
    yb = p.x("bar.top_y", 201, 15)
    Ub = np.array([p.x("upper.bottom_x", 165, 30), yb])
    Ubr = np.array([xl, yb + p.x("upper.corner_dy", 0, 12)])
    Urt = np.array([xl, p.x("upper.right_top_y", 110, 80)])
    upper = [(cubic(Ut, W, Ul, S, p.t("upper.t1"), p.t("upper.t2")), "upper counter", "upper counter: top"),
             (cubic(Ul, S, Ub, E, p.t("upper.t3"), p.t("upper.t4")), "upper counter", "upper counter: left"),
             (cubic(Ub, E, Ubr, p.ang("upper.corner_in", 5, 0, 30), p.t("upper.t5"), p.t("upper.t6")), "middle bar", "upper counter: bottom"),
             (line(Ubr, Urt), "upper counter", "upper counter: corner"),
             (cubic(Urt, N, Ut, W, p.t("upper.t7"), p.t("upper.t8")), "upper counter", "upper counter: right, top of straight")]
    # lower counter, anticlockwise
    yu = p.x("bar.under_y", 264, 15)
    Ltr = np.array([xl, yu])
    Ll = np.array([p.x("lower.left_x", 125, 15), p.x("lower.left_y", 300, 30)])
    Lb = np.array([p.x("lower.bottom_x", 237, 40), p.x("lower.bottom_y", 432, 12)])
    Lr = np.array([xl, p.x("lower.right_foot_y", 380, 80)])
    Lt = np.array([p.x("lower.top_x", 200, 60), p.x("lower.top_y", 262, 15)])
    lower = [(cubic(Ltr, p.ang("lower.corner_out", 185, 180, 220), Lt, W, p.t("lower.t7"), p.t("lower.t8")), "middle bar", "lower counter: corner"),
             (cubic(Lt, W, Ll, S, p.t("lower.t1"), p.t("lower.t2")), "lower counter", "lower counter: top"),
             (cubic(Ll, S, Lb, E, p.t("lower.t3"), p.t("lower.t4")), "lower counter", "lower counter: left"),
             (cubic(Lb, E, Lr, N, p.t("lower.t5"), p.t("lower.t6")), "lower counter", "lower counter: bottom"),
             (line(Lr, Ltr), "lower counter", "lower counter: right, foot of straight")]
    return {"contours": [run, upper, lower], "baseline": O_br[1]}


def oval_counter(p, i, pre="counter"):
    """An oval counter with a node at each extreme, anticlockwise: top, left, bottom, right."""
    Ct = np.array([p.x(f"{pre}.top_x", i["top"][0], 40), p.x(f"{pre}.top_y", i["top"][1], 15)])
    Cl = np.array([p.x(f"{pre}.left_x", i["left"][0], 15), p.x(f"{pre}.left_y", i["left"][1], 50)])
    Cb = np.array([p.x(f"{pre}.bottom_x", i["bottom"][0], 40), p.x(f"{pre}.bottom_y", i["bottom"][1], 15)])
    Cr = np.array([p.x(f"{pre}.right_x", i["right"][0], 15), p.x(f"{pre}.right_y", i["right"][1], 50)])
    return [(cubic(Ct, W, Cl, S, p.t(f"{pre}.t1"), p.t(f"{pre}.t2")), "counter", "counter: top"),
            (cubic(Cl, S, Cb, E, p.t(f"{pre}.t3"), p.t(f"{pre}.t4")), "counter", "counter: left"),
            (cubic(Cb, E, Cr, N, p.t(f"{pre}.t5"), p.t(f"{pre}.t6")), "counter", "counter: bottom"),
            (cubic(Cr, N, Ct, W, p.t(f"{pre}.t7"), p.t(f"{pre}.t8")), "counter", "counter: right")]


def C(p, K):
    """The uncial C: the E's bowl and right stroke without the middle bar. The counter is an oval:
    the stroke is straight outside and swells inside."""
    run, O_br = bowl_and_stroke(p, K, {"left": (25, 240), "top": (230, 25), "bottom": (230, 456), "notch": (322, 52),
                                       "stroke_right": 350, "top_curl": (381, 28), "stroke_top": 150, "stroke_foot": 340,
                                       "bottom_curl": (381, 454), "notch_b": (322, 430)})
    counter = oval_counter(p, {"top": (232, 50), "left": (118, 240), "bottom": (232, 432), "right": (314, 250)})
    return {"contours": [run, counter], "baseline": O_br[1]}


def O(p, K):
    """The O: an oval ring, heavy at the sides and light at top and bottom. A round ball hangs into
    the counter from the top, on the axis. From the floor a curl rises: the floor runs smoothly up
    into its ball on the left, and the ball rolls on round its right side to a sharp notch tucked
    under it."""
    ax, r = p.x("axis_x", 225.5, 15), p.fam("ball_r")
    # the outline, symmetric: from the bottom on the axis, clockwise up the left to the top
    Ob = np.array([ax, p.x("outer.bottom_y", 451, 12)])
    Ol = np.array([p.x("outer.left_x", 25, 15), p.x("outer.left_y", 240, 40)])
    Ot = np.array([ax, p.x("outer.top_y", 24, 12)])
    outer = [(cubic(Ob, W, Ol, N, p.t("outer.t1"), p.t("outer.t2")), "ring", "outline: bottom"),
             (cubic(Ol, N, Ot, E, p.t("outer.t3"), p.t("outer.t4")), "ring", "outline: left")]
    # the counter, anticlockwise: round the hanging ball (symmetric about the axis), down the left
    # wall, along the floor and up into the curl, then up the right wall
    ct = np.array([ax, p.x("ball_top.y", 54, 15)])
    a_l = p.ang("ball_top.meets_at", 215, 185, 265)
    top = arc(ct, r, 180 - a_l, a_l)
    Cl = np.array([p.x("counter.left_x", 120, 15), p.x("counter.left_y", 240, 40)])
    # the floor's curl: the floor runs down from the left wall and up into a round ball, which rolls
    # over and on round its far side to a sharp notch tucked under it
    cb = np.array([p.x("curl.x", 226, 15), p.x("curl.y", 396, 15)])
    rc = p.fam("curl") * K.curl_ball_r          # a curl, so the alphabet's curl's ball
    Fb = np.array([cb[0] - rc - p.length("floor.low_dx", 15, 2, 60), cb[1] + p.length("floor.low_dy", 25, 2, 50)])
    ball = arc(cb, rc, 180, 360 + p.ang("curl.notch_at", 70, 20, 110))
    tip = ball[-1][3]
    Pb = np.array([tip[0] + p.length("pocket.dx", 15, 2, 45), tip[1] + p.length("pocket.dy", 3, 0, 20)])
    Cr = np.array([p.x("counter.right_x", 331, 15), p.x("counter.right_y", 240, 40)])
    counter = [(s, "ball", "ball, top: meets the ring" if j == 0 else "ball, top") for j, s in enumerate(top)]
    counter += [(cubic(top[-1][3], p.ang("counter.top_out", 150, 95, 180), Cl, S, p.t("counter.t1"), p.t("counter.t2")), "counter", "ball, top: meets the ring, left"),
                (cubic(Cl, S, Fb, E, p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: left"),
                (cubic(Fb, E, ball[0][0], N, p.t("counter.t5"), p.t("counter.t6")), "counter", "counter: floor, lowest")]
    counter += [(s, "curl", "curl, floor: back" if j == 0 else "curl, floor") for j, s in enumerate(ball)]
    counter += [(cubic(tip, p.ang("pocket.out", 20, 0, 70), Pb, E, p.t("pocket.t1"), p.t("pocket.t2")), "counter", "curl, floor: notch"),
                (cubic(Pb, E, Cr, N, p.t("counter.t7"), p.t("counter.t8")), "counter", "pocket: lowest"),
                (cubic(Cr, N, top[0][0], p.ang("counter.top_in", 210, 180, 265), p.t("counter.t9"), p.t("counter.t10")), "counter", "counter: right")]
    half = (outer, "outline: top")
    return {"contours": [mirror_half(outer, ax, half[1]), counter], "halves": [outer, None], "axis": ax, "baseline": Ob[1]}


def D(p, K):
    """A stem with the I's top-left and bottom-left curls, and a round bowl on the right. The top
    edge dips a little over the stem before rising into the bowl; the bottom edge rises between
    the curl and the bowl."""
    ax, w, k = p.x("axis_x", 137, 20), p.fam("stem_armed"), p.fam("curl")
    run, O_bl, Otl = left_side(p, K, ax, w, k, {"bottom_half_width": 68, "bottom_y": 455, "foot_y": 390, "head_y": 100,
                                                  "top_half_width": 64, "top_y": 27})
    Tlow = np.array([p.x("top.low_x", 180, 40), p.x("top.low_y", 37, 12)])
    Bt = np.array([p.x("bowl.top_x", 270, 40), p.x("bowl.top_y", 25, 12)])
    Br = np.array([p.x("bowl.right_x", 464, 15), p.x("bowl.right_y", 245, 40)])
    Bb = np.array([p.x("bowl.bottom_x", 250, 40), p.x("bowl.bottom_y", 459, 12)])
    Bh = np.array([p.x("bottom.high_x", 140, 40), p.x("bottom.high_y", 448, 12)])
    run += [(cubic(Otl, E, Tlow, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, Bt, E, p.t("top.edge_t3"), p.t("top.edge_t4")), "top bar", "top bar: low point"),
            (cubic(Bt, E, Br, S, p.t("bowl.t1"), p.t("bowl.t2")), "bowl", "bowl: top"),
            (cubic(Br, S, Bb, W, p.t("bowl.t3"), p.t("bowl.t4")), "bowl", "bowl: right"),
            (cubic(Bb, W, Bh, W, p.t("bowl.t5"), p.t("bowl.t6")), "bottom bar", "bowl: bottom"),
            (cubic(Bh, W, O_bl, W, p.t("bottom.edge_t1"), p.t("bottom.edge_t2")), "bottom bar", "bottom bar: high point")]
    U1 = np.array([ax + w, p.x("counter.stem_top_y", 100, 30)])
    U2 = np.array([ax + w, p.x("counter.stem_foot_y", 395, 30)])
    Cb = np.array([p.x("counter.bottom_x", 260, 40), p.x("counter.bottom_y", 440, 12)])
    Cr = np.array([p.x("counter.right_x", 375, 15), p.x("counter.right_y", 245, 40)])
    Ct = np.array([p.x("counter.top_x", 255, 40), p.x("counter.top_y", 48, 12)])
    counter = [(line(U1, U2), "counter", "counter: stem, top of straight"),
               (cubic(U2, S, Cb, E, p.t("counter.t1"), p.t("counter.t2")), "counter", "counter: stem, foot of straight"),
               (cubic(Cb, E, Cr, N, p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: bottom"),
               (cubic(Cr, N, Ct, W, p.t("counter.t5"), p.t("counter.t6")), "counter", "counter: right"),
               (cubic(Ct, W, U1, S, p.t("counter.t7"), p.t("counter.t8")), "counter", "counter: top")]
    return {"contours": [run, counter], "baseline": O_bl[1]}


def H(p, K):
    """The uncial H: a stem with the I's top-left and bottom curls; a long top bar, dipping a little
    over the stem, out to a top-right curl; and a shoulder that springs from the stem under the bar,
    arches over and comes down to a foot sweeping right into the two-lobe terminal. Between the bar
    and the shoulder, a sliver of space comes to a point on the stem."""
    ax, w, k = p.x("axis_x", 136.5, 20), p.fam("stem_armed"), p.fam("curl")
    run, O_bl, Otl = left_side(p, K, ax, w, k, {"bottom_half_width": 70.5, "bottom_y": 446, "foot_y": 375, "head_y": 120,
                                                  "top_half_width": 69.5, "top_y": 25})
    Tlow = np.array([p.x("top.low_x", 145, 50), p.x("top.low_y", 32, 12)])
    Otr = np.array([p.x("top.right_x", 348, 20), Otl[1]])
    run.append((cubic(Otl, E, Tlow, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "curl, top-left: outer"))
    run.append((cubic(Tlow, E, Otr, E, p.t("top.edge_t3"), p.t("top.edge_t4")), "top bar", "top bar: low point"))
    segs, names, neck, leave = K.curl(Otr, "tr", k, p.ang("top_right.neck_deg", 5, 0, 40), place="curl, top-right")
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    # under the bar and down to the point of the sliver, on the stem's right side
    ST = np.array([ax + w, p.x("sliver.y", 166, 20)])
    run.append((cubic(neck, leave, ST, S, p.t("sliver.t1"), p.t("sliver.t2")), "flare", "curl, top-right: neck"))
    # the shoulder: up and over, and down its outside to the pocket above the terminal
    SHt = np.array([p.x("shoulder.top_x", 282, 30), p.x("shoulder.top_y", 72, 15)])
    run.append((cubic(ST, p.ang("shoulder.spring", 300, 270, 340), SHt, E, p.t("shoulder.t1"), p.t("shoulder.t2")), "shoulder", "sliver: point"))
    SHr = np.array([p.x("shoulder.right_x", 418, 15), p.x("shoulder.right_y", 205, 40)])
    run.append((cubic(SHt, E, SHr, S, p.t("shoulder.t3"), p.t("shoulder.t4")), "shoulder", "shoulder: top"))
    Pl = np.array([p.x("pocket.x", 344, 15), p.x("pocket.y", 385, 25)])
    run.append((cubic(SHr, S, Pl, S, p.t("shoulder.t5"), p.t("shoulder.t6")), "shoulder", "shoulder: outside, rightmost"))
    foot_run, J = lobed_foot(p, Pl, {"x": 383, "y": 388, "angle": 26})
    run += foot_run
    # along the foot's underside, up the shoulder's inside, over the arch and down to the stem
    FB = np.array([p.x("foot.bottom_x", 362, 25), J[1] + p.length("foot.drop", 8, 0, 30)])    # never above the terminal's end
    run.append((cubic(J, p.ang("foot.join_out", 160, 120, 180), FB, W, p.t("foot.t1"), p.t("foot.t2")), "foot", "two-lobe terminal: join"))
    IL = np.array([p.x("inside.left_x", 308, 15), p.x("inside.left_y", 370, 30)])
    run.append((cubic(FB, W, IL, N, p.t("foot.t3"), p.t("foot.t4")), "shoulder", "foot: bottom"))
    IR = np.array([p.x("inside.right_x", 329, 15), p.x("inside.right_y", 245, 40)])
    run.append((cubic(IL, N, IR, N, p.t("inside.t1"), p.t("inside.t2")), "shoulder", "shoulder: inside, leftmost"))
    AT = np.array([p.x("arch.top_x", 258, 30), p.x("arch.top_y", 126, 12)])
    run.append((cubic(IR, N, AT, W, p.t("arch.t1"), p.t("arch.t2")), "arch", "shoulder: inside, rightmost"))
    AS = np.array([ax + w, p.x("arch.foot_y", 200, 30)])
    run.append((cubic(AT, W, AS, S, p.t("arch.t3"), p.t("arch.t4")), "arch", "arch: top"))
    S4 = np.array([ax + w, p.x("stem.foot_y_right", 380, 40)])
    run.append((line(AS, S4), "stem", "stem: right, below the arch"))
    run += bottom_right(p, K, k, S4, O_bl, {"right_x": 250, "right_y": 445, "high_x": 140, "high_y": 437})
    return {"contours": [run], "baseline": O_bl[1]}


def K_(p, K):
    """A stem with the I's top-left and bottom curls. The top bar runs out to a square corner and
    drops as an arm to a crotch; from there a leg sweeps out, down and right into the two-lobe
    terminal. The arm closes a pointed upper counter against the stem; below, the lower counter
    comes to a point under the arm and opens at the bottom right."""
    ax, w, k = p.x("axis_x", 141, 20), p.fam("stem_armed"), p.fam("curl")
    run, O_bl, Otl = left_side(p, K, ax, w, k, {"bottom_half_width": 73, "bottom_y": 447, "foot_y": 375, "head_y": 100,
                                                  "top_half_width": 55, "top_y": 27})
    # the top edge dips over the stem before rising to the corner
    Tlow = np.array([p.x("top.low_x", 150, 70), p.x("top.low_y", 34, 12)])
    # the corner is rounded a little and ends at the arm's rightmost point, turned straight down
    kc = np.array([p.x("top.corner.x", 395, 15), p.x("top.corner.y", 35, 15)])
    kcorner = arc(kc, p.length("top.corner.r", 7, 3, 15), p.ang("top.corner.from", 265, 245, 290), 360)
    c0, h0, c1, _ = ends(kcorner)
    run.append((cubic(Otl, E, Tlow, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "curl, top-left: outer"))
    run.append((cubic(Tlow, E, c0, h0, p.t("top.edge_t3"), p.t("top.edge_t4")), "top bar", "top bar: low point"))
    run += [(s, "top bar", "top bar: rounded corner" if j == 0 else "top bar: rounded corner, extreme") for j, s in enumerate(kcorner)]
    # down the arm's outside to the crotch, then out along the leg
    Cr = np.array([p.x("crotch.x", 262, 15), p.x("crotch.y", 226, 15)])
    run.append((cubic(c1, S, Cr, p.ang("arm.crotch_in", 135, 100, 170), p.t("arm.t3"), p.t("arm.t4")), "arm", "arm: outside, rightmost"))
    Lt = np.array([p.x("leg.top_x", 305, 30), p.x("leg.top_y", 218, 12)])
    run.append((cubic(Cr, p.ang("leg.spring", 340, 300, 360), Lt, E, p.t("leg.t1"), p.t("leg.t2")), "leg", "crotch"))
    Lr = np.array([p.x("leg.right_x", 391, 15), p.x("leg.right_y", 330, 40)])
    run.append((cubic(Lt, E, Lr, S, p.t("leg.t3"), p.t("leg.t4")), "leg", "leg: top"))
    Pl = np.array([p.x("pocket.x", 384, 15), p.x("pocket.y", 400, 20)])
    run.append((cubic(Lr, S, Pl, S, p.t("leg.t5"), p.t("leg.t6")), "leg", "leg: outside, rightmost"))
    foot_run, J = lobed_foot(p, Pl, {"x": 418, "y": 410, "angle": 55})
    run += foot_run
    # along the foot's underside and up the leg's inside to the lower counter's point
    FB = np.array([p.x("foot.bottom_x", 395, 25), J[1] + p.length("foot.drop", 8, 0, 30)])    # never above the terminal's end
    run.append((cubic(J, p.ang("foot.join_out", 160, 120, 180), FB, W, p.t("foot.t1"), p.t("foot.t2")), "foot", "two-lobe terminal: join"))
    Li = np.array([p.x("inside.x", 335, 25), p.x("inside.y", 380, 40)])
    hli = p.ang("inside.heading", 250, 225, 268)
    run.append((cubic(FB, W, Li, hli, p.t("foot.t3"), p.t("foot.t4")), "leg", "foot: bottom"))
    V = np.array([p.x("lower.point_x", 236, 15), p.x("lower.point_y", 254, 15)])
    run.append((cubic(Li, hli, V, p.ang("lower.point_in", 225, 190, 260), p.t("inside.t1"), p.t("inside.t2")), "leg", "leg: inside"))
    SR1 = np.array([ax + w, p.x("lower.stem_top_y", 290, 25)])
    run.append((cubic(V, p.ang("lower.point_out", 125, 95, 170), SR1, S, p.t("lower.t1"), p.t("lower.t2")), "arm", "lower counter: point"))
    S4 = np.array([ax + w, p.x("stem.foot_y_right", 380, 40)])
    run.append((line(SR1, S4), "stem", "stem: right, below the arm"))
    run += bottom_right(p, K, k, S4, O_bl, {"right_x": 263, "right_y": 446, "high_x": 150, "high_y": 440})
    # the upper counter, anticlockwise: down the stem to its point, up the arm's inside, back along the top
    U1 = np.array([ax + w, p.x("upper.left_top_y", 80, 25)])
    Ub = np.array([ax + w, p.x("upper.point_y", 243, 15)])
    Urx = np.array([p.x("upper.right_x", 304, 15), p.x("upper.right_y", 85, 25)])
    Ut = np.array([p.x("upper.top_x", 250, 40), p.x("upper.top_y", 55, 12)])
    counter = [(line(U1, Ub), "upper counter", "upper counter: stem"),
               (cubic(Ub, p.ang("upper.point_out", 310, 280, 340), Urx, N, p.t("upper.t1"), p.t("upper.t2")), "upper counter", "upper counter: point"),
               (cubic(Urx, N, Ut, W, p.t("upper.t3"), p.t("upper.t4")), "upper counter", "upper counter: right"),
               (cubic(Ut, W, U1, S, p.t("upper.t5"), p.t("upper.t6")), "upper counter", "upper counter: top")]
    return {"contours": [run, counter], "baseline": O_bl[1]}


def Q(p, K):
    """The O's bowl, with a curl hanging into the counter from the top (its ball runs smoothly up into
    the top wall on the left and rolls on round its right side to a sharp notch over it) and a ball
    on its floor.
    At the bottom right the bowl's base runs on past the bowl to end in a round ball, and a flag
    rises from it, parted from the bowl by a pointed notch: its inside runs nearly flat, then rises
    and flows without a break into a round ball at its head; its outside meets that ball, and the
    ball at the base, at notches."""
    k, r = p.fam("curl"), p.fam("ball_r")
    bx = p.x("axis_x", 203, 15)
    Ol = np.array([p.x("outer.left_x", 26, 15), p.x("outer.left_y", 240, 40)])
    Ot = np.array([bx, p.x("outer.top_y", 24, 12)])
    Or = np.array([p.x("outer.right_x", 381, 15), p.x("outer.right_y", 240, 40)])
    Nq = np.array([p.x("notch.x", 252, 15), p.x("notch.y", 414, 15)])
    run = [(cubic(Ol, N, Ot, E, p.t("outer.t1"), p.t("outer.t2")), "bowl", "bowl: left"),
           (cubic(Ot, E, Or, S, p.t("outer.t3"), p.t("outer.t4")), "bowl", "bowl: top"),
           (cubic(Or, S, Nq, p.ang("notch.in", 120, 95, 170), p.t("outer.t5"), p.t("outer.t6")), "bowl", "bowl: right")]
    # up the flag's inside to its curl, and down its outside to the rounded end of the base
    # from the notch the flag's inside runs nearly flat to its lowest point, then rises to the curl
    # the flag's head is a round ball (the alphabet's curl's ball): the flag's inside runs smoothly
    # up into it, still leaning, and its outside meets it at a notch
    rc = k * K.curl_ball_r
    cb = np.array([p.x("flag.ball_x", 395, 15), p.x("flag.ball_y", 318, 20)])
    ball = arc(cb, rc, p.ang("flag.enters_at", 205, 170, 245), 360 + p.ang("flag.notch_at", 85, 40, 130))
    f0, fh0, f1, fh1 = ends(ball)
    Wb = np.array([Nq[0] + p.length("flag.low_dx", 48, 5, 110), Nq[1] + p.length("flag.low_dy", 4, 0, 20)])
    run.append((cubic(Nq, p.ang("notch.out", 10, 0, 45), Wb, E, p.t("flag.t1"), p.t("flag.t2")), "flag", "notch"))
    run.append((cubic(Wb, E, f0, fh0, p.t("flag.t7"), p.t("flag.t8")), "flag", "flag: inside, lowest"))
    run += [(s, "ball", "ball, head of the flag: the flag runs in" if j == 0 else "ball, head of the flag") for j, s in enumerate(ball)]
    Fr = np.array([p.x("flag.right_x", 398, 15), p.x("flag.right_y", 395, 25)])
    run.append((cubic(f1, p.ang("flag.out", 100, 75, 125), Fr, S, p.t("flag.t3"), p.t("flag.t4")), "flag", "ball, head of the flag: notch"))
    # the base ends in a round ball; the flag's outside meets it at a notch
    ce = np.array([p.x("end.x", 418, 12), p.x("end.y", 432, 10)])
    end = arc(ce, p.length("end.r", 15, 8, 24), p.ang("end.notch_at", 215, 180, 255), 450)
    e0, eh0, _, _ = ends(end)
    run.append((cubic(Fr, S, e0, p.ang("end.in", 90, 60, 120), p.t("flag.t5"), p.t("flag.t6")), "flag", "flag: outside, narrowest"))
    run += [(s_, "base", "base: end, notch" if j == 0 else "base: end") for j, s_ in enumerate(end)]
    Bb = np.array([p.x("outer.bottom_x", 215, 40), p.x("outer.bottom_y", 452, 10)])
    run.append((cubic(end[-1][3], W, Bb, W, p.t("base.t1"), p.t("base.t2")), "base", "base: end, bottom"))
    run.append((cubic(Bb, W, Ol, N, p.t("outer.t7"), p.t("outer.t8")), "bowl", "bowl: bottom"))
    # the counter, anticlockwise: up the right wall into the neck of the curl that hangs from the top,
    # round its ball, which runs smoothly back up into the top wall on the left, down the left wall,
    # and over the ball on the floor
    # the hanging curl: a round ball whose left side runs smoothly up into the top wall, and which
    # rolls on round its right side up to a sharp notch, the highest point of the counter's right wall
    ctq = np.array([p.x("curl_top.x", 204, 15), p.x("curl_top.y", 70, 15)])
    a_tip = p.ang("curl_top.notch_at", 300, 250, 350)
    rc = k * K.curl_ball_r                      # a curl, so the alphabet's curl's ball
    ball_t = arc(ctq, rc, a_tip, 540)
    Tt = np.array([ctq[0] - rc - p.length("counter.top_dx", 15, 2, 70), ctq[1] - p.length("counter.top_dy", 22, 2, 50)])
    tip_t = ball_t[0][0]
    Cl = np.array([p.x("counter.left_x", 126, 15), p.x("counter.left_y", 240, 40)])
    cf = np.array([bx, p.x("ball_floor.y", 381, 15)])
    floor = arc(cf, r, p.ang("ball_floor.meets_left", 160, 95, 180), 360 + p.ang("ball_floor.meets_right", 30, 0, 85))
    Cr = np.array([p.x("counter.right_x", 290, 15), p.x("counter.right_y", 245, 40)])
    counter = [(cubic(Cr, N, tip_t, p.ang("pocket.in", 215, 180, 265), p.t("counter.t7"), p.t("counter.t8")), "counter", "counter: right")]
    counter += [(s_, "curl", "curl, top: notch" if j == 0 else "curl, top") for j, s_ in enumerate(ball_t)]
    counter += [(cubic(ball_t[-1][3], N, Tt, W, p.t("counter.t9"), p.t("counter.t10")), "counter", "curl, top: back"),
                (cubic(Tt, W, Cl, S, p.t("counter.t1"), p.t("counter.t2")), "counter", "counter: top"),
                (cubic(Cl, S, floor[0][0], p.ang("counter.floor_in", 20, 0, 70), p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: left")]
    counter += [(s_, "ball", "ball, floor: meets the left wall" if j == 0 else "ball, floor") for j, s_ in enumerate(floor)]
    counter.append((cubic(floor[-1][3], p.ang("counter.floor_out", 300, 270, 345), Cr, N, p.t("counter.t5"), p.t("counter.t6")),
                    "counter", "ball, floor: meets the right wall"))
    return {"contours": [run, counter], "baseline": Bb[1]}


def trefoil_at(p, c, axis, enter=-100, leave=100, neck=None):
    """The alphabet's trefoil, its centre near c and its tip on `axis` (start, low, high). With
    `neck` (start, low, high), the stem it hangs from meets it that wide, centred on its axis: the
    stem's edges join the side lobes where lines that far apart cross them, so a spiral can thin
    to a neck before its trefoil."""
    C = np.array([p.x("trefoil.x", c[0], 20), p.x("trefoil.y", c[1], 20)])
    ax, r, d = p.ang("trefoil.axis", *axis), p.fam("trefoil_r"), p.fam("trefoil_d")
    if neck is None:
        return trefoil(C, ax, r, d, p.ang("trefoil.enter", enter, -175, -5), p.ang("trefoil.leave", leave, 5, 175))
    half = p.length("trefoil.neck", *neck) / 2
    s = -math.sqrt(max(r * r - (d - half) ** 2, 1e-6))
    a = math.degrees(math.atan2(s, half - d))
    return trefoil(C, ax, r, d, a, -a)


def P(p, K):
    """A stem with the I's top-left and bottom curls, the bottom bar running out to a bottom-right
    curl. The bowl comes round from the top and spirals inward, rising to end in a trefoil in the
    middle of the counter. The counter is open below the bowl."""
    ax, w, k = p.x("axis_x", 138, 20), p.fam("stem_armed"), p.fam("curl")
    run, O_bl, Otl = left_side(p, K, ax, w, k, {"bottom_half_width": 73, "bottom_y": 444, "foot_y": 380, "head_y": 110,
                                                  "top_half_width": 61, "top_y": 27})
    Tlow = np.array([p.x("top.low_x", 180, 40), p.x("top.low_y", 38, 12)])
    Bt = np.array([p.x("bowl.top_x", 290, 40), p.x("bowl.top_y", 26, 12)])
    Br = np.array([p.x("bowl.right_x", 428, 15), p.x("bowl.right_y", 185, 40)])
    Bb = np.array([p.x("bowl.bottom_x", 310, 40), p.x("bowl.bottom_y", 321, 15)])
    Sl = np.array([p.x("spiral.left_x", 220, 15), p.x("spiral.left_y", 245, 30)])
    run += [(cubic(Otl, E, Tlow, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, Bt, E, p.t("top.edge_t3"), p.t("top.edge_t4")), "top bar", "top bar: low point"),
            (cubic(Bt, E, Br, S, p.t("bowl.t1"), p.t("bowl.t2")), "bowl", "bowl: top"),
            (cubic(Br, S, Bb, W, p.t("bowl.t3"), p.t("bowl.t4")), "bowl", "bowl: right"),
            (cubic(Bb, W, Sl, N, p.t("bowl.t5"), p.t("bowl.t6")), "bowl", "bowl: bottom")]
    # up the spiral to the trefoil, round it, and down the spiral's inside into the counter
    tsegs, tnames, J1, J2 = trefoil_at(p, (268, 185), (315, 260, 360))
    run.append((cubic(Sl, N, J1, p.ang("spiral.enter_heading", 330, 280, 400), p.t("spiral.t1"), p.t("spiral.t2")), "spiral", "spiral: leftmost"))
    run += [(s, "trefoil", nm) for s, nm in zip(tsegs, tnames)]
    Il = np.array([p.x("inner.left_x", 247, 15), p.x("inner.left_y", 255, 25)])
    Ib = np.array([p.x("inner.bottom_x", 288, 30), p.x("inner.bottom_y", 291, 12)])
    Ir = np.array([p.x("inner.right_x", 356, 15), p.x("inner.right_y", 190, 40)])
    It = np.array([p.x("inner.top_x", 260, 40), p.x("inner.top_y", 56, 12)])
    U1 = np.array([ax + w, p.x("counter.stem_top_y", 100, 30)])
    S4 = np.array([ax + w, p.x("stem.foot_y_right", 380, 40)])
    run += [(cubic(J2, p.ang("spiral.leave_heading", 120, 70, 180), Il, S, p.t("inner.t1"), p.t("inner.t2")), "spiral", "trefoil: join, inside"),
            (cubic(Il, S, Ib, E, p.t("inner.t3"), p.t("inner.t4")), "counter", "counter: spiral's inside, leftmost"),
            (cubic(Ib, E, Ir, N, p.t("inner.t5"), p.t("inner.t6")), "counter", "counter: lowest"),
            (cubic(Ir, N, It, W, p.t("inner.t7"), p.t("inner.t8")), "counter", "counter: right"),
            (cubic(It, W, U1, S, p.t("inner.t9"), p.t("inner.t10")), "counter", "counter: top"),
            (line(U1, S4), "stem", "stem: right, top of straight")]
    run += bottom_right(p, K, k, S4, O_bl, {"right_x": 326, "right_y": 444, "high_x": 180, "high_y": 437})
    return {"contours": [run], "baseline": O_bl[1]}


def R(p, K):
    """A stem with the I's top-left and bottom curls, the bottom bar running out to a bottom-right
    curl. The bowl's lower stroke comes back toward the stem and ends in a trefoil pointing at it,
    a hair short of touching, so the bowl stays open. From the notch under the bowl a leg sweeps
    out and down to a curl at its foot."""
    ax, w, k = p.x("axis_x", 121.5, 20), p.fam("stem_armed"), p.fam("curl")
    run, O_bl, Otl = left_side(p, K, ax, w, k, {"bottom_half_width": 64.5, "bottom_y": 446, "foot_y": 385, "head_y": 110,
                                                  "top_half_width": 60.5, "top_y": 26})
    Tlow = np.array([p.x("top.low_x", 160, 40), p.x("top.low_y", 37, 12)])
    Bt = np.array([p.x("bowl.top_x", 235, 40), p.x("bowl.top_y", 24, 12)])
    Br = np.array([p.x("bowl.right_x", 381, 15), p.x("bowl.right_y", 150, 40)])
    V = np.array([p.x("notch.x", 300, 15), p.x("notch.y", 222, 15)])
    Lr = np.array([p.x("leg.right_x", 409, 15), p.x("leg.right_y", 300, 40)])
    Pl = np.array([p.x("pocket.x", 352, 15), p.x("pocket.y", 410, 20)])
    run += [(cubic(Otl, E, Tlow, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, Bt, E, p.t("top.edge_t3"), p.t("top.edge_t4")), "top bar", "top bar: low point"),
            (cubic(Bt, E, Br, S, p.t("bowl.t1"), p.t("bowl.t2")), "bowl", "bowl: top"),
            (cubic(Br, S, V, p.ang("notch.in", 135, 100, 170), p.t("bowl.t3"), p.t("bowl.t4")), "bowl", "bowl: right"),
            (cubic(V, p.ang("notch.out", 40, 0, 80), Lr, S, p.t("leg.t1"), p.t("leg.t2")), "leg", "notch"),
            (cubic(Lr, S, Pl, S, p.t("leg.t3"), p.t("leg.t4")), "leg", "leg: outside, rightmost")]
    # the curl at the leg's foot, rolling up and back over the pocket
    O_lf = np.array([p.x("foot.curl_x", 372, 15), p.x("foot.curl_y", 447, 10)])
    segs, names, neck, arrive = K.curl(O_lf, "br", k, p.ang("foot.neck_deg", 0, 0, 40), place="curl, foot of the leg")
    run.append((cubic(Pl, S, neck, arrive, p.t("pocket.t1"), p.t("pocket.t2")), "leg", "pocket: leftmost"))
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    # back along the foot, up the leg's inside, under the bowl's stroke to the trefoil
    IL = np.array([p.x("inside.left_x", 313, 15), p.x("inside.left_y", 400, 25)])
    IR = np.array([p.x("inside.right_x", 327, 15), p.x("inside.right_y", 320, 30)])
    run += [(cubic(O_lf, W, IL, N, p.t("foot.t1"), p.t("foot.t2")), "leg", "curl, foot of the leg: outer"),
            (cubic(IL, N, IR, N, p.t("inside.t1"), p.t("inside.t2")), "leg", "leg: inside, leftmost")]
    # the underside of the bowl's stroke rises all the way to the trefoil's lower lobe
    tsegs, tnames, J1, J2 = trefoil_at(p, (205, 228), (180, 150, 210))
    run.append((cubic(IR, N, J1, p.ang("under.enter_heading", 200, 180, 250), p.t("under.t1"), p.t("under.t2")), "leg", "leg: inside, rightmost"))
    run += [(s, "trefoil", nm) for s, nm in zip(tsegs, tnames)]
    # the counter: along the stroke's top, up the bowl's inside, over and down the stem
    Cr = np.array([p.x("counter.right_x", 301, 15), p.x("counter.right_y", 150, 30)])
    Ct = np.array([p.x("counter.top_x", 230, 40), p.x("counter.top_y", 48, 12)])
    U1 = np.array([ax + w, p.x("counter.stem_top_y", 95, 30)])
    S4 = np.array([ax + w, p.x("stem.foot_y_right", 390, 40)])
    run += [(cubic(J2, p.ang("counter.floor_heading", 340, 290, 360), Cr, N, p.t("counter.t1"), p.t("counter.t2")), "counter", "trefoil: join, top"),
            (cubic(Cr, N, Ct, W, p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: right"),
            (cubic(Ct, W, U1, S, p.t("counter.t5"), p.t("counter.t6")), "counter", "counter: top"),
            (line(U1, S4), "stem", "stem: right, top of straight")]
    run += bottom_right(p, K, k, S4, O_bl, {"right_x": 242, "right_y": 446, "high_x": 150, "high_y": 440})
    return {"contours": [run], "baseline": O_bl[1]}


def B(p, K):
    """A stem with the I's top-left and bottom-left curls, the bottom bar running into the lower
    bowl. Two bowls, the lower the larger, with a notch between them outside; at their waist a
    trefoil points back at the stem, leaving a gap, so the two counters are one."""
    ax, w, k = p.x("axis_x", 132, 20), p.fam("stem_armed"), p.fam("curl")
    run, O_bl, Otl = left_side(p, K, ax, w, k, {"bottom_half_width": 67, "bottom_y": 447, "foot_y": 390, "head_y": 100,
                                                  "top_half_width": 64, "top_y": 27})
    Tlow = np.array([p.x("top.low_x", 180, 40), p.x("top.low_y", 37, 12)])
    Ut = np.array([p.x("upper.top_x", 257, 40), p.x("upper.top_y", 25, 12)])
    Ur = np.array([p.x("upper.right_x", 414, 15), p.x("upper.right_y", 150, 40)])
    V = np.array([p.x("waist.x", 338, 15), p.x("waist.y", 232, 15)])
    Lr = np.array([p.x("lower.right_x", 435, 15), p.x("lower.right_y", 345, 40)])
    Lb = np.array([p.x("lower.bottom_x", 290, 40), p.x("lower.bottom_y", 461, 10)])
    # the bar between the bottom-left curl and the bowl rises to a high point, so the curl hangs below it
    Bh = np.array([p.x("bottom.high_x", 120, 50), p.x("bottom.high_y", 445, 12)])
    run += [(cubic(Otl, E, Tlow, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, Ut, E, p.t("top.edge_t3"), p.t("top.edge_t4")), "top bar", "top bar: low point"),
            (cubic(Ut, E, Ur, S, p.t("upper.t1"), p.t("upper.t2")), "upper bowl", "upper bowl: top"),
            (cubic(Ur, S, V, p.ang("waist.in", 135, 100, 175), p.t("upper.t3"), p.t("upper.t4")), "upper bowl", "upper bowl: right"),
            (cubic(V, p.ang("waist.out", 40, 5, 80), Lr, S, p.t("lower.t1"), p.t("lower.t2")), "lower bowl", "waist, outside"),
            (cubic(Lr, S, Lb, W, p.t("lower.t3"), p.t("lower.t4")), "lower bowl", "lower bowl: right"),
            (cubic(Lb, W, Bh, W, p.t("lower.t5"), p.t("lower.t6")), "bottom bar", "lower bowl: bottom"),
            (cubic(Bh, W, O_bl, W, p.t("bottom.t1"), p.t("bottom.t2")), "bottom bar", "bottom bar: high point")]
    # the counter, anticlockwise: down the stem, round the lower bowl, under the waist to the
    # trefoil, round it, along the waist's top and round the upper bowl
    U1 = np.array([ax + w, p.x("counter.stem_top_y", 95, 30)])
    U2 = np.array([ax + w, p.x("counter.stem_foot_y", 400, 30)])
    Cb = np.array([p.x("counter.bottom_x", 260, 40), p.x("counter.bottom_y", 437, 12)])
    Clr = np.array([p.x("counter.lower_right_x", 353, 15), p.x("counter.lower_right_y", 345, 40)])
    tsegs, tnames, J1, J2 = trefoil_at(p, (232, 228), (180, 150, 210))
    Cur = np.array([p.x("counter.upper_right_x", 335, 15), p.x("counter.upper_right_y", 150, 30)])
    Ct = np.array([p.x("counter.top_x", 250, 40), p.x("counter.top_y", 48, 12)])
    counter = [(line(U1, U2), "counter", "counter: stem, top of straight"),
               (cubic(U2, S, Cb, E, p.t("counter.t1"), p.t("counter.t2")), "counter", "counter: stem, foot of straight"),
               (cubic(Cb, E, Clr, N, p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: bottom"),
               (cubic(Clr, N, J1, p.ang("waist.enter_heading", 200, 180, 250), p.t("counter.t5"), p.t("counter.t6")), "counter", "counter: lower bowl, right")]
    counter += [(s, "trefoil", nm) for s, nm in zip(tsegs, tnames)]
    counter += [(cubic(J2, p.ang("waist.top_heading", 340, 290, 360), Cur, N, p.t("counter.t9"), p.t("counter.t10")), "counter", "trefoil: join, top"),
                (cubic(Cur, N, Ct, W, p.t("counter.t11"), p.t("counter.t12")), "counter", "counter: upper bowl, right"),
                (cubic(Ct, W, U1, S, p.t("counter.t13"), p.t("counter.t14")), "counter", "counter: top")]
    return {"contours": [run, counter], "baseline": O_bl[1]}


def G_(p, K):
    """The uncial G: a round bowl whose top runs out into a hooked beak, with a round nub on top,
    falling at the right to a round bulb. Its lower right rises as a stroke that arches over and spirals down to end in a
    trefoil pointing down. The counter opens to the outside between the bulb and that stroke."""
    Gl = np.array([p.x("bowl.left_x", 24, 15), p.x("bowl.left_y", 240, 40)])
    Gt = np.array([p.x("bowl.top_x", 250, 40), p.x("bowl.top_y", 28, 12)])
    # a round nub rises from the top of the beak: the bowl's top meets it at a notch, and its right
    # side runs down into the beak's outside
    nc = np.array([p.x("nub.x", 402, 15), p.x("nub.y", 38, 12)])
    nub = arc(nc, p.length("nub.r", 17, 8, 26), p.ang("nub.from", 205, 170, 250), 360)
    n0, nh0, n1, nh1 = ends(nub)
    # the bulb at the beak's tip: the beak's outside meets it at a corner, its inside leaves it smoothly
    bc = np.array([p.x("bulb.x", 423, 15), p.x("bulb.y", 162, 15)])
    bulb = arc(bc, p.length("bulb.r", 18, 8, 30), p.ang("bulb.from", 300, 250, 350), p.ang("bulb.to", 515, 470, 560))
    b0, bh0, b1, bh1 = ends(bulb)
    Ct = np.array([p.x("counter.top_x", 250, 40), p.x("counter.top_y", 58, 12)])
    Cl = np.array([p.x("counter.left_x", 126, 15), p.x("counter.left_y", 240, 40)])
    Cb = np.array([p.x("counter.bottom_x", 250, 40), p.x("counter.bottom_y", 424, 12)])
    Rr = np.array([p.x("stroke.inside_x", 351, 15), p.x("stroke.inside_y", 285, 40)])
    Ai = np.array([p.x("arch.inside_x", 275, 30), p.x("arch.inside_y", 175, 12)])
    run = [(cubic(Gl, N, Gt, E, p.t("bowl.t1"), p.t("bowl.t2")), "bowl", "bowl: left"),
           (cubic(Gt, E, n0, p.ang("nub.in", 5, -20, 40), p.t("beak.t1"), p.t("beak.t2")), "beak", "bowl: top")]
    run += [(s, "nub", "nub: notch" if j == 0 else "nub") for j, s in enumerate(nub)]
    run.append((cubic(n1, nh1, b0, p.ang("beak.into_bulb", 100, 90, 145), p.t("beak.t3"), p.t("beak.t4")), "beak", "nub: right, into the beak"))
    run += [(s, "bulb", "bulb" if j else "bulb: meets the beak") for j, s in enumerate(bulb)]
    run += [(cubic(b1, bh1, Ct, W, p.t("beak.t5"), p.t("beak.t6")), "beak", "bulb: leaves for the beak's inside"),
            (cubic(Ct, W, Cl, S, p.t("counter.t1"), p.t("counter.t2")), "counter", "counter: top"),
            (cubic(Cl, S, Cb, E, p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: left"),
            (cubic(Cb, E, Rr, N, p.t("counter.t5"), p.t("counter.t6")), "counter", "counter: bottom"),
            (cubic(Rr, N, Ai, W, p.t("counter.t7"), p.t("counter.t8")), "spiral", "spiral: inside, rightmost")]
    # down the spiral's inside to the trefoil, round it, and back up the spiral's outside and over
    tsegs, tnames, J1, J2 = trefoil_at(p, (222, 268), (90, 45, 135), neck=(18, 12, 26))
    Sl = np.array([p.x("spiral.left_x", 199, 15), p.x("spiral.left_y", 205, 25)])
    Ao = np.array([p.x("arch.top_x", 285, 30), p.x("arch.top_y", 147, 12)])
    Gr = np.array([p.x("bowl.right_x", 441, 15), p.x("bowl.right_y", 295, 40)])
    Gb = np.array([p.x("bowl.bottom_x", 250, 40), p.x("bowl.bottom_y", 451, 10)])
    run.append((cubic(Ai, W, J1, p.ang("spiral.enter_heading", 115, 90, 170), p.t("spiral.t1"), p.t("spiral.t2")), "spiral", "spiral: under the arch"))
    run += [(s, "trefoil", nm) for s, nm in zip(tsegs, tnames)]
    run += [(cubic(J2, p.ang("spiral.leave_heading", 280, 250, 320), Sl, N, p.t("spiral.t3"), p.t("spiral.t4")), "spiral", "trefoil: join, outside"),
            (cubic(Sl, N, Ao, E, p.t("spiral.t5"), p.t("spiral.t6")), "spiral", "spiral: outside, leftmost"),
            (cubic(Ao, E, Gr, S, p.t("spiral.t7"), p.t("spiral.t8")), "spiral", "arch: top"),
            (cubic(Gr, S, Gb, W, p.t("bowl.t3"), p.t("bowl.t4")), "bowl", "bowl: right"),
            (cubic(Gb, W, Gl, N, p.t("bowl.t5"), p.t("bowl.t6")), "bowl", "bowl: bottom")]
    return {"contours": [run], "baseline": Gb[1]}


def V(p, K):
    """Two straight arms meeting at a point, the left thick and the right thin, each headed by a
    bar with a curl at both ends. Between the arms, the counter comes to a point above the foot."""
    k = p.fam("curl")
    Vp = np.array([p.x("point.x", 271, 15), p.x("point.y", 441, 12)])
    Cr = np.array([p.x("crotch.x", 294, 15), p.x("crotch.y", 278, 25)])
    L1, hL1 = edge_point(p, "left_arm.outer", (107, 100), 243)      # up the left arm's outside
    R1, hR1 = edge_point(p, "left_arm.inner", (197, 100), 62, upright=True)       # down its inside
    L2, hL2 = edge_point(p, "right_arm.inner", (379, 100), 295, upright=True)     # up the right arm's inside
    R2, hR2 = edge_point(p, "right_arm.outer", (416, 100), 114)     # down its outside
    run = [(cubic(Vp, p.ang("point.out", 243, 225, 260), L1, hL1, p.t("left_arm.t1"), p.t("left_arm.t2")), "arm", "point")]
    run += cap_top(p, K, k, "left cap", L1, hL1, R1, hR1, {"y": 24, "left": 64, "right": 205})
    run.append((cubic(R1, hR1, Cr, p.ang("crotch.in", 62, 40, 85), p.t("left_arm.t3"), p.t("left_arm.t4")), "arm", "left arm: inside"))
    run.append((cubic(Cr, p.ang("crotch.out", 295, 275, 320), L2, hL2, p.t("right_arm.t1"), p.t("right_arm.t2")), "arm", "crotch"))
    run += cap_top(p, K, k, "right cap", L2, hL2, R2, hR2, {"y": 29, "left": 369, "right": 456})
    run.append((cubic(R2, hR2, Vp, p.ang("point.in", 114, 95, 135), p.t("right_arm.t3"), p.t("right_arm.t4")), "arm", "right arm: outside"))
    return {"contours": [run], "baseline": Vp[1]}


def X(p, K):
    """A thick stroke from top left to bottom right crossed by a thin one from top right to bottom
    left, each of the four arms ending in a bar with a curl at both ends. Where the arms meet there
    are four inside corners."""
    k = p.fam("curl")
    Ct = np.array([p.x("crotch_top.x", 257, 15), p.x("crotch_top.y", 192, 20)])
    Cr = np.array([p.x("crotch_right.x", 274, 15), p.x("crotch_right.y", 232, 20)])
    Cb = np.array([p.x("crotch_bottom.x", 212, 15), p.x("crotch_bottom.y", 248, 20)])
    Cl = np.array([p.x("crotch_left.x", 199, 15), p.x("crotch_left.y", 231, 20)])
    tl_o, h_tl_o = edge_point(p, "tl_arm.outer", (98, 80), 235)     # the top-left arm's lower-left edge, going up
    tl_i, h_tl_i = edge_point(p, "tl_arm.inner", (183, 80), 55, upright=True)     # its upper-right edge, going down
    tr_i, h_tr_i = edge_point(p, "tr_arm.inner", (330, 80), 270, upright=True)    # the top-right arm's left edge, going up
    tr_o, h_tr_o = edge_point(p, "tr_arm.outer", (417, 80), 115)    # its right edge, going down
    br_o, h_br_o = edge_point(p, "br_arm.outer", (394, 400), 50)    # the bottom-right arm's right edge, going down
    br_i, h_br_i = edge_point(p, "br_arm.inner", (297, 400), 240, upright=True)   # its left edge, going up
    bl_i, h_bl_i = edge_point(p, "bl_arm.inner", (156, 400), 95, upright=True)    # the bottom-left arm's right edge, going down
    bl_o, h_bl_o = edge_point(p, "bl_arm.outer", (76, 400), 290)    # its left edge, going up
    run = cap_top(p, K, k, "top-left cap", tl_o, h_tl_o, tl_i, h_tl_i, {"y": 34, "left": 71, "right": 194})
    run.append((cubic(tl_i, h_tl_i, Ct, p.ang("crotch_top.in", 55, 30, 80), p.t("tl.t1"), p.t("tl.t2")), "arm", "top-left arm: upper edge"))
    run.append((cubic(Ct, p.ang("crotch_top.out", 290, 250, 330), tr_i, h_tr_i, p.t("tr.t1"), p.t("tr.t2")), "arm", "crotch, top"))
    run += cap_top(p, K, k, "top-right cap", tr_i, h_tr_i, tr_o, h_tr_o, {"y": 27, "left": 306, "right": 439})
    run.append((cubic(tr_o, h_tr_o, Cr, p.ang("crotch_right.in", 130, 100, 165), p.t("tr.t3"), p.t("tr.t4")), "arm", "top-right arm: right edge"))
    run.append((cubic(Cr, p.ang("crotch_right.out", 50, 20, 80), br_o, h_br_o, p.t("br.t1"), p.t("br.t2")), "arm", "crotch, right"))
    run += cap_bottom(p, K, k, "bottom-right cap", br_o, h_br_o, br_i, h_br_i, {"y": 445, "left": 293, "right": 422})
    run.append((cubic(br_i, h_br_i, Cb, p.ang("crotch_bottom.in", 235, 205, 265), p.t("br.t3"), p.t("br.t4")), "arm", "bottom-right arm: left edge"))
    run.append((cubic(Cb, p.ang("crotch_bottom.out", 110, 80, 140), bl_i, h_bl_i, p.t("bl.t1"), p.t("bl.t2")), "arm", "crotch, bottom"))
    run += cap_bottom(p, K, k, "bottom-left cap", bl_i, h_bl_i, bl_o, h_bl_o, {"y": 446, "left": 58, "right": 172})
    run.append((cubic(bl_o, h_bl_o, Cl, p.ang("crotch_left.in", 300, 270, 330), p.t("bl.t3"), p.t("bl.t4")), "arm", "bottom-left arm: left edge"))
    run.append((cubic(Cl, p.ang("crotch_left.out", 235, 205, 265), tl_o, h_tl_o, p.t("tl.t3"), p.t("tl.t4")), "arm", "crotch, left"))
    return {"contours": [run], "baseline": p.x("bottom-left cap.y", 446, 15)}


def Z(p, K):
    """A top bar with a curl at each end; a thick diagonal from under its right end down to a
    rounded point at the bottom left; and a bottom bar that springs from a sharp slit beside that
    point, arches up and runs right to a curl. A matching slit sits under the top bar where the
    diagonal leaves it."""
    k = p.fam("curl")
    y = p.x("top.y", 30, 15)
    O_tl = np.array([p.x("top.left_x", 89, 20), y])
    O_tr = np.array([p.x("top.right_x", 338, 20), y])
    Dt = np.array([p.x("top.low_x", 220, 50), y + p.length("top.low_dy", 10, 0, 30)])
    segs_l, names_l, neck_l, arrive_l = K.curl(O_tl, "tl", k, p.ang("top.neck_l", 0, 0, 40), place="curl, top-left")
    # the diagonal leaves the top-right curl's neck steeply, so its right side can bow outward
    segs_r, names_r, neck_r, leave_r = K.curl(O_tr, "tr", k, p.ang("top.neck_r", 45, 0, 85), place="curl, top-right")
    run = [(cubic(O_tl, E, Dt, E, p.t("top.t1"), p.t("top.t2")), "top bar", "curl, top-left: outer"),
           (cubic(Dt, E, O_tr, E, p.t("top.t3"), p.t("top.t4")), "top bar", "top bar: low point")]
    run += [(s, "curl", nm) for s, nm in zip(segs_r, names_r)]
    # down the diagonal's right side, one convex sweep, to the slit at the bottom bar's root
    Sb = np.array([p.x("slit_bottom.x", 60, 15), p.x("slit_bottom.y", 411, 15)])
    run.append((cubic(neck_r, leave_r, Sb, p.ang("slit_bottom.in", 150, 115, 175), p.t("diagonal.t1"), p.t("diagonal.t2")), "diagonal",
                "curl, top-right: neck"))
    # the bottom bar arches up from the slit and runs right to its curl
    Bh = np.array([p.x("bottom.high_x", 160, 40), p.x("bottom.high_y", 370, 15)])
    O_br = np.array([p.x("bottom.right_x", 344, 20), p.x("bottom.y", 445, 12)])
    segs_b, names_b, neck_b, arrive_b = K.curl(O_br, "br", k, p.ang("bottom.neck", 0, 0, 40), place="curl, bottom-right")
    run += [(cubic(Sb, p.ang("slit_bottom.out", 330, 290, 360), Bh, E, p.t("bottom.t1"), p.t("bottom.t2")), "bottom bar", "slit, bottom"),
            (cubic(Bh, E, neck_b, arrive_b, p.t("bottom.t3"), p.t("bottom.t4")), "bottom bar", "bottom bar: top")]
    run += [(s, "curl", nm) for s, nm in zip(segs_b, names_b)]
    # back along the underside, a wave: down to its lowest under the right half, up to a crest, and
    # down again to meet the rounded point at the point's own lowest; then up the diagonal's left
    # side to the top slit
    pc = np.array([p.x("point.x", 36, 15), p.x("point.y", 428, 15)])
    pa = arc(pc, p.length("point.r", 8, 3, 15), 90, p.ang("point.to", 225, 190, 260))
    c0, h0, c1, h1 = ends(pa)
    corner = [(s, "diagonal", "diagonal: rounded point" if j == 0 else "diagonal: rounded point, extreme") for j, s in enumerate(pa)]
    Bm = np.array([p.x("bottom.under_x", 288, 40), p.x("bottom.under_y", 449, 10)])
    Bc = np.array([p.x("bottom.crest_x", 122, 40), p.x("bottom.crest_y", 429, 12)])
    St = np.array([p.x("slit_top.x", 258, 20), p.x("slit_top.y", 72, 15)])
    Dl = np.array([p.x("diagonal.left_x", 140, 30), p.x("diagonal.left_y", 220, 40)])
    hd_l = p.ang("diagonal.left_heading", 305, 285, 325)
    Ul = np.array([p.x("top.under_x", 170, 40), p.x("top.under_y", 88, 12)])
    run += [(cubic(O_br, W, Bm, W, p.t("bottom.t5"), p.t("bottom.t6")), "bottom bar", "curl, bottom-right: outer"),
            (cubic(Bm, W, Bc, W, p.t("bottom.t7"), p.t("bottom.t8")), "bottom bar", "bottom bar: underside, lowest"),
            (cubic(Bc, W, c0, W, p.t("bottom.t9"), p.t("bottom.t10")), "bottom bar", "bottom bar: underside, crest")]
    run += corner
    run += [(cubic(c1, h1, Dl, hd_l, p.t("diagonal.t5"), p.t("diagonal.t6")), "diagonal", "diagonal: rounded point, end"),
            (cubic(Dl, hd_l, St, p.ang("slit_top.in", 310, 285, 340), p.t("diagonal.t7"), p.t("diagonal.t8")), "diagonal", "diagonal: left side"),
            (cubic(St, p.ang("slit_top.out", 190, 165, 215), Ul, W, p.t("top.t5"), p.t("top.t6")), "top bar", "slit, top"),
            (cubic(Ul, W, neck_l, arrive_l, p.t("top.t7"), p.t("top.t8")), "top bar", "top bar: underside, lowest")]
    run += [(s, "curl", nm) for s, nm in zip(segs_l, names_l)]
    return {"contours": [run], "baseline": O_br[1]}


def N_(p, K):
    """The uncial N: the I's stem with a top-left curl and curls either side of its foot, and from
    the stem's top an arch that rises over, comes down the right and sweeps into the two-lobe
    terminal. The counter under the arch opens at the bottom."""
    ax, w, k = p.x("axis_x", 130.5, 20), p.fam("stem_armed"), p.fam("curl")
    run, O_bl, Otl = left_side(p, K, ax, w, k, {"bottom_half_width": 64.5, "bottom_y": 446, "foot_y": 385, "head_y": 105,
                                                  "top_half_width": 56.5, "top_y": 28})
    Tlow = np.array([p.x("top.low_x", 125, 30), p.x("top.low_y", 38, 12)])
    AT = np.array([p.x("arch.top_x", 240, 30), p.x("arch.top_y", 22, 12)])
    SHr = np.array([p.x("arch.right_x", 426, 15), p.x("arch.right_y", 205, 40)])
    Pl = np.array([p.x("pocket.x", 325, 15), p.x("pocket.y", 392, 20)])
    run += [(cubic(Otl, E, Tlow, E, p.t("top.t1"), p.t("top.t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, AT, E, p.t("top.t3"), p.t("top.t4")), "arch", "top bar: low point"),
            (cubic(AT, E, SHr, S, p.t("arch.t1"), p.t("arch.t2")), "arch", "arch: top"),
            (cubic(SHr, S, Pl, S, p.t("arch.t3"), p.t("arch.t4")), "arch", "arch: outside, rightmost")]
    foot_run, J = lobed_foot(p, Pl, {"x": 383, "y": 386, "angle": 35})
    run += foot_run
    FB = np.array([p.x("foot.bottom_x", 345, 25), J[1] + p.length("foot.drop", 8, 0, 30)])    # never above the terminal's end
    IL = np.array([p.x("inside.left_x", 289, 15), p.x("inside.left_y", 380, 25)])
    IR = np.array([p.x("inside.right_x", 331, 15), p.x("inside.right_y", 200, 40)])
    AI = np.array([p.x("arch.inside_x", 235, 30), p.x("arch.inside_y", 48, 12)])
    AS = np.array([ax + w, p.x("arch.foot_y", 130, 40)])
    S4 = np.array([ax + w, p.x("stem.foot_y_right", 380, 40)])
    run += [(cubic(J, p.ang("foot.join_out", 160, 120, 180), FB, W, p.t("foot.t1"), p.t("foot.t2")), "foot", "two-lobe terminal: join"),
            (cubic(FB, W, IL, N, p.t("foot.t3"), p.t("foot.t4")), "arch", "foot: bottom"),
            (cubic(IL, N, IR, N, p.t("inside.t1"), p.t("inside.t2")), "arch", "arch: inside, leftmost"),
            (cubic(IR, N, AI, W, p.t("inside.t3"), p.t("inside.t4")), "arch", "arch: inside, rightmost"),
            (cubic(AI, W, AS, S, p.t("inside.t5"), p.t("inside.t6")), "arch", "arch: inside, top"),
            (line(AS, S4), "stem", "stem: right, below the arch")]
    run += bottom_right(p, K, k, S4, O_bl, {"right_x": 197, "right_y": 445, "high_x": 140, "high_y": 438})
    return {"contours": [run], "baseline": O_bl[1]}


def Y(p, K):
    """A stem (the plain weight, like L's) with top-left and bottom-left curls; a top bar running the
    width of the letter to a top-right curl; and from it the right side, which curves down and round
    into the foot, closing the counter against the stem."""
    ax, w, k = p.x("axis_x", 131.5, 20), p.fam("stem_plain"), p.fam("curl")
    run, O_bl, Otl = left_side(p, K, ax, w, k, {"bottom_half_width": 65.5, "bottom_y": 448, "foot_y": 390, "head_y": 100,
                                                  "top_half_width": 64.5, "top_y": 28})
    Tlow = np.array([p.x("top.low_x", 240, 60), p.x("top.low_y", 34, 12)])
    O_tr = np.array([p.x("top.right_x", 421, 20), Otl[1]])
    segs, names, neck, leave = K.curl(O_tr, "tr", k, p.ang("top.neck_r", 5, 0, 40), place="curl, top-right")
    Ar = np.array([p.x("arm.right_x", 402, 15), p.x("arm.right_y", 110, 30)])
    Am = np.array([p.x("arm.mid_x", 330, 30), p.x("arm.mid_y", 340, 40)])
    hm = p.ang("arm.mid_heading", 125, 95, 160)
    run += [(cubic(Otl, E, Tlow, E, p.t("top.t1"), p.t("top.t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, O_tr, E, p.t("top.t3"), p.t("top.t4")), "top bar", "top bar: low point")]
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    run += [(cubic(neck, leave, Ar, S, p.t("arm.t1"), p.t("arm.t2")), "arm", "curl, top-right: neck"),
            (cubic(Ar, S, Am, hm, p.t("arm.t3"), p.t("arm.t4")), "arm", "arm: outside, rightmost"),
            (cubic(Am, hm, O_bl, W, p.t("arm.t5"), p.t("arm.t6")), "arm", "arm: outside")]
    # the counter, anticlockwise: down the stem, round the bottom, up the arm's inside, along the top
    U1 = np.array([ax + w, p.x("counter.stem_top_y", 100, 30)])
    U2 = np.array([ax + w, p.x("counter.stem_foot_y", 360, 40)])
    Cb = np.array([p.x("counter.bottom_x", 195, 30), p.x("counter.bottom_y", 403, 12)])
    Cr = np.array([p.x("counter.right_x", 317, 15), p.x("counter.right_y", 120, 40)])
    Ct = np.array([p.x("counter.top_x", 240, 40), p.x("counter.top_y", 45, 12)])
    counter = [(line(U1, U2), "counter", "counter: stem, top of straight"),
               (cubic(U2, S, Cb, E, p.t("counter.t1"), p.t("counter.t2")), "counter", "counter: stem, foot of straight"),
               (cubic(Cb, E, Cr, N, p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: bottom"),
               (cubic(Cr, N, Ct, W, p.t("counter.t5"), p.t("counter.t6")), "counter", "counter: right"),
               (cubic(Ct, W, U1, S, p.t("counter.t7"), p.t("counter.t8")), "counter", "counter: top")]
    return {"contours": [run, counter], "baseline": O_bl[1]}


def U(p, K):
    """The uncial U: a round bowl on the left, meeting the underside of a top bar at a notch; the bar
    runs the width of the letter with a curl at each end; on the right a stem comes down from the
    bar and flicks out at its foot into a pointed hook, parted from the bowl below by a notch."""
    ax, w, k = p.x("axis_x", 333.5, 20), p.fam("stem_armed"), p.fam("curl")
    Bl = np.array([p.x("bowl.left_x", 26, 15), p.x("bowl.left_y", 270, 40)])
    Nt = np.array([p.x("notch.x", 155, 15), p.x("notch.y", 62, 12)])
    y = p.x("top.y", 29, 12)
    O_tl = np.array([p.x("top.left_x", 100, 20), y])
    O_tr = np.array([p.x("top.right_x", 412, 20), y])
    Tlow = np.array([p.x("top.low_x", 250, 60), y + p.length("top.low_dy", 6, 0, 25)])
    segs_l, names_l, neck_l, arrive_l = K.curl(O_tl, "tl", k, p.ang("top.neck_l", 0, 0, 40), place="curl, top-left")
    segs_r, names_r, neck_r, leave_r = K.curl(O_tr, "tr", k, p.ang("top.neck_r", 0, 0, 40), place="curl, top-right")
    S1 = np.array([ax + w, p.x("stem.head_y", 110, 40)])
    S2 = np.array([ax + w, p.x("stem.foot_y", 380, 40)])
    Tip = np.array([p.x("hook.x", 437, 15), p.x("hook.y", 403, 15)])
    Hl = np.array([p.x("hook.low_x", 410, 15), p.x("hook.low_y", 426, 12)])
    Hb = np.array([p.x("hook.bottom_x", 390, 20), p.x("hook.bottom_y", 452, 10)])
    Nb = np.array([p.x("notch_b.x", 318, 15), p.x("notch_b.y", 411, 15)])
    Bb = np.array([p.x("bowl.bottom_x", 210, 40), p.x("bowl.bottom_y", 454, 10)])
    run = [(cubic(Bl, N, Nt, p.ang("notch.in", 300, 270, 340), p.t("bowl.t1"), p.t("bowl.t2")), "bowl", "bowl: left"),
           (cubic(Nt, p.ang("notch.out", 185, 160, 215), neck_l, arrive_l, p.t("top.t5"), p.t("top.t6")), "top bar", "notch")]
    run += [(s, "curl", nm) for s, nm in zip(segs_l, names_l)]
    run += [(cubic(O_tl, E, Tlow, E, p.t("top.t1"), p.t("top.t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, O_tr, E, p.t("top.t3"), p.t("top.t4")), "top bar", "top bar: low point")]
    run += [(s, "curl", nm) for s, nm in zip(segs_r, names_r)]
    run += [(cubic(neck_r, leave_r, S1, S, p.t("stem.t1"), p.t("stem.t2")), "flare", "curl, top-right: neck"),
            (line(S1, S2), "stem", "stem: right, top of straight"),
            # the hook: the inside dips and rises to a sharp tip up and to the right; the underside
            # comes back down to its lowest point and up to a notch where it meets the bowl
            (cubic(S2, S, Hl, E, p.t("hook.t1"), p.t("hook.t2")), "hook", "stem: right, foot of straight"),
            (cubic(Hl, E, Tip, p.ang("hook.in", 305, 270, 345), p.t("hook.t5"), p.t("hook.t6")), "hook", "hook: inside, lowest"),
            (cubic(Tip, p.ang("hook.out", 125, 95, 170), Hb, W, p.t("hook.t3"), p.t("hook.t4")), "hook", "hook: tip"),
            (cubic(Hb, W, Nb, p.ang("notch_b.in", 220, 190, 255), p.t("hook.t7"), p.t("hook.t8")), "hook", "hook: lowest"),
            (cubic(Nb, p.ang("notch_b.out", 150, 110, 175), Bb, W, p.t("bowl.t5"), p.t("bowl.t6")), "bowl", "notch, bottom"),
            (cubic(Bb, W, Bl, N, p.t("bowl.t3"), p.t("bowl.t4")), "bowl", "bowl: bottom")]
    # the counter, anticlockwise; its right side is the stem's inside
    Ct = np.array([p.x("counter.top_x", 225, 40), p.x("counter.top_y", 74, 12)])
    Cl = np.array([p.x("counter.left_x", 121, 15), p.x("counter.left_y", 270, 40)])
    Cb = np.array([p.x("counter.bottom_x", 205, 40), p.x("counter.bottom_y", 424, 12)])
    C1 = np.array([ax - w, p.x("counter.stem_foot_y", 340, 40)])
    C2 = np.array([ax - w, p.x("counter.stem_top_y", 150, 40)])
    counter = [(cubic(Ct, W, Cl, S, p.t("counter.t1"), p.t("counter.t2")), "counter", "counter: top"),
               (cubic(Cl, S, Cb, E, p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: left"),
               (cubic(Cb, E, C1, N, p.t("counter.t5"), p.t("counter.t6")), "counter", "counter: bottom"),
               (line(C1, C2), "stem", "counter: stem, foot of straight"),
               (cubic(C2, N, Ct, W, p.t("counter.t7"), p.t("counter.t8")), "counter", "counter: stem, top of straight")]
    return {"contours": [run, counter], "baseline": Bb[1]}


def A(p, K):
    """A top bar the width of the letter with a curl at each end; on the right a stem with curls
    either side of its foot; on the left a stroke that bows out and sweeps in to a bottom-left curl;
    a crossbar between them closing a squarish counter above it."""
    ax, w, k = p.x("axis_x", 307.5, 20), p.fam("stem_armed"), p.fam("curl")
    O_bl = np.array([p.x("left.curl_x", 70, 15), p.x("left.curl_y", 448, 10)])
    segs, names, neck, leave = K.curl(O_bl, "bl", k, p.ang("left.neck", 0, 0, 40), place="curl, bottom-left")
    run = [(s, "curl", nm) for s, nm in zip(segs, names)]
    Lx1 = np.array([p.x("left.foot_x", 101, 15), p.x("left.foot_y", 392, 20)])
    Lx2 = np.array([p.x("left.out_x", 51, 15), p.x("left.out_y", 225, 40)])
    Nt = np.array([p.x("notch.x", 130, 15), p.x("notch.y", 58, 12)])
    y = p.x("top.y", 27, 12)
    O_tl = np.array([p.x("top.left_x", 79, 20), y])
    O_tr = np.array([p.x("top.right_x", 378, 20), y])
    Tlow = np.array([p.x("top.low_x", 220, 60), y + p.length("top.low_dy", 4, 0, 20)])
    segs_l, names_l, neck_l, arrive_l = K.curl(O_tl, "tl", k, p.ang("top.neck_l", 0, 0, 40), place="curl, top-left")
    segs_r, names_r, neck_r, leave_r = K.curl(O_tr, "tr", k, p.ang("top.neck_r", 0, 0, 40), place="curl, top-right")
    S1 = np.array([ax + w, p.x("stem.head_y", 100, 40)])
    run += [(cubic(neck, leave, Lx1, N, p.t("left.t1"), p.t("left.t2")), "left stroke", "curl, bottom-left: neck"),
            (cubic(Lx1, N, Lx2, N, p.t("left.t3"), p.t("left.t4")), "left stroke", "left stroke: foot, rightmost"),
            (cubic(Lx2, N, Nt, p.ang("notch.in", 300, 270, 340), p.t("left.t5"), p.t("left.t6")), "left stroke", "left stroke: leftmost"),
            (cubic(Nt, p.ang("notch.out", 185, 160, 215), neck_l, arrive_l, p.t("top.t5"), p.t("top.t6")), "top bar", "notch")]
    run += [(s, "curl", nm) for s, nm in zip(segs_l, names_l)]
    run += [(cubic(O_tl, E, Tlow, E, p.t("top.t1"), p.t("top.t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, O_tr, E, p.t("top.t3"), p.t("top.t4")), "top bar", "top bar: low point")]
    run += [(s, "curl", nm) for s, nm in zip(segs_r, names_r)]
    Sr = np.array([ax + w, p.x("stem.foot_y", 370, 40)])
    Sl = np.array([ax - w, p.x("stem.foot_y", 370, 40)])
    run += [(cubic(neck_r, leave_r, S1, S, p.t("stem.t1"), p.t("stem.t2")), "flare", "curl, top-right: neck"),
            (line(S1, Sr), "stem", "stem: right, top of straight")]
    run += cap_bottom(p, K, k, "foot", Sr, S, Sl, N, {"y": 448, "left": 242, "right": 379})
    # up the stem's inside to the crossbar, along under it, and down the left stroke's inside
    yx = p.x("crossbar.under_y", 256, 15)
    Xr = np.array([ax - w, yx])
    Xl = np.array([p.x("left.inside_x", 153, 15), yx + p.length("crossbar.slope", 1, -10, 10)])
    Fb = np.array([p.x("left.bottom_x", 105, 25), p.x("left.bottom_y", 447, 10)])
    run += [(line(Sl, Xr), "stem", "stem: left, foot of straight"),
            (line(Xr, Xl), "crossbar", "crossbar: underside, right"),
            (cubic(Xl, p.ang("left.inside_heading", 92, 80, 110), Fb, W, p.t("left.t7"), p.t("left.t8")), "left stroke", "crossbar: underside, left"),
            (cubic(Fb, W, O_bl, W, p.t("left.t9"), p.t("left.t10")), "left stroke", "left stroke: foot, bottom")]
    # the counter above the crossbar, anticlockwise
    ct = p.x("counter.top_y", 61, 12)
    cb = p.x("counter.bottom_y", 212, 12)
    cx = p.x("counter.left_x", 154, 15)
    TL = np.array([cx, ct])
    BL = np.array([cx, cb])
    BR = np.array([ax - w, cb])
    TR = np.array([ax - w, ct])
    counter = [(line(TL, BL), "counter", "counter: top left"),
               (line(BL, BR), "crossbar", "counter: bottom left"),
               (line(BR, TR), "stem", "counter: bottom right"),
               (line(TR, TL), "top bar", "counter: top right")]
    return {"contours": [run, counter], "baseline": O_bl[1]}


def S_(p, K):
    """The S: an upper bowl and a lower bowl joined by a spine. At the top right the upper bowl meets a
    short upright flag at a notch; the flag's head is rounded, and at its foot a round ball sits out
    to the right, the flag's outside meeting it at a sharp notch and its inside running smoothly
    round under it. At the bottom left the same, turned over: a stroke rises from a rounded foot,
    parted from the lower bowl by a notch, to a round ball at its head. The balls are the alphabet's
    curl's ball. Both counters open toward them."""
    rc = p.fam("curl") * K.curl_ball_r
    A0 = np.array([p.x("upper.left_x", 56, 15), p.x("upper.left_y", 165, 30)])
    Ut = np.array([p.x("upper.top_x", 210, 40), p.x("upper.top_y", 26, 12)])
    Nt = np.array([p.x("notch.x", 322, 15), p.x("notch.y", 49, 15)])
    head, f0, fh0, f1, fh1 = rounded_corner(p, "flag.head", (351, 44), 22, (205, 180, 250), (360, 330, 390), "flag", "flag: head")
    cf = np.array([p.x("flag.ball_x", 366, 15), p.x("flag.ball_y", 182, 20)])
    ball_f = arc(cf, rc, p.ang("flag.notch_at", 270, 235, 305), 360 + p.ang("flag.leaves_at", 150, 115, 178))
    b0, bh0, b1, bh1 = ends(ball_f)
    run = [(cubic(A0, N, Ut, E, p.t("upper.t1"), p.t("upper.t2")), "upper bowl", "upper bowl: leftmost"),
           (cubic(Ut, E, Nt, p.ang("notch.in", 25, 0, 60), p.t("upper.t3"), p.t("upper.t4")), "upper bowl", "upper bowl: top"),
           (cubic(Nt, p.ang("notch.out", 285, 250, 320), f0, fh0, p.t("flag.t1"), p.t("flag.t2")), "flag", "notch, top")]
    run += head
    run.append((cubic(f1, fh1, b0, p.ang("flag.into_ball", 95, 70, 120), p.t("flag.t3"), p.t("flag.t4")), "flag", "flag: head, end"))
    run += [(s, "ball", "ball, foot of the flag: notch" if j == 0 else "ball, foot of the flag") for j, s in enumerate(ball_f)]
    # up the flag's inside, round the upper counter, and along the spine's top to the lower bowl
    Ct = np.array([p.x("upper_counter.top_x", 205, 40), p.x("upper_counter.top_y", 53, 12)])
    Cl = np.array([p.x("upper_counter.left_x", 110, 15), p.x("upper_counter.left_y", 130, 25)])
    Sp = np.array([p.x("spine.top_x", 270, 40), p.x("spine.top_y", 207, 15)])
    hs = p.ang("spine.top_heading", 20, 0, 50)
    Lr = np.array([p.x("lower.right_x", 398, 15), p.x("lower.right_y", 335, 30)])
    Lb = np.array([p.x("lower.bottom_x", 270, 40), p.x("lower.bottom_y", 463, 10)])
    run += [(cubic(b1, bh1, Ct, W, p.t("upper_counter.t1"), p.t("upper_counter.t2")), "upper bowl", "ball, foot of the flag: leaves"),
            (cubic(Ct, W, Cl, S, p.t("upper_counter.t3"), p.t("upper_counter.t4")), "upper bowl", "upper counter: top"),
            (cubic(Cl, S, Sp, hs, p.t("spine.t1"), p.t("spine.t2")), "spine", "upper counter: leftmost"),
            (cubic(Sp, hs, Lr, S, p.t("spine.t3"), p.t("spine.t4")), "spine", "spine: top"),
            (cubic(Lr, S, Lb, W, p.t("lower.t1"), p.t("lower.t2")), "lower bowl", "lower bowl: rightmost")]
    # along the bottom to the notch, round the foot of the left stroke and up it to its ball
    Nb = np.array([p.x("notch_b.x", 100, 15), p.x("notch_b.y", 413, 15)])
    Fb = np.array([p.x("foot.bottom_x", 64, 15), p.x("foot.bottom_y", 459, 10)])
    Fl = np.array([p.x("foot.left_x", 41, 12), p.x("foot.left_y", 436, 15)])
    Er = np.array([p.x("stroke.right_x", 56, 12), p.x("stroke.right_y", 362, 25)])
    ch = np.array([p.x("head.ball_x", 50, 15), p.x("head.ball_y", 283, 20)])
    ball_h = arc(ch, rc, p.ang("head.notch_at", 110, 75, 145), p.ang("head.leaves_at", 335, 300, 358))
    h0, hh0, h1, hh1 = ends(ball_h)
    run += [(cubic(Lb, W, Nb, p.ang("notch_b.in", 205, 180, 250), p.t("lower.t3"), p.t("lower.t4")), "lower bowl", "lower bowl: bottom"),
            (cubic(Nb, p.ang("notch_b.out", 120, 90, 160), Fb, W, p.t("foot.t1"), p.t("foot.t2")), "left stroke", "notch, bottom"),
            (cubic(Fb, W, Fl, N, p.t("foot.t3"), p.t("foot.t4")), "left stroke", "foot: bottom"),
            (cubic(Fl, N, Er, N, p.t("foot.t5"), p.t("foot.t6")), "left stroke", "foot: leftmost"),
            (cubic(Er, N, h0, p.ang("stroke.into_ball", 275, 250, 300), p.t("stroke.t1"), p.t("stroke.t2")), "left stroke", "left stroke: outside, rightmost")]
    run += [(s, "ball", "ball, head of the left stroke: notch" if j == 0 else "ball, head of the left stroke") for j, s in enumerate(ball_h)]
    # down the stroke's inside, round the lower counter, and up the spine's underside to the start
    Lc = np.array([p.x("lower_counter.bottom_x", 260, 40), p.x("lower_counter.bottom_y", 436, 12)])
    Lcr = np.array([p.x("lower_counter.right_x", 348, 15), p.x("lower_counter.right_y", 365, 30)])
    Sl = np.array([p.x("spine.under_x", 200, 40), p.x("spine.under_y", 290, 15)])
    hu = p.ang("spine.under_heading", 200, 180, 235)
    run += [(cubic(h1, hh1, Lc, E, p.t("lower_counter.t1"), p.t("lower_counter.t2")), "lower bowl", "ball, head of the left stroke: leaves"),
            (cubic(Lc, E, Lcr, N, p.t("lower_counter.t3"), p.t("lower_counter.t4")), "lower bowl", "lower counter: bottom"),
            (cubic(Lcr, N, Sl, hu, p.t("spine.t5"), p.t("spine.t6")), "spine", "lower counter: rightmost"),
            (cubic(Sl, hu, A0, N, p.t("spine.t7"), p.t("spine.t8")), "spine", "spine: underside")]
    return {"contours": [run], "baseline": Lb[1]}


def T_2(p, K):
    """The uncial T: a top bar the width of the letter with a curl at each end; from under its middle
    a stroke comes down and sweeps left into a round bowl, the bar's underside flowing into it in one
    curve on each side. The bowl comes round the bottom and up the right, and curls over at the top
    into a spiral that thins to a neck and ends in a trefoil in the middle of the counter. The
    counter opens between the stroke and the top of the spiral."""
    k = p.fam("curl")
    A0 = np.array([p.x("bowl.left_x", 31, 15), p.x("bowl.left_y", 275, 30)])
    # the bowl's outside rises into the bar's underside in one curve: its rightmost point is where it
    # turns from climbing to running left
    Jl = np.array([p.x("join_l.x", 200, 25), p.x("join_l.y", 82, 25)])
    y = p.x("top.y", 28, 12)
    O_tl = np.array([p.x("top.left_x", 52, 20), y])
    O_tr = np.array([p.x("top.right_x", 410, 20), y])
    Tlow = np.array([p.x("top.low_x", 230, 60), y + p.length("top.low_dy", 6, 0, 25)])
    segs_l, names_l, neck_l, arrive_l = K.curl(O_tl, "tl", k, p.ang("top.neck_l", 0, 0, 40), place="curl, top-left")
    segs_r, names_r, neck_r, leave_r = K.curl(O_tr, "tr", k, p.ang("top.neck_r", 0, 0, 40), place="curl, top-right")
    # on the right the bar's underside turns down into the stroke in one curve
    Jr = np.array([p.x("join_r.x", 268, 25), p.x("join_r.y", 80, 25)])
    hjr = p.ang("join_r.heading", 135, 100, 175)
    run = [(cubic(A0, N, Jl, N, p.t("bowl.t1"), p.t("bowl.t2")), "bowl", "bowl: leftmost"),
           (cubic(Jl, N, neck_l, arrive_l, p.t("top.t5"), p.t("top.t6")), "top bar", "stroke: outside, rightmost")]
    run += [(s, "curl", nm) for s, nm in zip(segs_l, names_l)]
    run += [(cubic(O_tl, E, Tlow, E, p.t("top.t1"), p.t("top.t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, O_tr, E, p.t("top.t3"), p.t("top.t4")), "top bar", "top bar: low point")]
    run += [(s, "curl", nm) for s, nm in zip(segs_r, names_r)]
    run.append((cubic(neck_r, leave_r, Jr, hjr, p.t("top.t7"), p.t("top.t8")), "top bar", "curl, top-right: neck"))
    # down the stroke's right side, sweeping left into the bowl's inside, round the counter
    Cl = np.array([p.x("counter.left_x", 134, 15), p.x("counter.left_y", 285, 30)])
    Cb = np.array([p.x("counter.bottom_x", 245, 40), p.x("counter.bottom_y", 428, 12)])
    Cr = np.array([p.x("counter.right_x", 356, 15), p.x("counter.right_y", 300, 30)])
    Pt = np.array([p.x("pocket.x", 283, 20), p.x("pocket.y", 180, 15)])
    run += [(cubic(Jr, hjr, Cl, S, p.t("stroke.t1"), p.t("stroke.t2")), "stroke", "bar: underside, into the stroke"),
            (cubic(Cl, S, Cb, E, p.t("counter.t1"), p.t("counter.t2")), "counter", "counter: leftmost"),
            (cubic(Cb, E, Cr, N, p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: bottom"),
            (cubic(Cr, N, Pt, W, p.t("counter.t5"), p.t("counter.t6")), "counter", "counter: rightmost")]
    # down the spiral's inside to the trefoil, round it, up the spiral's outside and down the bowl's right
    tsegs, tnames, J1, J2 = trefoil_at(p, (233, 290), (90, 45, 135), neck=(18, 12, 26))
    St = np.array([p.x("spiral.top_x", 300, 25), p.x("spiral.top_y", 164, 12)])
    Br = np.array([p.x("bowl.right_x", 441, 15), p.x("bowl.right_y", 300, 30)])
    Bb = np.array([p.x("bowl.bottom_x", 245, 40), p.x("bowl.bottom_y", 456, 10)])
    run.append((cubic(Pt, W, J1, p.ang("spiral.enter_heading", 120, 90, 175), p.t("spiral.t1"), p.t("spiral.t2")), "spiral", "pocket: top"))
    run += [(s, "trefoil", nm) for s, nm in zip(tsegs, tnames)]
    run += [(cubic(J2, p.ang("spiral.leave_heading", 290, 270, 330), St, E, p.t("spiral.t3"), p.t("spiral.t4")), "spiral", "trefoil: join, left"),
            (cubic(St, E, Br, S, p.t("bowl.t3"), p.t("bowl.t4")), "bowl", "spiral: top"),
            (cubic(Br, S, Bb, W, p.t("bowl.t5"), p.t("bowl.t6")), "bowl", "bowl: rightmost"),
            (cubic(Bb, W, A0, N, p.t("bowl.t7"), p.t("bowl.t8")), "bowl", "bowl: bottom")]
    return {"contours": [run], "baseline": Bb[1]}


def Y_2(p, K):
    """A modern Y, drawn by us on Pugin's V (Pugin's own Y is the uncial form): V's arms and capped
    tops, meeting not at a point but in a stem, which comes down to a foot with a curl at each side
    like the I's. It takes V's fitted measurements for the arms and caps; the stem is the armed weight."""
    k, w = p.fam("curl"), p.fam("stem_armed")
    ax = p.x("stem.x", 278, 20)
    yj = p.x("stem.join_y", 262, 30)                # where the arms' outsides meet the stem
    Cr = np.array([ax + p.x("crotch.dx", 6, 15), p.x("crotch.join_y", 222, 30)])
    L1, hL1 = edge_point(p, "left_arm.outer", (107, 100), 243)
    R1, hR1 = edge_point(p, "left_arm.inner", (197, 100), 62, upright=True)
    L2, hL2 = edge_point(p, "right_arm.inner", (379, 100), 295, upright=True)
    R2, hR2 = edge_point(p, "right_arm.outer", (416, 100), 114)
    Jl, Jr = np.array([ax - w, yj]), np.array([ax + w, yj])
    yf = p.x("stem.foot_y", 385, 30)
    Sl, Sr = np.array([ax - w, yf]), np.array([ax + w, yf])
    half = p.x("foot.half_width", 108, 20)
    # where each arm's outside joins the stem: the turn sits close to the stem, and the arm runs on
    # straight to its cap
    run = [(cubic(Jl, N, L1, hL1, p.t("join_l.t1", 0.3), p.t("join_l.t2", 0.9)), "arm", "stem: left, top")]
    run += cap_top(p, K, k, "left cap", L1, hL1, R1, hR1, {"y": 24, "left": 64, "right": 205})
    run.append((cubic(R1, hR1, Cr, p.ang("crotch.in", 62, 40, 85), p.t("left_arm.t3"), p.t("left_arm.t4")), "arm", "left arm: inside"))
    run.append((cubic(Cr, p.ang("crotch.out", 295, 275, 320), L2, hL2, p.t("right_arm.t1"), p.t("right_arm.t2")), "arm", "crotch"))
    run += cap_top(p, K, k, "right cap", L2, hL2, R2, hR2, {"y": 29, "left": 369, "right": 456})
    run += [(cubic(R2, hR2, Jr, S, p.t("join_r.t2", 0.9), p.t("join_r.t1", 0.3)), "arm", "right arm: outside"),
            (line(Jr, Sr), "stem", "stem: right, top of straight")]
    run += cap_bottom(p, K, k, "foot", Sr, S, Sl, N, {"y": 446, "left": ax - half, "right": ax + half})
    run.append((line(Sl, Jl), "stem", "stem: left, foot of straight"))
    return {"contours": [run], "baseline": p.x("foot.y", 446, 15)}


def M_2(p, K):
    """The straight M: two legs, splayed a little, each standing on a foot with a curl at both sides;
    across their heads a bar with a curl at each end, rising to a crest over the middle; and from
    under the bar between the legs a V, its arms thinner than the legs, coming to a point well above
    the baseline. Under the bar, between the V's arms, a counter like a teardrop. Built symmetric about
    its axis (Pugin's is nearly so)."""
    k = p.fam("curl")
    ax = p.x("axis_x", 257, 15)
    # the half, clockwise from the V's point on the axis: up the V's left arm to the crotch, down the
    # leg's inside, round the foot, up the leg's outside to the top-left curl, along the bar to the crest
    Vp = np.array([ax, p.x("point.y", 354, 20)])
    Cr = np.array([p.x("crotch.x", 182, 15), p.x("crotch.y", 166, 25)])
    Rs, hR = edge_point(p, "leg.inner", (161, 365), 90, upright=True)      # the leg's inside, at its leftmost
    Ls, hL = edge_point(p, "leg.outer", (96, 360), 282)                     # its outside, going up
    Lr = np.array([p.x("leg.outer_right_x", 119.5, 12), p.x("leg.outer_right_y", 125, 40)])
    O_tl = np.array([p.x("top.left_x", 97, 20), p.x("top.y", 24, 12)])
    segs, names, neck, arrive = K.curl(O_tl, "tl", k, p.ang("top.neck", 0, 0, 40), place="curl, top-left")
    Dl = np.array([p.x("top.low_x", 170, 30), p.x("top.low_y", 37, 12)])
    Ct = np.array([ax, p.x("top.crest_y", 24, 12)])
    half = [(cubic(Vp, p.ang("point.out", 250, 230, 270), Cr, p.ang("crotch.in", 250, 225, 275), p.t("v_arm.t1"), p.t("v_arm.t2")), "V", "V: point"),
            (cubic(Cr, p.ang("crotch.out", 96, 80, 120), Rs, hR, p.t("leg.t1"), p.t("leg.t2")), "leg", "crotch, left")]
    half += cap_bottom(p, K, k, "foot", Rs, hR, Ls, hL, {"y": 446, "left": 66, "right": 191})
    half += [(cubic(Ls, hL, Lr, N, p.t("leg.t3"), p.t("leg.t4")), "leg", "leg: outside"),
             (cubic(Lr, N, neck, arrive, p.t("leg.t5"), p.t("leg.t6")), "flare", "leg: outside, rightmost")]
    half += [(s, "curl", nm) for s, nm in zip(segs, names)]
    half += [(cubic(O_tl, E, Dl, E, p.t("top.t1"), p.t("top.t2")), "top bar", "curl, top-left: outer"),
             (cubic(Dl, E, Ct, E, p.t("top.t3"), p.t("top.t4")), "top bar", "top bar: low point")]
    # the counter, anticlockwise from its top on the axis to its point
    Cc = np.array([ax, p.x("counter.top_y", 44, 12)])
    Cl = np.array([p.x("counter.left_x", 199, 15), p.x("counter.left_y", 82, 30)])
    Cb = np.array([ax, p.x("counter.point_y", 267, 20)])
    chalf = [(cubic(Cc, W, Cl, S, p.t("counter.t1"), p.t("counter.t2")), "counter", "counter: top"),
             (cubic(Cl, S, Cb, p.ang("counter.point_in", 70, 45, 88), p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: left")]
    return {"contours": [mirror_half(half, ax, "top bar: crest"), mirror_half(chalf, ax, "counter: point")],
            "halves": [half, chalf], "axis": ax, "baseline": p.x("foot.y", 446, 15)}


def M_1(p, K):
    """The uncial M: two round bowls side by side, joined by a straight stem between their counters,
    standing on a thin bar that runs under both with a curl at each end. Each bowl's outside comes
    down into the bar at a notch inside its curl; the bar's underside rises between the curls. On
    top, the stem rises between the bowls to a pointed peak, with a notch each side where a bowl
    meets it. The counters are tall ovals, narrowing at the foot toward the outside. Built symmetric
    about its axis (Pugin's is nearly so)."""
    k = p.fam("curl")
    ax = p.x("axis_x", 230, 15)
    # the half, clockwise from the bar's underside on the axis to the peak
    Bh = np.array([ax, p.x("bar.high_y", 434, 12)])
    O_bl = np.array([p.x("bar.left_x", 60, 20), p.x("bar.y", 452, 12)])
    segs, names, neck, leave = K.curl(O_bl, "bl", k, p.ang("bar.neck", 0, 0, 40), place="curl, bottom-left")
    Np = np.array([p.x("pocket.x", 88, 15), p.x("pocket.y", 422, 12)])
    Bl = np.array([p.x("bowl.left_x", 18.5, 15), p.x("bowl.left_y", 215, 40)])
    Bt = np.array([p.x("bowl.top_x", 140, 30), p.x("bowl.top_y", 27, 12)])
    Nt = np.array([p.x("notch.x", 201, 15), p.x("notch.y", 50, 15)])
    Pk = np.array([ax, p.x("peak.y", 24, 12)])
    half = [(cubic(Bh, W, O_bl, W, p.t("bar.t1"), p.t("bar.t2")), "bar", "bar: underside, highest")]
    half += [(s, "curl", nm) for s, nm in zip(segs, names)]
    half += [(cubic(neck, leave, Np, p.ang("pocket.in", 340, 300, 380), p.t("pocket.t1"), p.t("pocket.t2")), "bar", "curl, bottom-left: neck"),
             (cubic(Np, p.ang("pocket.out", 246, 220, 270), Bl, N, p.t("bowl.t1"), p.t("bowl.t2")), "bowl", "pocket"),
             (cubic(Bl, N, Bt, E, p.t("bowl.t3"), p.t("bowl.t4")), "bowl", "bowl: leftmost"),
             (cubic(Bt, E, Nt, p.ang("notch.in", 50, 20, 80), p.t("bowl.t5"), p.t("bowl.t6")), "bowl", "bowl: top"),
             (cubic(Nt, p.ang("notch.out", 305, 270, 340), Pk, p.ang("peak.in", 335, 290, 359), p.t("peak.t1"), p.t("peak.t2")), "peak", "notch, left")]
    counter = [(q, l, nm.replace("counter", "left counter")) for q, l, nm in
               oval_counter(p, {"top": (152, 52), "left": (93, 270), "bottom": (119, 412), "right": (201, 270)})]
    return {"contours": [mirror_half(half, ax, "peak"), counter, mirror_copy(counter, ax)], "halves": [half, None, None],
            "axis": ax, "baseline": O_bl[1]}


def _named(run, name):
    """A run whose first node is given a name (a run that starts where a cut made a new node)."""
    return [(run[0][0], run[0][1], name)] + run[1:] if run else run


def W_1(p, K):
    """The W of two interlaced Vs. The left V is drawn as the V is, its left arm thick and its right
    arm thin, each headed by a bar with a curl at both ends; the right V is its mirror image, and the
    two thin arms cross on the axis. On each side the thick arm's bar runs into the thin arm's, the
    curls between them overlapping like two balls close together. Under the bars, between the thick
    arm and the crossing arms, is a counter each side; between the thin arms' bars the space opens to
    the top, and under the crossing to the foot. With eight curls along its top line where a letter
    has two or four, Pugin drew them smaller: they take their own size, fitted to this letter."""
    k = p.length("curl", 0.82, 0.6, 1.0)
    ball = -K.curl_nodes["back"][0] * k            # how far a curl's ball reaches past its outer node
    ax = p.x("axis_x", 240, 15)
    mx = lambda q: np.asarray(q, float) * [-1, 1] + [2 * ax, 0]
    Pt = np.array([p.x("point.x", 170, 15), p.x("point.y", 437, 12)])
    Cr = np.array([p.x("crotch.x", 197, 15), p.x("crotch.y", 293, 25)])
    y = p.x("bars.y", 27, 12)
    # the bars, placed inward from the axis: the thin bar's last curl keeps clear of its mirror image,
    # the bar has some length, and its first curl overlaps the thick bar's last, their crowns far
    # enough apart that they read as two balls (and the balls always meet)
    crown = -K.curl_nodes["crown"][0] * k
    tr = ax - ball - p.length("thin_bar.clear_of_axis", 12, 3, 40)
    tl = tr - p.length("thin_bar.length", 14, 4, 60)
    xr = tl - 2 * crown - k * p.length("bars.crowns_apart", 28, 14, 34)
    xl = p.x("thick_bar.left_x", 32, 25)
    # the thick arm and its bar, as the V's left arm
    L1, hL1 = edge_point(p, "thick_arm.outer", (52, 110), 247)
    # its bar's last curl sits over the arm's inside, which runs straight up into the curl's neck
    R1, hR1 = edge_point(p, "thick_arm.inner", (124, 90), 72)
    thick = cap_top(p, K, k, "thick bar", L1, hL1, R1, hR1, {}, at=(xl, xr, y), neck_r=(100, 0, 125))
    thick_out = cubic(Pt, p.ang("point.out", 247, 230, 265), L1, hL1, p.t("thick_arm.t1"), p.t("thick_arm.t2"))
    thick_in = cubic(R1, hR1, Cr, p.ang("crotch.in", 70, 50, 90), p.t("thick_arm.t3"), p.t("thick_arm.t4"))
    # the thin arm: the right V's left arm, from its bar down across the axis to that V's point (its
    # outside) and its crotch (its inside); the left V's thin arm is its mirror image
    Ls, hLs = edge_point(p, "thin_arm.outer", (172, 75), 248)
    Rs, hRs = edge_point(p, "thin_arm.inner", (198, 75), 70, upright=True)
    thin = cap_top(p, K, k, "thin bar", Ls, hLs, Rs, hRs, {}, at=(tl, tr, y))
    Eo = cubic(mx(Pt), p.ang("thin_arm.point_out", 248, 230, 265), Ls, hLs, p.t("thin_arm.t1"), p.t("thin_arm.t2"))
    Ei = cubic(Rs, hRs, mx(Cr), p.ang("thin_arm.crotch_in", 70, 50, 90), p.t("thin_arm.t3"), p.t("thin_arm.t4"))
    Vout, Vin = mx(Eo)[::-1], mx(Ei)[::-1]        # the left V's thin arm: outside down to the point, inside up from the crotch
    # the crossing: the crotches over and under it are on the axis; the counter's corner is where the
    # left V's thin arm's inside meets the right V's thin arm's outside
    _, under = cut([(Vout, "thin arm", None)], 0, cross_x(Vout, ax))
    over, _ = cut([(Ei, "thin arm", "thin bar: right edge, top")], 0, cross_x(Ei, ax))
    hit = crossings([Vin], [Eo])
    ta, tb = (hit[0][1], hit[0][3]) if hit else (0.5, 0.5)
    vin, _ = cut([(Vin, "thin arm", "crotch")], 0, ta)
    _, eo = cut([(Eo, "thin arm", None)], 0, tb)
    # where the two bars meet, the thick bar's last curl and the thin bar's first cross twice: above,
    # on the outline, and below, on the counter
    t_curl, f_curl = thick[6:9], thin[1:4]
    hits = sorted(crossings([q for q, _, _ in t_curl], [q for q, _, _ in f_curl]), key=lambda h: h[4][1])
    if len(hits) >= 2:
        (i1, a1, j1, b1, _), (i2, a2, j2, b2, _) = hits[0], hits[-1]
        top = cut(t_curl, i1, a1)[0] + _named(cut(f_curl, j1, b1)[1], "bars: notch, top")
        under_bars = cut(f_curl, j2, b2)[0] + _named(cut(t_curl, i2, a2)[1], "bars: notch, underneath")
    else:      # the balls don't meet: bridge them at their backs (a fit never ends here)
        top = t_curl[:1] + [(line(t_curl[0][0][3], f_curl[2][0][0]), "bar", "bars: bridge")] + f_curl[2:]
        under_bars = f_curl[:2] + [(line(f_curl[1][0][3], t_curl[1][0][0]), "bar", "bars: bridge, underneath")] + t_curl[1:]
    half = _named(under, "crossing: under") + [(thick_out, "thick arm", "point")] + thick[:6] + top + thin[4:] + over
    counter = (vin + _named(eo, "crossing: corner") + thin[:1] + under_bars + thick[9:] +
               [(thick_in, "thick arm", "thick bar: right edge, top")])
    return {"contours": [mirror_half(half, ax, "crossing: over"), counter, mirror_copy(counter, ax)],
            "halves": [half, None, None], "axis": ax, "baseline": Pt[1]}


def hooked_foot(p, pre, S2, i):
    """The foot of a straight stem that flicks out into a pointed hook, as the U's does, with a small
    round heel on its left, parted from the hook below by a notch. Clockwise from S2, the foot of the
    stem's right side: the hook's inside dips and rises to its tip, its underside comes down to its
    lowest point and up to the notch, and the heel's underside runs round to its leftmost point,
    where the run ends. `pre` names its parts; its measurements go under the same name in snake case."""
    m = pre.replace(" ", "_")
    Hl = np.array([p.x(f"{m}.hook.low_x", i["low"][0], 15), p.x(f"{m}.hook.low_y", i["low"][1], 10)])
    Tip = np.array([p.x(f"{m}.hook.x", i["tip"][0], 15), p.x(f"{m}.hook.y", i["tip"][1], 12)])
    Hb = np.array([p.x(f"{m}.hook.bottom_x", i["bottom"][0], 20), p.x(f"{m}.hook.bottom_y", i["bottom"][1], 10)])
    Nb = np.array([p.x(f"{m}.notch.x", i["notch"][0], 15), p.x(f"{m}.notch.y", i["notch"][1], 12)])
    Hh = np.array([p.x(f"{m}.heel.bottom_x", i["heel"][0], 15), p.x(f"{m}.heel.bottom_y", i["heel"][1], 10)])
    Hx = np.array([p.x(f"{m}.heel.left_x", i["heel_left"][0], 15), p.x(f"{m}.heel.left_y", i["heel_left"][1], 12)])
    run = [(cubic(S2, S, Hl, E, p.t(f"{m}.hook.t1"), p.t(f"{m}.hook.t2")), "hook", f"{pre}: right, foot of straight"),
           (cubic(Hl, E, Tip, p.ang(f"{m}.hook.in", 315, 280, 350), p.t(f"{m}.hook.t3"), p.t(f"{m}.hook.t4")), "hook", f"{pre}, hook: inside, lowest"),
           (cubic(Tip, p.ang(f"{m}.hook.out", 120, 90, 160), Hb, W, p.t(f"{m}.hook.t5"), p.t(f"{m}.hook.t6")), "hook", f"{pre}, hook: tip"),
           (cubic(Hb, W, Nb, p.ang(f"{m}.notch.in", 225, 195, 255), p.t(f"{m}.hook.t7"), p.t(f"{m}.hook.t8")), "hook", f"{pre}, hook: lowest"),
           (cubic(Nb, p.ang(f"{m}.notch.out", 150, 115, 180), Hh, W, p.t(f"{m}.heel.t1"), p.t(f"{m}.heel.t2")), "heel", f"{pre}: notch"),
           (cubic(Hh, W, Hx, N, p.t(f"{m}.heel.t3"), p.t(f"{m}.heel.t4")), "heel", f"{pre}, heel: lowest")]
    return run, Hx


def W_2(p, K):
    """The W as a rounded double U: a top bar the width of the letter with a curl at each end, and
    under it four strokes. The first two are bowls: the outer one comes down the left from a notch
    under the first curl, the inner one from under the bar, and each sweeps round at its foot into a
    pointed tail tucked under the next stroke. The last two are straight stems, each flicking out at
    its foot into a pointed hook, as the U's stem does, with a small round heel on its left, parted
    from the hook below by a notch. The inner bowl meets the first stem in a notch under the bar; the
    spaces between the strokes open at the foot."""
    k = p.fam("curl")
    A0 = np.array([p.x("outer_bowl.left_x", 24.5, 15), p.x("outer_bowl.left_y", 270, 40)])
    Nt = np.array([p.x("notch.x", 113, 15), p.x("notch.y", 48, 12)])
    y = p.x("top.y", 27, 12)
    O_tl = np.array([p.x("top.left_x", 97, 20), y])
    O_tr = np.array([p.x("top.right_x", 432, 20), y])
    Tlow = np.array([p.x("top.low_x", 260, 60), y + p.length("top.low_dy", 3, 0, 20)])
    segs_l, names_l, neck_l, arrive_l = K.curl(O_tl, "tl", k, p.ang("top.neck_l", 0, 0, 40), place="curl, top-left")
    segs_r, names_r, neck_r, leave_r = K.curl(O_tr, "tr", k, p.ang("top.neck_r", 0, 0, 40), place="curl, top-right")
    run = [(cubic(A0, N, Nt, p.ang("notch.in", 305, 270, 340), p.t("outer_bowl.t1"), p.t("outer_bowl.t2")), "outer bowl", "outer bowl: leftmost"),
           (cubic(Nt, p.ang("notch.out", 185, 160, 215), neck_l, arrive_l, p.t("top.t5"), p.t("top.t6")), "top bar", "notch")]
    run += [(s, "curl", nm) for s, nm in zip(segs_l, names_l)]
    run += [(cubic(O_tl, E, Tlow, E, p.t("top.t1"), p.t("top.t2")), "top bar", "curl, top-left: outer"),
            (cubic(Tlow, E, O_tr, E, p.t("top.t3"), p.t("top.t4")), "top bar", "top bar: low point")]
    run += [(s, "curl", nm) for s, nm in zip(segs_r, names_r)]
    # the last stem, down its right side to its hook, round its heel and up its left side
    xd, xdl = p.x("last_stem.right_x", 422, 12), p.x("last_stem.left_x", 361.5, 12)
    D1 = np.array([xd, p.x("last_stem.head_y", 100, 40)])
    D2 = np.array([xd, p.x("last_stem.foot_y", 360, 40)])
    run += [(cubic(neck_r, leave_r, D1, S, p.t("last_stem.t1"), p.t("last_stem.t2")), "flare", "curl, top-right: neck"),
            (line(D1, D2), "last stem", "last stem: right, top of straight")]
    foot, Hx = hooked_foot(p, "last stem", D2, {"low": (445, 413), "tip": (459, 407), "bottom": (434, 434), "notch": (381, 394),
                                                 "heel": (361, 408), "heel_left": (340.5, 389)})
    run += foot
    D3 = np.array([xdl, p.x("last_stem.left_foot_y", 330, 30)])
    D4 = np.array([xdl, p.x("last_stem.left_head_y", 62, 15)])
    # the space between the stems, closed at the top by the bar's underside
    Gt = np.array([p.x("gap.x", 343, 12), p.x("gap.y", 47, 10)])
    xc, xcl = p.x("first_stem.right_x", 324.5, 12), p.x("first_stem.left_x", 269.7, 12)
    C1 = np.array([xc, p.x("first_stem.head_y", 62, 15)])
    C2 = np.array([xc, p.x("first_stem.foot_y", 350, 40)])
    run += [(cubic(Hx, N, D3, N, p.t("last_stem.t3"), p.t("last_stem.t4")), "heel", "last stem, heel: leftmost"),
            (line(D3, D4), "last stem", "last stem: left, foot of straight"),
            (cubic(D4, N, Gt, W, p.t("gap.t1"), p.t("gap.t2")), "top bar", "last stem: left, top of straight"),
            (cubic(Gt, W, C1, S, p.t("gap.t3"), p.t("gap.t4")), "top bar", "between the stems: top"),
            (line(C1, C2), "first stem", "first stem: right, top of straight")]
    foot, Hx = hooked_foot(p, "first stem", C2, {"low": (362, 413), "tip": (378, 408), "bottom": (343, 434), "notch": (289, 391),
                                                  "heel": (256, 408), "heel_left": (231, 391)})
    run += foot
    C3 = np.array([xcl, p.x("first_stem.left_foot_y", 285, 30)])
    Nc = np.array([xcl, p.x("notch_b.y", 77, 15)])    # where the inner bowl's right side meets the stem
    run += [(cubic(Hx, N, C3, N, p.t("first_stem.t3"), p.t("first_stem.t4")), "heel", "first stem, heel: leftmost"),
            (line(C3, Nc), "first stem", "first stem: left, foot of straight")]
    # the inner bowl: down its right side and round into its tail, back under it and up its left side
    Br = np.array([p.x("inner_bowl.inside_x", 214.5, 15), p.x("inner_bowl.inside_y", 320, 40)])
    Tb = np.array([p.x("inner_bowl.tail_x", 311, 15), p.x("inner_bowl.tail_y", 426, 10)])
    Bb = np.array([p.x("inner_bowl.bottom_x", 272, 25), p.x("inner_bowl.bottom_y", 436, 10)])
    Bl = np.array([p.x("inner_bowl.left_x", 138.5, 15), p.x("inner_bowl.left_y", 285, 40)])
    yg = p.x("gap_b.y", 47, 10)
    Gr = np.array([p.x("gap_b.right_x", 239, 12), yg])
    Gl = np.array([p.x("gap_b.left_x", 169, 12), yg])
    run += [(cubic(Nc, p.ang("notch_b.out", 112, 95, 140), Br, S, p.t("inner_bowl.t1"), p.t("inner_bowl.t2")), "inner bowl", "notch, between the inner bowl and the first stem"),
            (cubic(Br, S, Tb, p.ang("inner_bowl.tail_in", 25, 0, 60), p.t("inner_bowl.t3"), p.t("inner_bowl.t4")), "inner bowl", "inner bowl: inside, leftmost"),
            (cubic(Tb, p.ang("inner_bowl.tail_out", 160, 130, 190), Bb, W, p.t("inner_bowl.t5"), p.t("inner_bowl.t6")), "inner bowl", "inner bowl: tail"),
            (cubic(Bb, W, Bl, N, p.t("inner_bowl.t7"), p.t("inner_bowl.t8")), "inner bowl", "inner bowl: lowest"),
            (cubic(Bl, N, Gr, p.ang("gap_b.right_in", 293, 270, 320), p.t("inner_bowl.t9"), p.t("inner_bowl.t10")), "inner bowl", "inner bowl: leftmost"),
            (line(Gr, Gl), "top bar", "between the bowls: top, right")]
    # the outer bowl: down its inside and round into its tail, back under it and up to the start
    Ai = np.array([p.x("outer_bowl.inside_x", 109.5, 15), p.x("outer_bowl.inside_y", 265, 40)])
    Ta = np.array([p.x("outer_bowl.tail_x", 208, 15), p.x("outer_bowl.tail_y", 426, 10)])
    Ab = np.array([p.x("outer_bowl.bottom_x", 172, 25), p.x("outer_bowl.bottom_y", 434, 10)])
    run += [(cubic(Gl, p.ang("gap_b.left_out", 120, 95, 145), Ai, S, p.t("outer_bowl.t3"), p.t("outer_bowl.t4")), "outer bowl", "between the bowls: top, left"),
            (cubic(Ai, S, Ta, p.ang("outer_bowl.tail_in", 30, 0, 60), p.t("outer_bowl.t5"), p.t("outer_bowl.t6")), "outer bowl", "outer bowl: inside, leftmost"),
            (cubic(Ta, p.ang("outer_bowl.tail_out", 155, 125, 185), Ab, W, p.t("outer_bowl.t7"), p.t("outer_bowl.t8")), "outer bowl", "outer bowl: tail"),
            (cubic(Ab, W, A0, N, p.t("outer_bowl.t9"), p.t("outer_bowl.t10")), "outer bowl", "outer bowl: lowest")]
    return {"contours": [run], "baseline": Ab[1]}


def _turn(q, c, n):
    """Points turned about c by n quarter turns, clockwise on the page."""
    d = np.asarray(q, float) - c
    for _ in range(n % 4):
        d = np.column_stack([-d[:, 1], d[:, 0]])
    return d + c


def cross(p, K):
    """The cross: four equal arms, narrow where they meet and widening to their ends, each end a bar
    with a curl at both corners rolling back toward the centre, its edge dipping a little between
    them. The arms' sides are hollow curves meeting at sharp inside corners. It is built on half of one
    arm, mirrored and turned through the four quarters, so it has the square's symmetry (Pugin's,
    drawn by hand, nearly has it). Its curls take their own size."""
    c = np.array([p.x("centre_x", 220, 15), p.x("centre_y", 243, 15)])
    k = p.length("curl", 0.95, 0.6, 1.5)
    X = c + p.length("crotch", 36, 15, 60) / math.sqrt(2) * np.array([-1.0, -1.0])
    O = c + np.array([-p.length("end.half_width", 96, 60, 140), -p.length("end.reach", 216, 180, 250)])
    segs, names, neck, arrive = K.curl(O, "tl", k, p.ang("end.neck", 0, 0, 40), place="curl, top arm, left")
    Ce = np.array([c[0], O[1] + p.length("end.dip", 18, 0, 35)])
    # an eighth: from the crotch up the arm's side, round the curl, and along the end to the axis
    eighth = [(cubic(X, p.ang("side.leave", 268, 240, 290), neck, arrive, p.t("side.t1"), p.t("side.t2")), "arm", "crotch, top arm, left")]
    eighth += [(s, "curl", nm) for s, nm in zip(segs, names)]
    eighth.append((cubic(O, E, Ce, E, p.t("end.t1"), p.t("end.t2")), "arm end", "curl, top arm, left: outer"))
    quarter = mirror_half(eighth, c[0], "top arm: end, centre")
    turn = lambda run, n, arm: [(_turn(q, c, n), l, nm.replace("top arm", arm)) for q, l, nm in run]
    m = len(eighth)
    half = turn(quarter[m:], 2, "bottom arm") + turn(quarter, 3, "left arm") + quarter[:m]
    return {"contours": [mirror_half(half, c[0], "top arm: end, centre")], "half": half, "axis": c[0], "baseline": 2 * c[1] - O[1]}


def ornament_dots(p, K):
    """Seventeen round dots: four squares of four about a dot in the middle. Pugin set his by hand;
    here they are all one size, on a square grid. It stands centred on half the cap height, as
    Pugin's does among the letters of its row."""
    c = np.array([p.x("centre_x", 167, 12), p.x("centre_y", 165, 12)])
    r = p.length("r", 20.8, 14, 28)
    a = p.length("pitch", 55.5, 40, 70)          # between the dots of a square
    b = p.length("spread", 185, 150, 220)        # between the squares' centres
    spots = [("middle", c)]
    for sy, row in ((-1, "upper"), (1, "lower")):
        for sx, col in ((-1, "left"), (1, "right")):
            for iy in (-1, 1):
                for ix in (-1, 1):
                    at = c + np.array([sx * b / 2 + ix * a / 2, sy * b / 2 + iy * a / 2])
                    spots.append((f"{row} {col} square, {'top' if iy < 0 else 'bottom'} {'left' if ix < 0 else 'right'}", at))
    contours = [[(s, "dot", f"dot, {nm}: {e}") for s, e in zip(arc(o, r, 0, 360), ("rightmost", "lowest", "leftmost", "highest"))]
                for nm, o in spots]
    return {"contours": contours, "baseline": c[1] + CAP_PX / 2}


LETTERS = {"I": I, "T.1": T_1, "L": L, "F": F, "E": E_, "H": H, "K": K_, "C": C, "O": O, "D": D, "Q": Q,
           "P": P, "R": R, "B": B, "G": G_, "V": V, "X": X, "Z": Z, "N": N_, "Y": Y, "U": U, "A": A,
           "S": S_, "T.2": T_2, "Y.2": Y_2, "M.2": M_2, "M.1": M_1, "W.1": W_1, "W.2": W_2,
           "cross": cross, "ornament.dots": ornament_dots}
