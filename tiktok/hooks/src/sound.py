"""Музика й SFX для TikTok-хуків PaperMagic: власні інструментальні треки, синтезовані тут кодом.
Без семплів і чужих мелодій. Укулеле — Karplus-Strong, ксилофон/глокеншпіль/піаніно — адитивний синтез,
шуми (олівець, ножиці, «пуф», дріб) — фільтрований шум. Акценти стоять на таймінгах сцен src/hook-N.html.
Вихід: WAV 48 кГц, 16 біт, стерео, ~-14 LUFS integrated, true peak ≤ -1 dBTP, fade-out 0.3 с.
python3 -I sound.py OUT.wav N DURATION   (N: 1..3)"""
import sys, wave
sys.dont_write_bytecode = True
import numpy as np
from scipy.signal import butter, sosfilt, lfilter, fftconvolve, resample_poly
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 48000
hz = lambda n: 440.0 * 2 ** ((n - 69) / 12)
rng = np.random.default_rng(7)

def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x, axis=0)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x, axis=0)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x, axis=0)
def tt(d): return np.arange(int(d * SR)) / SR
def env(t, a, dec): return np.minimum(1, t / a) * np.exp(-t / dec)
def noise(d): return rng.standard_normal(int(d * SR))

# ---------- інструменти ----------
def uke(f, d=0.9, damp=0.994, bright=0.6):
    """Щипкова струна (Karplus-Strong): блоками по періоду, потім точне підлаштування висоти."""
    N = max(8, int(round(SR / f - 0.5))); n = int(d * SR)
    y = np.zeros(n + N + 1)
    y[1:N + 1] = lp(rng.uniform(-1, 1, N), 1000 + 7000 * bright)
    for i in range(N + 1, len(y), N):
        m = min(N, len(y) - i)
        y[i:i + m] = damp * 0.5 * (y[i - N:i - N + m] + y[i - N - 1:i - N - 1 + m])
    y = y[1:]
    src = np.arange(n) * (f * (N + 0.5) / SR)  # частота KS = SR/(N+½) → перерахувати на f
    out = np.interp(src, np.arange(len(y)), y)
    t = tt(d); out *= np.minimum(1, t / 0.002); r = int(0.03 * SR); out[-r:] *= np.linspace(1, 0, r)
    return out

def xylo(f, d=0.5, dec=0.13):
    t = tt(d)
    w = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.03) \
        + 0.12 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t / 0.012)
    click = bp(noise(d), 2000, 8000) * np.exp(-t / 0.003) * 0.15
    return (w * env(t, 0.001, dec)) + click

def glock(f, d=1.6, dec=0.7):
    t = tt(d)
    parts = [(1, 1, dec), (2.76, .45, dec * .4), (5.4, .25, dec * .2), (8.93, .12, dec * .1)]
    return sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t / dc) for k, a, dc in parts) * np.minimum(1, t / 0.001)

def piano(f, d=1.5, vel=1.0):
    t = tt(d); B = 0.0004
    w = sum((1 / k ** 1.3) * np.sin(2 * np.pi * f * k * np.sqrt(1 + B * k * k) * t) * np.exp(-t * (1.2 + 0.9 * k) * (0.7 + 0.3 * vel))
            for k in range(1, 8))
    w += 0.6 * np.sin(2 * np.pi * f * t * 1.0012) * np.exp(-t / 1.2)   # друга струна хору
    hammer = lp(noise(d), 3000) * np.exp(-t / 0.004) * 0.05 * vel
    e = np.minimum(1, t / 0.002); r = int(0.06 * SR); e[-r:] *= np.linspace(1, 0, r)
    return (w + hammer) * e * vel

def bass(f, d=0.5):
    t = tt(d)
    w = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.08)
    e = env(t, 0.004, 0.35); r = min(len(t), int(0.04 * SR)); e[-r:] *= np.linspace(1, 0, r)
    return w * e

