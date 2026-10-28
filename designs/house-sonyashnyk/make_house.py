# Розмальовка «Будиночок «Соняшник»» — готовий аркуш А4 (SVG + PDF для друку).
# Запуск: python3 -I designs/house-sonyashnyk/make_house.py
# PDF друкує Chrome у фоновому режимі (тихо, один процес).
import math, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'sketches'))
from make_sketches import LOGO_INNER, INK, CUT, LINE, FOLD, TAB, poly, pl, ln, rect, circ, text, tab, window, flowers  # noqa: E402

# розміри фігурки, мм: фасад × глибина × висота стін, висота фронтону
F, D, H, G = 52, 40, 48, 24
SLOPE = math.hypot(D / 2, G)            # довжина ската даху
EAVE = 3                                # звис даху з боків
X0, TOP = 13, 154                       # ліве ребро стрічки стін, верх стін
XS = [X0, X0 + F, X0 + F + D, X0 + 2 * F + D, X0 + 2 * F + 2 * D]
BOT = TOP + H


def shutters(x, y, w, h):
    return rect(x - 4, y, 3.2, h) + rect(x + w + 0.8, y, 3.2, h) + \
        ''.join(ln(x - 4, y + h * i / 4, x - 0.8, y + h * i / 4, LINE) + ln(x + w + 0.8, y + h * i / 4, x + w + 4, y + h * i / 4, LINE) for i in (1, 2, 3))


def curtains(x, y, w, h):
    return f'<path d="M{x} {y} q{w * .3} {h * .4} 0 {h * .75}" {LINE}/><path d="M{x + w} {y} q{-w * .3} {h * .4} 0 {h * .75}" {LINE}/>'


def stones(x0, x1, y):
    s = ln(x0, y, x1, y, LINE)
    x, i = x0 + 1.5, 0
    while x + 6 < x1:
        s += rect(x, y + 0.8, 5.5, 2.6, LINE, 0.8) if i % 2 == 0 else rect(x, y + 0.8, 4, 2.6, LINE, 0.8)
        x += 7 if i % 2 == 0 else 5.5; i += 1
    return s


def sunflower(cx, cy, r=2.4, stem=12):
    petals = ''.join(
        f'<ellipse cx="{cx + math.cos(math.radians(a)) * r * 1.5:.1f}" cy="{cy + math.sin(math.radians(a)) * r * 1.5:.1f}" rx="{r * .8:.1f}" ry="{r * .42:.1f}" '
        f'transform="rotate({a} {cx + math.cos(math.radians(a)) * r * 1.5:.1f} {cy + math.sin(math.radians(a)) * r * 1.5:.1f})" {LINE}/>' for a in range(0, 360, 30))
    leaf = f'<path d="M{cx} {cy + stem * .6} q4 -3 6 0 q-3 3 -6 0z" {LINE}/>'
    return ln(cx, cy + r, cx, cy + stem, LINE) + leaf + petals + circ(cx, cy, r) + circ(cx, cy, r * .45)


def walls():
    s = ''
    # фронтони на бокових стінах + клапани під дах
    for i in (1, 3):
        a, b = XS[i], XS[i + 1]; m = (a + b) / 2
        s += poly([(a, TOP), (m, TOP - G), (b, TOP)])
        s += tab((a, TOP), (m, TOP - G), 4) + tab((m, TOP - G), (b, TOP), 4)
    # стрічка стін
    s += poly([(XS[0], TOP), (XS[4], TOP), (XS[4], BOT), (XS[0], BOT)])
    for x in XS[1:4]: s += ln(x, TOP, x, BOT)
    for i in (1, 3): s += ln(XS[i], TOP, XS[i + 1], TOP)          # згин фронтону
    s += tab((XS[4], TOP), (XS[4], BOT), 6)                        # бічний клапан → до фасаду зсередини
    for i in (1, 2, 3): s += tab((XS[i + 1], BOT), (XS[i], BOT), 5)  # клапани стін → до дна
    # фундамент по низу всіх стін
    s += stones(XS[0], XS[4], BOT - 4.4)
    return s


