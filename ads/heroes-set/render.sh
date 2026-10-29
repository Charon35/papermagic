#!/bin/bash
# render.sh OUT.png T — один кадр scene.html у момент T секунд (1080×1920)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC="$(cd "$(dirname "$0")" && pwd)/scene.html"
URL="file://$(python3 -I -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$SRC")?t=$2"
PROF="$(mktemp -d "${TMPDIR:-/tmp}/pmchrome.XXXXXX")"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --no-first-run --no-default-browser-check \
  --allow-file-access-from-files --user-data-dir="$PROF" --virtual-time-budget=1500 \
  --window-size=1080,1920 --screenshot="$1" "$URL" >/dev/null 2>&1
rm -rf "$PROF"
