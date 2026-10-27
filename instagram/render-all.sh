#!/bin/bash
# render-all.sh — усі картинки, а потім рілси, у «тихому» режимі
cd "$(dirname "$0")"; date +%T
{
echo "out/posts/01-intro.png 1080 1350 kind=post&id=intro"
for i in 0 1 2 3 4; do echo "out/posts/02-how-$((i+1)).png 1080 1350 kind=post&id=how&slide=$i"; done
for i in 0 1 2 3 4 5 6 7 8; do echo "out/posts/03-catalog-$((i+1)).png 1080 1350 kind=post&id=catalog&slide=$i"; done
echo "out/posts/04-bundle.png 1080 1350 kind=post&id=bundle"
for h in catalog order bundle process reviews; do echo "out/highlights/hl-$h.png 1080 1920 kind=hl&id=$h"; done
echo "out/avatar.png 1080 1080 kind=avatar"
} | taskpolicy -b nice -n 19 xargs -P 2 -L 1 ./render.sh
echo "stills done $(date +%T)"
./reel.sh police 12.5 && echo "police $(date +%T)" && ./reel.sh shark 9.5 && echo "shark $(date +%T)" && ./reel.sh catalog 10.4 && echo "catalog $(date +%T)"