def roof():
    """Два скати над фасадом: перший кріпиться до верху фасаду, другий — клапаном до верху задньої стіни."""
    xa, xb = XS[0] - EAVE, XS[1] + EAVE
    r1, r2 = TOP - SLOPE, TOP - 2 * SLOPE
    s = poly([(xa, TOP), (xb, TOP), (xb, r2), (xa, r2)])
    s += ln(XS[0], TOP, XS[1], TOP) + ln(xa, r1, xb, r1)          # згин біля фасаду і по гребеню
    s += tab((XS[0], r2), (XS[1], r2), 5)                         # клапан назовні → до задньої стіни зсередини
    # черепиця лусочками
    rows = 5
    for half in (0, 1):
        y0 = TOP - half * SLOPE
        for r in range(rows):
            yy = y0 - (r + 0.6) * SLOPE / (rows + 0.2)
            off = 3 if r % 2 else 0
            n = int((xb - xa - off) / 6)
            arcs = ' '.join('a3 3 0 0 0 6 0' for _ in range(n))
            s += f'<path d="M{xa + off + 0.5:.1f} {yy:.1f} {arcs}" {LINE}/>'
    # мансардне віконце на передньому скаті
    wx, wy = (xa + xb) / 2 - 6, TOP - SLOPE + 7
    s += rect(wx - 1, wy - 1, 14, 12, CUT, 1.5) + rect(wx + 1, wy + 1, 10, 8, LINE, 1) + ln(wx + 6, wy + 1, wx + 6, wy + 9, LINE) + ln(wx + 1, wy + 5, wx + 11, wy + 5, LINE)
    return s


def floor():
    s = poly([(XS[0], BOT), (XS[1], BOT), (XS[1], BOT + D), (XS[0], BOT + D)])
    s += ln(XS[0], BOT, XS[1], BOT)
    # доріжка з плитки і травичка
    for i in range(4):
        s += rect(XS[0] + F / 2 - 5, BOT + 3 + i * 7, 10, 5, LINE, 1.2)
    for (u, v) in [(6, 10), (12, 28), (40, 8), (44, 30), (8, 34)]:
        x, y = XS[0] + u, BOT + v
        s += pl([(x, y), (x + 1, y - 2.5), (x + 2, y), (x + 3, y - 2), (x + 4, y)])
    s += text(XS[0] + F - 3, BOT + D - 3, "дно", 2.8, 700, "end", 'opacity=".45"')
    return s


def front():
    fx, s = XS[0], ''
    # двері з аркою, козирок, сходинка, ручка
    dx, dw, dh = fx + 20, 12, 22
    s += f'<path d="M{dx} {BOT - 4.4} V{BOT - dh + dw / 2} A{dw / 2} {dw / 2} 0 0 1 {dx + dw} {BOT - dh + dw / 2} V{BOT - 4.4}" {LINE}/>'
    s += rect(dx + 2, BOT - dh + 7, dw - 4, 5, LINE, 1) + circ(dx + dw - 2.2, BOT - 11, 0.8)
    s += poly([(dx - 3, BOT - dh - 1), (dx + dw / 2, BOT - dh - 6), (dx + dw + 3, BOT - dh - 1)], LINE)
    s += rect(dx - 2, BOT - 4.4, dw + 4, 1.6, LINE)
    # ліхтарик біля дверей
    s += pl([(dx + dw + 4, BOT - 17), (dx + dw + 6, BOT - 17), (dx + dw + 6, BOT - 15)]) + rect(dx + dw + 4.8, BOT - 15, 2.4, 3.4, LINE, 0.6)
    # вікна з віконницями і ящиками квітів
    for wx in (fx + 6, fx + 36):
        s += window(wx, TOP + 9, 10, 12) + shutters(wx, TOP + 9, 10, 12)
        s += rect(wx - 1, TOP + 23.5, 12, 3) + flowers(wx + 1, TOP + 23, 3, 4)
    # табличка з номером і вивіска-сердечко
    s += rect(fx + 19, TOP + 2.5, 14, 5, LINE, 1) + text(fx + 26, TOP + 6.3, "12", 3.2, 800, "middle")
    return s


def side_a():
    sx, s = XS[1], ''
    s += circ(sx + D / 2, TOP - G / 2 + 3, 4.2) + circ(sx + D / 2, TOP - G / 2 + 3, 2.4) + ln(sx + D / 2 - 2.4, TOP - G / 2 + 3, sx + D / 2 + 2.4, TOP - G / 2 + 3, LINE)
    s += window(sx + 15, TOP + 11, 12, 14) + curtains(sx + 15, TOP + 11, 12, 14)
    s += sunflower(sx + 7, TOP + 22, 2.3, 17) + sunflower(sx + 34, TOP + 26, 1.8, 13)
    return s


