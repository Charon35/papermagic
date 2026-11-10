#!/bin/bash
# 3D-модель поліцейської машинки з ОЧИЩЕНОГО аркуша (той самий конвеєр, що instagram/reels-v3/src/fig/make_figs.sh, лише police)
# bash figs.sh SHEET_CLEAN.png OUT_DIR
set -e
F=$(cd "$(dirname "$0")/../../../instagram/reels-v3/src/fig" && pwd); S=$1; B=$2
mkdir -p $B
python3 -I $F/net.py $S 50 290 212 700 $B/police-side
python3 -I $F/net.py $S 216 222 348 786 $B/police-strip rect
python3 -I $F/net.py $S 353 290 560 700 $B/police-side2 tr
python3 -I - $B/police-side2 <<'PY'
import sys, cv2, numpy as np
p = sys.argv[1]; m = cv2.imread(p + '-mask.png', 0); k = 1 / 0.45
m[:int(478 * k), :int(30 * k)] = 0; m[int(822 * k):, :int(30 * k)] = 0   # прибрати клапани стрічки
n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0).astype(np.uint8)); i = 1 + np.argmax(st[1:, 4])
cv2.imwrite(p + '-mask.png', ((lab == i) * 255).astype(np.uint8))
PY
for p in police-side police-strip police-side2; do python3 -I $F/colorize.py $B/$p $F/seeds.json $p; done
python3 -I - $B/police-side2-color.png <<'PY'
import sys, cv2
f = sys.argv[1]; a = cv2.imread(f, cv2.IMREAD_UNCHANGED); cv2.imwrite(f, a[61:])   # зрізати залишки клапанів над дахом
PY
python3 -I $F/model.py $B/police-side $B/police-strip $B/police.json 128
cp $F/police.extra.json $B/police.extra.json
