# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#   "numpy>=1.26",
#   "scipy>=1.11",
#   "opencv-python-headless>=4.9",
#   "pillow>=10",
# ]
# ///
"""Flatten photographed book pages onto true rectangles.

The plates in reference/pugin-glossary were photographed in their binding. They lie
flat across most of the page and curve down into the gutter on the spine side. This tool
models each photograph in 3D and unrolls the page:

  camera   a pinhole camera with one radial-distortion term (k1), at distance f from the
           page, rotated by (rx, ry, rz). The principal point is the image center.
  surface  a "generalized cylinder": the sheet bends across its width only. Depth z is a
           natural cubic spline in X through editable knots. Lines along the spine stay
           straight, which is how paper bends.
  page     a rectangle in flat coordinates (u, Y), where u is arc length across the sheet.

The model is fitted to lines that are known to be straight on the printed page (each
plate's ruled frame), then every output pixel is mapped back to the photograph and
resampled. Everything needed to reproduce or adjust a result is saved per plate in
reference/pugin-glossary/flatten/<plate>.json.

Usage (from the repository root; uv installs the dependencies):
  uv run tools/flatten/flatten.py detect 09-alphabets-no-1     # find the frame rules
  uv run tools/flatten/flatten.py fit    09-alphabets-no-1     # fit camera + surface
  uv run tools/flatten/flatten.py render 09-alphabets-no-1     # write the flat page
  uv run tools/flatten/flatten.py shade  09-alphabets-no-1     # fit and remove the gutter shading
  uv run tools/flatten/flatten.py all    09 10 11 12           # all three, by prefix
  uv run tools/flatten/flatten.py serve                        # the grid editor
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import cv2
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix

ROOT = Path(__file__).resolve().parents[2]
TOOL = Path(__file__).resolve().parent
PLATES = ROOT / "reference/pugin-glossary/plates"
DATA = ROOT / "reference/pugin-glossary/flatten"
OUT = ROOT / "reference/pugin-glossary/flattened"
CACHE = ROOT / "build/flatten-cache"

VERSION = 1


def anchors(srf: dict) -> list[int]:
    """Knots pinned at z = 0. Two are needed to fix the page plane's depth and tilt (the camera's
    rotation absorbs the rest). By default they sit on the flat side, leaving the fore-edge knot free."""
    n = len(srf["x_knots"])
    return list(srf.get("anchors", [n - 3, n - 2]))


def full_z(srf: dict, zfree) -> np.ndarray:
    anc = anchors(srf)
    z = np.zeros(len(srf["x_knots"]))
    z[[i for i in range(len(z)) if i not in anc]] = zfree
    return z


# ── Plates and images ─────────────────────────────────────────────────────────

def plate_ids() -> list[str]:
    return sorted(p.stem for p in PLATES.iterdir() if p.suffix.lower() in (".jp2", ".heic", ".jpg", ".png", ".tif"))


def resolve(prefixes: list[str]) -> list[str]:
    ids = plate_ids()
    out = []
    for pre in prefixes:
        hits = [i for i in ids if i == pre or i.startswith(pre.zfill(2) + "-") or i.startswith(pre)]
        if not hits:
            sys.exit(f"No plate matches {pre!r}")
        out += [h for h in hits if h not in out]
    return out


def source_path(pid: str) -> Path:
    for p in PLATES.iterdir():
        if p.stem == pid:
            return p
    raise FileNotFoundError(pid)


def load_bgr(pid: str) -> np.ndarray:
    """Decode a plate once into a lossless cache (JPEG 2000 decoding is slow)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{pid}.png"
    if not cached.exists():
        src = source_path(pid)
        if src.suffix.lower() == ".heic":  # Pillow can't read HEIC; macOS sips can
            subprocess.run(["sips", "-s", "format", "png", str(src), "--out", str(cached)], check=True, capture_output=True)
        else:
            rgb = np.array(Image.open(src).convert("RGB"))
            cv2.imwrite(str(cached), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    img = cv2.imread(str(cached), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"Could not read {cached}")
    return img


def display_jpeg(pid: str) -> Path:
    """A full-resolution JPEG the browser can show (browsers can't decode JPEG 2000)."""
    path = CACHE / f"{pid}.display.jpg"
    if not path.exists():
        cv2.imwrite(str(path), load_bgr(pid), [cv2.IMWRITE_JPEG_QUALITY, 90])
    return path


# ── Feature detection: the printed frame's four rules ─────────────────────────

def redness(img: np.ndarray) -> np.ndarray:
    b, g, r = (img[..., i].astype(np.float32) for i in range(3))
    red = np.clip((r - g) - 22.0, 0, None) * (r > 110)
    return cv2.GaussianBlur(red, (0, 0), 1.0)


def _trace(R: np.ndarray, axis: str, pos0: float, start: int, stop: int, step=4, win=10, minmass=150.0):
    """Follow a thin line from a seed, taking the weighted centroid across it at each step."""
    pts, p, miss = [], float(pos0), 0
    rng = range(start, stop, step) if stop > start else range(start, stop, -step)
    limit = R.shape[0] if axis == "h" else R.shape[1]
    for t in rng:
        lo, hi = int(round(p - win)), int(round(p + win)) + 1
        if lo < 0 or hi > limit:
            break
        s = R[lo:hi, t] if axis == "h" else R[t, lo:hi]
        m = float(s.sum())
        if m < minmass:
            miss += 1
            if miss > 6:
                break
            continue
        miss = 0
        idx = np.arange(lo, hi)
        c = float((s * idx).sum() / m)
        if math.sqrt(float((s * (idx - c) ** 2).sum() / m)) > 5.5:  # a blob, not a rule
            continue
        pts.append((t, c) if axis == "h" else (c, t))
        p = c
    return pts


def _clean(pts: list, axis: str, tol=2.5) -> np.ndarray:
    """Drop points pulled off the rule by touching ink: compare with a running median."""
    a = np.array(pts, dtype=float)
    if len(a) < 15:
        return a
    k = 1 if axis == "h" else 0
    v = a[:, k]
    pad = np.pad(v, 7, mode="edge")
    med = np.array([np.median(pad[i:i + 15]) for i in range(len(v))])
    return a[np.abs(v - med) < tol]


def detect_frame(img: np.ndarray) -> list[dict]:
    R = redness(img)
    H, W = R.shape
    k = 4
    small = cv2.resize(np.clip(R * 2, 0, 255).astype(np.uint8), (W // k, H // k), interpolation=cv2.INTER_AREA)
    segs = cv2.createLineSegmentDetector(0).detect(small)[0]
    segs = segs.reshape(-1, 4) * k if segs is not None else np.zeros((0, 4))
    hs, vs = [], []
    for x1, y1, x2, y2 in segs:
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        if abs(dy) < abs(dx) * 0.05 and L > W * 0.15:
            hs.append(((y1 + y2) / 2, (x1 + x2) / 2))
        if abs(dx) < abs(dy) * 0.05 and L > H * 0.10:
            vs.append(((x1 + x2) / 2, (y1 + y2) / 2))
    if len(hs) < 2 or len(vs) < 2:
        raise RuntimeError("Could not find a ruled frame; add features by hand in the editor.")
    hs.sort()
    vs.sort()
    found = {}
    for name, (y, xm) in (("frame-top", hs[0]), ("frame-bottom", hs[-1])):
        xm = int(xm)
        found[name] = ("h", _trace(R, "h", y, xm, 0)[::-1] + _trace(R, "h", y, xm + 4, W))
    for name, (x, ym) in (("frame-left", vs[0]), ("frame-right", vs[-1])):
        ym = int(ym)
        found[name] = ("v", _trace(R, "v", x, ym, 0)[::-1] + _trace(R, "v", x, ym + 4, H))
    found = {n: v for n, v in found.items() if len(v[1]) >= 10}
    if len([1 for d, _ in found.values() if d == "h"]) < 2 or len([1 for d, _ in found.values() if d == "v"]) < 2:
        raise RuntimeError("Found the frame but could not trace all four rules.")
    # keep clear of the corners, where the crossing rule pulls the centroid
    vx = {n: np.median(np.array(p)[:, 0]) for n, (d, p) in found.items() if d == "v"}
    hy = {n: np.median(np.array(p)[:, 1]) for n, (d, p) in found.items() if d == "h"}
    out = []
    for name, (d, pts) in found.items():
        a = _clean(pts, d)
        if d == "h":
            a = a[(a[:, 0] > min(vx.values()) + 24) & (a[:, 0] < max(vx.values()) - 24)]
        else:
            a = a[(a[:, 1] > min(hy.values()) + 24) & (a[:, 1] < max(hy.values()) - 24)]
        a = a[::2]  # 8 px spacing is plenty
        out.append({"name": name, "dir": d, "source": "auto", "pts": [[round(float(x), 2), round(float(y), 2)] for x, y in a]})
    return out


# ── The model ─────────────────────────────────────────────────────────────────

def rotation(rx: float, ry: float, rz: float) -> np.ndarray:
    """R = Rz · Ry · Rx, angles in degrees."""
    a, b, c = (math.radians(v) for v in (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


class Spline:
    """Natural cubic spline z(X) through the knots, continued linearly beyond them."""

    def __init__(self, xk, zk):
        self.x = np.asarray(xk, float)
        self.z = np.asarray(zk, float)
        n = len(self.x)
        h = np.diff(self.x)
        M = np.zeros(n)
        if n > 2:
            A = np.zeros((n - 2, n - 2))
            rhs = np.zeros(n - 2)
            for i in range(1, n - 1):
                if i > 1:
                    A[i - 1, i - 2] = h[i - 1]
                A[i - 1, i - 1] = 2 * (h[i - 1] + h[i])
                if i < n - 2:
                    A[i - 1, i] = h[i]
                rhs[i - 1] = 6 * ((self.z[i + 1] - self.z[i]) / h[i] - (self.z[i] - self.z[i - 1]) / h[i - 1])
            M[1:-1] = np.linalg.solve(A, rhs)
        self.M, self.h = M, h
        self.b = (self.z[1:] - self.z[:-1]) / h - h * (2 * M[:-1] + M[1:]) / 6
        self.slope0 = self.b[0]
        hl = h[-1]
        self.slope1 = self.b[-1] + M[-2] * hl + (M[-1] - M[-2]) * hl / 2

    def __call__(self, X):
        X = np.asarray(X, float)
        i = np.clip(np.searchsorted(self.x, X) - 1, 0, len(self.x) - 2)
        t = X - self.x[i]
        z = self.z[i] + self.b[i] * t + self.M[i] / 2 * t ** 2 + (self.M[i + 1] - self.M[i]) / (6 * self.h[i]) * t ** 3
        z = np.where(X < self.x[0], self.z[0] + self.slope0 * (X - self.x[0]), z)
        z = np.where(X > self.x[-1], self.z[-1] + self.slope1 * (X - self.x[-1]), z)
        return z


class Model:
    def __init__(self, params: dict):
        cam, srf = params["camera"], params["surface"]
        self.f = float(cam["f"])
        self.k1 = float(cam.get("k1", 0.0))
        self.k2 = float(cam.get("k2", 0.0))
        self.R = rotation(*cam["rot_deg"])
        self.cx = float(cam.get("cx", params["image"]["width"] / 2))
        self.cy = float(cam.get("cy", params["image"]["height"] / 2))
        self.spline = Spline(srf["x_knots"], srf["z_knots"])
        self._arc = None

    def project(self, X, Y):
        X = np.asarray(X, float)
        Y = np.broadcast_to(np.asarray(Y, float), X.shape)
        Z = self.spline(X)
        P = np.stack([X, Y, Z], -1) @ self.R.T
        Zc = P[..., 2] + self.f
        xn, yn = P[..., 0] / Zc, P[..., 1] / Zc
        r2 = xn * xn + yn * yn
        d = 1 + self.k1 * r2 + self.k2 * r2 * r2
        return self.f * xn * d + self.cx, self.f * yn * d + self.cy

    # arc length across the sheet, measured from the first knot
    def arc_table(self, xmin=-20000.0, xmax=20000.0, step=0.5):
        if self._arc is None:
            X = np.arange(xmin, xmax + step, step)
            z = self.spline(X)
            ds = np.sqrt(1 + (np.gradient(z, step)) ** 2) * step
            s = np.concatenate([[0], np.cumsum((ds[1:] + ds[:-1]) / 2)])
            s -= np.interp(self.spline.x[0], X, s)
            self._arc = (X, s)
        return self._arc

    def u_of_x(self, X):
        Xt, s = self.arc_table()
        return np.interp(X, Xt, s)

    def x_of_u(self, u):
        Xt, s = self.arc_table()
        return np.interp(u, s, Xt)


# ── Fitting ───────────────────────────────────────────────────────────────────

def initial_params(pid: str, img_shape, features: list[dict]) -> dict:
    H, W = img_shape[:2]
    cx, cy = W / 2, H / 2
    # in-plane rotation from the rules' average slope
    slopes = []
    for ft in features:
        a = np.array(ft["pts"])
        if len(a) < 10:
            continue
        if ft["dir"] == "h":
            slopes.append(np.polyfit(a[:, 0], a[:, 1], 1)[0])
        else:
            slopes.append(-np.polyfit(a[:, 1], a[:, 0], 1)[0])
    rz = math.degrees(math.atan(float(np.median(slopes)))) if slopes else 0.0
    vx = [np.median(np.array(ft["pts"])[:, 0]) for ft in features if ft["dir"] == "v"]
    left = min(vx) if vx else W * 0.05
    right = max(vx) if vx else W * 0.75
    # knots from the gutter side of the photograph to past the frame, dense near the spine
    xa, xb = -cx, (right - cx) + 0.12 * (right - left)
    fr = [0, 0.015, 0.035, 0.06, 0.09, 0.13, 0.18, 0.25, 0.35, 0.5, 0.7, 1.0]
    return {
        "version": VERSION,
        "plate": pid,
        "image": {"file": str(source_path(pid).relative_to(ROOT)), "width": W, "height": H},
        "camera": {"f": 8000.0, "k1": 0.0, "rot_deg": [0.0, 0.0, rz]},
        "surface": {"model": "generalized-cylinder", "x_knots": [round(xa + t * (xb - xa), 2) for t in fr], "z_knots": [0.0] * len(fr),
                    "anchors": [len(fr) - 3, len(fr) - 2]},
        "page": None,
        "frame": None,
        "fit": None,
        "features": features,
    }


def fit(params: dict, lock: set[str] | None = None, smooth=0.02, verbose=True, behind_glass=True) -> dict:
    """Fit one plate. See fit_many."""
    return fit_many([params], lock, smooth, verbose, behind_glass)[0]


def fit_many(plist: list[dict], lock: set[str] | None = None, smooth=0.02, verbose=True, behind_glass=True) -> list[dict]:
    """Least squares over the camera and each plate's pose and surface.

    The focal length f and lens distortion k1 are shared by every plate in the list: one lens
    photographed them all, and a single plate can't separate f from the depth of the gutter.
    Each observed point also gets its own position along its line, so a residual is the
    point's distance from the model's line, in pixels."""
    lock = lock or set()
    t0 = time.time()
    cam0 = plist[0]["camera"]
    W0, H0 = plist[0]["image"]["width"], plist[0]["image"]["height"]
    # shared lens: f, k1, k2 (both carried × 100), and the principal point's offset from the image center
    NS = 5
    x0 = [cam0["f"], cam0.get("k1", 0.0) * 1e2, cam0.get("k2", 0.0) * 1e2,
          cam0.get("cx", W0 / 2) - W0 / 2, cam0.get("cy", H0 / 2) - H0 / 2]
    lo, hi = [1500.0, -50.0, -50.0, -400.0, -400.0], [80000.0, 50.0, 50.0, 400.0, 400.0]
    free = ["f" not in lock, "k1" not in lock, "k2" not in lock, "pp" not in lock, "pp" not in lock]
    blocks = []
    for prm in plist:
        W, H = prm["image"]["width"], prm["image"]["height"]
        cx, cy = W / 2, H / 2  # the principal point's offset is a shared unknown
        feats = [f for f in prm["features"] if len(f["pts"]) >= 5 and f.get("weight", 1.0) > 0]
        xk = np.array(prm["surface"]["x_knots"], float)
        anc = anchors(prm["surface"])
        nfree = len(xk) - len(anc)
        cam = prm["camera"]
        R0 = rotation(*cam["rot_deg"])
        b = {"prm": prm, "cx": cx, "cy": cy, "feats": feats, "xk": xk, "nfree": nfree, "off": len(x0)}
        z0 = [max(v, 0.0) if behind_glass else v for i, v in enumerate(prm["surface"]["z_knots"]) if i not in anc]
        x0 += list(cam["rot_deg"]) + z0
        lo += [-np.inf] * 3 + [0.0 if behind_glass else -np.inf] * nfree
        hi += [np.inf] * (3 + nfree)
        free += ["rotation" not in lock] * 3 + ["surface" not in lock] * nfree
        # each line's offset, then each point's position along it, from undoing the rotation on z = 0
        lines, pts, obs, owner, kinds = [], [], [], [], []
        for li, ft in enumerate(feats):
            a = np.array(ft["pts"], float)
            Wc = np.stack([a[:, 0] - cx, a[:, 1] - cy, np.zeros(len(a))], -1) @ R0
            if ft["dir"] == "h":
                lines.append(float(np.median(Wc[:, 1])))
                pts += list(Wc[:, 0])
            else:
                lines.append(float(np.median(Wc[:, 0])))
                pts += list(Wc[:, 1])
            obs.append(a)
            owner += [li] * len(a)
            kinds.append(ft["dir"])
        b.update(nl=len(lines), npt=len(pts), obs=np.concatenate(obs), owner=np.array(owner),
                 wt=np.sqrt(np.array([feats[o].get("weight", 1.0) for o in owner])),
                 is_h=np.array([kinds[o] == "h" for o in owner]), lines_off=len(x0) + 0)
        x0 += lines
        b["pts_off"] = len(x0)
        x0 += pts
        lo += [-np.inf] * (len(lines) + len(pts))
        hi += [np.inf] * (len(lines) + len(pts))
        free += [True] * (len(lines) + len(pts))
        blocks.append(b)
    x0 = np.array(x0, float)
    lo, hi, free = np.array(lo), np.array(hi), np.array(free)

    def penalty(b, z):
        """Second divided differences of the profile: smoothness where no line passes."""
        xk = b["xk"]
        zz = full_z(b["prm"]["surface"], z)
        h = np.diff(xk)
        d2 = np.diff(np.diff(zz) / h) / ((h[:-1] + h[1:]) / 2)
        return smooth * d2 * (xk[-1] - xk[0]) ** 2 / 100

    def plate_residuals(x, b):
        f, k1, k2 = x[0], x[1] * 1e-2, x[2] * 1e-2
        cx, cy = b["cx"] + x[3], b["cy"] + x[4]
        o = b["off"]
        R = rotation(*x[o:o + 3])
        z = x[o + 3:o + 3 + b["nfree"]]
        sp = Spline(b["xk"], full_z(b["prm"]["surface"], z))
        lines = x[b["lines_off"]:b["lines_off"] + b["nl"]]
        pts = x[b["pts_off"]:b["pts_off"] + b["npt"]]
        X = np.where(b["is_h"], pts, lines[b["owner"]])
        Y = np.where(b["is_h"], lines[b["owner"]], pts)
        P = np.stack([X, Y, sp(X)], -1) @ R.T
        Zc = P[:, 2] + f
        xn, yn = P[:, 0] / Zc, P[:, 1] / Zc
        r2 = xn * xn + yn * yn
        d = 1 + k1 * r2 + k2 * r2 * r2
        return (f * xn * d + cx - b["obs"][:, 0]) * b["wt"], (f * yn * d + cy - b["obs"][:, 1]) * b["wt"], penalty(b, z)

    def residuals(xf):
        x = x0.copy()
        x[free] = xf
        out = []
        for b in blocks:
            u, v, pen = plate_residuals(x, b)
            out += [u, v, pen]
        return np.concatenate(out)

    # sparsity: a residual depends on the shared camera, its plate's pose and surface, its line, its point
    nres = sum(2 * b["npt"] + len(b["xk"]) - 2 for b in blocks)
    S = lil_matrix((nres, len(x0)), dtype=np.int8)
    row = 0
    for b in blocks:
        npt, o = b["npt"], b["off"]
        S[row:row + 2 * npt, 0:NS] = 1
        S[row:row + 2 * npt, o:o + 3 + b["nfree"]] = 1
        for i in range(npt):
            for r in (row + i, row + npt + i):
                S[r, b["lines_off"] + b["owner"][i]] = 1
                S[r, b["pts_off"] + i] = 1
        row += 2 * npt
        S[row:row + len(b["xk"]) - 2, o + 3:o + 3 + b["nfree"]] = 1
        row += len(b["xk"]) - 2
    S = S.tocsr()[:, free]

    # two passes: plain least squares to reach the right basin, then a robust pass that
    # stops a few stray points (ink touching a rule) from pulling the fit
    xf = np.clip(x0[free], lo[free] + 1e-9, hi[free] - 1e-9)
    for loss, fs, n in (("linear", 1.0, 300), ("soft_l1", 1.0, 600)):
        xf = least_squares(residuals, xf, jac_sparsity=S, bounds=(lo[free], hi[free]), loss=loss,
                           f_scale=fs, x_scale="jac", max_nfev=n, verbose=0).x
    x = x0.copy()
    x[free] = xf
    secs = round(time.time() - t0, 1)

    outs = []
    for b in blocks:
        u, v, _ = plate_residuals(x, b)
        dist = np.hypot(u, v) / b["wt"]
        o = b["off"]
        out = json.loads(json.dumps(b["prm"]))
        out["camera"] = {"f": round(float(x[0]), 3), "k1": round(float(x[1] * 1e-2), 8), "k2": round(float(x[2] * 1e-2), 8),
                         "cx": round(float(b["cx"] + x[3]), 3), "cy": round(float(b["cy"] + x[4]), 3),
                         "rot_deg": [round(float(v), 6) for v in x[o:o + 3]]}
        out["surface"]["z_knots"] = [round(float(v), 4) for v in full_z(out["surface"], x[o + 3:o + 3 + b["nfree"]])]
        out["surface"]["anchors"] = anchors(out["surface"])
        model = Model(out)
        lines = x[b["lines_off"]:b["lines_off"] + b["nl"]]
        frame, per = {}, {}
        for li, ft in enumerate(b["feats"]):
            if ft["name"].startswith("frame-"):
                frame[ft["name"][6:]] = round(float(lines[li] if ft["dir"] == "h" else model.u_of_x(lines[li])), 3)
            d = dist[b["owner"] == li]
            per[ft["name"]] = {"rms_px": round(float(np.sqrt((d ** 2).mean())), 3), "max_px": round(float(d.max()), 3), "n": int(len(d))}
        if {"top", "bottom", "left", "right"} <= frame.keys():
            out["frame"] = {"u0": frame["left"], "u1": frame["right"], "y0": frame["top"], "y1": frame["bottom"]}
        out["fit"] = {
            "rms_px": round(float(np.sqrt((dist ** 2).mean())), 3),
            "max_px": round(float(dist.max()), 3),
            "per_feature": per,
            "locked": sorted(lock),
            "behind_glass": behind_glass,
            "jointly_with": [p["plate"] for p in plist if p is not b["prm"]],
            "seconds": secs,
            "when": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        if out.get("page") is None and out.get("frame"):
            out["page"] = default_page(out)
        if verbose:
            c = out["camera"]
            print(f"  {out['plate']}: rms {out['fit']['rms_px']} px (max {out['fit']['max_px']}), f={c['f']:.0f}, k1={c['k1']:+.4f}, "
                  f"k2={c['k2']:+.4f}, pp=({c['cx']:.0f},{c['cy']:.0f}), rot={c['rot_deg']}, deepest {max(out['surface']['z_knots']):.1f}")
        outs.append(out)
    return outs


def default_page(params: dict) -> dict:
    """A starting page rectangle: the frame plus margins. Refined by auto_page() after a render."""
    fr = params["frame"]
    w, h = fr["u1"] - fr["u0"], fr["y1"] - fr["y0"]
    return {"u0": round(fr["u0"] - 0.04 * w, 1), "u1": round(fr["u1"] + 0.10 * w, 1),
            "y0": round(fr["y0"] - 0.12 * h, 1), "y1": round(fr["y1"] + 0.14 * h, 1)}


# ── Rendering ─────────────────────────────────────────────────────────────────

def remap_maps(params: dict, rect: dict, scale: float):
    m = Model(params)
    W = int(round((rect["u1"] - rect["u0"]) * scale))
    H = int(round((rect["y1"] - rect["y0"]) * scale))
    u = rect["u0"] + (np.arange(W) + 0.5) / scale
    y = rect["y0"] + (np.arange(H) + 0.5) / scale
    X = m.x_of_u(u)
    mx = np.empty((H, W), np.float32)
    my = np.empty((H, W), np.float32)
    for r0 in range(0, H, 256):  # in bands, to keep memory modest
        Yb = y[r0:r0 + 256, None]
        xx, yy = m.project(np.broadcast_to(X, (len(Yb), W)), Yb)
        mx[r0:r0 + 256] = xx
        my[r0:r0 + 256] = yy
    return mx, my


def render(params: dict, img: np.ndarray, scale=1.0, rect: dict | None = None) -> np.ndarray:
    rect = rect or params["page"]
    mx, my = remap_maps(params, rect, scale)
    interp = cv2.INTER_LANCZOS4 if scale >= 0.75 else cv2.INTER_AREA
    if scale < 0.75:  # pre-shrink the source so downscaled previews don't alias
        k = scale
        small = cv2.resize(img, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        return cv2.remap(small, (mx + 0.5) * k - 0.5, (my + 0.5) * k - 0.5, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(40, 40, 40))
    return cv2.remap(img, mx, my, interp, borderMode=cv2.BORDER_CONSTANT, borderValue=(40, 40, 40))


def auto_page(params: dict, img: np.ndarray) -> dict:
    """Find the page's own edges in a flattened low-resolution render. Paper is bright and smooth;
    the boards and the gutter are darker; the stack of leaves at the fore-edge is striped."""
    fr = params["frame"]
    w, h = fr["u1"] - fr["u0"], fr["y1"] - fr["y0"]
    big = {"u0": fr["u0"] - 0.25 * w, "u1": fr["u1"] + 0.35 * w, "y0": fr["y0"] - 0.3 * h, "y1": fr["y1"] + 0.3 * h}
    s = 0.25
    flat = render(params, img, s, big)
    gray = cv2.cvtColor(flat, cv2.COLOR_BGR2GRAY).astype(float)
    fu0, fu1 = int((fr["u0"] - big["u0"]) * s), int((fr["u1"] - big["u0"]) * s)
    fy0, fy1 = int((fr["y0"] - big["y0"]) * s), int((fr["y1"] - big["y0"]) * s)
    inner = gray[fy0 + 8:fy1 - 8, fu0 + 8:fu1 - 8]
    paper = float(np.percentile(inner, 75))  # the ground, not the ink
    col = np.median(gray[fy0:fy1, :], axis=0)
    row = np.median(gray[:, fu0:fu1], axis=1)
    # horizontal texture: the fore-edge stack is a run of fine vertical lines
    gx = np.abs(np.diff(cv2.GaussianBlur(gray, (0, 0), 0.7), axis=1))
    tex = np.median(gx[fy0:fy1, :], axis=0)
    calm = float(np.median(tex[fu0 + 8:fu1 - 8]))
    thr = paper * 0.82

    def edge(profile, start, step, textured=None):
        i = start + 6 * step  # step off the rule first
        while 0 <= i + step < len(profile) and profile[i + step] > thr and (textured is None or textured[i + step] < max(3 * calm, calm + 2)):
            i += step
        return i

    u0, u1 = edge(col, fu0, -1), edge(col, fu1, +1, tex)
    y0, y1 = edge(row, fy0, -1), edge(row, fy1, +1)
    inset = 2  # preview pixels, to stay just inside the edge
    return {"u0": round(big["u0"] + (u0 + inset) / s, 1), "u1": round(big["u0"] + (u1 - inset) / s, 1),
            "y0": round(big["y0"] + (y0 + inset) / s, 1), "y1": round(big["y0"] + (y1 - inset) / s, 1)}


def check(flat: np.ndarray, params: dict, scale: float) -> dict:
    """Re-detect the frame in the flattened page and measure how straight and square it is."""
    if scale < 0.75:  # the detector is tuned for full-resolution rules
        flat = cv2.resize(flat, None, fx=1 / scale, fy=1 / scale, interpolation=cv2.INTER_CUBIC)
        scale = 1.0
    try:
        feats = detect_frame(flat)
    except RuntimeError as e:
        return {"error": str(e)}
    out, lines = {}, {}
    for ft in feats:
        a = np.array(ft["pts"])
        if len(a) < 20:
            out[ft["name"]] = {"error": "too few points to measure"}
            continue
        if ft["dir"] == "h":
            p = np.polyfit(a[:, 0], a[:, 1], 1)
            dev = a[:, 1] - np.polyval(p, a[:, 0])
            ang = math.degrees(math.atan(p[0]))
        else:
            p = np.polyfit(a[:, 1], a[:, 0], 1)
            dev = a[:, 0] - np.polyval(p, a[:, 1])
            ang = -math.degrees(math.atan(p[0]))
        lines[ft["name"]] = ang
        out[ft["name"]] = {"straightness_max_px": round(float(np.abs(dev).max() / scale), 2),
                           "straightness_rms_px": round(float(dev.std() / scale), 3),
                           "tilt_deg": round(ang, 4)}
    out["squareness_deg"] = round(max(abs(a) for a in lines.values()), 4) if lines else None
    out["frame_px"] = {ft["name"][6:]: round(float(np.median(np.array(ft["pts"])[:, 1 if ft["dir"] == "h" else 0])) / scale, 1)
                       for ft in feats if len(ft["pts"])}
    return out


def _write(path: Path, img: np.ndarray):
    cv2.imwrite(str(path), img, [cv2.IMWRITE_PNG_COMPRESSION, 6])
    prev = cv2.resize(img, None, fx=1200 / img.shape[0], fy=1200 / img.shape[0], interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(path.with_suffix(".preview.jpg")), prev, [cv2.IMWRITE_JPEG_QUALITY, 85])


def write_outputs(pid: str, params: dict, img: np.ndarray, scale=1.0) -> dict:
    """Write the flattened page, and, when the plate has a shading fit, the flattened page with the
    gutter shading removed (<plate>.deshaded.png)."""
    OUT.mkdir(parents=True, exist_ok=True)
    flat = render(params, img, scale)
    full = OUT / f"{pid}.png"
    _write(full, flat)
    out = {"file": str(full.relative_to(ROOT)), "size": [flat.shape[1], flat.shape[0]], "scale": scale,
           "check": check(flat, params, scale), "when": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if params.get("shading"):
        even = deshade(flat, params["shading"], params["page"])
        _write(OUT / f"{pid}.deshaded.png", even)
        out["deshaded_file"] = str((OUT / f"{pid}.deshaded.png").relative_to(ROOT))
        params["shading"]["check"] = {"before": evenness(flat), "after": evenness(even)}
    return out


def cmd_shade(pid: str):
    """Fit the gutter shading on the flattened page and write the evened page."""
    params = load_params(pid)
    flat_path = OUT / f"{pid}.png"
    img = load_bgr(pid)
    flat = cv2.imread(str(flat_path)) if flat_path.exists() else render(params, img, 1.0)
    if flat.shape[1] != int(round(params["page"]["u1"] - params["page"]["u0"])):  # page changed since the last render
        flat = render(params, img, 1.0)
    strength = (params.get("shading") or {}).get("strength", 1.0)
    params["shading"] = fit_shading(params, flat)
    params["shading"]["strength"] = strength
    params["render"] = write_outputs(pid, params, img, 1.0)
    save_params(pid, params)
    c = params["shading"]["check"]
    print(f"  paper spread across the page {c['before']['spread_pct']}% → {c['after']['spread_pct']}%; "
          f"gutter quarter {c['before']['gutter_quarter']:.3f} → {c['after']['gutter_quarter']:.3f} of the open page")


# ── Shading: the darkening into the gutter (part 2) ───────────────────────────
#
# In flat coordinates the sheet bends only across its width (the generalized cylinder), so the light
# it receives is, to a good approximation, a function of position across the sheet. That lets the
# shading be measured from all the bare paper in a column (margins and the gaps between letters) and
# divided out under the letters too. Per color channel, in logarithms:
#
#     log L(u, y) = c + g0(u) + y·g1(u) + p(y)
#
# g0 is the darkening across the sheet: free near the gutter, with knots packed where the surface
# curves, and anchored at 0 on the far side. g1 lets that darkening grow or fade from top to bottom.
# p(y) is the gentle falloff of the lights from top to bottom. Everything is linear in its
# coefficients, so the fit is a robust (iteratively reweighted) least squares on paper pixels.

def paper_mask(img: np.ndarray, chroma: np.ndarray | None = None):
    """Bare paper: the page's own color (by chromaticity, which shading barely changes) and as bright as
    the paper nearby. Ink, its halo, and dust are excluded."""
    f = img.astype(np.float32) + 1
    lum = f.mean(2)
    chrom = f / f.sum(2, keepdims=True)
    if chroma is None:
        chroma = np.median(chrom[lum > np.percentile(lum, 60)], axis=0)
    ceil = cv2.dilate(cv2.GaussianBlur(lum, (0, 0), 3), np.ones((61, 61), np.uint8))
    paper = (np.linalg.norm(chrom - chroma, axis=2) < 0.03) & (lum > 0.6 * ceil)
    ink = cv2.dilate((~paper).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    return ~ink, chroma


def _hats(x: np.ndarray, knots: np.ndarray) -> np.ndarray:
    """Piecewise-linear 'hat' basis on the knots, flat beyond the ends."""
    x = np.clip(x, knots[0], knots[-1])
    i = np.clip(np.searchsorted(knots, x) - 1, 0, len(knots) - 2)
    t = (x - knots[i]) / (knots[i + 1] - knots[i])
    B = np.zeros((len(x), len(knots)), np.float32)
    B[np.arange(len(x)), i] = 1 - t
    B[np.arange(len(x)), i + 1] = t
    return B


def shading_knots(params: dict) -> tuple[np.ndarray, np.ndarray]:
    """Knots across the sheet follow the surface: close together where it curves, sparse where it is flat."""
    pg, fr = params["page"], params["frame"]
    m = Model(params)
    u0, u1 = pg["u0"], pg["u1"]
    Xs = m.x_of_u(np.linspace(u0, u1, 400))
    curved = m.u_of_x(Xs[np.abs(np.gradient(m.spline(Xs), Xs)) > 0.002].max()) if (np.abs(np.gradient(m.spline(Xs), Xs)) > 0.002).any() else u0
    # finest at the gutter edge, where the glass edge brightens a narrow band and the paper then drops away
    ku = np.unique(np.concatenate([np.arange(u0, u0 + 150, 12), np.arange(u0 + 150, curved + 300, 30),
                                   np.arange(curved + 300, u1, 160), [u1]]))
    ky = np.linspace(pg["y0"], pg["y1"], 12)
    return ku, ky


def _design(u, y, ku, ky, yc, yh):
    yn = (y - yc) / yh
    Bu = _hats(u, ku)
    Bu1 = _hats(u, ku[::3] if len(ku) > 6 else ku)
    By = _hats(y, ky)
    # anchors: g0 and g1 are 0 at the fore-edge end; p has no constant (c carries it)
    return np.concatenate([np.ones((len(u), 1), np.float32), Bu[:, :-1], (Bu1[:, :-1] * yn[:, None]), By[:, 1:]], 1)


def fit_shading(params: dict, flat: np.ndarray, iters=2, smooth=3.0) -> dict:
    H, W = flat.shape[:2]
    pg = params["page"]
    ku, ky = shading_knots(params)
    ku1 = ku[::3] if len(ku) > 6 else ku
    yc, yh = (pg["y0"] + pg["y1"]) / 2, (pg["y1"] - pg["y0"]) / 2
    uu = pg["u0"] + (np.arange(W) + 0.5) * (pg["u1"] - pg["u0"]) / W
    yy = pg["y0"] + (np.arange(H) + 0.5) * (pg["y1"] - pg["y0"]) / H
    img = flat.astype(np.float32)
    chroma = None
    rng = np.random.default_rng(0)
    coef = None
    for it in range(iters):
        work = img if coef is None else apply_shading_field(img, shading_field({"u_knots": ku.tolist(), "u1_knots": ku1.tolist(), "y_knots": ky.tolist(), "yc": yc, "yh": yh, "coef": coef}, pg, H, W))
        mask, chroma = paper_mask(np.clip(work, 0, 255).astype(np.uint8), None if it == 0 else chroma)
        rows, cols = np.nonzero(mask)
        pick = rng.choice(len(rows), size=min(250000, len(rows)), replace=False)
        rows, cols = rows[pick], cols[pick]
        A = _design(uu[cols], yy[rows], ku, ky, yc, yh)
        # smoothness: second differences of g0, g1 and p, each in its own block
        nb = [1, len(ku) - 1, len(ku1) - 1, len(ky) - 1]
        offs = np.cumsum([0] + nb)
        P = []
        for bi in (1, 2, 3):
            n = nb[bi]
            for k in range(n - 2):
                r = np.zeros(A.shape[1], np.float32)
                r[offs[bi] + k:offs[bi] + k + 3] = (1, -2, 1)
                P.append(r)
        P = np.array(P) * smooth * math.sqrt(len(rows) / 1000)
        coef = {}
        for ci, ch in enumerate("bgr"):
            b = np.log(img[rows, cols, ci] + 1)
            w = np.ones(len(b), np.float32)
            for _ in range(4):  # Huber reweighting: ink fringes and foxing don't pull the fit
                Aw = A * w[:, None]
                x = np.linalg.lstsq(np.vstack([Aw, P]), np.concatenate([b * w, np.zeros(len(P))]), rcond=None)[0]
                r = b - A @ x
                s = 1.4826 * np.median(np.abs(r)) + 1e-6
                w = np.sqrt(np.minimum(1.0, 1.5 * s / (np.abs(r) + 1e-9))).astype(np.float32)
            coef[ch] = [round(float(v), 6) for v in x]
    # normalise to the well-lit paper: the median of the field over the outer 60% of the frame is 1,
    # so the page keeps its own color and exposure and only the unevenness is removed
    fr = params["frame"]
    ref_u = np.linspace(fr["u0"] + 0.4 * (fr["u1"] - fr["u0"]), fr["u1"], 60)
    ref_y = np.linspace(fr["y0"], fr["y1"], 60)
    Ur, Yr = np.meshgrid(ref_u, ref_y)
    Ar = _design(Ur.ravel(), Yr.ravel(), ku, ky, yc, yh)
    ref = {ch: round(float(np.median(Ar[:, 1:] @ np.array(coef[ch][1:]))), 6) for ch in "bgr"}
    sh = {"model": "log L = c + g0(u) + y*g1(u) + p(y), per channel, on bare paper in flat coordinates",
          "ref_log": ref,
          "u_knots": [round(float(v), 2) for v in ku], "u1_knots": [round(float(v), 2) for v in ku1],
          "y_knots": [round(float(v), 2) for v in ky], "yc": round(yc, 2), "yh": round(yh, 2),
          "coef": coef, "paper_chroma_bgr": [round(float(v), 5) for v in chroma], "strength": 1.0,
          "when": time.strftime("%Y-%m-%dT%H:%M:%S")}
    return sh


def shading_field(sh: dict, rect: dict, H: int, W: int) -> np.ndarray:
    """The fitted light field, normalised to 1 on the well-lit paper, as an H×W×3 array."""
    ku, ku1, ky = (np.array(sh[k]) for k in ("u_knots", "u1_knots", "y_knots"))
    uu = rect["u0"] + (np.arange(W) + 0.5) * (rect["u1"] - rect["u0"]) / W
    yy = rect["y0"] + (np.arange(H) + 0.5) * (rect["y1"] - rect["y0"]) / H
    Bu, Bu1, By = _hats(uu, ku)[:, :-1], _hats(uu, ku1)[:, :-1], _hats(yy, ky)[:, 1:]
    yn = (yy - sh["yc"]) / sh["yh"]
    out = np.empty((H, W, 3), np.float32)
    n0, n1 = Bu.shape[1], Bu1.shape[1]
    s = float(sh.get("strength", 1.0))
    for ci, ch in enumerate("bgr"):
        c = np.array(sh["coef"][ch], np.float32)
        g0 = Bu @ c[1:1 + n0]
        g1 = Bu1 @ c[1 + n0:1 + n0 + n1]
        p = By @ c[1 + n0 + n1:]
        out[..., ci] = np.exp(s * (g0[None, :] + yn[:, None] * g1[None, :] + p[:, None] - sh.get("ref_log", {}).get(ch, 0.0)))
    return out


def apply_shading_field(img: np.ndarray, field: np.ndarray) -> np.ndarray:
    return img.astype(np.float32) / field


def deshade(flat: np.ndarray, sh: dict, rect: dict) -> np.ndarray:
    H, W = flat.shape[:2]
    return np.clip(apply_shading_field(flat, shading_field(sh, rect, H, W)) + 0.5, 0, 255).astype(np.uint8)


def evenness(img: np.ndarray, chroma=None, band=40) -> dict:
    """How even the bare paper is: brightness of the paper in column bands across the page, relative to
    the well-lit side. Reported as the darkest band and the spread."""
    mask, _ = paper_mask(img, chroma)
    lum = img.astype(np.float32).mean(2)
    W = img.shape[1]
    vals = []
    for c0 in range(0, W - band, band):
        m = mask[:, c0:c0 + band]
        if m.sum() > 500:
            vals.append(float(np.median(lum[:, c0:c0 + band][m])))
    v = np.array(vals)
    ref = np.median(v[len(v) // 2:])
    v = v / ref
    return {"darkest": round(float(v.min()), 4), "spread_pct": round(float((np.percentile(v, 95) - np.percentile(v, 5)) * 100), 2),
            "gutter_quarter": round(float(v[: max(1, len(v) // 4)].mean()), 4)}


# ── Saved parameters ──────────────────────────────────────────────────────────

def params_path(pid: str) -> Path:
    return DATA / f"{pid}.json"


def load_params(pid: str) -> dict | None:
    p = params_path(pid)
    return json.loads(p.read_text()) if p.exists() else None


def save_params(pid: str, params: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    order = ["version", "plate", "image", "camera", "surface", "frame", "page", "fit", "render", "edited", "notes", "features"]
    ordered = {k: params[k] for k in order if k in params}
    ordered.update({k: v for k, v in params.items() if k not in ordered})
    text = json.dumps(ordered, indent=2)
    # keep the long point lists on one line each so the file stays readable
    for ft in ordered.get("features", []):
        pts = json.dumps(ft["pts"], indent=2)
        text = text.replace(_indent(pts, 6), json.dumps(ft["pts"], separators=(",", ":")), 1)
    params_path(pid).write_text(text + "\n")


def _indent(s: str, n: int) -> str:
    lines = s.split("\n")
    return "\n".join([lines[0]] + [" " * n + ln for ln in lines[1:]])


# ── Camera calibration, shared across plates ─────────────────────────────────

CAMERA = DATA / "_camera.json"


def load_camera() -> dict | None:
    return json.loads(CAMERA.read_text()) if CAMERA.exists() else None


def fresh_start(params: dict, f: float, k1: float | None = None) -> dict:
    """Reset pose and surface so a fit starts from a flat page facing the camera."""
    q = json.loads(json.dumps(params))
    n = len(q["surface"]["x_knots"])
    rz = q["camera"]["rot_deg"][2]
    lens = {k: q["camera"][k] for k in ("k2", "cx", "cy") if k in q["camera"]}
    q["camera"] = {"f": float(f), "k1": -0.045 * (f / 8000) ** 2 if k1 is None else k1, **lens, "rot_deg": [0.0, 0.0, rz]}
    q["surface"]["z_knots"] = [0.0] * n
    q["surface"]["anchors"] = anchors(q["surface"])
    return q


def cmd_calibrate(pids: list[str], sweep: bool, full_lens=False):
    """Fit the lens (f, k1) jointly across plates photographed together, then save it."""
    base = []
    for pid in pids:
        if load_params(pid) is None:
            cmd_detect(pid)
        base.append(load_params(pid))
    # k2 and an off-center principal point are supported, but on plates 9–12 they bought little and made
    # the fit unstable (they trade off against f and k1), so by default they stay at 0 and the image center
    lens_lock = set() if full_lens else {"k2", "pp"}
    for p in base:
        if not full_lens:
            p["camera"].update(k2=0.0, cx=p["image"]["width"] / 2, cy=p["image"]["height"] / 2)
    table = []
    if sweep:
        for f in (6000, 7000, 8000, 9000, 10000, 11000, 12500, 14000, 17000):
            o = fit_many([fresh_start(p, f) for p in base], {"f"} | lens_lock, verbose=False)
            rms = float(np.sqrt(np.mean([x["fit"]["rms_px"] ** 2 for x in o])))
            table.append({"f": f, "rms_px": round(rms, 4), "k1": o[0]["camera"]["k1"]})
            print(f"  f={f:6d}  rms {rms:.4f}")
    outs = fit_many([fresh_start(p, 9000) for p in base], lens_lock)
    c0 = outs[0]["camera"]
    cam = {"f": c0["f"], "k1": c0["k1"], "k2": c0["k2"], "cx": c0["cx"], "cy": c0["cy"],
           "plates": pids,
           "rms_px": round(float(np.sqrt(np.mean([x["fit"]["rms_px"] ** 2 for x in outs]))), 4),
           "when": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "note": "One lens photographed every plate, so f and k1 are shared. A single plate cannot separate the "
                   "focal length from the depth of the gutter; fitting several plates together can. The fit is "
                   "shallow around the minimum (see sweep), so treat f as known to roughly ±15%."}
    if table:
        cam["sweep"] = table
    elif load_camera() and load_camera().get("sweep"):
        cam["sweep"] = load_camera()["sweep"]
    DATA.mkdir(parents=True, exist_ok=True)
    CAMERA.write_text(json.dumps(cam, indent=2) + "\n")
    for o in outs:
        save_params(o["plate"], o)
    print(f"  camera: f={cam['f']:.0f} px, k1={cam['k1']:+.5f}, rms {cam['rms_px']} px → {CAMERA.relative_to(ROOT)}")


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_detect(pid: str):
    img = load_bgr(pid)
    feats = detect_frame(img)
    params = load_params(pid)
    if params is None:
        params = initial_params(pid, img.shape, feats)
    else:
        params["features"] = [f for f in params["features"] if f.get("source") != "auto"] + feats
    save_params(pid, params)
    print(f"  {pid}: " + ", ".join(f"{f['name']} {len(f['pts'])} pts" for f in feats))


def cmd_fit(pid: str, lock: set[str], free_camera=False, fresh=False):
    params = load_params(pid)
    if params is None:
        cmd_detect(pid)
        params = load_params(pid)
    cam = load_camera()
    if cam and not free_camera:  # use the shared lens calibration and hold it fixed
        for k in ("f", "k1", "k2", "cx", "cy"):
            params["camera"][k] = cam[k]
        lock = lock | {"f", "k1", "k2", "pp"}
    if fresh or params.get("fit") is None:
        params = fresh_start(params, params["camera"]["f"], params["camera"]["k1"])
    params = fit(params, lock)
    save_params(pid, params)


def cmd_render(pid: str, scale: float, page: bool):
    params = load_params(pid)
    img = load_bgr(pid)
    if page or params.get("page") is None or params["page"].get("auto", True):
        params["page"] = {**auto_page(params, img), "auto": True}
    params["render"] = write_outputs(pid, params, img, scale)
    save_params(pid, params)
    c = params["render"]["check"]
    worst = max((v["straightness_max_px"] for k, v in c.items() if isinstance(v, dict) and "straightness_max_px" in v), default=None)
    print(f"  wrote {params['render']['file']} {params['render']['size']}; rules straight to ≤{worst} px, "
          f"square to {c.get('squareness_deg')}°")


# ── The editor's server ───────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body: bytes, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj).encode())

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"null")

    def do_GET(self):
        url = urlparse(self.path)
        parts = url.path.strip("/").split("/")
        try:
            if url.path in ("/", "/editor.html"):
                return self._send(200, (TOOL / "editor.html").read_bytes(), "text/html; charset=utf-8")
            if parts[:2] == ["api", "plates"]:
                return self._json([{"id": p, "fitted": bool((load_params(p) or {}).get("fit")),
                                    "rms": ((load_params(p) or {}).get("fit") or {}).get("rms_px")} for p in plate_ids()])
            if parts[:2] == ["api", "camera"]:
                cam = load_camera()
                return self._json(cam) if cam else self._json({"error": "no shared calibration yet"}, 404)
            if parts[:2] == ["api", "plate"] and len(parts) == 3:
                prm = load_params(parts[2])
                return self._json(prm) if prm else self._json({"error": "no params yet"}, 404)
            if parts[0] == "img" and len(parts) == 2:
                return self._send(200, display_jpeg(parts[1].removesuffix(".jpg")).read_bytes(), "image/jpeg")
            if parts[0] == "preview" and len(parts) == 2:
                return self._send(200, (CACHE / parts[1]).read_bytes(), "image/jpeg")
            self._json({"error": "not found"}, 404)
        except Exception as e:  # report, don't crash the server
            self._json({"error": f"{type(e).__name__}: {e}"}, 500)

    def do_PUT(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        try:
            if parts[:2] == ["api", "plate"] and len(parts) == 3:
                prm = self._body()
                prm["edited"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                save_params(parts[2], prm)
                return self._json({"ok": True, "edited": prm["edited"]})
            self._json({"error": "not found"}, 404)
        except Exception as e:
            self._json({"error": f"{type(e).__name__}: {e}"}, 500)

    def do_POST(self):
        url = urlparse(self.path)
        parts = url.path.strip("/").split("/")
        q = parse_qs(url.query)
        try:
            pid = parts[2]
            if parts[:2] == ["api", "plate"] and parts[3:] == ["detect"]:
                img = load_bgr(pid)
                prm = self._body() or load_params(pid)
                feats = detect_frame(img)
                if prm is None:
                    prm = initial_params(pid, img.shape, feats)
                else:
                    prm["features"] = [f for f in prm["features"] if f.get("source") != "auto"] + feats
                return self._json(prm)
            if parts[:2] == ["api", "plate"] and parts[3:] == ["fit"]:
                body = self._body()
                prm, lock = body["params"], set(body.get("lock", []))
                if prm is None:
                    img = load_bgr(pid)
                    prm = initial_params(pid, img.shape, detect_frame(img))
                return self._json(fit(prm, lock, verbose=False))
            if parts[:2] == ["api", "plate"] and parts[3:] == ["shade"]:
                prm = self._body()
                img = load_bgr(pid)
                flat = render(prm, img, 0.5)  # the light field is smooth; half size is plenty and quick
                strength = (prm.get("shading") or {}).get("strength", 1.0)
                prm["shading"] = fit_shading(prm, flat)
                prm["shading"]["strength"] = strength
                even = deshade(flat, prm["shading"], prm["page"])
                prm["shading"]["check"] = {"before": evenness(flat), "after": evenness(even)}
                name = f"{pid}.flat.jpg"
                cv2.imwrite(str(CACHE / name), cv2.resize(even, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 88])
                return self._json({"params": prm, "url": f"/preview/{name}?t={time.time()}"})
            if parts[:2] == ["api", "plate"] and parts[3:] == ["render"]:
                prm = self._body()
                scale = float(q.get("scale", ["0.25"])[0])
                img = load_bgr(pid)
                if q.get("page", ["0"])[0] == "1":
                    prm["page"] = {**auto_page(prm, img), "auto": True}
                if scale >= 1:
                    prm["render"] = write_outputs(pid, prm, img, scale)
                    save_params(pid, prm)
                    flat = cv2.imread(str(OUT / (f"{pid}.deshaded.preview.jpg" if prm.get("shading") else f"{pid}.preview.jpg")))
                    name = f"{pid}.flat.jpg"
                    cv2.imwrite(str(CACHE / name), flat, [cv2.IMWRITE_JPEG_QUALITY, 88])
                    return self._json({"url": f"/preview/{name}?t={time.time()}", "params": prm})
                flat = render(prm, img, scale)
                if q.get("deshade", ["0"])[0] == "1" and prm.get("shading"):
                    flat = deshade(flat, prm["shading"], prm["page"])
                name = f"{pid}.flat.jpg"
                cv2.imwrite(str(CACHE / name), flat, [cv2.IMWRITE_JPEG_QUALITY, 88])
                return self._json({"url": f"/preview/{name}?t={time.time()}", "page": prm["page"], "check": check(flat, prm, scale)})
            self._json({"error": "not found"}, 404)
        except Exception as e:
            self._json({"error": f"{type(e).__name__}: {e}"}, 500)


def cmd_serve(port: int):
    CACHE.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Plate flattener: http://127.0.0.1:{port}/  (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("detect", "fit", "render", "shade", "all", "calibrate"):
        s = sub.add_parser(name)
        s.add_argument("plates", nargs="+", help="plate ids or number prefixes, e.g. 09 or 09-alphabets-no-1")
        if name in ("fit", "all"):
            s.add_argument("--lock", default="", help="comma list of f,k1,k2,pp,rotation,surface to hold fixed")
            s.add_argument("--free-camera", action="store_true", help="fit f and k1 for this plate instead of using _camera.json")
            s.add_argument("--fresh", action="store_true", help="start from a flat page instead of the saved fit")
        if name == "calibrate":
            s.add_argument("--sweep", action="store_true", help="also tabulate the fit against focal length")
            s.add_argument("--full-lens", action="store_true", help="also fit k2 and the principal point")
        if name in ("render", "all"):
            s.add_argument("--scale", type=float, default=1.0)
            s.add_argument("--auto-page", action="store_true", help="re-detect the page edges")
    s = sub.add_parser("serve")
    s.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    if a.cmd == "serve":
        return cmd_serve(a.port)
    if a.cmd == "calibrate":
        return cmd_calibrate(resolve(a.plates), a.sweep, a.full_lens)
    for pid in resolve(a.plates):
        print(pid)
        if a.cmd in ("detect", "all"):
            cmd_detect(pid)
        if a.cmd in ("fit", "all"):
            cmd_fit(pid, {x for x in a.lock.split(",") if x}, a.free_camera, a.fresh)
        if a.cmd in ("render", "all"):
            cmd_render(pid, a.scale, a.auto_page)
        if a.cmd in ("shade", "all"):
            cmd_shade(pid)


if __name__ == "__main__":
    main()
