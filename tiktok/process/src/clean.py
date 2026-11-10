"""Чистий аркуш для процес-відео: замальовує білим друкований логотип, блок «Інструкція…» і напис на стрічці —
у кадрі не має бути жодного тексту чи лого. Рамки — у пікселях листа 595×842 (src/figs.json → clean).
python3 -I clean.py SHEET OUT.png '[[x0,y0,x1,y1],...]'"""
import sys, json, cv2
im = cv2.imread(sys.argv[1]); k = im.shape[1] / 595
for x0, y0, x1, y1 in json.loads(sys.argv[3]):
    im[int(y0 * k):int(y1 * k), int(x0 * k):int(x1 * k)] = 255
cv2.imwrite(sys.argv[2], im)
