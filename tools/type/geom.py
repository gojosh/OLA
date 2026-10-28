"""Outline geometry for the Pugin fonts: cubic Béziers fitted the way a type designer draws them.

Contours are lists of cubic segments, each a 4×2 array [P0, P1, P2, P3], in image pixels (y down)
until they are written to a font. Nodes sit where a designer puts them: at the curve's horizontal and
vertical extremes, at inflections when a span needs one, and at true corners."""
from __future__ import annotations

import math

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from skimage import measure


# ── Cubic basics ──────────────────────────────────────────────────────────────

def bez(P, t):
    t = np.asarray(t, float)[..., None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


def bez_d(P, t):
    t = np.asarray(t, float)[..., None]
    return 3 * (1 - t) ** 2 * (P[1] - P[0]) + 6 * (1 - t) * t * (P[2] - P[1]) + 3 * t ** 2 * (P[3] - P[2])


def bez_dd(P, t):
    t = np.asarray(t, float)[..., None]
    return 6 * (1 - t) * (P[2] - 2 * P[1] + P[0]) + 6 * t * (P[3] - 2 * P[2] + P[1])


def split(P, t):
    """de Casteljau: one cubic into two at t."""
    a, b, c = P[0] + t * (P[1] - P[0]), P[1] + t * (P[2] - P[1]), P[2] + t * (P[3] - P[2])
    d, e = a + t * (b - a), b + t * (c - b)
    f = d + t * (e - d)
    return np.array([P[0], a, d, f]), np.array([f, e, c, P[3]])


def extrema_ts(P, eps=1e-4):
    """Parameters inside (0, 1) where the curve's x or y derivative is zero."""
    ts = []
    for k in (0, 1):
        p0, p1, p2, p3 = P[:, k]
        a, b, c = -p0 + 3 * p1 - 3 * p2 + p3, 2 * (p0 - 2 * p1 + p2), p1 - p0
        if abs(a) < 1e-12:
            roots = [-c / b] if abs(b) > 1e-12 else []
        else:
            disc = b * b - 4 * a * c
            roots = [] if disc < 0 else [(-b + s * math.sqrt(disc)) / (2 * a) for s in (1, -1)]
        ts += [r for r in roots if eps < r < 1 - eps]
    return sorted(ts)


def transform(segs, M=np.eye(2), t=(0.0, 0.0)):
    return [P @ np.asarray(M).T + np.asarray(t) for P in segs]


def reverse(segs):
    return [P[::-1].copy() for P in segs[::-1]]


def sample(segs, n=40):
    return np.concatenate([bez(P, np.linspace(0, 1, n, endpoint=False)) for P in segs])


def signed_area(segs):
    p = sample(segs, 24)
    return 0.5 * float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]))


# ── Fitting ───────────────────────────────────────────────────────────────────

def _fit_one(pts, u, t1, t2):
    """Least-squares cubic through the end points with fixed end tangent directions."""
    p0, p3 = pts[0], pts[-1]
    A1 = (3 * (1 - u) ** 2 * u)[:, None] * t1
    A2 = (3 * (1 - u) * u ** 2)[:, None] * t2
    C = np.array([[np.sum(A1 * A1), np.sum(A1 * A2)], [np.sum(A1 * A2), np.sum(A2 * A2)]])
    base = bez(np.array([p0, p0, p3, p3]), u)
    X = np.array([np.sum(A1 * (pts - base)), np.sum(A2 * (pts - base))])
    det = C[0, 0] * C[1, 1] - C[0, 1] ** 2
    seg = np.linalg.norm(p3 - p0)
    a1, a2 = ((X[0] * C[1, 1] - X[1] * C[0, 1]) / det, (C[0, 0] * X[1] - C[0, 1] * X[0]) / det) if abs(det) > 1e-12 else (seg / 3, seg / 3)
    if a1 < 1e-3 * seg or a2 < 1e-3 * seg:
        a1 = a2 = seg / 3
    return np.array([p0, p0 + a1 * t1, p3 + a2 * t2, p3])


