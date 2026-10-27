#!/bin/bash
# reel.sh ID DURATION — рендерить кадри рілса й збирає MP4 у «тихому» режиму:
# 2 паралельні процеси, низький пріоритет (taskpolicy -b → енергоефективні ядра)
cd "$(dirname "$0")"; ID=$1; DUR=$2; FPS=24
FR="out/frames/$ID"; rm -rf "$FR"; mkdir -p "$FR" out/reels
N=$(python3 -I -c "import math;print(math.ceil($DUR*$FPS))")
for ((i=0;i<N;i++)); do printf "%s/f%05d.png 1080 1920 kind=reel&id=%s&t=%s\n" "$FR" $i "$ID" "$(python3 -I -c "print(round($i/$FPS,4))")"; done \
  | taskpolicy -b nice -n 19 xargs -P 2 -L 1 ./render.sh
[ -x ./encode ] || taskpolicy -b nice -n 19 swiftc -O encode.swift -o encode
taskpolicy -b nice -n 19 ./encode "$FR" "out/reels/reel-$ID.mp4" $FPS
