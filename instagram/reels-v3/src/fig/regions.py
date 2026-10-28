"""Нумерує замкнені області боковини (для вибору кольорів). python3 regions.py PREFIX"""
import sys, cv2, numpy as np
p = sys.argv[1]
line = cv2.imread(p + '-line.png', 0); mask = cv2.imread(p + '-mask.png', 0) > 0
free = ((line > 128) & mask).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(free, connectivity=4)
np.save(p + '-labels.npy', lab)
dbg = cv2.cvtColor(line, cv2.COLOR_GRAY2BGR)
rng = np.random.default_rng(1)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] < 400: continue
    dbg[lab == i] = rng.integers(120, 255, 3)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] < 400: continue
    x, y = map(int, cen[i]); cv2.putText(dbg, str(i), (x - 20, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 0), 4)
cv2.imwrite(p + '-regions.jpg', cv2.resize(dbg, None, fx=0.45, fy=0.45))
