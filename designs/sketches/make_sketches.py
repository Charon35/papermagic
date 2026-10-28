# Ескізи нових розмальовок PaperMagic (власні дизайни): аркуш А4, розгортка, лінії згину пунктиром, клапани для клею.
# Запуск: python3 -I designs/sketches/make_sketches.py  → SVG поруч зі скриптом
import math, pathlib, re

OUT = pathlib.Path(__file__).parent
LOGO = (OUT.parent.parent / 'brand' / 'logo-inline.txt').read_text().strip()
LOGO_INNER = re.sub(r'^<svg[^>]*>|</svg>$', '', LOGO).replace('currentColor', '#2a2440')

INK = '#2a2440'
CUT = f'fill="#fff" stroke="{INK}" stroke-width="0.9" stroke-linejoin="round"'
LINE = f'fill="none" stroke="{INK}" stroke-width="0.6" stroke-linejoin="round" stroke-linecap="round"'
FOLD = f'fill="none" stroke="{INK}" stroke-width="0.45" stroke-dasharray="2 1.4"'
TAB = f'fill="#fff" stroke="{INK}" stroke-width="0.7" stroke-linejoin="round"'


def pts(a): return ' '.join(f'{x:.1f},{y:.1f}' for x, y in a)
def poly(a, s=CUT): return f'<polygon points="{pts(a)}" {s}/>'
def pl(a, s=LINE): return f'<polyline points="{pts(a)}" {s}/>'
def ln(x1, y1, x2, y2, s=FOLD): return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {s}/>'
def rect(x, y, w, h, s=LINE, rx=0): return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" {s}/>'
def circ(x, y, r, s=LINE): return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" {s}/>'
def text(x, y, t, size=4, w=700, anchor='start', extra=''):
    return f'<text x="{x}" y="{y}" font-family="Nunito, Arial, sans-serif" font-size="{size}" font-weight="{w}" fill="{INK}" text-anchor="{anchor}" {extra}>{t}</text>'


def tab(p, q, d=5, inset=0.25):
    """Клапан для клею назовні від ребра p→q (ліворуч від напрямку руху)."""
    (x1, y1), (x2, y2) = p, q
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy); nx, ny = dy / L, -dx / L
    a = (x1 + dx * inset + nx * d, y1 + dy * inset + ny * d)
    b = (x2 - dx * inset + nx * d, y2 - dy * inset + ny * d)
    return poly([p, a, b, q], TAB)


def window(x, y, w, h, arch=False):
    s = rect(x, y, w, h) if not arch else pl([(x, y + h), (x, y + w / 2)], LINE) + \
        f'<path d="M{x} {y + w / 2} A{w / 2} {w / 2} 0 0 1 {x + w} {y + w / 2}" {LINE}/>' + pl([(x + w, y + w / 2), (x + w, y + h), (x, y + h)], LINE)
    s += ln(x + w / 2, y + (w / 2 if arch else 0), x + w / 2, y + h, LINE) + ln(x, y + h / 2 + (w / 4 if arch else 0), x + w, y + h / 2 + (w / 4 if arch else 0), LINE)
    s += rect(x - 1.2, y + h, w + 2.4, 2.2)  # підвіконня
    return s


def flowers(x, y, n=3, gap=5):
    s = ''
    for i in range(n):
        cx = x + i * gap
        for a in range(0, 360, 72):
            s += circ(cx + math.cos(math.radians(a)) * 1.4, y + math.sin(math.radians(a)) * 1.4, 1.1)
        s += circ(cx, y, 0.7)
    return s


