#!/bin/bash
# Збирає процес-відео фігурки: tiktok/process/<out>.mp4 (1080×1920, 30 к/с, H.264, БЕЗ звуку) + 5 ключових кадрів.
# bash build.sh [police|racer]   (налаштування фігурок — src/figs.json; без аргументу — police)
# Потрібно: node + playwright (Chromium), python3 + opencv-python-headless + numpy, ffmpeg, pdfimages (poppler-utils, для PDF-аркушів).
# Рендер важкий (≈9 хв) — запускати в хмарі.
set -e
cd "$(dirname "$0")"
F=${1:-police}
R=$(cd ../../.. && pwd); B=$R/tiktok/process/build/$F; OUT=$R/tiktok/process
cfg() { node -e "const c=require('./figs.json')['$F'];const v=($1);console.log(typeof v==='string'?v:JSON.stringify(v))"; }
NAME=$(cfg c.out); SRC=$R/$(cfg c.src)
mkdir -p $B
# 1) аркуш (з PDF — вбудоване зображення сторінки) → чистий аркуш без логотипа/інструкції/напису
if [[ $SRC == *.pdf ]]; then pdfimages -j -f 1 -l 1 $SRC $B/src; SRC=$(ls $B/src-000.*); fi
python3 -I clean.py $SRC $B/sheet-clean.png "$(cfg c.clean)"
# 2) деталі й 3D-модель, ассети 2D-сцени
bash $(cfg c.figs) $B/sheet-clean.png $B/fig
python3 -I prep.py $B/sheet-clean.png $B/fig $B/a "$(cfg c.parts)"
# 3) 3D-кадри складання й обертання за спільним таймлайном
node -e "const TL=require('./timeline.js'),n=Math.round((TL.DUR-TL.T3)*TL.FPS);
require('fs').writeFileSync('$B/frames3d.json',JSON.stringify(Array.from({length:n},(_,i)=>({name:'f'+String(i).padStart(4,'0'),...TL.cam3d(TL.T3+i/TL.FPS)}))))"
rm -rf $B/v3; node render3d.js $B/fig/$(cfg c.model).json $B/a/assets.json $B/v3 1080 1920 $B/frames3d.json "$(cfg "c.strip.join(',')")"
# 4) кадри сцени (рендерер TikTok-хуків) → H.264 без аудіодоріжки
DUR=$(node -e "console.log(require('./timeline.js').DUR)")
rm -rf $B/frames; node $R/tiktok/hooks/src/render.js $NAME.html $B/frames $DUR 30
ffmpeg -y -loglevel error -framerate 30 -i $B/frames/f%04d.png -an -c:v libx264 -preset slow -crf 20 -maxrate 6M -bufsize 12M \
  -pix_fmt yuv420p -profile:v high -movflags +faststart $OUT/$NAME.mp4
# 5) ключові кадри — по одному на етап
i=1; for t in 1.2 5.2 10.9 16.4 21.5; do
  n=$(printf %04d $(node -e "console.log(Math.round($t*30))"))
  cp $B/frames/f$n.png $OUT/$NAME-$i.png; i=$((i+1)); done
ls -la $OUT/$NAME.mp4