def fit_span(pts, t1, t2, iters=30):
    u = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    u = u / u[-1]
    for _ in range(iters):
        P = _fit_one(pts, u, t1, t2)
        d = bez(P, u) - pts
        D1, D2 = bez_d(P, u), bez_dd(P, u)
        num = np.sum(d * D1, 1)
        den = np.sum(D1 * D1, 1) + np.sum(d * D2, 1)
        u = np.clip(u - np.where(np.abs(den) > 1e-12, num / den, 0), 0, 1)
    P = _fit_one(pts, u, t1, t2)
    return P, np.linalg.norm(bez(P, u) - pts, axis=1)


def _unit(v):
    return v / (np.linalg.norm(v) + 1e-12)


def contours_from_coverage(alpha: np.ndarray, scale=4, blur=0.7, level=0.5):
    """The coverage map's level contour, traced on a smoothed, upsampled copy: closed (x, y) polylines
    in the original pixels, outer contours first."""
    big = cv2.resize(alpha.astype(np.float32), None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    big = cv2.GaussianBlur(big, (0, 0), scale * blur)
    out = []
    for c in measure.find_contours(big, level):
        if len(c) < 30:
            continue
        p = (np.array(c)[:, ::-1] + 0.5) / scale - 0.5
        if np.linalg.norm(p[0] - p[-1]) < 1e-6:
            p = p[:-1]
        out.append(p)
    out.sort(key=lambda p: -abs(_poly_area(p)))
    return out


def _poly_area(p):
    return 0.5 * float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]))


