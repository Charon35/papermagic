"""Навчальні рілси v3: python3 -I build.py N [N ...]   (N: 1, 2, 3)
Новий стиль: мʼякі переходи (xfade), теплий «плівковий» грейд, оверлей reels.html, спокійна lo-fi музика music.py.
Сегменти edit.json:
  "clip": кліп з ads/thumbs/sdr (in, speed, crop [x,y,w,h], zoom — повільний наїзд)
  "scene": 3D-сцена з build/scenes/<name>.mp4 (паперові фігурки на столі; створюється тут же з build/fig/tt)
  "place": [x, y, w, h] — вписати відео в прямокутник кадру (для порівняння на пів екрана), решта — колір паперу
Тривалість сегмента = скільки він видно; сусіди перекриваються на XF секунд (перехід)."""
import json, os, subprocess, sys, shutil
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(REELS))
RAW = f'{ROOT}/ads/raw'
SDR = f'{ROOT}/ads/thumbs/sdr'
TONEMAP = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,'
           'zscale=t=bt709:m=bt709:r=tv,format=yuv420p')
BUILD = f'{REELS}/build'
OUT = os.environ.get('OUT', REELS)
FPS, XF = 30, 0.4
GRADE = ('eq=saturation=0.96:contrast=1.04:brightness=0.01,colorbalance=rs=0.04:gs=0.01:bs=-0.035:rm=0.025:bm=-0.02,'
         'vignette=angle=PI/5.5,noise=alls=5:allf=t')

def run(*a): subprocess.run(a, check=True)

def sdr(c):
    src = f'{SDR}/{c}.mp4'
    if not os.path.exists(src):
        os.makedirs(SDR, exist_ok=True)
        run('ffmpeg', '-v', 'error', '-y', '-i', f'{RAW}/{c} (1).MOV', '-vf', f'{TONEMAP},scale=1080:1920',
            '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-an', src)
    return src

# ---------- 3D-сцени: фото столу (кадр з відео, розмите) + кадри обертання фігурок ----------
SCENES = {
    'police': [('police', 0, 330, 1.0)],
    'hip': [('hip', 0, 280, 1.0)],
    'duo': [('hip', 400, 300, 0.66), ('police', -20, 500, 0.66)],
}
def scene(name):
    out = f'{BUILD}/scenes/{name}.mp4'
    if os.path.exists(out): return out
    os.makedirs(f'{BUILD}/scenes', exist_ok=True)
    plate = f'{BUILD}/scenes/plate.png'
    if not os.path.exists(plate):
        run('ffmpeg', '-v', 'error', '-y', '-ss', '0.3', '-i', sdr('IMG_4398'), '-frames:v', '1', '-vf',
            'crop=iw*0.5:ih*0.5:iw*0.25:ih*0.5,scale=1080:1920,gblur=sigma=7,eq=brightness=0.015', plate)
    ins, fil, last = ['-loop', '1', '-framerate', str(FPS), '-t', '8', '-i', plate], '', '0:v'
    for i, (fig, x, y, s) in enumerate(SCENES[name], 1):
        ins += ['-framerate', str(FPS), '-i', f'{BUILD}/fig/tt/{fig}/f%04d.png']
        fil += f'[{i}:v]scale=iw*{s}:-1[f{i}];[{last}][f{i}]overlay={x}:{y}:eof_action=repeat[o{i}];'; last = f'o{i}'
    run('ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fil + f'[{last}]format=yuv420p[v]',
        '-map', '[v]', '-t', '8', '-r', str(FPS), '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', out)
    return out

