# Кубо-супергерої PaperMagic (власні персонажі): аркуш А4 альбомний, чорні контури під розмальовку,
# кольорове прев'ю зібраної фігурки вгорі справа. Голова-куб, тулуб із ногами, руки, плащ.
# Запуск: python3 -I designs/cube-heroes/make_heroes.py  → SVG, PDF і PNG-прев'ю поруч зі скриптом
import math, pathlib, re, subprocess

HERE = pathlib.Path(__file__).parent
LOGO = (HERE.parent.parent / 'brand' / 'logo-inline.txt').read_text().strip()
LOGO_INNER = re.sub(r'^<svg[^>]*>|</svg>$', '', LOGO).replace('currentColor', '#000')

S = 36                  # ребро голови-куба
W, D, H = 32, 18, 46    # тулуб із ногами: ширина, глибина, висота
BELT, BOOT = 28, 38     # пояс і верх чобіт від верху тулуба
A, L = 9, 34            # рука: переріз і довжина
TABD = 5

CUT = 'fill="#fff" stroke="#000" stroke-width="0.9" stroke-linejoin="round"'
FOLD = 'fill="none" stroke="#000" stroke-width="0.45" stroke-dasharray="2 1.4"'
LINE = 'fill="none" stroke="#000" stroke-width="0.6" stroke-linejoin="round" stroke-linecap="round"'
WHITE = None            # палітра None = аркуш для розмальовки (тільки чорний)


def pts(a): return ' '.join(f'{x:.2f},{y:.2f}' for x, y in a)


def text(x, y, t, size=4, w=800, anchor='start'):
    return f'<text x="{x}" y="{y}" font-family="Nunito, Arial, sans-serif" font-size="{size}" font-weight="{w}" fill="#000" text-anchor="{anchor}">{t}</text>'


class Ink:
    """Малює деталі або кольорові (прев'ю), або білі з чорним контуром (аркуш)."""
    def __init__(self, pal): self.pal = pal

    def f(self, key, sw=0.6):
        c = '#fff' if self.pal is None else self.pal.get(key, key)
        if key == 'black': c = '#000'
        return f'fill="{c}" stroke="#000" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'

    def rect(self, x, y, w, h, key, sw=0.6): return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" {self.f(key, sw)}/>'
    def poly(self, a, key, sw=0.6): return f'<polygon points="{pts(a)}" {self.f(key, sw)}/>'
    def path(self, d, key, sw=0.6): return f'<path d="{d}" {self.f(key, sw)}/>'
    def circ(self, x, y, r, key, sw=0.6): return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" {self.f(key, sw)}/>'
    def ell(self, x, y, rx, ry, key, sw=0.6): return f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" {self.f(key, sw)}/>'


def line(x1, y1, x2, y2, s=LINE): return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {s}/>'


def bolt(cx, cy, r):
    return [(cx + r * .25, cy - r), (cx - r * .45, cy + r * .12), (cx - r * .02, cy + r * .12),
            (cx - r * .25, cy + r), (cx + r * .45, cy - r * .12), (cx + r * .02, cy - r * .12)]


def star(cx, cy, r):
    return [(cx + (r if i % 2 == 0 else r * .45) * math.sin(math.pi * i / 5),
             cy - (r if i % 2 == 0 else r * .45) * math.cos(math.pi * i / 5)) for i in range(10)]


def sun(cx, cy, r):
    return [(cx + (r if i % 2 == 0 else r * .62) * math.sin(math.pi * i / 8),
             cy - (r if i % 2 == 0 else r * .62) * math.cos(math.pi * i / 8)) for i in range(16)]


def drop(cx, cy, r):
    a = [(cx, cy - r)]
    for i in range(1, 20):
        t = math.pi * (-.15 + 1.3 * i / 20)
        a.append((cx + r * .62 * math.cos(t), cy + r * .35 + r * .62 * math.sin(t)))
    return a


def moon(cx, cy, r):
    outer = [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in (math.pi * (.35 + 1.3 * i / 16) for i in range(17))]
    inner = [(cx + r * .35 + r * .78 * math.cos(t), cy - r * .1 + r * .78 * math.sin(t)) for t in (math.pi * (1.6 - 1.15 * i / 16) for i in range(17))]
    return outer + inner


