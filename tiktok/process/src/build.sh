#!/bin/bash
# Збирає процес-відео: tiktok/process/police-process.mp4 (1080×1920, 30 к/с, H.264, БЕЗ звуку) + 5 ключових кадрів.
# Потрібно: node + playwright (Chromium), python3 + opencv-python-headless + numpy, ffmpeg. Рендер важкий — запускати в хмарі.
set -e
cd "$(dirname "$0")"
R=$(cd ../../.. && pwd); B=$R/tiktok/process/build; OUT=$R/tiktok/process
mkdir -p $B
# 1) чистий аркуш (без логотипа, інструкції й напису) → 3D-модель і ассети деталей
python3 -I clean.py $R/papermagic-site/img/sheet-3.jpg $B/sheet-clean.png
bash figs.sh $B/sheet-clean.png $B/fig
python3 -I prep.py $B/sheet-clean.png $B/fig $B/a
# 2) 3D-кадри складання й обертання за спільним таймлайном
node -e "const TL=require('./timeline.js'),n=Math.round((TL.DUR-TL.T3)*TL.FPS);
require('fs').writeFileSync('$B/frames3d.json',JSON.stringify(Array.from({length:n},(_,i)=>({name:'f'+String(i).padStart(4,'0'),...TL.cam3d(TL.T3+i/TL.FPS)}))))"
rm -rf $B/v3; node render3d.js $B/fig/police.json $B/a/assets.json $B/v3 1080 1920 $B/frames3d.json
# 3) кадри сцени (рендерер TikTok-хуків) → H.264 без аудіодоріжки
DUR=$(node -e "console.log(require('./timeline.js').DUR)")
rm -rf $B/frames; node $R/tiktok/hooks/src/render.js police-process.html $B/frames $DUR 30
ffmpeg -y -loglevel error -framerate 30 -i $B/frames/f%04d.png -an -c:v libx264 -preset slow -crf 20 -maxrate 6M -bufsize 12M \
  -pix_fmt yuv420p -profile:v high -movflags +faststart $OUT/police-process.mp4
# 4) ключові кадри — по одному на етап
i=1; for t in 1.2 5.2 10.9 16.4 21.5; do
  n=$(printf %04d $(node -e "console.log(Math.round($t*30))"))
  cp $B/frames/f$n.png $OUT/police-process-$i.png; i=$((i+1)); done
ls -la $OUT/police-process.mp4
