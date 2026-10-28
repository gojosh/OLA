"""Lombardic letter constructions (decision 0008).

Each construction draws one letter from the kit's parts (construct.py): the stem, its flares, the
bars, the curl, the trefoil, and curves fitted where a letter has a stroke of its own (an arm, a
bowl). It asks for its measurements through `p`, each with a starting value read off Pugin's
letter and the bounds the fit may move it within; `p.fam` asks for one shared by the whole alphabet.

A construction returns its contours (lists of (segment, part, node name)), the baseline (the outer
edge of the bottom curls), and, for a symmetric letter, the left half and the axis. Coordinates are
the letter's reference image, in plate pixels, y down."""
from __future__ import annotations

import numpy as np

from construct import E, N, ORIENT, S, W, arc, cubic, line, mirror_half, trefoil


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


def symmetric(half, ax, end_name, baseline):
    return {"contours": [mirror_half(half, ax, end_name)], "half": half, "axis": ax, "baseline": baseline}


# ── Letters ───────────────────────────────────────────────────────────────────

def I(p, K):
    """A straight stem that flares into a top and a bottom bar, each ending in a curl at both sides."""
    ax, w = p.x("axis_x", 178.5, 20), p.fam("stem")
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
    ax, w, k = p.x("axis_x", 235, 20), p.fam("stem"), p.fam("curl")
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
    ax, w, k = p.x("axis_x", 137.5, 20), p.fam("stem"), p.fam("curl")
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
    ax, w, k = p.x("axis_x", 119, 20), p.fam("stem"), p.fam("curl")
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


def E_(p, K):
    """The uncial E: a round bowl, closed on the right by a stroke that ends in a top-right and a
    bottom-right curl, with a bar across the middle. Two counters."""
    k = p.fam("curl")
    E0 = np.array([p.x("bowl.left_x", 25, 15), p.x("bowl.left_y", 237, 40)])
    Et = np.array([p.x("bowl.top_x", 231, 40), p.x("bowl.top_y", 26, 12)])
    Eb = np.array([p.x("bowl.bottom_x", 231, 40), p.x("bowl.bottom_y", 455, 12)])
    Nt = np.array([p.x("notch.x", 322, 15), p.x("notch.y", 59, 15)])
    xr, xl = p.x("stroke.right_x", 355, 15), p.x("stroke.left_x", 310, 15)
    run = [(cubic(E0, N, Et, E, p.t("bowl.t1"), p.t("bowl.t2")), "bowl", "bowl: left"),
           (cubic(Et, E, Nt, p.ang("notch.in", 25, 0, 60), p.t("bowl.t3"), p.t("bowl.t4")), "bowl", "bowl: top")]
    O_tr = np.array([p.x("top.curl_x", 376, 15), p.x("top.curl_y", 27, 12)])
    run.append((cubic(Nt, p.ang("notch.out", 330, 290, 360), O_tr, E, p.t("top.edge_t1"), p.t("top.edge_t2")), "top bar", "notch, top"))
    segs, names, neck, leave = K.curl(O_tr, "tr", k, p.ang("top.neck_deg", 15, -20, 60), place="curl, top-right")
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    R1 = np.array([xr, p.x("stroke.top_y", 140, 90)])
    R2 = np.array([xr, p.x("stroke.foot_y", 380, 40)])
    run.append((cubic(neck, leave, R1, S, p.t("top.flare_t1"), p.t("top.flare_t2")), "flare", "curl, top-right: neck"))
    run.append((line(R1, R2), "right stroke", "right stroke: top of straight"))
    O_br = np.array([p.x("bottom.curl_x", 376, 15), p.x("bottom.curl_y", 452, 12)])
    segs, names, bneck, arrive = K.curl(O_br, "br", k, p.ang("bottom.neck_deg", 0, 0, 40), place="curl, bottom-right")
    run.append((cubic(R2, S, bneck, arrive, p.t("bottom.flare_t1"), p.t("bottom.flare_t2")), "flare", "right stroke: foot of straight"))
    run += [(s, "curl", nm) for s, nm in zip(segs, names)]
    Nb = np.array([p.x("notch_b.x", 330, 15), p.x("notch_b.y", 422, 15)])
    run.append((cubic(O_br, W, Nb, p.ang("notch_b.in", 200, 180, 250), p.t("bottom.edge_t1"), p.t("bottom.edge_t2")), "bottom bar", "curl, bottom-right: outer"))
    run.append((cubic(Nb, p.ang("notch_b.out", 150, 110, 180), Eb, W, p.t("bowl.t7"), p.t("bowl.t8")), "bowl", "notch, bottom"))
    run.append((cubic(Eb, W, E0, N, p.t("bowl.t5"), p.t("bowl.t6")), "bowl", "bowl: bottom"))
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


LETTERS = {"I": I, "T.1": T_1, "L": L, "F": F, "E": E_}