def clap(d=0.25):
    t = tt(d); n = noise(d); e = np.zeros_like(t)
    for o in (0, 0.009, 0.018): e += (t >= o) * np.exp(-np.maximum(0, t - o) / (0.006 if o < 0.018 else 0.07))
    return bp(n, 900, 3500) * e * 0.5

def shaker(d=0.08):
    t = tt(d); return hp(noise(d), 6000) * np.sin(np.pi * t / d) ** 2 * 0.25

def pop(f0=500, f1=1400, d=0.11):
    """«Буль»: синус із різким підйомом висоти."""
    t = tt(d); f = f0 + (f1 - f0) * (1 - np.exp(-t / 0.02))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(t, 0.001, 0.03)

def shimmer(d=1.4):
    """Блискучий «шурх» конфеті: високий шум, що наростає й згасає."""
    t = tt(d); e = np.minimum(1, t / 0.04) * np.exp(-t / 0.45)
    return bp(noise(d), 5000, 14000) * e * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t)) * 0.35

def whoosh(d=0.5, lo=300, hi=3000, rev=False):
    t = tt(d); n = noise(d); out = np.zeros_like(t); S = 16; L = len(t) // S + 1
    for s in range(S):     # смуга, що повзе вгору (або вниз)
        c = lo * (hi / lo) ** (s / (S - 1)); seg = bp(n, c * 0.7, min(c * 1.4, 20000))
        w = np.zeros_like(t); w[s * L:(s + 1) * L] = 1; out += seg * uniform_filter1d(w, L)
    out *= np.sin(np.pi * t / d) ** 1.5
    return out[::-1] if rev else out

def roll(d=0.7):
    """Барабанний дріб: удари малого кожні ~28 мс, крещендо."""
    t = tt(d); out = np.zeros_like(t); hit = tt(0.06)
    h = (bp(noise(0.06), 1500, 7000) + 0.6 * np.sin(2 * np.pi * 210 * hit)) * np.exp(-hit / 0.012)
    k = 0.0
    while k < d - 0.02:
        i = int(k * SR); m = min(len(h), len(t) - i); out[i:i + m] += h[:m] * (0.25 + 0.75 * (k / d) ** 1.5) * rng.uniform(.8, 1)
        k += 0.028
    return out * 0.5

def pencil(d):
    """Шурхіт олівця: зернистий шум, штрихи туди-сюди."""
    t = tt(d); n = bp(noise(d), 2500, 7500) * (1 + 0.5 * bp(noise(d), 30, 120) * 20)
    stroke = np.abs(np.sin(7 * t * 2)) ** 0.6     # штрих ≈ кожні 0.22 с (як рух олівця в сцені)
    return n * stroke * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.08) * 0.1

def snip():
    """Клацання ножиць: металевий клік + короткий «шк»."""
    t = tt(0.09)
    ring = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(3100, .5), (4700, .35), (6900, .2)]) * np.exp(-t / 0.012)
    return ring * 0.5 + bp(noise(0.09), 3000, 9000) * np.exp(-t / 0.02) * 0.4

