"""Виділяє боковину паперової машинки з шаблону: маска, контур профілю.
python3 net.py SHEET x0 y0 x1 y1 OUT_PREFIX  (координати в пікселях листа 595×842)"""
import sys, json
import cv2, numpy as np
sheet, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
SC = 6  # апскейл: лінії стають чіткими після порогу
im = cv2.imread(sheet, cv2.IMREAD_GRAYSCALE)[y0:y1, x0:x1]
big = cv2.resize(im, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)
big = cv2.GaussianBlur(big, (0, 0), SC * 0.35)
ink = (big < 170).astype(np.uint8)
# замикаємо краї кропу лінією, щоб боковина не «витікала» в сусідні деталі
h, w = ink.shape
cv2.rectangle(ink, (0, 0), (w - 1, h - 1), 1, 2)
inner = 1 - ink
ff = inner.copy(); m = np.zeros((h + 2, w + 2), np.uint8)
seed = (w - 8, 8) if len(sys.argv) > 7 and sys.argv[7] == 'tr' else (6, 6)
cv2.floodFill(ff, m, seed, 2)            # зовнішній простір (з урахуванням рамки — всередині рамки)
mask = ((ff != 2)).astype(np.uint8)
if len(sys.argv) > 7 and sys.argv[7] == 'rect': mask[:] = 1
cv2.rectangle(mask, (0, 0), (w - 1, h - 1), 0, 3)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
big_i = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); mask = (lab == big_i).astype(np.uint8)
cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cs, key=cv2.contourArea)[:, 0, :]
cv2.imwrite(out + '-line.png', 255 - (big < 170).astype(np.uint8) * 255)
cv2.imwrite(out + '-mask.png', mask * 255)
json.dump({'scale': SC, 'size': [w, h], 'contour': c[::4].tolist()}, open(out + '-contour.json', 'w'))
dbg = cv2.cvtColor(big, cv2.COLOR_GRAY2BGR); dbg[mask > 0] = (dbg[mask > 0] * 0.6 + np.array([80, 160, 255]) * 0.4).astype(np.uint8)
cv2.imwrite(out + '-debug.jpg', cv2.resize(dbg, None, fx=0.5, fy=0.5))
print(out, w, h, len(c))