# ---------- герої ----------
HEROES = {
    'kapitan-blyskavka': dict(
        name='Капітан Блискавка', emblem=bolt, hair='spiky', tail=False,
        pal=dict(skin='#f6c9a0', hair='#5a3416', suit='#2f6fdc', accent='#ffd23f', mask='#d9302c',
                 cape='#d9302c', boots='#d9302c', glove='#ffd23f', mark='#d9302c', cheek='#f39a8c')),
    'divchynka-zirka': dict(
        name='Дівчинка-Зірка', emblem=star, hair='bangs', tail=True,
        pal=dict(skin='#f8d2b0', hair='#f2a03d', suit='#8e4fd6', accent='#ff7eb6', mask='#ff7eb6',
                 cape='#2bb6a8', boots='#ff7eb6', glove='#ffffff', mark='#ffe14d', cheek='#f39a8c')),
    'super-sonyashnyk': dict(
        name='Супер-Соняшник', emblem=sun, hair='curly', tail=False,
        pal=dict(skin='#f3c49a', hair='#3b2414', suit='#3aa655', accent='#ffcc1f', mask='#ffcc1f',
                 cape='#ffcc1f', boots='#6b3f1f', glove='#3aa655', mark='#f08a12', cheek='#f39a8c')),
    'kapitan-khvylia': dict(
        name='Капітан Хвиля', emblem=drop, hair='spiky', tail=False,
        pal=dict(skin='#e9b48a', hair='#1d1d2b', suit='#17a3c4', accent='#ffffff', mask='#0d4f8b',
                 cape='#0d4f8b', boots='#0d4f8b', glove='#ffffff', mark='#17a3c4', cheek='#f39a8c')),
    'misiachna-tin': dict(
        name='Місячна Тінь', emblem=moon, hair='bangs', tail=True,
        pal=dict(skin='#f6cfae', hair='#2a2a3d', suit='#33357a', accent='#c9d3e6', mask='#c9d3e6',
                 cape='#6b4fc4', boots='#c9d3e6', glove='#c9d3e6', mark='#ffe36b', cheek='#f39a8c')),
}


# ---------- грані (локальні координати 0..w × 0..h, верх грані — y=0) ----------
def head_front(k, h):
    s = S
    o = k.rect(0, 0, s, s, 'skin', 0)
    if h['hair'] == 'spiky':
        fr = [(s - i * s / 8, .2 * s if i % 2 == 0 else .3 * s) for i in range(9)]
    elif h['hair'] == 'curly':
        fr = [(s - i * s / 24, (.26 - .07 * math.sin(math.pi * (i % 4) / 4)) * s) for i in range(25)]
    else:
        fr = [(s, .34 * s), (.75 * s, .22 * s), (.5 * s, .3 * s), (.25 * s, .2 * s), (0, .3 * s)]
    o += k.poly([(0, 0), (s, 0)] + fr, 'hair')
    o += k.poly([(0, .4 * s), (.38 * s, .37 * s), (.5 * s, .42 * s), (.62 * s, .37 * s), (s, .4 * s),
                 (s, .56 * s), (.62 * s, .6 * s), (.5 * s, .53 * s), (.38 * s, .6 * s), (0, .56 * s)], 'mask')
    for ex in (.3 * s, .7 * s):
        o += k.ell(ex, .48 * s, .1 * s, .065 * s, '#fff')
        o += k.circ(ex + (.02 * s if ex < s / 2 else -.02 * s), .485 * s, .03 * s, 'black', 0)
    o += k.circ(.2 * s, .7 * s, .045 * s, 'cheek', .4) + k.circ(.8 * s, .7 * s, .045 * s, 'cheek', .4)
    o += f'<path d="M{.38 * s:.2f} {.7 * s:.2f} Q{.5 * s:.2f} {.82 * s:.2f} {.62 * s:.2f} {.7 * s:.2f}" {LINE.replace("0.6", "0.8")}/>'
    return o


def head_side(k, h):
    """Бокова грань: ребро біля обличчя — u=0."""
    s = S
    o = k.rect(0, 0, s, s, 'skin', 0)
    o += k.poly([(0, 0), (s, 0), (s, .78 * s), (.62 * s, .78 * s), (.55 * s, .3 * s), (0, .25 * s)], 'hair')
    o += k.poly([(0, .4 * s), (.45 * s, .42 * s), (.45 * s, .55 * s), (0, .56 * s)], 'mask')
    o += k.ell(.5 * s, .6 * s, .07 * s, .1 * s, 'skin')
    o += f'<path d="M{.48 * s:.2f} {.56 * s:.2f} q{.03 * s:.2f} {.04 * s:.2f} 0 {.08 * s:.2f}" {LINE}/>'
    return o