def puff():
    """«Пуф» склеювання: мʼякий видих шуму + глухий «тук»."""
    t = tt(0.45)
    air = lp(noise(0.45), 1800) * np.minimum(1, t / 0.01) * np.exp(-t / 0.12)
    thump = np.sin(2 * np.pi * np.cumsum(90 + 80 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.08)
    return air * 0.5 + thump * 0.5

def rustle(d=0.5):
    t = tt(d); return bp(noise(d), 800, 5000) * np.abs(bp(noise(d), 8, 40)) * 6 * np.sin(np.pi * t / d) * 0.25

# ---------- мікс ----------
class Mix:
    def __init__(s, dur): s.n = int(round(dur * SR)); s.dry = np.zeros((s.n, 2)); s.fx = np.zeros((s.n, 2))
    def put(s, sig, t, g=1.0, pan=0.0, rev=0.25):
        i = int(round(t * SR))
        if i >= s.n: return
        if i < 0: sig = sig[-i:]; i = 0
        m = min(len(sig), s.n - i); a = sig[:m] * g
        lr = np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
        s.dry[i:i + m] += a[:, None] * lr; s.fx[i:i + m] += a[:, None] * lr * rev
    def chord(s, notes, t, g, inst=uke, spread=0.012, pan=0.0, **kw):
        for j, nn in enumerate(notes):
            s.put(inst(hz(nn), **kw), t + j * spread, g, pan + 0.25 * (j / max(1, len(notes) - 1) - 0.5))
    def render(s):
        ir_t = tt(1.1); ir = np.stack([rng.standard_normal(len(ir_t)), rng.standard_normal(len(ir_t))], 1) * np.exp(-ir_t / 0.3)[:, None]
        ir = lp(ir, 5000) * 0.02
        wet = np.stack([fftconvolve(s.fx[:, c], ir[:, c])[:s.n] for c in (0, 1)], 1)
        return hp(s.dry + wet, 40)

# ---------- гучність (ITU-R BS.1770) ----------
def lufs(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1, -2, 1], [1, -1.99004745483398, 0.99007225036621]
    y = lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    z = np.array([np.sum(np.mean(y[i:i + blk] ** 2, 0)) for i in range(0, len(y) - blk + 1, hop)])
    L = -0.691 + 10 * np.log10(z + 1e-12)
    z = z[L > -70]; rel = -0.691 + 10 * np.log10(np.mean(z)) - 10
    z = z[-0.691 + 10 * np.log10(z) > rel]
    return -0.691 + 10 * np.log10(np.mean(z))

def true_peak(x): return 20 * np.log10(np.max(np.abs(resample_poly(x, 4, 1, axis=0))) + 1e-12)

def limit(x, ceil_db=-1.5):
    """Лімітер з передбаченням 3 мс за пробами з 4× передискретизацією."""
    thr = 10 ** (ceil_db / 20)
    pk = np.max(np.abs(resample_poly(x, 4, 1, axis=0)), 1)[:len(x) * 4].reshape(-1, 4).max(1)
    g = np.minimum(1, thr / (pk + 1e-12)); w = int(0.003 * SR)
    g = minimum_filter1d(g, 2 * w + 1); g = uniform_filter1d(g, w)
    return x * g[:, None]

def master(x, target=-14.0):
    x = np.tanh(x * 1.2) / 1.2                  # мʼяка сатурація
    for _ in range(6):
        x = x * 10 ** ((target - lufs(x)) / 20)
        x = limit(x)
    f = int(0.3 * SR); x[-f:] *= np.linspace(1, 0, f)[:, None] ** 1.5
    return x

# ---------- хук 1: «Це був аркуш паперу» — укулеле-піцикато, D-дур, 114 → 120 BPM ----------
CH = {'D': [62, 66, 69, 74], 'G': [62, 67, 71, 74], 'A': [61, 64, 69, 73], 'Bm': [62, 66, 71, 74], 'Em': [64, 67, 71, 76],
      'Am': [64, 69, 72, 76], 'C': [64, 67, 72, 76], 'E': [64, 68, 71, 76], 'Dm': [62, 65, 69, 74], 'F': [65, 69, 72, 77],
      'Bb': [62, 65, 70, 74], 'A7': [64, 67, 69, 73], 'Cmaj': [60, 64, 67, 72]}
ROOT = {'D': 38, 'G': 43, 'A': 45, 'Bm': 47, 'Em': 40, 'Am': 45, 'C': 48, 'E': 40, 'Dm': 38, 'F': 41, 'Bb': 46, 'A7': 45, 'Cmaj': 48}
MOTIF = [3, 1, 2, 3, 2, 1, 0, 1]              # контур мелодії по тонах акорду (власний)

def groove(m, chords, e, t_end, mel_inst=None, mel_g=0.0, claps=True, uke_g=0.22, oct_up=12):
    """Піцикато-укулеле восьмими + бас на долі + мелодія з тонів акорду. chords: [(start, name)], e — тривалість восьмої."""
    for ci, (t0, name) in enumerate(chords):
        t1 = chords[ci + 1][0] if ci + 1 < len(chords) else t_end
        tones = CH[name]; k = 0; t = t0
        while t < t1 - 1e-6:
            nn = tones[[0, 3, 1, 2, 3, 1, 2, 3][k % 8]] + (12 if k % 2 else 0)
            m.put(uke(hz(nn), 0.35, damp=0.985), t, uke_g * (1.0 if k % 2 == 0 else 0.7), -0.25 + 0.5 * (k % 2))
            if k % 2 == 0: m.put(bass(hz(ROOT[name] + (7 if k % 4 == 2 else 0)), e * 1.8), t, 0.5, 0, rev=0.05)
            if claps and k % 4 == 2: m.put(clap(), t, 0.22, 0.1)
            if claps: m.put(shaker(), t + e * 0.5, 0.18, 0.3, rev=0.05)
            if mel_inst and k % 2 == 0 and MOTIF[(k // 2 + ci) % 8] >= 0:
                m.put(mel_inst(hz(tones[MOTIF[(k // 2 + ci * 3) % 8]] + oct_up)), t, mel_g, 0.15)
            k += 1; t += e

def hook1(dur):
    m = Mix(dur)
    # 0–2.1 с: 114 BPM (4 долі = 2.1 с), одразу з 0.0 — яскравий удар
    a = Mix(2.1); e = 2.1 / 8
    a.chord(CH['D'] + [78], 0.0, 0.25, spread=0.01, d=1.0); a.put(glock(hz(86)), 0.0, 0.25, 0.2)
    groove(a, [(0.0, 'D'), (1.05, 'G')], e, 2.1, xylo, 0.22)
    a.put(pop(600, 1500), 1.15, 0.3, 0.2)                                   # «серйозно 👇»
    A = a.render(); f = int(0.01 * SR); A[-f:] *= np.linspace(1, 0, f)[:, None]
    m.dry[:len(A)] += A
    # 2.1–2.9 с: «перемотка» — музику назад з прискоренням, плюс стрічкове хитання
    n_rw = int(0.78 * SR); u = np.arange(n_rw) / n_rw
    src = (2.1 - 2.05 * (u ** 1.6)) * SR                                     # читаємо зворотно, дедалі швидше
    src += 0.004 * SR * np.sin(2 * np.pi * 9 * u)
    rw = np.stack([np.interp(src, np.arange(len(A)), A[:, c]) for c in (0, 1)], 1)
    rw = hp(lp(rw, 5000), 250) * (np.minimum(1, u / 0.03) * (1 - u ** 4))[:, None] * 1.3
    i0 = int(2.1 * SR); m.dry[i0:i0 + n_rw] += rw
    m.put(whoosh(0.8, 400, 5000, rev=True), 2.1, 0.25, 0, rev=0.1)          # стрічковий «вжух» назад
    m.put(whoosh(0.25, 2000, 9000), 2.68, 0.25, 0, rev=0.2)                  # у спалах
    # 2.9 с: спалах → аркуш «просто PDF»: дзвіночок + шелест паперу
    m.put(glock(hz(81), 1.8), 2.9, 0.3, -0.1); m.put(glock(hz(88), 1.8), 2.93, 0.18, 0.2); m.put(rustle(0.4), 2.9, 0.5, 0)
    e = 0.25                                                                  # далі 120 BPM від 2.9 с
    groove(m, [(2.9, 'G'), (3.9, 'A'), (4.6, 'Bm'), (5.4, 'G'), (5.9, 'A')], e, 6.4, xylo, 0.12, claps=False, uke_g=0.18)
    m.put(pop(500, 1300), 2.95, 0.25, -0.1)                                   # «Ось він 📄»
    m.put(pop(550, 1500), 4.6, 0.3, 0.1)                                      # «Розфарбуй ✏️»
    m.put(pencil(1.15), 4.75, 0.35, 0.2)                                       # олівець 4.75–5.9 с
    m.put(snip(), 5.9, 0.35, -0.2); m.put(snip(), 6.05, 0.3, 0.2)              # «Виріж ✂️»
    for k in range(4): m.put(clap(), 5.9 + k * 0.125, 0.12 + 0.05 * k, 0)      # розгін до 6.4
    # 6.4 с: знову 3D-машинка + конфеті — яскравий акорд і дзвіночок
    m.chord(CH['D'] + [78, 81], 6.4, 0.32, spread=0.008, d=1.4, damp=0.996)
    m.chord([50, 57, 62, 66, 69], 6.4, 0.16, inst=piano, spread=0, d=1.6)
    m.put(glock(hz(90), 2.0, 0.9), 6.4, 0.32, 0.25); m.put(shimmer(), 6.42, 0.4, 0)
    groove(m, [(6.4, 'D'), (7.4, 'G'), (7.9, 'A')], e, 8.4, glock, 0.12)
    m.put(pop(650, 1700), 7.4, 0.28, 0.2)                                     # «з одного аркуша ✨»
    # 8.4–10.4 с: фінальна картка — акорд, дзвіночок на логотип, каденція
    m.chord(CH['D'] + [78], 8.4, 0.28, spread=0.01, d=1.2, damp=0.995); m.put(glock(hz(86), 2.0), 8.45, 0.3, 0)
    m.put(pop(500, 1300), 8.5, 0.2, -0.2)
    groove(m, [(8.4, 'D'), (9.4, 'G')], e, 9.9, glock, 0.08, claps=False, uke_g=0.14)
    m.chord(CH['D'] + [78, 81], 9.9, 0.26, spread=0.025, d=0.6, damp=0.997); m.put(glock(hz(93), 0.6, 0.5), 9.9, 0.2, 0.2)
    m.put(bass(hz(38), 0.5), 9.9, 0.5)
    return m.render()

# ---------- хук 2: «Вгадай, хто з них був папером?» — «підкрадливий» ксилофон, ля мінор → ля мажор ----------
def hook2(dur):
    m = Mix(dur); e = 0.35                                                   # восьма 0.35 с: 2.1, 5.6, 6.3, 8.4 — на сітці
    # одразу з 0.0: троє героїв уже в кадрі — легкий ксилофонний «стрибок» і поп; ще двоє — поп на 0.3 і 0.6 с
    m.put(pop(450, 1200), 0.0, 0.35, -0.3)
    m.put(pop(520, 1400), 0.3, 0.35, 0.3); m.put(pop(600, 1650), 0.6, 0.38, 0.0)
    SNEAK = [76, None, 72, None, 75, 76, None, 69, 72, None, 71, None, 69, None, 68, 69]   # власний «навшпиньки»-мотив
    BASS = [45, None, 52, None, 45, None, 52, None, 50, None, 52, None, 45, None, 44, None]
    for k in range(16):                                                       # 0–5.6 с
        t = k * e
        if SNEAK[k] and k >= 1: m.put(xylo(hz(SNEAK[k]), 0.25, 0.06), t, 0.33, 0.2)
        if BASS[k]: m.put(uke(hz(BASS[k] + 12), 0.3, damp=0.97, bright=0.3), t, 0.45, -0.1, rev=0.05)
        if BASS[k]: m.put(bass(hz(BASS[k]), 0.25), t, 0.45, 0, rev=0.03)
        if k % 2 == 1: m.put(shaker(0.05), t, 0.15, 0.4, rev=0.05)
        if k % 4 == 3: m.put(xylo(hz(57), 0.15, 0.03), t + e * 0.5, 0.15, -0.3)   # тихий «крок»
    m.put(xylo(hz(64), 0.2, 0.05), 0.0, 0.3, 0.2)
    # прожектор по черзі 2.1, 2.8, 3.5, 4.2, 4.9 с: поп і нота, що росте до №5
    for i in range(5):
        t = 2.1 + 0.7 * i
        m.put(pop(480 + 90 * i, 1300 + 200 * i), t, 0.3, -0.4 + 0.2 * i); m.put(glock(hz(76 + [0, 2, 4, 7, 9][i]), 0.6, 0.25), t, 0.15, 0.1)
    # 5.6–6.3 с: «Відповідь… 🥁» — музика стихає, барабанний дріб
    m.put(roll(0.7), 5.6, 0.9, 0, rev=0.15); m.put(bass(hz(40), 0.7), 5.6, 0.25)
    # 6.3 с: «УСІ 😄» — тріумфальний акорд ля мажор, конфеті
    m.chord([57, 61, 64, 69, 73, 76], 6.3, 0.26, spread=0.008, d=1.5, damp=0.996)
    m.chord([45, 57, 61, 64, 69], 6.3, 0.18, inst=piano, spread=0, d=1.8)
    m.put(glock(hz(88), 2.0, 0.9), 6.3, 0.3, 0.2); m.put(glock(hz(93), 2.0, 0.9), 6.33, 0.2, -0.2)
    m.put(clap(), 6.3, 0.4, 0); m.put(shimmer(1.6), 6.32, 0.4, 0); m.put(bass(hz(33), 0.9), 6.3, 0.6)
    for i in range(5): m.put(glock(hz([69, 71, 73, 76, 78][i] + 12), 0.5, 0.2), 6.55 + i * 0.12, 0.16, -0.4 + 0.2 * i)  # перевороти на аркуш
    m.put(pop(600, 1600), 6.9, 0.28, 0.2)                                     # «усі 5 — з паперу ✂️»
    groove(m, [(6.65, 'A'), (7.0, 'D'), (7.7, 'E')], e / 2, 8.4, xylo, 0.18, uke_g=0.16)
    # 8.4 с: логотип і вся команда — акорд, дзвіночок, п'ять попів героїв
    m.chord([57, 61, 64, 69, 73], 8.4, 0.24, spread=0.01, d=1.2, damp=0.995); m.put(glock(hz(81), 1.8), 8.45, 0.28, 0)
    for i in range(5): m.put(pop(500 + 60 * i, 1300 + 120 * i, 0.09), 8.5 + i * 0.07, 0.2, -0.5 + 0.25 * i)
    groove(m, [(8.4, 'A'), (9.1, 'D')], e / 2, 9.8, glock, 0.07, claps=False, uke_g=0.13)
    m.chord([57, 61, 64, 69, 73, 76], 9.8, 0.24, spread=0.02, d=0.6, damp=0.997); m.put(bass(hz(33), 0.6), 9.8, 0.45)
    m.put(glock(hz(88), 0.6, 0.4), 9.8, 0.18, 0.2)
    return m.render()

# ---------- хук 3: «POV: 40 хв без телефону» — піаніно + укулеле, фа мажор, 100 BPM на 3/4 (такт = 1.8 с = етап) ----------
def hook3(dur):
    m = Mix(dur); q = 0.6
    bars = [(0.0, 'F'), (1.8, 'C'), (3.6, 'Dm'), (5.4, 'Bb'), (7.2, 'F'), (9.0, 'Bb')]
    MEL = {'F': [77, 76, 74, 72, 74, 77], 'C': [76, 74, 72, 67, 72, 76], 'Dm': [74, 72, 69, 72, 74, 77],
           'Bb': [74, 77, 74, 72, 70, 69], 'F2': [81, 79, 77, 76, 77, 81]}   # власна мелодія піаніно восьмими/четвертями
    for b, (t0, name) in enumerate(bars):
        r = ROOT[name] + (12 if ROOT[name] < 40 else 0)
        tones = CH[name]
        m.put(piano(hz(r), 1.8, 0.9), t0, 0.32, -0.1, rev=0.2)   # бас на «раз»
        m.put(bass(hz(r - 12), 1.0), t0, 0.35, 0, rev=0.05)
        for j in (1, 2): m.chord([n - 12 for n in tones[1:]], t0 + j * q, 0.1, inst=piano, spread=0.006, d=0.55, vel=0.6)
        for k in range(6):                                                   # укулеле-арпеджіо восьмими
            nn = tones[[0, 1, 2, 3, 2, 1][k]]
            m.put(uke(hz(nn), 0.6, damp=0.99, bright=0.45), t0 + k * q / 2, 0.15 if k else 0.2, 0.35)
        mel = MEL['F2' if b == 4 else name]
        steps = [0, 1, 2, 3, 4, 5] if b in (1, 3, 4) else [0, 2, 4]
        for s in steps:
            if t0 + s * q / 2 < dur - 0.4: m.put(piano(hz(mel[s]), 0.9, 0.8), t0 + s * q / 2 + (0.0 if s % 2 == 0 else 0.03), 0.16, 0.15)
        if b >= 1:
            for j in (1, 2): m.put(clap(0.18), t0 + j * q, 0.08, 0.2)            # легкі клапи на 2 і 3
    m.put(glock(hz(77)), 0.0, 0.2, 0.2)                                       # перший кадр — одразу з дзвоном
    m.put(pop(520, 1400), 0.9, 0.25, 0.2)                                     # «як це було 👇»
    for t in (1.8, 3.6, 5.4): m.put(pop(480, 1250), t, 0.25, -0.2)            # плашки етапів
    m.put(pencil(1.5), 2.0, 0.45, 0.2)                                        # 1. Розфарбовує 2.0–3.5 с
    k = 3.75
    while k < 4.8: m.put(snip(), k, 0.32, -0.3 + 0.6 * ((k - 3.7) / 1.1)); k += 0.22   # 2. Вирізає 3.7–4.8 с
    m.put(rustle(0.5), 4.8, 0.7, 0)                                           # аркуш падає
    m.put(whoosh(0.7, 300, 1500), 5.45, 0.18, 0)                               # 3. Склеює: деталі з'їжджаються
    m.put(lp(noise(0.15), 2500) * np.exp(-tt(0.15) / 0.05) * 0.3, 5.75, 0.5, 0.3)   # «пшик» клею
    m.put(puff(), 6.4, 0.8, 0, rev=0.3); m.put(glock(hz(84), 1.2), 6.45, 0.15, 0)    # «пуф» + спалах → 3D
    m.put(pop(550, 1500), 6.5, 0.22, 0.1)
    # 7.2 с: «Готово! 🙌» — яскравий акорд, дзвіночок, конфеті
    m.chord([65, 69, 72, 77, 81], 7.2, 0.22, spread=0.01, d=1.4, damp=0.996); m.put(glock(hz(89), 2.0, 0.9), 7.2, 0.3, 0.2)
    m.put(glock(hz(96), 1.6, 0.6), 7.24, 0.14, -0.2); m.put(shimmer(), 7.22, 0.35, 0)
    # 8.6 с: логотип — дзвіночок
    m.put(glock(hz(84), 1.8), 8.6, 0.26, 0); m.put(pop(500, 1300), 8.7, 0.18, -0.2)
    m.chord([53, 65, 69, 72, 77], 9.6, 0.2, inst=piano, spread=0.03, d=1.0, vel=0.8); m.put(glock(hz(89), 1.0, 0.5), 9.6, 0.15, 0.2)
    return m.render()

if __name__ == '__main__':
    out, n, dur = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    x = master({1: hook1, 2: hook2, 3: hook3}[n](dur))
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f'{out}: {len(x) / SR:.3f} s, {lufs(x):.1f} LUFS, TP {true_peak(x):.1f} dBTP')