def back():
    bx, s = XS[2], ''
    for wx in (bx + 8, bx + 32):
        s += window(wx, TOP + 10, 12, 14) + curtains(wx, TOP + 10, 12, 14)
    for (u, v) in [(3, 32), (12, 36), (40, 31), (46, 37), (24, 4), (2, 6)]: s += rect(bx + u, TOP + v, 5, 2.4, LINE, 0.4)
    s += circ(bx + F / 2, TOP + 5, 1.8)  # вентиляційне віконце
    # водостічна труба
    s += pl([(bx + F - 3, TOP + 1), (bx + F - 3, BOT - 6), (bx + F - 6, BOT - 4.6)]) + pl([(bx + F - 1.6, TOP + 1), (bx + F - 1.6, BOT - 5.4)])
    return s


def side_b():
    kx, s = XS[3], ''
    s += f'<path d="M{kx + D / 2} {TOP - G / 2 + 6} l-3 -3 a2 2 0 0 1 3 -2.6 a2 2 0 0 1 3 2.6 z" {LINE}/>'  # сердечко у фронтоні
    s += window(kx + 14, TOP + 11, 12, 14)
    # кошеня на підвіконні
    cx, cy = kx + 20, TOP + 25
    s += f'<path d="M{cx - 4} {cy} q0 -6 4 -6 q4 0 4 6" {LINE}/>' + pl([(cx - 3.6, cy - 4.6), (cx - 3, cy - 7.4), (cx - 1.4, cy - 5.6)]) + pl([(cx + 1.4, cy - 5.6), (cx + 3, cy - 7.4), (cx + 3.6, cy - 4.6)])
    s += circ(cx - 1.4, cy - 3.2, 0.5, f'fill="{INK}"') + circ(cx + 1.4, cy - 3.2, 0.5, f'fill="{INK}"')
    # кущики в горщиках
    for px in (kx + 4, kx + 29):
        s += poly([(px, BOT - 9), (px + 7, BOT - 9), (px + 6, BOT - 4.6), (px + 1, BOT - 4.6)], LINE)
        s += ''.join(circ(px + 3.5 + dx, BOT - 12 + dy, 2.2) for dx, dy in [(-2, 0), (2, 0), (0, -2.4)])
    return s


def stand_foot(x0, x1, y, foot=5.5):
    """Клапан-ніжка під декорацією: відгинається назад, щоб фігурка стояла."""
    return poly([(x0, y), (x1, y), (x1 - 1.2, y + foot), (x0 + 1.2, y + foot)], TAB) + ln(x0, y, x1, y)


def decorations():
    s = ''
    # деревце
    x, y = 78, 214
    crown = f'<path d="M{x + 4} {y + 22} a8 8 0 0 1 2 -14 a9 9 0 0 1 16 -2 a8 8 0 0 1 4 15 z" {CUT}/>'
    trunk = rect(x + 12, y + 21, 5, 13, CUT)
    apples = ''.join(circ(x + u, y + v, 1.2) for u, v in [(9, 12), (16, 8), (21, 15), (13, 17)])
    s += trunk + crown + apples + stand_foot(x + 9, x + 20, y + 34)
    # поштова скринька
    x, y = 112, 222
    box = f'<path d="M{x} {y + 10} V{y + 4} a6 4 0 0 1 12 0 V{y + 10} z" {CUT}/>' + rect(x + 5, y + 10, 2.4, 16, CUT)
    box += text(x + 6, y + 8.6, "ПОШТА", 2, 900, "middle") + pl([(x + 12, y + 3), (x + 14.5, y + 3), (x + 14.5, y + 6.5), (x + 12, y + 6.5)])
    s += box + stand_foot(x + 2, x + 10.4, y + 26)
    # тинок (паркан)
    x, y, n = 135, 226, 9
    pick = ''.join(poly([(x + i * 6, y + 18), (x + i * 6, y + 3), (x + i * 6 + 2.5, y), (x + i * 6 + 5, y + 3), (x + i * 6 + 5, y + 18)], CUT) for i in range(n))
    rails = rect(x - 1, y + 6, n * 6, 2.6, CUT) + rect(x - 1, y + 12, n * 6, 2.6, CUT)
    s += pick + rails + stand_foot(x, x + n * 6 - 1, y + 18)
    # соняшник-підставка
    x, y = 112, 256
    s += sunflower(x + 6, y + 6, 2.6, 16) + stand_foot(x + 1, x + 11, y + 22)
    s += text(160, 268, "Деталі-декорації: виріж, відігни", 2.8, 700, "middle", 'opacity=".55"')
    s += text(160, 272, "ніжку назад і постав біля будиночка", 2.8, 700, "middle", 'opacity=".55"')
    return s


