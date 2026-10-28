"""Звук для рілсів 1, 2, 4: легка фонова музика + звукові ефекти під моменти відео.
Усе синтезовано тут (інструменти з ads/src/music.py), без чужих семплів і прав.
python3 -I sound.py N OUT.wav      (N: 1, 2 або 4; таймінги збігаються з reels.html)"""
import os, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), 'ads', 'src'))
from music import SR, note_hz, env, pluck, marimba, glock, pad, bass, kick, shaker, chord, MAJOR  # noqa: E402

rng = np.random.default_rng(42)

def _t(d): return np.arange(int(d * SR)) / SR

def lowpass(x, a):  # однополюсний ФНЧ, a — коефіцієнт (можна масив)
    y = np.empty_like(x); acc = 0.0
    a = np.broadcast_to(a, x.shape)
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc); y[i] = acc
    return y

# ---------------- звукові ефекти ----------------
def pop(f0=900, d=0.09):  # «бульк» на появу плашки
    t = _t(d); f = f0 * (1 + 1.2 * np.exp(-t / 0.012))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.025) * 0.55

def whoosh(d=0.45, up=True):  # повітряний «вжух» на перехід
    t = _t(d); nz = rng.standard_normal(len(t))
    x = t / d; a = 0.02 + 0.35 * (x if up else 1 - x) ** 2
    e = np.sin(np.pi * x) ** 1.6
    return lowpass(nz, a) * e * 0.9

def shutter():  # клац камери на стоп-кадр
    t = _t(0.12); nz = rng.standard_normal(len(t))
    c = (np.exp(-t / 0.004) + 0.7 * np.exp(-np.maximum(0, t - 0.055) / 0.006) * (t > 0.055))
    return np.diff(np.concatenate([[0], nz])) * c * 0.5

def scratch(d=0.42):  # «скретч» платівки: музика зупиняється
    t = _t(d); x = t / d
    rate = np.where(x < 0.35, 1 + 2.5 * x, 1.9 - 2.6 * (x - 0.35))  # туди-назад
    f = 180 * np.clip(rate, 0.05, None)
    tone = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25
    nz = lowpass(rng.standard_normal(len(t)), 0.25) * 0.6
    return (tone + nz) * np.sin(np.pi * x) ** 0.6 * 0.7

def rewind(d):  # перемотка касети: швидке «ж-ж-ж» з плаваючою висотою
    t = _t(d); x = t / d
    f = 900 + 500 * np.sin(2 * np.pi * 7 * t) + 700 * x
    chirp = np.sin(2 * np.pi * np.cumsum(f) / SR)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 23 * t)
    nz = lowpass(rng.standard_normal(len(t)), 0.3)
    e = np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.05)
    return (chirp * 0.18 * am + nz * 0.35) * e

def clunk():  # «клац» кнопки касетника — перемотка закінчилась
    t = _t(0.18); f = 140 * (1 + 2 * np.exp(-t / 0.01))
    out = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.04)
    c = shutter(); out[:len(c)] += c * 0.8
    return out * 0.7

def fastfwd(d):  # прискорення: швидкі висхідні «біп-біп»
    out = np.zeros(int(d * SR)); step = 0.085; i = 0
    while i * step < d - 0.05:
        n = 72 + (i % 8) + 2 * (i // 8)
        s = marimba(note_hz(n), 0.12) * 0.32; k = int(i * step * SR)
        out[k:k + len(s)] += s[:len(out) - k]; i += 1
    return out

def ding(n=84):  # «дзинь» лічильника
    return glock(note_hz(n), 0.5) * 0.4

def tada():  # «Тадам!»: швидкий арпеджіо + блиск
    out = np.zeros(int(1.6 * SR))
    for i, n in enumerate([72, 76, 79, 84, 88]):
        s = glock(note_hz(n), 1.0) * 0.32; k = int(i * 0.06 * SR)
        out[k:k + len(s)] += s[:len(out) - k]
    return out + sparkle(1.6) * 0.8

def sparkle(d=1.2):  # конфеті / чарівний блиск
    out = np.zeros(int(d * SR))
    for _ in range(int(d * 14)):
        k = int(rng.random() * (d - 0.15) * SR); s = glock(note_hz(int(rng.integers(88, 100))), 0.15) * 0.07
        out[k:k + len(s)] += s
    return out

def boing(d=0.5):  # кумедне «боїнг»
    t = _t(d); f = 220 + 160 * np.sin(2 * np.pi * 9 * t) * np.exp(-t / 0.25) + 120 * np.exp(-t / 0.05)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28) * 0.5

