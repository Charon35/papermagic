"""Синтез власної фонової музики для реклам (без чужих семплів і прав).
python3 music.py OUT.wav STYLE DURATION   (STYLE: 1..4)"""
import sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)

def note_hz(n):  # MIDI → Hz
    return 440.0 * 2 ** ((n - 69) / 12)

def env(n, a=0.005, d=0.25, s=0.0, r=0.05, length=None):
    length = length or n
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) if a > 0 else np.ones(n)
    dec = s + (1 - s) * np.exp(-np.maximum(0, t - a) / d)
    e = e * dec
    rel_start = max(0, length - int(r * SR))
    if rel_start < n:
        e[rel_start:] *= np.linspace(1, 0, n - rel_start)
    return e

def pluck(freq, dur, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    w = (np.sin(2*np.pi*freq*t) + 0.35*bright*np.sin(2*np.pi*2*freq*t) + 0.12*bright*np.sin(2*np.pi*3*freq*t))
    return w * env(n, 0.003, 0.18 + 0.1/bright)

def marimba(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    w = np.sin(2*np.pi*freq*t) + 0.25*np.sin(2*np.pi*4*freq*t)*np.exp(-t/0.03)
    return w * env(n, 0.002, 0.28)

def glock(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    w = np.sin(2*np.pi*freq*t) + 0.4*np.sin(2*np.pi*2.76*freq*t)*np.exp(-t/0.12) + 0.2*np.sin(2*np.pi*5.4*freq*t)*np.exp(-t/0.05)
    return w * env(n, 0.001, 0.5)

def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    w = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.12):
            ff = f * 2 ** (det / 12)
            w += 2 * ((t * ff) % 1) - 1  # saw
    # gentle low-pass (one-pole)
    y = np.zeros(n); a = 0.04; acc = 0.0
    for i in range(0, n):
        acc += a * (w[i] - acc); y[i] = acc
    return y / (len(freqs) * 2) * env(n, 0.08, 9, 0.8, 0.15)

def bass(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    w = np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*2*freq*t)
    return np.tanh(1.5*w) * env(n, 0.004, 0.22, 0.35, 0.03)

def kick(dur=0.35):
    n = int(dur*SR); t = np.arange(n)/SR
    f = 50 + 110*np.exp(-t/0.035)
    ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph) * np.exp(-t/0.12) * 1.1

def clap(dur=0.25):
    n = int(dur*SR); t = np.arange(n)/SR
    nz = rng.standard_normal(n)
    nz = nz - np.concatenate([[0], nz[:-1]])*0.6  # highpass-ish
    e = np.exp(-t/0.06)
    for off in (0.0, 0.011, 0.022):
        e += 0.5*np.exp(-np.maximum(0, t-off)/0.006)*(t >= off)
    return nz * e * 0.25

def hat(dur=0.06, open_=False):
    d = 0.18 if open_ else dur
    n = int(d*SR); t = np.arange(n)/SR
    nz = rng.standard_normal(n); nz = np.diff(np.concatenate([[0], nz]))
    return nz * np.exp(-t/(0.05 if open_ else 0.012)) * 0.12

def shaker(dur=0.08):
    n = int(dur*SR); t = np.arange(n)/SR
    nz = rng.standard_normal(n); nz = np.diff(np.concatenate([[0], nz]))
    return nz * np.sin(np.pi*t/dur)**2 * 0.05

STYLES = {
    # bpm, key root (MIDI), progression (scale degrees as chords), melody pattern, lead instrument
    1: dict(bpm=118, root=60, prog=[0, 7, 9, 5], lead='marimba', swing=0.0),   # C: I V vi IV — енергійний «процес»
    2: dict(bpm=100, root=65, prog=[0, 9, 5, 7], lead='glock', swing=0.08),    # F: I vi IV V — теплий для батьків
    3: dict(bpm=124, root=62, prog=[0, 5, 9, 7], lead='pluck', swing=0.0),     # D: святковий «набір»
    4: dict(bpm=96, root=67, prog=[0, 4, 9, 5], lead='glock', swing=0.1),      # G: мʼякий UGC
}
MAJOR = [0, 2, 4, 5, 7, 9, 11]

def chord(root, deg):  # deg is semitone offset of chord root in major key
    minor = deg in (2, 4, 9)
    third = 3 if minor else 4
    return [root + deg, root + deg + third, root + deg + 7]

def build(style, dur):
    st = STYLES[style]
    beat = 60 / st['bpm']; bar = 4 * beat
    n = int((dur + 2) * SR)
    L = np.zeros(n); R = np.zeros(n)
    def put(sig, t, gl=1.0, gr=1.0):
        i = int(t * SR)
        if i >= n: return
        m = min(len(sig), n - i)
        L[i:i+m] += sig[:m] * gl; R[i:i+m] += sig[:m] * gr
    lead = {'marimba': marimba, 'glock': glock, 'pluck': lambda f, d: pluck(f, d, 1.6)}[st['lead']]
    mrng = np.random.default_rng(style * 11)
    nbars = int(np.ceil(dur / bar)) + 1
    # melodic motif (2 bars), repeated with variation
    motif = []
    for b in range(2):
        for s in range(8):
            if mrng.random() < (0.75 if s % 2 == 0 else 0.4):
                motif.append((b, s, int(mrng.choice([0, 2, 4, 4, 7, 7, 9, 12]))))
    for b in range(nbars):
        t0 = b * bar
        deg = st['prog'][b % 4]
        ch = chord(st['root'], deg)
        intro = b == 0
        # pad
        put(pad([note_hz(x) for x in ch], bar) * 0.16, t0)
        # drums
        for q in range(4):
            tq = t0 + q * beat
            if not intro or q >= 2:
                put(kick(), tq, 0.9, 0.9)
            if q in (1, 3) and not intro:
                put(clap(), tq, 0.75, 0.85)
            for e8 in range(2):
                sw = st['swing'] * beat if e8 == 1 else 0
                put(hat(open_=(e8 == 1 and q == 3)), tq + e8 * beat / 2 + sw, 0.7, 1.0)
            for s16 in range(4):
                put(shaker(), tq + s16 * beat / 4, 1.0, 0.6)
        # bass: root on 8ths with octave pops
        broot = st['root'] - 24 + deg
        for e in range(8):
            if intro and e < 4: continue
            nn = broot + (12 if e in (3, 7) else 0)
            put(bass(note_hz(nn), beat / 2 * 0.95) * 0.32, t0 + e * beat / 2)
        # arpeggio pluck
        for s in range(8):
            nn = ch[s % 3] + (12 if s >= 4 else 0)
            sw = st['swing'] * beat if s % 2 else 0
            put(pluck(note_hz(nn), beat / 2) * 0.10, t0 + s * beat / 2 + sw, 0.6, 1.0)
        # lead melody from bar 2
        if b >= 1:
            for (mb, s, off) in motif:
                if mb != (b % 2): continue
                nn = st['root'] + 12 + deg + off
                # keep in key
                while (nn - st['root']) % 12 not in MAJOR: nn += 1
                sw = st['swing'] * beat if s % 2 else 0
                put(lead(note_hz(nn), beat * 0.9) * 0.20, t0 + s * beat / 2 + sw, 1.0, 0.75)
    # simple stereo delay on everything (ping-pong-ish)
    dl = int(beat * 0.75 * SR)
    L2 = L.copy(); R2 = R.copy()
    L2[dl:] += R[:-dl] * 0.18; R2[dl:] += L[:-dl] * 0.18
    mix = np.stack([L2, R2], 1)[:int(dur * SR)]
    # master: soft clip + normalize + fades
    mix = np.tanh(mix * 1.2)
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.89
    fi = int(0.03 * SR); fo = int(1.2 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    return mix

if __name__ == '__main__':
    out, style, dur = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    m = build(style, dur)
    pcm = (m * 32767).astype(np.int16)
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(out, f'{len(m)/SR:.1f}s')