def segment(sg, p, length):
    sp = sg.get('speed', 1.0)
    if 'scene' in sg: src, sp = scene(sg['scene']), 1.0
    else: src = sdr(sg['clip'])
    cx, cy, cw, ch = sg.get('crop', [0, 0, 1, 1])
    px, py, pw, ph = [round(v) for v in (sg['place'][0] * 1080, sg['place'][1] * 1920, sg['place'][2] * 1080, sg['place'][3] * 1920)] if 'place' in sg else (0, 0, 1080, 1920)
    vf = (f"crop=iw*{cw}:ih*{ch}:iw*{cx}:ih*{cy},scale={pw}:{ph}:force_original_aspect_ratio=increase,"
          f"crop={pw}:{ph},setsar=1,setpts=PTS/{sp},fps={FPS}")
    if sg.get('zoom'):  # повільний мʼякий наїзд до центру за весь сегмент
        z = sg['zoom']
        vf += (f",scale={pw * 2}:{ph * 2},zoompan=z='1+{z}*on/({length}*{FPS})':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
               f":d=1:s={pw}x{ph}:fps={FPS}")
    if 'place' in sg: vf += f",pad=1080:1920:{px}:{py}:color=0xf6efe4"
    run('ffmpeg', '-v', 'error', '-y', '-ss', str(sg.get('in', 0)), '-t', str(length * sp + 0.2), '-i', src, '-an', '-vf', vf,
        '-t', str(length), '-r', str(FPS), '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p', p)

def main(n):
    cfg = json.load(open(f'{HERE}/edit.json'))[str(n)]
    segs = cfg['segments']
    total = sum(sg['dur'] for sg in segs)
    if abs(total - cfg['dur']) > 0.05:
        sys.exit(f"reel {n}: сегменти дають {total:.2f} с, а треба {cfg['dur']} с — виправ edit.json")
    work = f'{BUILD}/r{n}'; shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    parts = []
    for i, sg in enumerate(segs):
        p = f'{work}/s{i:02d}.mp4'; segment(sg, p, sg['dur'] + (XF if i < len(segs) - 1 else 0)); parts.append(p)
    # мʼякі переходи між усіма сегментами
    ins = sum([['-i', p] for p in parts], [])
    fil, last, off = '', '0:v', 0.0
    for i in range(1, len(parts)):
        off += segs[i - 1]['dur']
        fil += f"[{last}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}];"; last = f'x{i}'
    base = f'{work}/base.mp4'
    run('ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fil + f'[{last}]{GRADE},format=yuv420p[v]', '-map', '[v]',
        '-t', str(cfg['dur']), '-r', str(FPS), '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', base)
    if os.environ.get('PREVIEW'):  # PREVIEW=t1,t2,... — ключові кадри у build/rN/preview.jpg
        ts = os.environ['PREVIEW'].split(',')
        run('node', f'{HERE}/overlay.js', str(n), f'{work}/pv', str(FPS), ','.join(ts))
        for i, t in enumerate(ts):
            png = f"{work}/pv/t{('%g' % float(t)).replace('.', '_')}.png"
            run('ffmpeg', '-v', 'error', '-y', '-ss', t, '-i', base, '-i', png, '-filter_complex',
                f"[0:v][1:v]overlay,drawbox=y=250:w=1080:h=3:c=red:t=fill,drawbox=y=1570:w=1080:h=3:c=red:t=fill", '-frames:v', '1', f'{work}/pv/p{i:02d}.jpg')
        run('ffmpeg', '-v', 'error', '-y', '-pattern_type', 'glob', '-i', f'{work}/pv/p*.jpg', '-vf',
            f"scale=360:640,tile={min(6, len(ts))}x{(len(ts) + 5) // 6}", '-frames:v', '1', f'{work}/preview.jpg')
        print('preview', f'{work}/preview.jpg'); return
    run('node', f'{HERE}/overlay.js', str(n), f'{work}/ov', str(FPS))
    run('python3', '-I', f'{HERE}/music.py', f'{work}/music.wav', str(cfg.get('music', n)), str(cfg['dur']))
    out = f'{OUT}/reel-{n}.mp4'
    run('ffmpeg', '-v', 'error', '-y', '-i', base, '-framerate', str(FPS), '-i', f'{work}/ov/f%05d.png', '-i', f'{work}/music.wav',
        '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v];[2:a]loudnorm=I=-15:TP=-1.5:LRA=8,aresample=48000[a]',
        '-map', '[v]', '-map', '[a]', '-t', str(cfg['dur']), '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.1',
        '-crf', '19', '-preset', 'slow', '-r', str(FPS), '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        '-movflags', '+faststart', out)
    run('ffmpeg', '-v', 'error', '-y', '-ss', str(cfg.get('cover', 1.5)), '-i', out, '-frames:v', '1', '-q:v', '2', f'{OUT}/reel-{n}-cover.jpg')
    print('done', out)

if __name__ == '__main__':
    for a in sys.argv[1:]: main(int(a))