def hmm(d=0.9):  # загадкове «хм?» — дві ноти вгору
    out = np.zeros(int(d * SR))
    for i, n in enumerate([67, 70]):
        s = marimba(note_hz(n), 0.4) * 0.4; k = int(i * 0.22 * SR)
        out[k:k + len(s)] += s[:len(out) - k]
    return out

def chime():  # фінальна картка
    out = np.zeros(int(1.6 * SR))
    for i, n in enumerate([79, 84, 91]):
        s = glock(note_hz(n), 1.2) * 0.3; k = int(i * 0.11 * SR)
        out[k:k + len(s)] += s[:len(out) - k]
    return out

# ---------------- легка фонова музика ----------------
def bed(dur, bpm, root, prog, seed, anchor=0.0, intro_until=0.0, sus_until=0.0):
    """Мʼякий трек: пед, арпеджіо, дзвіночки, тихий бас і легкий ритм.
    anchor — секунда, на яку припадає сильна доля (дроп); до intro_until — тихіше, без ритму;
    до sus_until — «загадковий» режим (тільки низький пед)."""
    beat = 60 / bpm; bar = 4 * beat
    n = int((dur + 1) * SR); L = np.zeros(n); R = np.zeros(n)
    def put(sig, t, gl=1.0, gr=1.0):
        i = int(t * SR)
        if i < 0 or i >= n: return
        m = min(len(sig), n - i); L[i:i + m] += sig[:m] * gl; R[i:i + m] += sig[:m] * gr
    mr = np.random.default_rng(seed)
    motif = [(b, s, int(mr.choice([0, 2, 4, 7, 9, 12]))) for b in range(2) for s in range(8)
             if mr.random() < (0.6 if s % 2 == 0 else 0.25)]
    first = int(np.floor((0 - anchor) / bar)) - 1
    for b in range(first, int(np.ceil((dur - anchor) / bar)) + 1):
        t0 = anchor + b * bar
        if t0 + bar < 0: continue
        deg = prog[b % len(prog)]; ch = chord(root, deg)
        sus = t0 < sus_until; quiet = t0 < intro_until
        put(pad([note_hz(x - (12 if sus else 0)) for x in ch], bar) * (0.2 if sus else 0.13), t0)
        if sus: continue
        for e in range(8):  # арпеджіо
            nn = ch[e % 3] + (12 if e >= 4 else 0)
            put(pluck(note_hz(nn), beat / 2, 1.2) * (0.05 if quiet else 0.085), t0 + e * beat / 2, 0.6, 1.0)
        if quiet: continue
        for q in range(4):
            tq = t0 + q * beat
            if q in (0, 2): put(kick() * 0.32, tq)
            for s16 in range(4): put(shaker() * 0.8, tq + s16 * beat / 4, 1.0, 0.6)
        for e in (0, 3, 4, 6):
            put(bass(note_hz(root - 24 + deg), beat * 0.45) * 0.16, t0 + e * beat / 2)
        for (mb, s, off) in motif:
            if mb != b % 2: continue
            nn = root + 12 + deg + off
            while (nn - root) % 12 not in MAJOR: nn += 1
            put(glock(note_hz(nn), beat) * 0.10, t0 + s * beat / 2, 1.0, 0.75)
    dl = int(beat * 0.75 * SR); L2 = L.copy(); R2 = R.copy()
    L2[dl:] += R[:-dl] * 0.2; R2[dl:] += L[:-dl] * 0.2
    return np.stack([L2, R2], 1)[:int(dur * SR)]

# ---------------- монтаж звуку ----------------
def fade_gap(m, a, b, f=0.03):  # музика замовкає на [a, b] (стоп-кадр) і повертається
    ia, ib, fi = int(a * SR), int(b * SR), int(f * SR)
    g = np.ones(len(m)); g[ia:ib] = 0
    g[max(0, ia - fi):ia] = np.linspace(1, 0, min(fi, ia)); g[ib:ib + fi] = np.linspace(0, 1, len(g[ib:ib + fi]))
    return m * g[:, None]

def tape_reverse(m, a, b, speed=2.2):  # на [a, b] музика крутиться назад і швидше (як касета)
    ia, ib = int(a * SR), int(b * SR); need = int((ib - ia) * speed)
    src = m[max(0, ia - need):ia][::-1]
    idx = np.linspace(0, len(src) - 1, ib - ia)
    seg = np.stack([np.interp(idx, np.arange(len(src)), src[:, c]) for c in (0, 1)], 1)
    w = np.linspace(0, 1, len(seg))
    seg *= (0.55 + 0.25 * np.sin(2 * np.pi * 5 * w * (b - a)))[:, None]  # «плавання» касети
    out = m.copy(); out[ia:ib] = seg; return out