def head_back(k, h):
    s = S
    o = k.rect(0, 0, s, s, 'skin', 0)
    o += k.poly([(0, 0), (s, 0), (s, .78 * s), (0, .78 * s)], 'hair')
    o += k.rect(0, .41 * s, s, .14 * s, 'mask')
    o += k.poly([(.5 * s, .48 * s), (.36 * s, .78 * s), (.46 * s, .8 * s)], 'mask')
    o += k.poly([(.5 * s, .48 * s), (.64 * s, .8 * s), (.54 * s, .82 * s)], 'mask')
    o += k.circ(.5 * s, .48 * s, .05 * s, 'mask')
    if h['tail']:
        o += k.path(f'M{.42 * s:.2f} {.12 * s:.2f} Q{.2 * s:.2f} {.45 * s:.2f} {.5 * s:.2f} {.36 * s:.2f} '
                    f'Q{.8 * s:.2f} {.45 * s:.2f} {.58 * s:.2f} {.12 * s:.2f} Z', 'hair')
        o += k.rect(.43 * s, .1 * s, .14 * s, .06 * s, 'accent')
    return o


def head_top(k, h):
    s = S
    o = k.rect(0, 0, s, s, 'hair', 0)
    for i in range(1, 5):
        x = i * s / 5
        o += f'<path d="M{x:.2f} {.85 * s:.2f} Q{x + 3:.2f} {.5 * s:.2f} {x:.2f} {.12 * s:.2f}" {LINE.replace("0.6", "0.45")}/>'
    return o


def head_bottom(k, h): return k.rect(0, 0, S, S, 'skin', 0)


def body_front(k, h):
    o = k.rect(0, 0, W, H, 'suit', 0)
    o += k.poly([(W * .34, 0), (W / 2, 4), (W * .66, 0)], 'accent')
    o += k.circ(W / 2, 15, 8.5, 'accent')
    o += k.poly(h['emblem'](W / 2, 15, 6.2), 'mark')
    o += k.rect(0, BELT, W, 3, 'accent') + k.rect(W / 2 - 3, BELT - .5, 6, 4, 'mark')
    o += k.rect(0, BOOT, W, H - BOOT, 'boots')
    o += line(W / 2, BELT + 3, W / 2, H, LINE)
    return o


def body_side(k, h):
    o = k.rect(0, 0, D, H, 'suit', 0)
    o += k.rect(0, BELT, D, 3, 'accent') + k.rect(0, BOOT, D, H - BOOT, 'boots')
    o += k.rect((D - A) / 2, 2, A, L - 3, 'suit', .3).replace('stroke-width="0.3"', 'stroke-width="0.4" stroke-dasharray="1.5 1.2"')
    return o


def body_back(k, h):
    o = k.rect(0, 0, W, H, 'suit', 0)
    o += k.rect(0, BELT, W, 3, 'accent') + k.rect(0, BOOT, W, H - BOOT, 'boots')
    o += line(W / 2, BELT + 3, W / 2, H, LINE)
    o += k.rect(W / 2 - 15, 1, 30, 5.5, 'suit').replace('stroke-width="0.6"', 'stroke-width="0.4" stroke-dasharray="1.5 1.2"')
    return o


def body_top(k, h): return k.rect(0, 0, W, D, 'suit', 0)


def body_bottom(k, h): return k.rect(0, 0, W, D, 'boots', 0) + line(W / 2, 0, W / 2, D, LINE)


def arm_face(k, h):
    o = k.rect(0, 0, A, L, 'suit', 0)
    o += k.rect(0, L - 10, A, 10, 'glove') + k.rect(0, L - 11.5, A, 2, 'accent')
    return o


def arm_top(k, h): return k.rect(0, 0, A, A, 'suit', 0)


def arm_bottom(k, h): return k.rect(0, 0, A, A, 'glove', 0)


# ---------- розгортки ----------
def tab(p, q, d=TABD, inset=0.25):
    """Клапан назовні від ребра p→q (ліворуч від напрямку руху в координатах SVG)."""
    (x1, y1), (x2, y2) = p, q
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy); nx, ny = dy / n, -dx / n
    a = (x1 + dx * inset + nx * d, y1 + dy * inset + ny * d)
    b = (x2 - dx * inset + nx * d, y2 - dy * inset + ny * d)
    return f'<polygon points="{pts([p, a, b, q])}" {CUT.replace("0.9", "0.7")}/>'


