"""Спокійна lo-fi музика для навчальних рілсів v3 (новий трек, не з реклами й не з рілсів v2).
Електропіано (FM, як Rhodes), мʼякий бас, «щіточки» замість барабанів, шум платівки, калімба.
Усе синтезовано тут, без семплів і чужих прав.
python3 -I music.py OUT.wav STYLE DURATION   (STYLE: 1..3)"""
import sys, wave
sys.dont_write_bytecode = True
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
hz = lambda n: 440.0 * 2 ** ((n - 69) / 12)

def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x, axis=0)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x, axis=0)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x, axis=0)

def rhodes(f, d, vel=1.0):
    """FM-електропіано: модулятор 1:1 з індексом, що згасає, + «дзвінок» 14:1 на атаці."""
    n = int(d * SR); t = np.arange(n) / SR
    idx = 1.6 * vel * np.exp(-t / 0.35) + 0.25
    mod = np.sin(2 * np.pi * f * t) * idx
    tine = 0.12 * vel * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t / 0.03)
    w = np.sin(2 * np.pi * f * t + mod) + tine
    e = np.minimum(1, t / 0.004) * np.exp(-t / 1.6) * (0.9 + 0.1 * np.sin(2 * np.pi * 4.5 * t))  # трохи тремоло
    rel = max(1, int(0.12 * SR)); e[-rel:] *= np.linspace(1, 0, rel)
    return w * e

def kalimba(f, d):
    n = int(d * SR); t = np.arange(n) / SR
    w = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.05)
    return w * np.minimum(1, t / 0.002) * np.exp(-t / 0.7)

def sub(f, d):
    n = int(d * SR); t = np.arange(n) / SR
    w = np.sin(2 * np.pi * f * t) + 0.15 * np.sin(4 * np.pi * f * t)
    e = np.minimum(1, t / 0.02) * (0.55 + 0.45 * np.exp(-t / 0.4))
    rel = max(1, int(0.08 * SR)); e[-rel:] *= np.linspace(1, 0, rel)
    return w * e

rng = np.random.default_rng(3)
def kick():
    t = np.arange(int(0.4 * SR)) / SR
    f = 48 + 60 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) * 0.9
def brush(d=0.22):
    t = np.arange(int(d * SR)) / SR
    return bp(rng.standard_normal(len(t)), 1800, 7000) * (np.exp(-t / 0.07) + 0.15 * np.sin(np.pi * t / d)) * 0.35
def rim():
    t = np.arange(int(0.08 * SR)) / SR
    return (np.sin(2 * np.pi * 1700 * t) * 0.5 + bp(rng.standard_normal(len(t)), 2500, 6000)) * np.exp(-t / 0.012) * 0.18
def hat():
    t = np.arange(int(0.05 * SR)) / SR
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t / 0.01) * 0.10

STYLES = {
    # bpm, тональність (MIDI корінь), акорди як (ступінь у півтонах, тип), свінг
    1: dict(bpm=78, root=53, swing=0.11, prog=[(2, 'm9'), (7, '13'), (0, 'maj9'), (9, 'm9')]),      # F: ii–V–I–vi
    2: dict(bpm=74, root=55, swing=0.13, prog=[(0, 'maj9'), (4, 'm7'), (9, 'm9'), (5, 'maj7#11')]), # G: I–iii–vi–IV
    3: dict(bpm=82, root=51, swing=0.09, prog=[(5, 'maj9'), (4, 'm7'), (2, 'm9'), (0, 'maj9')]),    # Eb: IV–iii–ii–I
}
VOICE = {'m9': [0, 3, 7, 10, 14], '13': [0, 4, 10, 14, 21], 'maj9': [0, 4, 7, 11, 14], 'm7': [0, 3, 7, 10], 'maj7#11': [0, 4, 11, 18]}

