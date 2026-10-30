"""Готує ассети для сцен з результатів instagram/reels-v3/src/fig/make_figs.sh:
деталі машинок «чорно-білий контур» і «розфарбована» (горизонтально, RGBA, ½ розміру).
python3 -I prep.py FIG_BUILD OUT"""
import sys, os, cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for p in ['police-side', 'police-strip', 'hip-side', 'hip-strip']:
    c = cv2.imread(f'{src}/{p}-color.png', cv2.IMREAD_UNCHANGED)
    line = cv2.imread(f'{src}/{p}-line.png', 0)
    if not p.endswith('strip'): line = cv2.rotate(line, cv2.ROTATE_90_COUNTERCLOCKWISE)  # як color (model.py)
    a = c[..., 3]
    bw = np.dstack([line, line, line, a])           # білий папір + контури, та сама форма
    k = 0.5
    for nm, im in [('color', c), ('line', bw)]:
        cv2.imwrite(f'{out}/{p}-{nm}.png', cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_AREA))
    print(p, c.shape)
