"""Розфарбовує деталь шаблону «кольоровими олівцями».
python3 colorize.py PREFIX seeds.json KEY  →  PREFIX-color.png (RGBA, альфа = маска деталі)
seeds.json: {KEY: {"default": "#fff", "seeds": [[x, y, "#hex"], ...], "rects": [[x0,y0,x1,y1,maxArea,"#hex"]]}}"""
import sys, json, cv2, numpy as np
p, sj, key = sys.argv[1:4]
cfg = json.load(open(sj))[key]
line = cv2.imread(p + '-line.png', 0); mask = cv2.imread(p + '-mask.png', 0) > 0
h, w = line.shape
free = ((line > 128) & mask).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(free, connectivity=4)
hexc = lambda s: np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
col = np.zeros((n, 3), np.float32); col[:] = hexc(cfg.get('default', '#ffffff'))
for x0, y0, x1, y1, amax, c in cfg.get('rects', []):
    for i in range(1, n):
        cx, cy = cen[i]
        if x0 <= cx <= x1 and y0 <= cy <= y1 and st[i, cv2.CC_STAT_AREA] <= amax: col[i] = hexc(c)
for x, y, c in cfg['seeds']:
    i = lab[int(y), int(x)]
    if i: col[i] = hexc(c)
rgb = col[lab]
yy0, xx0 = np.mgrid[0:h, 0:w]
for cx, cy, r0, r1, c in cfg.get('circles', []):
    d = np.hypot(xx0 - cx, yy0 - cy); ring = (d >= r0) & (d <= r1) & (free > 0)
    rgb[ring] = hexc(c)
rng = np.random.default_rng(len(key))
# штрихування олівцем: смуги під кутом + шум, кожна область — трохи інший тиск
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
ang = np.deg2rad(cfg.get('angle', 32))
u = xx * np.cos(ang) + yy * np.sin(ang)
noise = cv2.resize(rng.random((h // 6 + 1, w // 6 + 1)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
fine = cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 0.8)
stroke = 0.5 + 0.5 * np.sin(u * 0.55 + noise * 7.0)
press = 0.72 + 0.28 * cv2.resize(rng.random((h // 60 + 2, w // 60 + 2)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
cover = np.clip(press * (0.66 + 0.34 * stroke) - 0.25 * (fine - 0.5), 0, 1)[..., None]
paper = np.array([250, 248, 243], np.float32)
white = (np.abs(rgb - 255).sum(-1, keepdims=True) < 8)
out = np.where(white, paper - 6 * (fine[..., None] - 0.5), paper * (1 - cover) + rgb * cover)
# колір трохи заходить за лінії й не доходить до країв — як у дитини
edge = cv2.GaussianBlur((line < 128).astype(np.float32), (0, 0), 1.2)[..., None]
ink = (1 - np.clip((255 - line.astype(np.float32)) / 255 * 1.1, 0, 1))[..., None]
out = out * (0.25 + 0.75 * ink) * (1 - 0.06 * edge)
out = np.clip(out, 0, 255).astype(np.uint8)
a = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 0.7)
rgba = np.dstack([out[..., ::-1], (a * 255).astype(np.uint8)])
rot = cfg.get('rotate')  # 'ccw' | 'cw' | None
if rot == 'ccw': rgba = cv2.rotate(rgba, cv2.ROTATE_90_COUNTERCLOCKWISE)
if rot == 'transpose': rgba = cv2.transpose(rgba)
if rot == 'cw': rgba = cv2.rotate(rgba, cv2.ROTATE_90_CLOCKWISE)
cv2.imwrite(p + '-color.png', rgba)
cv2.imwrite(p + '-color-prev.jpg', cv2.resize(cv2.cvtColor(rgba, cv2.COLOR_BGRA2BGR), None, fx=0.35, fy=0.35))
print(p, rgba.shape)
