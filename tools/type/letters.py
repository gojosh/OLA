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

import numpy as np

from construct import E, N, ORIENT, S, W, arc, cubic, line, mirror_half, trefoil, two_lobe


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
    """The two-lobe terminal at the foot of a stroke that sweeps right (H, K). The stroke's outside
    comes down to the pocket's leftmost point Pl, runs along the pocket's floor into a sharp neck
    under the first lobe, goes over both lobes, and leaves the second at a corner onto the
    stroke's underside. Returns the segments and that last corner."""
    r = p.fam("two_lobe_r")
    c1 = np.array([p.x("terminal.x", i["x"], 20), p.x("terminal.y", i["y"], 20)])
    segs, names, neck, J = two_lobe(c1, r, r * p.fam("two_lobe_spread"), p.fam("two_lobe_angle"),
                                    p.ang("terminal.neck_at", 95, 60, 150), p.ang("terminal.join_at", 145, 100, 175),
                                    place="two-lobe terminal")
    out = [(cubic(Pl, S, neck, p.ang("terminal.neck_in", 10, 0, 40), p.t("pocket.t1"), p.t("pocket.t2")), "stroke", "pocket: leftmost")]
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
    as it rises and turns over into a curl. Pugin's curl here is lumpy, as if drawn twice; the
    construction uses the alphabet's curl."""
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
    Ot = np.array([p.x("arm.curl_x", 388, 20), p.x("arm.curl_y", 53, 20)])
    run.append((cubic(A1, ha, Ot, E, p.t("arm.inner_t1"), p.t("arm.inner_t2")), "arm", "arm: inside"))
    segs, names, neck, leave = K.curl(Ot, "tr", k, p.ang("arm.neck_deg", 30, -20, 80), place="curl, top of arm")
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    A2 = np.array([p.x("arm.outer_x", 365, 20), p.x("arm.outer_y", 210, 60)])
    run.append((cubic(neck, leave, A2, S, p.t("arm.under_t1"), p.t("arm.under_t2")), "arm", "curl, top of arm: neck"))
    # the foot of the arm comes to a rounded point: a small arc, met tangentially by the arm's
    # outside and left the same way by the base's underside
    tc = np.array([p.x("tip.x", 393, 15), p.x("tip.y", 446, 15)])
    tr = p.x("tip.r", 6, 4)
    a0, a1 = p.ang("tip.from", -15, -60, 0), p.ang("tip.to", 105, 90, 160)
    tip = arc(tc, tr, a0, a1)
    run.append((cubic(A2, S, tip[0][0], a0 + 90, p.t("arm.outer_t1"), p.t("arm.outer_t2")), "arm", "arm: outside"))
    run += [(s, "arm", nm) for s, nm in zip(tip, ["arm: rounded point"] + ["arm: rounded point, extreme"] * (len(tip) - 1))]
    Bc = np.array([p.x("base.under_x", 245), p.x("base.under_y", 432, 15)])
    run.append((cubic(tip[-1][3], a1 + 90, Bc, W, p.t("base.under_t1"), p.t("base.under_t2")), "base", "base: foot of the arm"))
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
    TR = np.array([p.x("top.corner_x", 397, 15), p.x("top.corner_y", 24, 15)])
    Tlow = np.array([p.x("top.low_x", 220, 90), p.x("top.low_y", 32, 15)])
    run.append((cubic(Otl, E, Tlow, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "curl, top-left: outer"))
    run.append((cubic(Tlow, E, TR, p.ang("top.corner_in", 355, 320, 360), p.t("top.edge_t3"), p.t("top.edge_t4")), "top bar", "top bar: low point"))
    # the stroke's inside leaves the trefoil's lower lobe no further round than the lobe's leftmost
    # point, so the edge climbs from there without swinging out and back
    axis = p.ang("trefoil.axis", 45, 0, 90)
    tsegs, tnames, J1, J2 = trefoil(np.array([p.x("trefoil.x", 388, 20), p.x("trefoil.y", 330, 20)]), axis,
                                    p.fam("trefoil_r"), p.fam("trefoil_d"), p.ang("trefoil.enter", -100, -175, -5),
                                    p.ang("trefoil.leave_at", 175, 120, 180) - (axis + 90))
    Sw = np.array([p.x("stroke.waist_x", 368, 15), p.x("stroke.waist_y", 270, 40)])
    run.append((cubic(TR, p.ang("stroke.top_heading", 95, 90, 120), Sw, S, p.t("stroke.t1"), p.t("stroke.t2")), "right stroke", "top bar: square end"))
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
    """The O: an oval ring, heavy at the sides and light at top and bottom, with a round ball hanging
    into the counter from the top and one rising from the bottom. Symmetric about its axis; Pugin's
    lower ball sits off to the left, the construction centres it."""
    ax = p.x("axis_x", 225.5, 15)
    r = p.fam("ball_r")
    # the outline, from the bottom on the axis, clockwise up the left to the top
    Ob = np.array([ax, p.x("outer.bottom_y", 451, 12)])
    Ol = np.array([p.x("outer.left_x", 25, 15), p.x("outer.left_y", 240, 40)])
    Ot = np.array([ax, p.x("outer.top_y", 24, 12)])
    outer = [(cubic(Ob, W, Ol, N, p.t("outer.t1"), p.t("outer.t2")), "ring", "outline: bottom"),
             (cubic(Ol, N, Ot, E, p.t("outer.t3"), p.t("outer.t4")), "ring", "outline: left")]
    # the counter, anticlockwise from the top ball's lowest point: round the ball to where it meets
    # the counter's top, down the left side, along the bottom to the lower ball, over its top
    ct = np.array([ax, p.x("ball_top.y", 54, 15)])
    a1 = p.ang("ball_top.meets_at", 215, 180, 265)
    top_ball = arc(ct, r, 90, a1)
    Cl = np.array([p.x("counter.left_x", 120, 15), p.x("counter.left_y", 240, 40)])
    cb = np.array([ax, p.x("ball_bottom.y", 402, 15)])
    a2 = p.ang("ball_bottom.meets_at", 145, 95, 180)
    q2 = cb + r * np.array([np.cos(np.radians(a2)), np.sin(np.radians(a2))])
    bottom_ball = arc(cb, r, a2, 270)
    counter = [(s, "ball", "ball, top: lowest" if j == 0 else "ball, top") for j, s in enumerate(top_ball)]
    counter.append((cubic(top_ball[-1][3], p.ang("counter.top_out", 150, 95, 180), Cl, S, p.t("counter.t1"), p.t("counter.t2")),
                    "counter", "ball, top: meets the ring"))
    # the floor runs down to the ball and meets it at its lowest point, so it may not rise on the way
    counter.append((cubic(Cl, S, q2, p.ang("counter.bottom_in", 20, 0, 70), p.t("counter.t3"), p.t("counter.t4")), "counter", "counter: left"))
    counter += [(s, "ball", "ball, bottom: meets the ring" if j == 0 else "ball, bottom") for j, s in enumerate(bottom_ball)]
    base = Ob[1]
    halves = [(outer, "outline: top"), (counter, "ball, bottom: highest")]
    return {"contours": [mirror_half(h, ax, e) for h, e in halves], "halves": [h for h, _ in halves], "axis": ax, "baseline": base}


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
    foot_run, J = lobed_foot(p, Pl, {"x": 383, "y": 388})
    run += foot_run
    # along the foot's underside, up the shoulder's inside, over the arch and down to the stem
    FB = np.array([p.x("foot.bottom_x", 362, 25), p.x("foot.bottom_y", 447, 10)])
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
    TR = np.array([p.x("top.corner_x", 402, 15), p.x("top.corner_y", 28, 12)])
    Tlow = np.array([p.x("top.low_x", 240, 80), p.x("top.low_y", 32, 12)])
    run.append((cubic(Otl, E, Tlow, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "curl, top-left: outer"))
    run.append((cubic(Tlow, E, TR, p.ang("top.corner_in", 355, 320, 360), p.t("top.edge_t3"), p.t("top.edge_t4")), "top bar", "top bar: low point"))
    # down the arm's outside to the crotch, then out along the leg
    Ar = np.array([p.x("arm.right_x", 403, 15), p.x("arm.right_y", 65, 25)])
    run.append((cubic(TR, p.ang("arm.top_heading", 85, 60, 90), Ar, S, p.t("arm.t1"), p.t("arm.t2")), "arm", "top bar: square end"))
    Cr = np.array([p.x("crotch.x", 262, 15), p.x("crotch.y", 226, 15)])
    run.append((cubic(Ar, S, Cr, p.ang("arm.crotch_in", 135, 100, 170), p.t("arm.t3"), p.t("arm.t4")), "arm", "arm: outside, rightmost"))
    Lt = np.array([p.x("leg.top_x", 305, 30), p.x("leg.top_y", 218, 12)])
    run.append((cubic(Cr, p.ang("leg.spring", 340, 300, 360), Lt, E, p.t("leg.t1"), p.t("leg.t2")), "leg", "crotch"))
    Lr = np.array([p.x("leg.right_x", 391, 15), p.x("leg.right_y", 330, 40)])
    run.append((cubic(Lt, E, Lr, S, p.t("leg.t3"), p.t("leg.t4")), "leg", "leg: top"))
    Pl = np.array([p.x("pocket.x", 384, 15), p.x("pocket.y", 400, 20)])
    run.append((cubic(Lr, S, Pl, S, p.t("leg.t5"), p.t("leg.t6")), "leg", "leg: outside, rightmost"))
    foot_run, J = lobed_foot(p, Pl, {"x": 418, "y": 410})
    run += foot_run
    # along the foot's underside and up the leg's inside to the lower counter's point
    FB = np.array([p.x("foot.bottom_x", 395, 25), p.x("foot.bottom_y", 448, 10)])
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
    """The O's bowl, with a ball hanging into the counter from the top and one sitting on its floor.
    At the bottom right the bowl's base runs on past the bowl to a rounded end, and a flag rises
    from it, parted from the bowl by a pointed notch, to a curl at its head rolling out to the right."""
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
    O_f = np.array([p.x("flag.curl_x", 375, 20), p.x("flag.curl_y", 338, 20)])
    run.append((cubic(Nq, p.ang("notch.out", 315, 280, 350), O_f, N, p.t("flag.t1"), p.t("flag.t2")), "flag", "notch"))
    segs, names, neck, leave = K.curl(O_f, "head-right", k, p.ang("flag.neck_deg", 5, -20, 40), place="curl, head of the flag")
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    Fr = np.array([p.x("flag.right_x", 398, 15), p.x("flag.right_y", 405, 20)])
    run.append((cubic(neck, leave, Fr, S, p.t("flag.t3"), p.t("flag.t4")), "flag", "curl, head of the flag: neck"))
    ce = np.array([p.x("end.x", 418, 12), p.x("end.y", 432, 10)])
    re_ = p.length("end.r", 13, 6, 20)
    end = arc(ce, re_, 270, 450)
    run.append((cubic(Fr, S, end[0][0], E, p.t("flag.t5"), p.t("flag.t6")), "flag", "flag: outside, narrowest"))
    run += [(s_, "base", nm) for s_, nm in zip(end, ["base: end, top", "base: end"])]
    Bb = np.array([p.x("outer.bottom_x", 215, 40), p.x("outer.bottom_y", 452, 10)])
    run.append((cubic(end[-1][3], W, Bb, W, p.t("base.t1"), p.t("base.t2")), "base", "base: end, bottom"))
    run.append((cubic(Bb, W, Ol, N, p.t("outer.t7"), p.t("outer.t8")), "bowl", "bowl: bottom"))
    # the counter, anticlockwise from where the top ball meets the counter's right wall
    ct = np.array([bx, p.x("ball_top.y", 68, 15)])
    top = arc(ct, r, p.ang("ball_top.meets_right", 320, 280, 355), 360 + p.ang("ball_top.meets_left", 220, 185, 260))
    Cl = np.array([p.x("counter.left_x", 126, 15), p.x("counter.left_y", 240, 40)])
    cf = np.array([bx, p.x("ball_floor.y", 381, 15)])
    floor = arc(cf, r, p.ang("ball_floor.meets_left", 160, 95, 180), 360 + p.ang("ball_floor.meets_right", 30, 0, 85))
    Cr = np.array([p.x("counter.right_x", 290, 15), p.x("counter.right_y", 245, 40)])
    counter = [(s_, "ball", "ball, top: meets the right wall" if j == 0 else "ball, top") for j, s_ in enumerate(top)]
    counter.append((cubic(top[-1][3], p.ang("counter.top_out", 150, 95, 180), Cl, S, p.t("counter.t1"), p.t("counter.t2")),
                    "counter", "ball, top: meets the left wall"))
    counter.append((cubic(Cl, S, floor[0][0], p.ang("counter.floor_in", 20, 0, 70), p.t("counter.t3"), p.t("counter.t4")),
                    "counter", "counter: left"))
    counter += [(s_, "ball", "ball, floor: meets the left wall" if j == 0 else "ball, floor") for j, s_ in enumerate(floor)]
    counter.append((cubic(floor[-1][3], p.ang("counter.floor_out", 300, 270, 345), Cr, N, p.t("counter.t5"), p.t("counter.t6")),
                    "counter", "ball, floor: meets the right wall"))
    counter.append((cubic(Cr, N, top[0][0], p.ang("counter.top_in", 200, 180, 260), p.t("counter.t7"), p.t("counter.t8")),
                    "counter", "counter: right"))
    return {"contours": [run, counter], "baseline": Bb[1]}


LETTERS = {"I": I, "T.1": T_1, "L": L, "F": F, "E": E_, "H": H, "K": K_, "C": C, "O": O, "D": D, "Q": Q}