def sheet(title, body, preview, n):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297" width="1050" height="1485">
<rect width="210" height="297" fill="#fff"/>
<g transform="translate(14 10) scale(0.03)">{LOGO_INNER}</g>
{text(14, 40, "PaperMagic", 6.5, 900)}
{text(14, 50, "Інструкція:", 4, 700)}
{text(14, 56, "- Роздрукуй", 3.6, 600)}{text(14, 61, "- Розмалюй", 3.6, 600)}{text(14, 66, "- Виріж", 3.6, 600)}{text(14, 71, "- Склей 3D фігурку", 3.6, 600)}
{text(196, 290, f"ЕСКІЗ {n} · {title}", 3.2, 800, "end", 'opacity=".55"')}
{text(14, 290, "— — згинати   ▭ клапан для клею", 3, 600, "start", 'opacity=".55"')}
<g>{preview}</g>
<g>{body}</g>
</svg>'''


# ---------- 1. Будиночок «Соняшник» ----------
def house():
    F, D, H, G = 52, 40, 46, 24          # ширина фасаду, глибина, висота стін, висота фронтону
    x0, top = 15, 168                    # ліве ребро стрічки стін, верх стін
    xs = [x0, x0 + F, x0 + F + D, x0 + 2 * F + D, x0 + 2 * F + 2 * D]
    bot = top + H
    s = ''
    # фронтони на бокових стінах
    for i in (1, 3):
        a, b = xs[i], xs[i + 1]
        s += poly([(a, top), ((a + b) / 2, top - G), (b, top)])
        s += tab((a, top), ((a + b) / 2, top - G), 4) + tab(((a + b) / 2, top - G), (b, top), 4)
    # стіни
    s += poly([(xs[0], top), (xs[4], top), (xs[4], bot), (xs[0], bot)])
    for x in xs[1:4]: s += ln(x, top, x, bot)
    for x in (*xs[1:4],): pass
    s += tab((xs[4], top), (xs[4], bot), 5)       # бічний клапан
    for i in range(4): s += tab((xs[i + 1], bot), (xs[i], bot), 5)  # клапани до дна
    # дах: два скати над фасадом
    slope = math.hypot(D / 2, G)
    r1, r2 = top - slope, top - 2 * slope
    s += poly([(xs[0] - 3, top), (xs[1] + 3, top), (xs[1] + 3, r2), (xs[0] - 3, r2)])
    s += ln(xs[0] - 3, top, xs[1] + 3, top) + ln(xs[0] - 3, r1, xs[1] + 3, r1)
    # черепиця
    for row in range(1, 5):
        for yy in (top - row * slope / 4.5, r1 - row * slope / 4.5):
            k = int((F + 6) / 6)
            d = ' '.join(f'a3 3 0 0 0 6 0' for _ in range(k))
            s += f'<path d="M{xs[0] - 3} {yy:.1f} {d}" {LINE}/>'
    # дно
    s += poly([(xs[0], bot), (xs[1], bot), (xs[1], bot + D), (xs[0], bot + D)]) + tab((xs[1], bot), (xs[1], bot + D), 4)
    s += text((xs[0] + xs[1]) / 2, bot + D / 2 + 1.5, "дно", 3.2, 700, "middle", 'opacity=".5"')
    # фасад: двері, вікна, ящики з квітами, табличка
    fx = xs[0]
    s += f'<path d="M{fx + 20} {bot} V{bot - 20} A6 6 0 0 1 {fx + 32} {bot - 20} V{bot}" {LINE}/>' + circ(fx + 29.5, bot - 10, 0.9)
    s += window(fx + 5, top + 8, 10, 12) + window(fx + 37, top + 8, 10, 12)
    s += rect(fx + 4, top + 22.5, 12, 3) + flowers(fx + 6, top + 22, 3, 4) + rect(fx + 36, top + 22.5, 12, 3) + flowers(fx + 38, top + 22, 3, 4)
    s += rect(fx + 19, top + 3, 14, 5, LINE, 1) + text(fx + 26, top + 6.8, "12", 3.2, 800, "middle")
    # бокова стіна: кругле вікно + соняшник
    sx = xs[1]
    s += circ(sx + D / 2, top - G / 2 + 3, 4) + circ(sx + D / 2, top - G / 2 + 3, 2.2)
    s += window(sx + 14, top + 12, 12, 14)
    cx, cy = sx + 8, bot - 12
    s += ln(cx, cy, cx, bot, LINE) + ''.join(f'<ellipse cx="{cx + math.cos(math.radians(a)) * 3.4:.1f}" cy="{cy + math.sin(math.radians(a)) * 3.4:.1f}" rx="1.8" ry="1" transform="rotate({a} {cx + math.cos(math.radians(a)) * 3.4:.1f} {cy + math.sin(math.radians(a)) * 3.4:.1f})" {LINE}/>' for a in range(0, 360, 30)) + circ(cx, cy, 2.2)
    # задня стіна: вікно і цегла
    bx = xs[2]
    s += window(bx + 8, top + 10, 12, 14) + window(bx + 32, top + 10, 12, 14)
    for (u, v) in [(4, 34), (12, 38), (40, 33), (46, 40), (24, 4)]: s += rect(bx + u, top + v, 5, 2.4)
    # друга бокова: кошеня у вікні
    kx = xs[3]
    s += circ(kx + D / 2, top - G / 2 + 3, 4)
    s += window(kx + 14, top + 12, 12, 14)
    s += f'<path d="M{kx + 16} {top + 26} q0 -5 4 -5 q4 0 4 5" {LINE}/>' + pl([(kx + 16.5, top + 22), (kx + 17, top + 19.5), (kx + 18.5, top + 21.3)]) + pl([(kx + 21.5, top + 21.3), (kx + 23, top + 19.5), (kx + 23.5, top + 22)])
    s += rect(kx + 6, bot - 9, 6, 9) + rect(kx + 28, bot - 9, 6, 9)  # кущики-горщики
    # превʼю зібраного будиночка (ізометрія: x — вправо-вниз, z — вправо-вгору)
    px, py, k = 128, 78, 0.62
    def P(x, y, z): return (px + (x + z) * 0.87 * k, py + (x - z) * 0.5 * k - y * k)
    w_, d_, h_ = F, D, H
    pv = poly([P(w_, 0, 0), P(w_, 0, d_), P(w_, h_, d_), P(w_, h_, 0)])                 # бокова стіна
    pv += poly([P(w_, h_, 0), P(w_, h_ + G, d_ / 2), P(w_, h_, d_)])                     # фронтон
    pv += poly([P(0, 0, 0), P(w_, 0, 0), P(w_, h_, 0), P(0, h_, 0)])                    # фасад
    pv += poly([P(-3, h_, -2), P(w_ + 3, h_, -2), P(w_ + 3, h_ + G, d_ / 2), P(-3, h_ + G, d_ / 2)])  # скат даху
    face = lambda x0, y0, x1, y1: poly([P(x0, y0, 0), P(x1, y0, 0), P(x1, y1, 0), P(x0, y1, 0)], LINE)
    pv += face(20, 0, 32, 20) + face(5, 26, 15, 38) + face(37, 26, 47, 38)
    c = P(w_, h_ + G / 2 - 2, d_ / 2); pv += circ(c[0], c[1], 2.2)
    sw = lambda z0, y0, z1, y1: poly([P(w_, y0, z0), P(w_, y0, z1), P(w_, y1, z1), P(w_, y1, z0)], LINE)
    pv += sw(14, 20, 26, 34)
    return sheet("Будиночок «Соняшник»", s, pv, 1)


# ---------- 2. Спорткар «Комета 7» ----------
def car():
    cx0, cx1 = 86, 124                 # центральна смуга (верх машини), ширина 38
    seg = [("бампер", 8), ("капот", 40), ("лобове", 20), ("дах", 30), ("заднє", 16), ("багажник", 30), ("бампер", 8)]
    y = 108; ys = [y]
    for _, h in seg: y += h; ys.append(y)
    s = poly([(cx0, ys[0]), (cx1, ys[0]), (cx1, ys[-1]), (cx0, ys[-1])])
    for v in ys[1:-1]: s += ln(cx0, v, cx1, v)
    # профіль: висота над землею для кожної точки по довжині
    yb0, yh0, yh1, yr0, yr1, yt0, yt1 = ys[1], ys[1], ys[2], ys[3], ys[4], ys[5], ys[6]
    hgt = [(ys[0], 12), (yh0, 18), (yh1, 18), (yr0, 31), (yr1, 31), (yt0, 22), (yt1, 22), (ys[7], 13)]
    out = ''
    for sign, base in ((-1, cx0), (1, cx1)):
        outer = [(base + sign * (31 - h), yy) for yy, h in hgt]
        ground = base + sign * 31
        shape = outer + [(ground, ys[7]), (ground, ys[0])]
        out += poly(shape)
        out += ln(base, ys[3], base, ys[4])  # згин даху
        # колеса
        for wy in (ys[0] + 26, ys[7] - 26):
            out += circ(ground - sign * 0.5, wy, 11) + circ(ground - sign * 0.5, wy, 6.5) + circ(ground - sign * 0.5, wy, 1.6)
            for a in range(0, 360, 60):
                out += ln(ground - sign * 0.5 + math.cos(math.radians(a)) * 2, wy + math.sin(math.radians(a)) * 2, ground - sign * 0.5 + math.cos(math.radians(a)) * 6, wy + math.sin(math.radians(a)) * 6, LINE)
        # бокове вікно
        wx = base + sign * 3.5
        out += poly([(base + sign * 10, ys[2] + 4), (wx, ys[3] + 1), (wx, ys[4] - 1), (base + sign * 8, ys[5] - 2)], LINE)
        # смуга-блискавка і номер
        mx = base + sign * 20
        out += pl([(mx, ys[1] - 2), (mx - sign * 2.5, ys[2] + 6), (mx + sign * 1.5, ys[2] + 8), (mx - sign * 1, ys[5] + 6)], LINE)
        out += circ(base + sign * 17, (ys[3] + ys[4]) / 2, 5.5) + text(base + sign * 17, (ys[3] + ys[4]) / 2 + 2.1, "7", 6, 900, "middle")
        # клапани по краю профілю (крім ребра даху)
        for (p, q) in zip(outer[:3], outer[1:4]):
            out += tab(p, q, 4) if sign < 0 else tab(q, p, 4)
        for (p, q) in zip(outer[4:-1], outer[5:]):
            out += tab(p, q, 4) if sign < 0 else tab(q, p, 4)
    s = out + s
    # деталі на смузі
    s += rect(cx0 + 4, ys[0] + 2, 7, 3.5, LINE, 1) + rect(cx1 - 11, ys[0] + 2, 7, 3.5, LINE, 1)   # фари
    for i in range(5): s += ln(cx0 + 12 + i * 3.5, ys[0] + 2, cx0 + 12 + i * 3.5, ys[0] + 6, LINE)  # решітка
    s += pl([(cx0 + 19, ys[1] + 6), (cx0 + 19, ys[2] - 6)], LINE) + pl([(cx1 - 19, ys[1] + 6), (cx1 - 19, ys[2] - 6)], LINE)
    s += f'<path d="M{(cx0 + cx1) / 2 - 7} {ys[1] + 24} l7 -12 l7 12 l-7 -4 z" {LINE}/>'  # зірка-комета
    s += rect(cx0 + 3, ys[2] + 3, cx1 - cx0 - 6, ys[3] - ys[2] - 6, LINE, 2) + rect(cx0 + 4, ys[4] + 3, cx1 - cx0 - 8, ys[5] - ys[4] - 6, LINE, 2)
    s += rect(cx0 + 2, ys[5] + 2, cx1 - cx0 - 4, 5, LINE, 1)  # спойлер
    s += rect(cx0 + 4, ys[7] - 6, 7, 3.5, LINE, 1) + rect(cx1 - 11, ys[7] - 6, 7, 3.5, LINE, 1)
    s += text((cx0 + cx1) / 2, ys[6] - 10, "КОМЕТА", 3.6, 900, "middle")
    # превʼю: вигляд збоку
    px, gy, k = 118, 72, 0.48
    prof = [(px + (yy - ys[0]) * k, gy - h * k) for yy, h in hgt]
    pv = poly(prof + [(px + (ys[7] - ys[0]) * k, gy), (px, gy)])
    pv += poly([(px + (ys[2] + 4 - ys[0]) * k, gy - 20 * k), (px + (ys[3] + 1 - ys[0]) * k, gy - 28 * k), (px + (ys[4] - 1 - ys[0]) * k, gy - 28 * k), (px + (ys[5] - 2 - ys[0]) * k, gy - 21 * k)], LINE)
    for wx in (26, ys[7] - ys[0] - 26):
        pv += circ(px + wx * k, gy, 11 * k) + circ(px + wx * k, gy, 6 * k)
    pv += circ(px + ((ys[3] + ys[4]) / 2 - ys[0]) * k, gy - 13 * k, 5 * k) + text(px + ((ys[3] + ys[4]) / 2 - ys[0]) * k, gy - 13 * k + 1.2, "7", 3.2, 900, "middle")
    pv += f'<ellipse cx="{px + (ys[7] - ys[0]) * k / 2:.1f}" cy="{gy + 7}" rx="{(ys[7] - ys[0]) * k / 2 + 4:.1f}" ry="1.6" fill="#2a2440" opacity=".08"/>'
    return sheet("Спорткар «Комета 7»", s, pv, 2)


# ---------- 3. Мінінабір «Українське село»: хатка, пекарня, криниця ----------
def mini_house(x0, top, F, D, H, G, front_fn, label, thatch=False):
    xs = [x0, x0 + F, x0 + F + D, x0 + 2 * F + D, x0 + 2 * F + 2 * D]
    bot = top + H
    s = ''
    for i in (1, 3):
        a, b = xs[i], xs[i + 1]
        s += poly([(a, top), ((a + b) / 2, top - G), (b, top)]) + tab((a, top), ((a + b) / 2, top - G), 3) + tab(((a + b) / 2, top - G), (b, top), 3)
    s += poly([(xs[0], top), (xs[4], top), (xs[4], bot), (xs[0], bot)])
    for x in xs[1:4]: s += ln(x, top, x, bot)
    s += tab((xs[4], top), (xs[4], bot), 4)
    for i in range(4): s += tab((xs[i + 1], bot), (xs[i], bot), 3.5)
    slope = math.hypot(D / 2, G)
    s += poly([(xs[0] - 2, top), (xs[1] + 2, top), (xs[1] + 2, top - 2 * slope), (xs[0] - 2, top - 2 * slope)])
    s += ln(xs[0] - 2, top - slope, xs[1] + 2, top - slope)
    if thatch:
        for i in range(int((F + 4) / 2.5)):
            xx = xs[0] - 1 + i * 2.5
            s += ln(xx, top - 1, xx + 0.8, top - slope + 1.5, LINE) + ln(xx, top - slope - 1, xx + 0.8, top - 2 * slope + 1.5, LINE)
    else:
        for r in range(1, 4):
            for yy in (top - r * slope / 3.3, top - slope - r * slope / 3.3):
                s += ln(xs[0] - 2, yy, xs[1] + 2, yy, LINE)
    s += front_fn(xs[0], top, F, H)
    s += text((xs[0] + xs[4]) / 2, bot + 9.5, label, 3.4, 800, "middle", 'opacity=".6"')
    return s


def hata_front(x, top, F, H):
    bot = top + H
    s = rect(x + F / 2 - 4, bot - 15, 8, 15) + circ(x + F / 2 + 2.5, bot - 7.5, 0.6)
    s += window(x + 3.5, top + 6, 7, 8) + window(x + F - 10.5, top + 6, 7, 8)
    # орнамент-вишиванка по низу
    for i in range(int(F / 4)):
        cx = x + 2 + i * 4
        s += poly([(cx, bot - 3), (cx + 1.5, bot - 4.5), (cx + 3, bot - 3), (cx + 1.5, bot - 1.5)], LINE)
    s += flowers(x + 5, top + 17, 2, 3.5) + flowers(x + F - 8.5, top + 17, 2, 3.5)
    return s


def bakery_front(x, top, F, H):
    bot = top + H
    s = rect(x + 3, top + 3, F - 6, 6, LINE, 1) + text(x + F / 2, top + 7.4, "ПЕКАРНЯ", 3, 900, "middle")
    s += rect(x + 4, top + 12, 14, 12) + ln(x + 11, top + 12, x + 11, top + 24, LINE)
    s += f'<path d="M{x + 6} {top + 21} q5 -6 10 0 z" {LINE}/>'  # хлібина у вітрині
    s += f'<path d="M{x + F - 16} {bot} V{bot - 15} A6 6 0 0 1 {x + F - 4} {bot - 15} V{bot}" {LINE}/>'
    # маркиза
    for i in range(6):
        s += f'<path d="M{x + 3 + i * (F - 6) / 6:.1f} {top + 10} a{(F - 6) / 12:.1f} 2 0 0 0 {(F - 6) / 6:.1f} 0" {LINE}/>'
    return s


def well():
    # криниця: шестикутний зруб-смужка + дашок
    x0, y0, w, h = 150, 236, 8, 14
    s = ''
    for i in range(6):
        s += rect(x0 - 20 + i * w, y0, w, h, CUT)
        for j in range(3): s += ln(x0 - 20 + i * w, y0 + 3.5 + j * 3.5, x0 - 20 + (i + 1) * w, y0 + 3.5 + j * 3.5, LINE)
    for i in range(1, 6): s += ln(x0 - 20 + i * w, y0, x0 - 20 + i * w, y0 + h)
    s += tab((x0 - 20 + 6 * w, y0), (x0 - 20 + 6 * w, y0 + h), 4)
    s += poly([(x0 - 14, y0 - 30), (x0 + 14, y0 - 30), (x0 + 14, y0 - 6), (x0 - 14, y0 - 6)]) + ln(x0 - 14, y0 - 18, x0 + 14, y0 - 18)
    for yy in (y0 - 26, y0 - 22, y0 - 14, y0 - 10): s += ln(x0 - 14, yy, x0 + 14, yy, LINE)
    s += text(x0 + 4, y0 + h + 9.5, "криниця", 3.4, 800, "middle", 'opacity=".6"')
    return s


def village():
    s = mini_house(15, 120, 34, 26, 30, 16, hata_front, "хатка під стріхою", thatch=True)
    s += mini_house(15, 215, 32, 24, 28, 14, bakery_front, "пекарня")
    s += well()
    # соняшники-«декорації» на підставці
    for i, (x, y) in enumerate([(176, 150), (192, 150)]):
        s += poly([(x - 6, y + 14), (x + 6, y + 14), (x + 6, y + 18), (x - 6, y + 18)]) + ln(x - 6, y + 14, x + 6, y + 14)
        s += ln(x, y + 14, x, y + 2, LINE) + circ(x, y, 3.2) + ''.join(circ(x + math.cos(math.radians(a)) * 4.6, y + math.sin(math.radians(a)) * 4.6, 1.5) for a in range(0, 360, 40))
    pv = text(150, 50, "3 фігурки на 1 аркуші", 3.6, 800, "middle", 'opacity=".6"')
    return sheet("Мінінабір «Українське село»", s, pv, 3)


if __name__ == '__main__':
    for name, fn in [('sketch-1-house', house), ('sketch-2-car', car), ('sketch-3-village', village)]:
        (OUT / f'{name}.svg').write_text(fn())
        print('ok', name)