def box_net(x0, y0, faces, h, ci, cd, cap_top, cap_bot, k, hero, d=TABD):
    """Стрічка граней [(ширина, малюнок, дзеркально)] висотою h, кришки над/під гранню ci глибиною cd."""
    xs = [x0]
    for w, *_ in faces: xs.append(xs[-1] + w)
    xc, wc = xs[ci], faces[ci][0]
    y1 = y0 + h
    o = tab((xs[-1], y0), (xs[-1], y1), d)                               # бічний клапан на кінці стрічки
    for top, y in ((True, y0 - cd), (False, y1)):
        a, b, c_, e = (xc, y + cd), (xc, y), (xc + wc, y), (xc + wc, y + cd)
        if top: o += tab(a, b, d) + tab(b, c_, d) + tab(c_, e, d)
        else:
            a, b, c_, e = (xc, y), (xc + wc, y), (xc + wc, y + cd), (xc, y + cd)
            o += tab(b, c_, d) + tab(c_, e, d) + tab(e, a, d)
    out = [(x0, y0), (xc, y0), (xc, y0 - cd), (xc + wc, y0 - cd), (xc + wc, y0), (xs[-1], y0),
           (xs[-1], y1), (xc + wc, y1), (xc + wc, y1 + cd), (xc, y1 + cd), (xc, y1), (x0, y1)]
    o += f'<polygon points="{pts(out)}" {CUT}/>'
    for i, (w, draw, mirror) in enumerate(faces):
        tr = f'translate({xs[i] + w:.2f} {y0}) scale(-1 1)' if mirror else f'translate({xs[i]:.2f} {y0})'
        o += f'<g transform="{tr}">{draw(k, hero)}</g>'
    o += f'<g transform="translate({xc} {y0 - cd})">{cap_top(k, hero)}</g>'
    o += f'<g transform="translate({xc} {y1})">{cap_bot(k, hero)}</g>'
    o += f'<polygon points="{pts(out)}" fill="none" stroke="#000" stroke-width="0.9" stroke-linejoin="round"/>'
    for x in xs[1:-1]: o += line(x, y0, x, y1, FOLD)
    o += line(xc, y0, xc + wc, y0, FOLD) + line(xc, y1, xc + wc, y1, FOLD)
    return o


HEAD_AT, BODY_AT, ARM_AT = (84, 46), (70, 132), [(12, 22), (12, 84)]
CAPE_AT = (35, 147)    # середина верхнього краю плаща


def cape(k, hero, x, y, d=6):
    top, bot, hh = 30, 48, 46
    outline = [(x - top / 2, y), (x + top / 2, y), (x + bot / 2, y + hh)]
    for i in range(6, -1, -1):
        outline.append((x - bot / 2 + i * bot / 6, y + hh + (0 if i % 2 == 0 else -3.5)))
    o = tab((x - top / 2, y), (x + top / 2, y), d, 0.08)
    o += k.poly(outline, 'cape', 0.9)
    o += k.poly(hero['emblem'](x, y + 24, 7), 'accent')
    o += line(x - top / 2, y, x + top / 2, y, FOLD)
    return o


def nets(hero):
    k = Ink(None)
    o = box_net(*HEAD_AT, [(S, head_side, True), (S, head_front, False), (S, head_side, False), (S, head_back, False)],
                S, 1, S, head_top, head_bottom, k, hero)
    o += box_net(*BODY_AT, [(W, body_front, False), (D, body_side, False), (W, body_back, False), (D, body_side, True)],
                 H, 0, D, body_top, body_bottom, k, hero)
    for x, y in ARM_AT:
        o += box_net(x, y, [(A, arm_face, False)] * 4, L, 1, A, arm_top, arm_bottom, k, hero, 4)
    o += cape(k, hero, *CAPE_AT)
    return o


# ---------- кольорове прев'ю зібраної фігурки ----------
PX, PY, PK = 252, 79, 0.55


def P(x, y, z): return (PX + (x + z) * .87 * PK, PY + (x - z) * .5 * PK - y * PK)


def box3d(k, hero, x0, y0, z0, w, h, d, front, right, top):
    c, sn, kk = .87 * PK, .5 * PK, PK
    o = f'<g transform="matrix({c:.4f} {sn:.4f} 0 {kk:.4f} {PX + (x0 + z0) * c:.3f} {PY + (x0 - z0) * sn - (y0 + h) * kk:.3f})">{front(k, hero)}</g>'
    o += (f'<g transform="matrix({c:.4f} {-sn:.4f} 0 {kk:.4f} {PX + (x0 + w + z0) * c:.3f} {PY + (x0 + w - z0) * sn - (y0 + h) * kk:.3f})">'
          f'{right(k, hero)}<rect width="{d}" height="{h}" fill="#000" opacity=".14"/></g>')
    o += (f'<g transform="matrix({c:.4f} {sn:.4f} {-c:.4f} {sn:.4f} {PX + (x0 + z0 + d) * c:.3f} {PY + (x0 - z0 - d) * sn - (y0 + h) * kk:.3f})">'
          f'{top(k, hero)}<rect width="{w}" height="{d}" fill="#fff" opacity=".12"/></g>')
    return o


