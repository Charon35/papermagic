"""Контактний аркуш кадрів для перегляду: python3 -I sheet.py OUT.jpg a.png b.png …"""
import sys, cv2, numpy as np
ims = []
for f in sys.argv[2:]:
    im = cv2.resize(cv2.imread(f), (270, 480))
    # безпечна зона TikTok для текстів (x 60–900, y 200–1500) — червона рамка
    cv2.rectangle(im, (15, 50), (225, 375), (0, 0, 255), 1)
    cv2.putText(im, f.split('/')[-1][:-4], (6, 470), 0, .6, (0, 0, 255), 2)
    ims.append(im)
while len(ims) % 5: ims.append(np.zeros_like(ims[0]))
rows = [np.hstack(ims[i:i + 5]) for i in range(0, len(ims), 5)]
cv2.imwrite(sys.argv[1], np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
