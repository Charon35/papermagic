#!/bin/bash
# render.sh               — увесь ролик: kindergarten.mp4 (H.264, 24 fps, 13 с) + 4 ключові кадри key-*.png
# render.sh OUT.png T     — один кадр scene.html у момент T секунд (1080×1920)
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ $# -ge 2 ]; then exec node "$HERE/../tools/frames.js" "$HERE/scene.html" "$1" --t "$2"; fi
exec "$HERE/../tools/build.sh" "$HERE" 13 "0.6 5.6 8.6 12.6"
