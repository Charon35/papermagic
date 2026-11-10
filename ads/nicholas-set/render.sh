#!/bin/bash
# render.sh               — увесь ролик: nicholas-set.mp4 (H.264, 24 fps, 12 с) + 4 ключові кадри key-*.png
# render.sh OUT.png T     — один кадр scene.html у момент T секунд (1080×1920)
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ $# -ge 2 ]; then exec node "$HERE/../tools/frames.js" "$HERE/scene.html" "$1" --t "$2"; fi
exec "$HERE/../tools/build.sh" "$HERE" 12 "1.2 4.8 8.4 11.6"
