"""Ассети процес-відео з чистого аркуша й розфарбованих деталей (figs.sh).
python3 -I prep.py SHEET_CLEAN.png FIG_DIR OUT_DIR
OUT: line.png (чорно-білий аркуш ×3), color.png (аркуш з розфарбованими деталями), rest.png (аркуш з дірками),
     part-N.png (вирізані деталі), reveal-N.png (порядок розфарбовування, 0…255), assets.json (рамки, контури)"""
import sys, os, json, cv2, numpy as np
sheet, fig, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
K = 3                                    # масштаб відносно листа 595×842
g = cv2.imread(sheet, 0)
big = cv2.GaussianBlur(cv2.resize(g, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC), (0, 0), 6 * .35).astype(np.float32)
v = np.clip((big - 140) / 60, 0, 1); v = v * v * (3 - 2 * v)          # чіткі лінії з м'яким краєм
line = cv2.resize((v * 255).astype(np.uint8), None, fx=K / 6, fy=K / 6, interpolation=cv2.INTER_AREA)
H, W = line.shape
paper = np.dstack([line] * 3).astype(np.float32)
cv2.imwrite(f'{out}/line.png', paper.astype(np.uint8))

def load(nm, undo, dx=0):
    a = cv2.imread(f'{fig}/{nm}-color.png', cv2.IMREAD_UNCHANGED)
    if undo == 'cw': a = cv2.rotate(a, cv2.ROTATE_90_CLOCKWISE)
    if undo == 'T': a = cv2.transpose(a)
    return cv2.resize(a, None, fx=K / 6, fy=K / 6, interpolation=cv2.INTER_AREA), dx * K / 6
parts = [('police-side', 'cw', 50, 290, 0), ('police-strip', None, 216, 222, 0), ('police-side2', 'T', 353, 290, 61)]
color = paper.copy(); alphas = []; meta = []
rng = np.random.default_rng(7)
for i, (nm, undo, sx, sy, dx) in enumerate(parts):
    im, ox = load(nm, undo, dx)
    x0, y0 = int(round(sx * K + ox)), int(sy * K); h, w = im.shape[:2]
    A = np.zeros((H, W), np.float32); A[y0:y0 + h, x0:x0 + w] = im[..., 3] / 255
    C = np.zeros((H, W, 3), np.float32); C[y0:y0 + h, x0:x0 + w] = im[..., :3]
    color = color * (1 - A[..., None]) + C * A[..., None]
    alphas.append(A)
    ys, xs = np.where(A > .5); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    # порядок розфарбовування: смуги зверху вниз, «змійкою», з шумом на краю штриха
    nb = 9 if i != 1 else 12
    yy, xx = np.mgrid[by0:by1, bx0:bx1].astype(np.float32)
    b = np.minimum(((yy - by0) / (by1 - by0) * nb).astype(int), nb - 1)
    u = (xx - bx0) / (bx1 - bx0); p = np.where(b % 2 == 0, u, 1 - u)
    nz = cv2.resize(rng.random(((by1 - by0) // 18 + 2, (bx1 - bx0) // 18 + 2)).astype(np.float32), (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_CUBIC)
    t = np.clip((b + p + (nz - .5) * .9) / nb, 0, 1)
    rv = np.full((by1 - by0, bx1 - bx0, 4), 0, np.uint8)
    rv[..., 0] = rv[..., 1] = rv[..., 2] = (t * 254).astype(np.uint8); rv[..., 3] = (A[by0:by1, bx0:bx1] * 255).astype(np.uint8)
    cv2.imwrite(f'{out}/reveal-{i}.png', rv)
    # контур для ножиць (рівномірно розставлені точки)
    cs, _ = cv2.findContours((A > .5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(np.float32)
    c = cv2.approxPolyDP(c.reshape(-1, 1, 2), 2.0, True)[:, 0, :]
    c = np.vstack([c, c[:1]]); seg = np.hypot(*np.diff(c, axis=0).T); s = np.concatenate([[0], np.cumsum(seg)])
    st = np.argmin(c[:-1, 0] + c[:-1, 1])                 # старт біля лівого верхнього кута
    n = 240; ss = (s[st] + np.linspace(0, s[-1], n, endpoint=False)) % s[-1]
    pts = np.stack([np.interp(ss, s, c[:, 0]), np.interp(ss, s, c[:, 1])], 1)
    meta.append(dict(name=nm, box=[int(bx0), int(by0), int(bx1 - bx0), int(by1 - by0)], nb=nb, cut=np.round(pts, 1).tolist()))
color = np.clip(color, 0, 255).astype(np.uint8)
cv2.imwrite(f'{out}/color.png', color)
for i, A in enumerate(alphas):
    x, y, w, h = meta[i]['box']
    cv2.imwrite(f'{out}/part-{i}.png', np.dstack([color[y:y + h, x:x + w], (A[y:y + h, x:x + w] * 255).astype(np.uint8)]))
hole = cv2.dilate((sum(alphas) > .05).astype(np.uint8), np.ones((5, 5), np.uint8))
cv2.imwrite(f'{out}/rest.png', np.dstack([color, (1 - hole) * 255]))
json.dump(dict(W=W, H=H, parts=meta), open(f'{out}/assets.json', 'w'))
print('assets', W, H, [m['box'] for m in meta])
