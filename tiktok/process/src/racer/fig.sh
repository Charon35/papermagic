#!/bin/bash
# 3D-модель «Блискавки 95» з очищеного аркуша високої роздільності: bash fig.sh SHEET_CLEAN.png OUT_DIR
set -e
H=$(cd "$(dirname "$0")" && pwd); S=$1; B=$2
mkdir -p $B
python3 -I $H/netx.py $S 50 304 211 704 $B/racer-side L
python3 -I $H/netx.py $S 218 254 382 794 $B/racer-strip rect
python3 -I $H/netx.py $S 384 304 545 704 $B/racer-side2 R
python3 -I $H/fig.py $B
