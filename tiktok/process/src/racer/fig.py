"""«Блискавка 95»: розфарбовка деталей, вирівнювання боковин (лінія низу коліс — горизонтально) і 3D-модель.
python3 -I fig.py BUILD_FIG_DIR   (перед цим netx.py вже зробив racer-{side,strip,side2}-{line,mask}.png)
Результат: racer-*-flat.png (деталь як на аркуші, для 2D), racer-*-color.png (текстура 3D), racer.json"""
import sys, os, json, subprocess, cv2, numpy as np
B = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.abspath(os.path.join(HERE, '../../../../instagram/reels-v3/src/fig'))
CROPS = {'racer-side': (50, 304, 211, 704), 'racer-strip': (218, 254, 382, 794), 'racer-side2': (384, 304, 545, 704)}
cfg = json.load(open(os.environ.get('COLORS', f'{HERE}/colors.json')))   # COLORS — інша розфарбовка (напр. real/colors.json)
seeds = {}
for p, c in cfg.items():
    if p == '_': continue
    line = cv2.imread(f'{B}/{p}-line.png', 0); mask = cv2.imread(f'{B}/{p}-mask.png', 0) > 0
    free = (line > 128) & mask; ys, xs = np.where(free)
    snap = lambda x, y: (lambda i: [int(xs[i]), int(ys[i])])(np.argmin((xs - x) ** 2 + (ys - y) ** 2))
    s = dict(default=c['default'], angle=c['angle'], seeds=[snap(x, y) + [col] for x, y, col in c['seeds']], rects=c.get('rects', []))
    # колеса: точне коло з Хафа біля заданого центру → шина темна, диск світло-сірий
    s['circles'] = []
    sm = cv2.resize(line, None, fx=.25, fy=.25)
    cs = cv2.HoughCircles(cv2.GaussianBlur(sm, (0, 0), 2), cv2.HOUGH_GRADIENT, 1.2, 100, param1=120, param2=35, minRadius=45, maxRadius=70)
    for wx, wy in c.get('wheels', []):
        cx, cy, r = min((cs[0] * 4).tolist(), key=lambda q: (q[0] - wx) ** 2 + (q[1] - wy) ** 2)
        s['circles'] += [[cx, cy, 0, r * .6, '#c9ccd6'], [cx, cy, r * .6, r * 1.02, '#34343c']]
    seeds[p] = s
json.dump(seeds, open(f'{B}/racer-seeds.json', 'w'))
for p in CROPS: subprocess.run(['python3', '-I', f'{FIG}/colorize.py', f'{B}/{p}', f'{B}/racer-seeds.json', p], check=True)

def rot(im, deg, interp=cv2.INTER_LINEAR):
    h, w = im.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1)
    c, s = abs(M[0, 0]), abs(M[0, 1]); W, H = int(np.ceil(h * s + w * c)), int(np.ceil(h * c + w * s))
    M[0, 2] += (W - w) / 2; M[1, 2] += (H - h) / 2
    return cv2.warpAffine(im, M, (W, H), flags=interp, borderValue=0)
def ground_angle(m):
    """кут нижнього ребра опуклої оболонки, що торкається обох коліс (у градусах, для cv2 — проти год. стрілки)"""
    cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    h = cv2.convexHull(max(cs, key=cv2.contourArea))[:, 0, :].astype(float); H, W = m.shape
    best = max(((h[i], h[(i + 1) % len(h)]) for i in range(len(h))), key=lambda e: abs(e[1][0] - e[0][0]) * (min(e[0][1], e[1][1]) > H * .55))
    (x0, y0), (x1, y1) = best if best[0][0] < best[1][0] else best[::-1]
    return float(np.degrees(np.arctan2(y1 - y0, x1 - x0)))
flat = {}
for p, how in [('racer-side', 'ccw'), ('racer-side2', 'T')]:
    col = cv2.imread(f'{B}/{p}-color.png', cv2.IMREAD_UNCHANGED); m = cv2.imread(f'{B}/{p}-mask.png', 0)
    cv2.imwrite(f'{B}/{p}-flat.png', col)
    f = (lambda a: cv2.rotate(a, cv2.ROTATE_90_COUNTERCLOCKWISE)) if how == 'ccw' else cv2.transpose
    tc, tm = f(col), f(m)
    a = ground_angle(tm > 0)
    tc, tm = rot(tc, a), rot(tm, a, cv2.INTER_NEAREST)
    print(p, 'нахил', round(a, 2), '→', round(ground_angle(tm > 0), 2))
    cv2.imwrite(f'{B}/{p}-color.png', tc)
    if p == 'racer-side': cv2.imwrite(f'{B}/{p}-mask.png', cv2.rotate(tm, cv2.ROTATE_90_CLOCKWISE))   # model.py сам поверне ccw
    x0, y0, x1, y1 = CROPS[p]
    flat[p] = dict(c=[(x0 + x1) / 2, (y0 + y1) / 2], ang=float(np.radians(a)), how=how)
cv2.imwrite(f'{B}/racer-strip-flat.png', cv2.imread(f'{B}/racer-strip-color.png', cv2.IMREAD_UNCHANGED))
subprocess.run(['python3', '-I', f'{FIG}/model.py', f'{B}/racer-side', f'{B}/racer-strip', f'{B}/racer.json', '160'], check=True)
d = json.load(open(f'{B}/racer.json')); d['flat'] = {'side': flat['racer-side'], 'side2': flat['racer-side2']}
json.dump(d, open(f'{B}/racer.json', 'w'), indent=1)
json.dump({'extras': []}, open(f'{B}/racer.extra.json', 'w'))