def preview():
    px, py, k = 132, 74, 0.6
    def P(x, y, z): return (px + (x + z) * 0.87 * k, py + (x - z) * 0.5 * k - y * k)
    pv = poly([P(F, 0, 0), P(F, 0, D), P(F, H, D), P(F, H, 0)])
    pv += poly([P(F, H, 0), P(F, H + G, D / 2), P(F, H, D)])
    pv += poly([P(0, 0, 0), P(F, 0, 0), P(F, H, 0), P(0, H, 0)])
    pv += poly([P(-EAVE, H, -1.5), P(F + EAVE, H, -1.5), P(F + EAVE, H + G, D / 2), P(-EAVE, H + G, D / 2)])
    fq = lambda x0, y0, x1, y1: poly([P(x0, y0, 0), P(x1, y0, 0), P(x1, y1, 0), P(x0, y1, 0)], LINE)
    sq = lambda z0, y0, z1, y1: poly([P(F, y0, z0), P(F, y0, z1), P(F, y1, z1), P(F, y1, z0)], LINE)
    pv += fq(20, 4, 32, 22) + fq(6, 27, 16, 39) + fq(36, 27, 46, 39) + fq(19, 40, 33, 45)
    pv += sq(15, 23, 27, 37)
    c = P(F, H + G / 2 - 3, D / 2); pv += circ(c[0], c[1], 2.4)
    for i in range(1, 4):
        a, b = P(-EAVE, H + G * i / 4, D / 2 * i / 4 - 1.5 * (1 - i / 4)), P(F + EAVE, H + G * i / 4, D / 2 * i / 4 - 1.5 * (1 - i / 4))
        pv += ln(a[0], a[1], b[0], b[1], LINE)
    g0, g1 = P(-8, 0, -6), P(F + 8, 0, -6)
    pv += f'<ellipse cx="{(g0[0] + g1[0]) / 2 + 10:.1f}" cy="{(g0[1] + g1[1]) / 2 + 4:.1f}" rx="38" ry="5" fill="{INK}" opacity=".07"/>'
    return pv


def sheet():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297" width="210mm" height="297mm">
<rect width="210" height="297" fill="#fff"/>
<g transform="translate(14 10) scale(0.03)">{LOGO_INNER}</g>
{text(14, 40, "PaperMagic", 6.5, 900)}
{text(14, 50, "Інструкція:", 4, 700)}
{text(14, 56, "- Роздрукуй", 3.6, 600)}{text(14, 61, "- Розмалюй", 3.6, 600)}{text(14, 66, "- Виріж", 3.6, 600)}{text(14, 71, "- Склей 3D фігурку", 3.6, 600)}
{text(14, 80, "Будиночок «Соняшник» · легко · 40–50 хв", 3.2, 700, "start", 'opacity=".6"')}
<g>{preview()}</g>
<g>{roof()}{walls()}{floor()}{front()}{side_a()}{back()}{side_b()}{decorations()}</g>
{text(14, 290, "- - - згинати      ▭ клапан — намаж клеєм", 3, 600, "start", 'opacity=".55"')}
{text(196, 290, "© PaperMagic · @papermagic_ua · лише для особистого друку", 2.8, 600, "end", 'opacity=".55"')}
</svg>'''


def check():
    """Перевірка розгортки: що зійдеться при складанні."""
    assert abs(SLOPE - math.hypot(D / 2, G)) < 1e-9
    gable_edge = math.hypot(D / 2, G)
    assert abs(gable_edge - SLOPE) < 1e-9, 'ребро фронтону = ширина ската'
    assert XS[1] - XS[0] == XS[3] - XS[2] == F and XS[2] - XS[1] == XS[4] - XS[3] == D
    assert TOP - 2 * SLOPE - 5 > 82, 'дах не залазить на шапку аркуша'
    assert XS[4] + 6 <= 204 and BOT + D <= 285, 'усе в межах друку'
    print(f'ок: скат {SLOPE:.1f} мм = ребро фронтону; фігурка {F}×{D}×{H + G:.0f} мм')


if __name__ == '__main__':
    check()
    svg = HERE / 'papermagic-budynochok-sonyashnyk.svg'
    svg.write_text(sheet())
    pdf = HERE / 'papermagic-budynochok-sonyashnyk.pdf'
    html = HERE / '_print.html'
    html.write_text(f'<!doctype html><meta charset="utf-8"><style>@page{{size:A4;margin:0}}html,body{{margin:0}}img{{width:210mm;height:297mm;display:block}}</style><img src="{svg.name}">')
    chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    subprocess.run(['taskpolicy', '-b', 'nice', '-n', '19', chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf}', html.as_uri()], check=True, capture_output=True, timeout=120)
    html.unlink()
    print('ok', svg.name, pdf.name)
