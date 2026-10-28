"""Профіль паперової машинки з маски боковини → JSON для fig3d.html.
python3 model.py PREFIX_SIDE PREFIX_STRIP OUT.json width [extra.json]"""
import sys, json, cv2, numpy as np
ps, pt, out, width = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
extra = json.load(open(sys.argv[5])) if len(sys.argv) > 5 else {}
SC = 6
m = cv2.imread(ps + '-mask.png', 0) > 0
m = cv2.rotate(m.astype(np.uint8), cv2.ROTATE_90_COUNTERCLOCKWISE) > 0   # так само, як текстура (ccw)
H, L = m.shape
cols = np.where(m.any(0))[0]
x0, x1 = cols[0], cols[-1]
top = np.array([np.argmax(m[:, x]) for x in range(L)])               # перший піксель маски зверху
bot = np.array([H - 1 - np.argmax(m[::-1, x]) for x in range(L)])
# поріг (рівень порога/днища): медіана нижнього краю між колесами
mid = slice(x0 + (x1 - x0) // 3, x1 - (x1 - x0) // 3)
sill = int(np.median(bot[mid]))
pts = [(x0 + 2, sill)]
for x in range(x0 + 2, x1 - 1, 3): pts.append((x, top[x]))
pts.append((x1 - 2, sill))
poly = np.array(pts, np.float32).reshape(-1, 1, 2)
simp = cv2.approxPolyDP(poly, 2.2 * SC, False)[:, 0, :]
# у одиниці «пікселі листа», y догори, x від переду
path = [[float(x / SC), float((H - y) / SC)] for x, y in simp]
strip = cv2.imread(pt + '-color.png', cv2.IMREAD_UNCHANGED)
d = dict(L=L / SC, H=H / SC, width=width, sill=(H - sill) / SC, wheelBottom=(H - bot.max()) / SC,
         path=path, stripLen=strip.shape[0] / SC, stripW=strip.shape[1] / SC,
         side=ps.split('/')[-1] + '-color.png', strip=pt.split('/')[-1] + '-color.png', **extra)
def bbox(f):
    a = cv2.imread(f, cv2.IMREAD_UNCHANGED)[..., 3] > 128
    ys, xs = np.where(a); hh, ww = a.shape
    return dict(w=ww / SC, h=hh / SC, x0=xs.min() / SC, x1=xs.max() / SC, yTop=ys.min() / SC, yBot=ys.max() / SC)
import os
d['sideBox'] = bbox(ps + '-color.png')
if os.path.exists(ps + '2-color.png'):
    d['side2'] = ps.split('/')[-1] + '2-color.png'; d['side2Box'] = bbox(ps + '2-color.png')
arc = sum(np.hypot(*np.subtract(path[i + 1], path[i])) for i in range(len(path) - 1))
d['arc'] = arc
json.dump(d, open(out, 'w'), indent=1)
print(out, 'L', round(L / SC), 'H', round(H / SC), 'arc', round(arc), 'stripLen', round(d['stripLen']), 'pts', len(path))