def build(style, dur):
    st = STYLES[style]; beat = 60 / st['bpm']; bar = 4 * beat
    n = int((dur + 3) * SR); L = np.zeros(n); R = np.zeros(n)
    def put(sig, t, gl=1.0, gr=1.0):
        i = int(t * SR)
        if i < 0 or i >= n: return
        m = min(len(sig), n - i); L[i:i + m] += sig[:m] * gl; R[i:i + m] += sig[:m] * gr
    sw = lambda k: st['swing'] * beat if k % 2 else 0.0
    mel = np.random.default_rng(style * 5)
    nbars = int(np.ceil(dur / bar)) + 1
    for b in range(nbars):
        t0 = b * bar; deg, q = st['prog'][b % 4]; root = st['root'] + deg
        notes = [root + 12 + v for v in VOICE[q]]
        # електропіано: акорд на «раз» і легкий повтор на «три з половиною», ноти трохи розкидані (strum)
        for j, nn in enumerate(notes):
            pan = 0.35 + 0.3 * (j / len(notes))
            put(rhodes(hz(nn), bar * 0.95, 0.8) * 0.085, t0 + j * 0.012, 1 - pan + 0.5, pan + 0.5)
            put(rhodes(hz(nn), beat * 1.4, 0.45) * 0.05, t0 + 2.5 * beat + sw(1) + j * 0.01, 1 - pan + 0.5, pan + 0.5)
        # бас
        put(sub(hz(root - 12), beat * 1.9) * 0.30, t0)
        put(sub(hz(root - 12 + (7 if b % 2 else 12)), beat * 0.9) * 0.22, t0 + 2.5 * beat + sw(1))
        put(sub(hz(root - 12), beat * 0.9) * 0.2, t0 + 3.5 * beat + sw(1))
        if b == 0: continue  # вступ без ударних
        # ударні: мʼякий кік, щіточка/рімшот на 2 і 4, тихий хет восьмими зі свінгом
        put(kick() * 0.55, t0); put(kick() * 0.4, t0 + 2.5 * beat + sw(1))
        put(brush() * 0.9, t0 + beat, 0.8, 1.0); put(rim(), t0 + 3 * beat, 1.0, 0.8)
        for k in range(8): put(hat() * (0.7 if k % 2 else 1.0), t0 + k * beat / 2 + sw(k), 0.7, 1.0)
        # калімба: коротка фраза кожен другий такт
        if b % 2 == 1:
            for k in range(8):
                if mel.random() < 0.45:
                    nn = root + 24 + int(mel.choice(VOICE[q]))
                    put(kalimba(hz(nn), beat * 1.5) * 0.07, t0 + k * beat / 2 + sw(k), 0.9, 0.6)
    mix = np.stack([L, R], 1)
    # «касета»: легке плавання висоти (wow) через змінну затримку
    t = np.arange(n) / SR
    dl = (0.0025 + 0.0012 * np.sin(2 * np.pi * 0.6 * t)) * SR
    idx = np.clip(np.arange(n) - dl, 0, n - 1)
    i0 = idx.astype(int); fr = idx - i0; i1 = np.minimum(i0 + 1, n - 1)
    mix = mix[i0] * (1 - fr)[:, None] + mix[i1] * fr[:, None]
    # теплий звук: зрізати верх, трохи сатурації
    mix = lp(mix, 6500); mix = hp(mix, 35)
    mix = np.tanh(mix * 1.6) / 1.6
    # шум платівки: тихе шипіння + рідкі потріскування
    hiss = lp(hp(rng.standard_normal((n, 2)), 1500), 6000) * 0.006
    cr = np.zeros((n, 2)); pos = rng.integers(0, n - 200, int(dur * 9))
    for p in pos: cr[p:p + 60] += rng.standard_normal((60, 2)) * np.exp(-np.arange(60) / 8)[:, None] * rng.uniform(0.01, 0.06)
    mix = mix + hiss + hp(cr, 2000)
    mix = mix[:int(dur * SR)]
    mix /= np.max(np.abs(mix)) + 1e-9; mix *= 0.89
    fi, fo = int(0.6 * SR), int(1.8 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.6
    return mix

if __name__ == '__main__':
    out, style, dur = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    m = build(style, dur)
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print(out, f'{len(m) / SR:.1f}s')