def fit_with_extrema(pts: np.ndarray, tol=0.35, corner_deg=55, min_gap=3.0):
    """Fit a closed polyline with cubics whose nodes sit at x and y extremes and true corners, adding
    a node (at an inflection if there is one) only where a span can't be matched within tol pixels.
    Returns (segments, nodes) where nodes[i] = {"kind", "xy"} is the start of segments[i]."""
    n = len(pts)
    step = np.median(np.linalg.norm(np.diff(pts, axis=0), axis=1))
    # light smoothing along the contour removes the tracing's stair-steps
    k = max(1, int(round(0.8 / step)))
    sm = np.zeros_like(pts)
    for o in range(-2 * k, 2 * k + 1):
        sm += np.roll(pts, o, 0) * math.exp(-0.5 * (o / k) ** 2)
    sm /= sum(math.exp(-0.5 * (o / k) ** 2) for o in range(-2 * k, 2 * k + 1))
    span = max(2, int(round(1.5 / step)))
    tan = np.roll(sm, -span, 0) - np.roll(sm, span, 0)
    gap = max(2, int(round(min_gap / step)))
    nodes = {}
    # corners: the direction turns sharply over a short distance
    cs = max(2, int(round(3.0 / step)))
    vin, vout = sm - np.roll(sm, cs, 0), np.roll(sm, -cs, 0) - sm
    turn = np.degrees(np.arccos(np.clip(np.sum(vin * vout, 1) / (np.linalg.norm(vin, axis=1) * np.linalg.norm(vout, axis=1) + 1e-12), -1, 1)))
    for i in range(n):
        if turn[i] > corner_deg and turn[i] == turn[[(i + o) % n for o in range(-cs, cs + 1)]].max():
            nodes[i] = "corner"
    # extremes: the tangent's x or y component changes sign
    for kind, comp in (("x", 0), ("y", 1)):
        s = np.sign(tan[:, comp])
        for i in range(n):
            if s[i] != 0 and s[i] != s[(i + 1) % n]:
                j = i if abs(tan[i, comp]) <= abs(tan[(i + 1) % n, comp]) else (i + 1) % n
                if all(min((j - c) % n, (c - j) % n) > gap for c, kd in nodes.items() if kd == "corner"):
                    nodes[j] = kind
    # merge extremes that crowd each other (a flat run can flicker)
    idx = sorted(nodes)
    kept = []
    for i in idx:
        if kept and (i - kept[-1]) < gap and nodes[kept[-1]] != "corner" and nodes[i] != "corner":
            continue
        kept.append(i)
    if len(kept) > 1 and (kept[0] + n - kept[-1]) < gap and nodes[kept[-1]] != "corner":
        kept.pop()
    if not kept:
        kept = [int(np.argmin(pts[:, 0]))]
        nodes[kept[0]] = "x"

    def tangent_at(i, kind, side):
        t = _unit(tan[i])
        if kind == "x":
            return np.array([0.0, math.copysign(1, t[1])])
        if kind == "y":
            return np.array([math.copysign(1, t[0]), 0.0])
        if side == "out":
            return _unit(sm[(i + cs) % n] - sm[i])
        return _unit(sm[i] - sm[(i - cs) % n])

    segs, info = [], []

    def fit_rec(a, b, ta, tb, kind_a):
        idxs = np.arange(a, b + 1) % n if b > a else np.concatenate([np.arange(a, n), np.arange(0, b + 1)])
        run = sm[idxs]
        run[0], run[-1] = sm[a % n], sm[b % n]
        P, err = fit_span(run, ta, -tb)
        if err.max() <= tol or len(run) < 8:
            segs.append(P)
            info.append({"kind": kind_a, "xy": [round(float(v), 3) for v in P[0]]})
            return
        # split: at an inflection if the span has one, otherwise where the fit is worst. Curvature is
        # taken over a few pixels so the tracing's small wobbles don't read as inflections.
        smr = gaussian_filter1d(run, max(1.0, 2.0 / step), axis=0, mode="nearest")
        d1 = np.gradient(smr, axis=0)
        d2 = np.gradient(d1, axis=0)
        curv = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / (np.linalg.norm(d1, axis=1) ** 3 + 1e-12)
        m = len(run)
        lo, hi = m // 6, m - m // 6
        floor = 0.1 * np.abs(curv[lo:hi]).max()
        flips = [i for i in range(lo, hi) if np.sign(curv[i]) != np.sign(curv[i + 1])
                 and np.abs(curv[max(0, i - 3):i + 1]).max() > floor and np.abs(curv[i + 1:i + 5]).max() > floor]
        j = min(flips, key=lambda i: abs(i - m // 2)) if flips else int(np.clip(np.argmax(err), lo, hi - 1))
        mid = idxs[j]
        tm = _unit(tan[mid])
        # indices run unwrapped (b may pass n) so each half is strictly shorter than the whole
        fit_rec(a, a + j, ta, tm, kind_a)
        fit_rec(a + j, b, tm, tb, "inflection" if flips else "smooth")

    for q, i in enumerate(kept):
        j = kept[(q + 1) % len(kept)]
        b = j if j > i else j + n
        fit_rec(i, b, tangent_at(i, nodes[i], "out"), tangent_at(j % n, nodes[j % n], "in"), nodes[i])
    return segs, info


def fit_error(segs, pts):
    """Distance from each traced point to the fitted outline (pixels)."""
    dense = sample(segs, 120)
    d = np.empty(len(pts))
    for s in range(0, len(pts), 2000):
        chunk = pts[s:s + 2000]
        d[s:s + 2000] = np.sqrt(((chunk[:, None, :] - dense[None, :, :]) ** 2).sum(2)).min(1)
    return d


# ── Drawing ───────────────────────────────────────────────────────────────────

def rasterize(contours, shape, ss=4, n=40):
    """Anti-aliased coverage of filled contours (non-zero winding, union of overlaps)."""
    H, W = shape
    big = np.zeros((H * ss, W * ss), np.uint8)
    polys = [np.round((sample(c, n) + 0.5) * ss - 0.5).astype(np.int32) for c in contours]
    cv2.fillPoly(big, polys, 255, lineType=cv2.LINE_AA)
    return cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def svg_path(contours):
    out = []
    for segs in contours:
        out.append("M{:.2f} {:.2f} ".format(*segs[0][0]) + " ".join(
            "C{:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}".format(*P[1], *P[2], *P[3]) for P in segs) + " Z")
    return " ".join(out)


def svg_nodes(contours, r=2.2):
    """On-curve nodes as squares, handles as small circles joined to their nodes, as in a font editor."""
    els = []
    for segs in contours:
        for P in segs:
            for a, b in ((P[0], P[1]), (P[3], P[2])):
                if np.linalg.norm(a - b) > 0.5:
                    els.append(f'<line class="h" x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}"/>'
                               f'<circle class="hc" cx="{b[0]:.2f}" cy="{b[1]:.2f}" r="{r * 0.6:.2f}"/>')
            els.append(f'<rect class="n" x="{P[0][0] - r:.2f}" y="{P[0][1] - r:.2f}" width="{2 * r:.2f}" height="{2 * r:.2f}"/>')
    return "".join(els)