def preview(hero):
    k = Ink(hero['pal'])
    ax = (D - A) / 2
    o = box3d(k, hero, -A, H - 2 - L, ax, A, L, A, arm_face, arm_face, arm_top)       # ліва рука
    cz = D + .3
    o += f'<polygon points="{pts([P(1, H - 1, cz), P(W - 1, H - 1, cz), P(W + 5, 4, cz), P(-5, 4, cz)])}" {k.f("cape", .5)}/>'
    o += box3d(k, hero, 0, 0, 0, W, H, D, body_front, body_side, body_top)
    o += box3d(k, hero, W, H - 2 - L, ax, A, L, A, arm_face, arm_face, arm_top)        # права рука
    o += box3d(k, hero, (W - S) / 2, H, (D - S) / 2, S, S, S, head_front, head_side, head_top)
    return o


def sheet(hero):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 297 210" width="297mm" height="210mm">
<rect width="297" height="210" fill="#fff"/>
{text(289, 15, "PaperMagic", 9, 900, "end")}
<g>{preview(hero)}</g>
{text(268, 95, hero["name"], 3.6, 800, "middle")}
<g transform="translate(248 116) scale(0.048)">{LOGO_INNER}</g>
{text(188, 141, "Інструкція:", 4, 700)}
{text(188, 147, "- Роздрукуй", 3.6, 600)}{text(188, 152, "- Розмалюй", 3.6, 600)}{text(188, 157, "- Виріж", 3.6, 600)}{text(188, 162, "- Склей 3D фігурку", 3.6, 600)}
{text(188, 171, f"{hero['name']} · середньо · 30–40 хв", 3.2, 700)}
{text(188, 177, "Руки й плащ клей на пунктирні місця", 3, 600)}
{text(188, 198, "- - - згинати      ▭ клапан — намаж клеєм", 3, 600)}
{text(289, 204, "© PaperMagic · @papermagic_ua · лише для особистого друку", 2.8, 600, "end")}
<g>{nets(hero)}</g>
</svg>'''


def check():
    """Розміри ребер, що склеюються, і межі аркуша."""
    hx, hy = HEAD_AT; bx, by = BODY_AT
    assert hx + 4 * S + TABD <= 236, 'голова не налазить на прев\'ю'
    assert hy - S - TABD >= 4 and by + H + D + TABD <= 206, 'усе в межах друку (вертикаль)'
    assert hx + S - TABD > bx + W + TABD, 'кришка тулуба не перетинає низ голови'
    assert hy + 2 * S + TABD < by, 'низ голови вище за стрічку тулуба'
    assert A < D and L < BOOT, 'рука вміщається на бічній грані тулуба'
    print(f'ок: голова {S}×{S}×{S}, тулуб {W}×{D}×{H}, фігурка ≈{H + S} мм заввишки')


SITE = HERE.parent.parent / 'papermagic-site' / 'img'


def site_fig(hero):
    """Кольорова фігурка для карток сайту (viewBox 320×260, як в інших фігурок)."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="225 19 90 73">'
            f'<ellipse cx="268" cy="86" rx="22" ry="3.2" fill="#2a2440" opacity=".1"/>{preview(hero)}</svg>')


if __name__ == '__main__':
    check()
    chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    for slug, hero in HEROES.items():
        svg = HERE / f'papermagic-{slug}.svg'
        svg.write_text(sheet(hero))
        pdf, html = svg.with_suffix('.pdf'), HERE / '_print.html'
        html.write_text(f'<!doctype html><meta charset="utf-8"><style>@page{{size:A4 landscape;margin:0}}html,body{{margin:0}}'
                        f'img{{width:297mm;height:210mm;display:block}}</style><img src="{svg.name}">')
        subprocess.run(['taskpolicy', '-b', 'nice', '-n', '19', chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={pdf}', html.as_uri()], check=True, capture_output=True, timeout=120)
        html.unlink()
        subprocess.run(['sips', '-s', 'format', 'png', '-Z', '1600', str(pdf), '--out', str(svg.with_suffix('.png'))],
                       check=True, capture_output=True)
        (SITE / f'hero-{slug}.svg').write_text(site_fig(hero))
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '70', '-Z', '842', str(svg.with_suffix('.png')),
                        '--out', str(SITE / f'sheet-hero-{slug}.jpg')], check=True, capture_output=True)
        print('ok', svg.name, pdf.name)
