#!/bin/bash
# build.sh DIR SECONDS "T1 T2 T3 T4" — рендер DIR/scene.html у DIR/<назва>.mp4 (H.264, 24 fps, 1080×1920, без звуку)
# і 4 ключові кадри DIR/key-<T>s.png. Потрібні node + playwright (Chromium) і ffmpeg.
set -euo pipefail
DIR="$(cd "$1" && pwd)"; SEC="$2"; KEYS="$3"; NAME="$(basename "$DIR")"
TOOLS="$(cd "$(dirname "$0")" && pwd)"
FR="$(mktemp -d "${TMPDIR:-/tmp}/pmframes.XXXXXX")"; trap 'rm -rf "$FR"' EXIT
node "$TOOLS/frames.js" "$DIR/scene.html" "$FR" "$SEC" 24
ffmpeg -y -loglevel error -framerate 24 -i "$FR/frame-%05d.png" -c:v libx264 -preset slow -crf 18 \
  -pix_fmt yuv420p -profile:v high -movflags +faststart -an "$DIR/$NAME.mp4"
rm -f "$DIR"/key-*.png
for t in $KEYS; do node "$TOOLS/frames.js" "$DIR/scene.html" "$DIR/key-${t}s.png" --t "$t"; done
echo "$DIR/$NAME.mp4"
