#!/bin/bash
# Генерує 3D-фігурки з шаблонів (papermagic-site/img/sheet-*.jpg) і рендерить анімації обертання.
# Результат: instagram/reels-v3/build/fig/{police,hip}.json, текстури й кадри tt/{police,hip}/f*.png
set -e
cd "$(dirname "$0")"
R=$(cd ../../../.. && pwd); I=$R/papermagic-site/img; B=$R/instagram/reels-v3/build/fig
mkdir -p $B
# поліцейське авто (лист 3): ліва боковина, стрічка-дах, права боковина
python3 -I net.py $I/sheet-3.jpg 50 290 212 700 $B/police-side
python3 -I net.py $I/sheet-3.jpg 216 222 348 786 $B/police-strip rect
python3 -I net.py $I/sheet-3.jpg 353 290 560 700 $B/police-side2 tr
python3 -I - $B/police-side2 <<'PY'
import sys, cv2, numpy as np
p = sys.argv[1]; m = cv2.imread(p + '-mask.png', 0); k = 1 / 0.45
m[:int(478 * k), :int(30 * k)] = 0; m[int(822 * k):, :int(30 * k)] = 0   # прибрати клапани стрічки
n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0).astype(np.uint8)); i = 1 + np.argmax(st[1:, 4])
cv2.imwrite(p + '-mask.png', ((lab == i) * 255).astype(np.uint8))
PY
# хіпі-фургон (лист 1)
python3 -I net.py $I/sheet-1.jpg 45 350 226 675 $B/hip-side
python3 -I net.py $I/sheet-1.jpg 238 218 360 767 $B/hip-strip rect
python3 -I net.py $I/sheet-1.jpg 362 350 565 675 $B/hip-side2 tr
python3 -I - $B/hip-side2 <<'PY'
import sys, cv2
p = sys.argv[1]; m = cv2.imread(p + '-mask.png', 0); k = 1 / 0.45
m[:, :int(22 * k)] = 0
for cx, cy in [(430, 243), (430, 595)]: cv2.circle(m, (int(cx * k), int(cy * k)), int(63 * k), 255, -1)   # колеса в масці
cv2.imwrite(p + '-mask.png', m)
PY
for p in police-side police-strip police-side2 hip-side hip-side2 hip-strip; do python3 -I colorize.py $B/$p seeds.json $p; done
python3 -I - $B/police-side2-color.png <<'PY'
import sys, cv2
f = sys.argv[1]; a = cv2.imread(f, cv2.IMREAD_UNCHANGED); cv2.imwrite(f, a[61:])   # зрізати залишки клапанів над дахом
PY
python3 -I model.py $B/police-side $B/police-strip $B/police.json 128
python3 -I model.py $B/hip-side $B/hip-strip $B/hip.json 122
cp police.extra.json $B/police.extra.json
# обертання: 150 кадрів, плавно (ease in-out)
python3 -I - $B <<'PY'
import sys, json, math
B = sys.argv[1]; N = 150
for nm, a, b in [('police', 0.15, 1.55), ('hip', 0.25, 1.65)]:
    fr = [{'name': 'f%04d' % i, 'rot': a + (b - a) * (0.5 - 0.5 * math.cos(math.pi * i / (N - 1))), 'el': 0.36, 'dist': 980, 'lookY': 70} for i in range(N)]
    json.dump(fr, open(f'{B}/tt-{nm}.json', 'w'))
PY
node render3d.js $B/police.json $B/tt/police 1080 1080 $B/tt-police.json
node render3d.js $B/hip.json $B/tt/hip 1080 1080 $B/tt-hip.json