def sped(m, a, b, k=1.5):  # на [a, b] музика прискорена (вища), як при перемотці вперед
    ia, ib = int(a * SR), int(b * SR)
    idx = np.clip(ia + (np.arange(ib - ia) * k), 0, len(m) - 1)
    out = m.copy()
    for c in (0, 1): out[ia:ib, c] = np.interp(idx, np.arange(len(m)), m[:, c])
    return out

def place(mix, sig, t, g=1.0, pan=0.0):
    i = int(t * SR); m = min(len(sig), len(mix) - i)
    if m <= 0: return
    mix[i:i + m, 0] += sig[:m] * g * (1 - max(0, pan)); mix[i:i + m, 1] += sig[:m] * g * (1 + min(0, pan))

def reel(n):
    if n == 1:
        dur = 16.6
        m = bed(dur, 112, 60, [0, 7, 9, 5], 3, anchor=2.6, intro_until=2.6)
        m = fade_gap(m, 1.2, 2.6)              # стоп-кадр: музика різко обривається
        m = sped(m, 9.4, 11.2, 1.45)           # ×4 — музика теж «біжить»
        fx = [(pop(), 0.02), (scratch(), 1.08), (shutter(), 1.2, 1.1), (hmm(), 1.75, 0.8),
              (whoosh(0.4), 2.32), (pop(1000), 2.6), (pop(), 5.0), (pop(780), 6.8),
              (whoosh(0.3), 9.3, 0.7), (fastfwd(1.8), 9.4, 0.8), (pop(1100), 9.42, 0.7),
              (tada(), 11.2), (whoosh(0.45, False), 13.2), (chime(), 13.4)]
    elif n == 2:
        dur = 19.0
        m = bed(dur, 104, 65, [0, 9, 5, 7], 8, anchor=2.4, sus_until=2.4)
        m = tape_reverse(m, 6.0, 9.2)
        fx = [(hmm(), 0.15), (whoosh(0.5), 1.95), (pop(), 2.4), (sparkle(1.0), 4.0, 1.2), (pop(1100), 4.0),
              (whoosh(0.3), 5.75, 0.8), (rewind(3.2), 6.0, 0.6), (pop(700), 6.02, 0.7), (clunk(), 9.12), (pop(), 9.25),
              (pop(), 11.0), (pop(1000), 13.6), (whoosh(0.45, False), 15.6), (chime(), 15.8)]
    elif n == 4:
        dur = 18.2
        m = bed(dur, 120, 62, [0, 5, 9, 7], 5, anchor=2.6, intro_until=2.6)
        m = sped(m, 0.0, 2.6, 1.25)            # хук на прискоренні — музика бадьоріша
        m = fade_gap(m, 9.8, 11.0)             # стоп-кадр «контролер якості»
        per = (2.6 - 0.2 - 0.3) / 5            # лічильник 1…5 (як sheetCounter у reels.html)
        fx = [(pop(), 0.02)] + [(ding(79 + 2 * k), 0.2 + k * per, 0.75) for k in range(5)]
        fx += [(whoosh(0.4), 2.35), (pop(1000), 2.6), (pop(), 4.2), (pop(800), 6.6),
               (shutter(), 9.8, 1.1), (boing(), 9.95), (pop(1050), 11.0), (pop(), 12.4),
               (whoosh(0.45, False), 14.0), (chime(), 14.2)]
    else:
        sys.exit('звук робимо лише для рілсів 1, 2, 4 (у рілсі 3 — озвучка)')
    m = m / (np.max(np.abs(m)) + 1e-9) * 0.42  # музика — фоном, ефекти поверх
    for e in fx:
        sig, t, g = e[0], e[1], (e[2] if len(e) > 2 else 1.0)
        place(m, sig, t, g * 0.5, pan=float(rng.uniform(-0.25, 0.25)))
    m = np.tanh(m * 1.1); m /= np.max(np.abs(m)) + 1e-9; m *= 0.89
    fo = int(0.8 * SR); m[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    return m

if __name__ == '__main__':
    n, out = int(sys.argv[1]), sys.argv[2]
    m = reel(n); pcm = (m * 32767).astype(np.int16)
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(out, f'{len(m) / SR:.1f}s')
