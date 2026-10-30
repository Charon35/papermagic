#!/bin/bash
# Збирає TikTok-хуки: tiktok/hooks/hook-{1,2,3}.mp4 + ключові кадри hook-N-{start,mid,end}.png
# Потрібно: node + playwright (Chromium), python3 + opencv-python-headless, ffmpeg. Рендер важкий — запускати в хмарі.
# bash build.sh [1 2 3]
set -e
cd "$(dirname "$0")"
R=$(cd ../../.. && pwd); FIG=$R/instagram/reels-v3/build/fig; B=$R/tiktok/hooks/build; OUT=$R/tiktok/hooks
FPS=30
# 1) 3D-моделі машинок з аркушів (спільний конвеєр рілсів v3)
[ -f $FIG/police.json ] && [ -f $FIG/hip.json ] || bash $R/instagram/reels-v3/src/fig/make_figs.sh
# 2) деталі «контур / розфарбовано» і повні оберти фігурок (120 кадрів на оберт)
python3 -I prep.py $FIG $B/parts
python3 -I - $B <<'PY'
import sys, json, math
B = sys.argv[1]; N = 120
for nm, a in [('police', 0.15), ('hip', 0.25)]:
    json.dump([{'name': 'f%04d' % i, 'rot': a + 2 * math.pi * i / N, 'el': 0.34, 'dist': 900, 'lookY': 70} for i in range(N)], open(f'{B}/spin-{nm}.json', 'w'))
PY
for nm in police hip; do
  [ -f $B/spin/$nm/f0119.png ] || node $R/instagram/reels-v3/src/fig/render3d.js $FIG/$nm.json $B/spin/$nm 1080 1080 $B/spin-$nm.json
done
# 3) кадри сцен → H.264 без звуку
for n in ${@:-1 2 3}; do
  DUR=$(grep -o 'dur: [0-9.]*' hook-$n.html | grep -o '[0-9.]*')
  rm -rf $B/frames-$n
  node render.js hook-$n.html $B/frames-$n $DUR $FPS
  ffmpeg -y -loglevel error -framerate $FPS -i $B/frames-$n/f%04d.png -an -c:v libx264 -preset slow -crf 21 -maxrate 5M -bufsize 10M \
    -pix_fmt yuv420p -profile:v high -movflags +faststart $OUT/hook-$n.mp4
  # ключові кадри: 0.0 с, середина, останній кадр
  N=$(ls $B/frames-$n | wc -l)
  cp $B/frames-$n/f0000.png $OUT/hook-$n-start.png
  cp $B/frames-$n/f$(printf %04d $((N / 2))).png $OUT/hook-$n-mid.png
  cp $B/frames-$n/f$(printf %04d $((N - 1))).png $OUT/hook-$n-end.png
  ls -la $OUT/hook-$n.mp4
done
