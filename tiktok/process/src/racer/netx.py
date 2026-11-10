"""Як instagram/reels-v3/src/fig/net.py, але з аркуша високої роздільності (координати — у пікселях листа 595×842).
python3 -I netx.py SHEET_HI x0 y0 x1 y1 OUT_PREFIX [L|R|rect]  → OUT-line.png, OUT-mask.png (масштаб ×6 від 595)"""
import sys, cv2, numpy as np
sheet, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
mode = sys.argv[7] if len(sys.argv) > 7 else ''
SC = 6
im = cv2.imread(sheet, cv2.IMREAD_GRAYSCALE); R = im.shape[1] / 595
w, h = (x1 - x0) * SC, (y1 - y0) * SC
M = np.float32([[R / SC, 0, x0 * R], [0, R / SC, y0 * R]])     # піксель кропу ×6 → піксель аркуша
big = cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP, borderValue=255)
big = cv2.GaussianBlur(big, (0, 0), 1.2)
ink = (big < 170).astype(np.uint8)
cv2.rectangle(ink, (0, 0), (w - 1, h - 1), 1, 2)
ff = (1 - ink).copy(); m = np.zeros((h + 2, w + 2), np.uint8)
# край кропу з боку стрічки (mode 'L' — стрічка праворуч, 'R' — ліворуч) не беремо: там деталь доходить до краю
xs = [6] if mode == 'L' else [w - 7] if mode == 'R' else [6, w - 7]
border = [(x, y) for x in range(6, w - 6, 8) for y in (6, h - 7)] + [(x, y) for y in range(6, h - 6, 8) for x in xs]
for sd in border:      # «зовні» — усе, що торкається краю кропу (кишені між деталлю й клапанами стрічки теж)
    if ff[sd[1], sd[0]] == 1: cv2.floodFill(ff, m, sd, 2)
mask = (ff != 2).astype(np.uint8)
if mode == 'rect': mask[:] = 1
cv2.rectangle(mask, (0, 0), (w - 1, h - 1), 0, 3)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
mask = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
v = np.clip((big.astype(np.float32) - 140) / 60, 0, 1)
cv2.imwrite(out + '-line.png', (v * v * (3 - 2 * v) * 255).astype(np.uint8))
cv2.imwrite(out + '-mask.png', mask * 255)
dbg = cv2.cvtColor(big, cv2.COLOR_GRAY2BGR); dbg[mask > 0] = (dbg[mask > 0] * 0.6 + np.array([80, 160, 255]) * 0.4).astype(np.uint8)
cv2.imwrite(out + '-debug.jpg', cv2.resize(dbg, None, fx=0.25, fy=0.25))
print(out, w, h)
