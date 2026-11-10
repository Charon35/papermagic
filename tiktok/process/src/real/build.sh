#!/bin/bash
# «Блискавка 95» з реальних відео: розфарбовування й вирізання — живі кадри (ads/raw/IMG_*.MOV),
# склеювання — живі кадри, готова машинка — 3D на тому ж дерев'яному столі (готової машинки у відео немає). Без тексту поверх і без звуку.
# Перед запуском: сирі відео в ads/raw/ (див. ads/BRIEF.md) і зібраний «racer» (bash ../build.sh racer — потрібні його build/racer/a).
# bash build.sh
set -e
cd "$(dirname "$0")"
R=$(cd ../../../.. && pwd); RAW=$R/ads/raw; B=$R/tiktok/process/build/racer-real; OUT=$R/tiktok/process; NAME=blyskavka-95-real
mkdir -p $B/clips
# 1) 3D-модель у кольорах дітей (кораловий кузов, синє 95) і кадри обертання готової машинки
COLORS=$PWD/colors.json bash ../racer/fig.sh $R/tiktok/process/build/racer/sheet-clean.png $B/fig
# лише вже склеєна машинка: з 3.5 с 3D-таймлайну (складання позаду), 6 с обертання
node -e "const TL=require('../timeline.js'),n=Math.round(6*TL.FPS);
require('fs').writeFileSync('$B/frames3d.json',JSON.stringify(Array.from({length:n},(_,i)=>({name:'f'+String(i).padStart(4,'0'),...TL.cam3d(TL.T3+3.5+i/TL.FPS)}))))"
rm -rf $B/v3; node ../render3d.js $B/fig/racer.json $R/tiktok/process/build/racer/a/assets.json $B/v3 1080 1920 $B/frames3d.json 218,254,164
# 2) тло для 3D — порожній шматок того самого столу з IMG_4398, трохи розмитий (глибина різкості)
ffmpeg -v error -y -ss 0.4 -i $RAW/IMG_4398.MOV -frames:v 1 -vf "crop=1080:1000:0:920,scale=-2:1920,crop=1080:1920,gblur=sigma=6,eq=brightness=0.02" $B/table.png
ffmpeg -v error -y -loop 1 -framerate 30 -i $B/table.png -framerate 30 -i $B/v3/f%04d.png -filter_complex "[0][1]overlay=shortest=1,format=yuv420p" \
  -c:v libx264 -crf 16 -preset fast $B/clips/e.mp4
# 3) живі кадри: файл, початок, кінець, прискорення (обличчя дітей не потрапляють у кадр)
cut() { ffmpeg -v error -y -ss $2 -to $3 -i $RAW/$1 -an -vf "setpts=PTS/$4,fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p" \
  -c:v libx264 -crf 16 -preset fast $B/clips/$5.mp4; }
cut IMG_4393.MOV 0.3 5.8 1.1 a      # розфарбовування червоним олівцем
cut IMG_4396.MOV 1.6 5.9 1.2 b      # ще кольори: жовтий, синій
cut IMG_4397.MOV 0.2 6.9 1.3 c      # вирізання ножицями
cut IMG_4398.MOV 0.0 0.65 0.5 d     # склеювання: машинку тримають у руках (сповільнено ×0.5, з 0.7 с у кадр заходить інша фігурка)
# 4) склейка з м'якими переходами 0.3 с → H.264 без аудіодоріжки
X=0.3; o=0; f=""; prev="[0:v]"; i=1
for c in a b c d; do d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $B/clips/$c.mp4); o=$(echo "$o + $d - $X" | bc -l)
  f="$f${prev}[$i:v]xfade=transition=fade:duration=$X:offset=$o[v$i];"; prev="[v$i]"; i=$((i+1)); done
ffmpeg -v error -y -i $B/clips/a.mp4 -i $B/clips/b.mp4 -i $B/clips/c.mp4 -i $B/clips/d.mp4 -i $B/clips/e.mp4 -filter_complex "${f%;}" -map "$prev" -an \
  -c:v libx264 -preset slow -crf 20 -maxrate 6M -bufsize 12M -pix_fmt yuv420p -profile:v high -r 30 -movflags +faststart $OUT/$NAME.mp4
# 5) ключові кадри: розфарбовування, ще кольори, вирізання, склеювання, готова машинка
i=1; for t in 2.5 6.4 10.5 13.2 17.5; do ffmpeg -v error -y -ss $t -i $OUT/$NAME.mp4 -frames:v 1 $OUT/$NAME-$i.png; i=$((i+1)); done
ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT/$NAME.mp4
