"""Збирає органічний рілс: python3 -I build.py N [N ...]
Як ads/src/build.py: сегменти з edit.json → 1080×1920@30, анімований оверлей з reels.html (кадри з overlay.js).
Відмінності: БЕЗ музики (трек користувач додає в Instagram), у рілсі з "voice" — тільки голос з voice.wav.
Додаткові ефекти сегмента: "freeze" (стоп-кадр), "reverse" (перемотка назад), "zoom_at" [x, y] (наїзд на точку, напр. обличчя)."""
import json, os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(REELS))
RAW = os.environ.get('RAW', f'{ROOT}/ads/raw')
SDR = f'{ROOT}/ads/thumbs/sdr'   # iPhone HLG → SDR BT.709, 1080×1920 (той самий кеш, що й у реклами)
TONEMAP = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,'
           'zscale=t=bt709:m=bt709:r=tv,format=yuv420p')
OUT = os.environ.get('OUT', REELS)
TMP = f'{ROOT}/ads/thumbs/reels'
FPS = 30

def run(*a): subprocess.run(a, check=True)

def segment(sg, src, p):
    sp, d = sg.get('speed', 1.0), sg['dur']
    cx, cy, cw, ch = sg.get('crop', [0, 0, 1, 1])
    vf = (f"crop=iw*{cw}:ih*{ch}:iw*{cx}:ih*{cy},scale=1080:1920:force_original_aspect_ratio=increase,"
          f"crop=1080:1920,setsar=1")
    if sg.get('reverse'): vf += ',reverse'
    vf += (f",setpts=PTS/{sp},fps={FPS},"
           f"eq=saturation={sg.get('sat', 1.12)}:contrast=1.04:brightness={sg.get('bright', 0.02)}")
    if sg.get('zoom'):  # наїзд: до центру або до точки zoom_at (частки кадру); "zoom_fast" — різкий «панч» за 0.25 с
        z, (zx, zy) = sg['zoom'], sg.get('zoom_at', [0.5, 0.5])
        k = f"min(1,on/({0.25 if sg.get('zoom_fast') else d}*{FPS}))"
        vf += (f",scale=2160:3840,zoompan=z='1+{z}*{k}':x='max(0,min(iw-iw/zoom,{zx}*iw-iw/zoom/2))'"
               f":y='max(0,min(ih-ih/zoom,{zy}*ih-ih/zoom/2))':d=1:s=1080x1920:fps={FPS}")
    if sg.get('freeze'):  # стоп-кадр: один кадр, розтягнутий на dur
        frame = p.replace('.mp4', '.png')
        run('ffmpeg', '-v', 'error', '-y', '-ss', str(sg['in']), '-i', src, '-frames:v', '1', frame)
        inp = ['-loop', '1', '-framerate', str(FPS), '-t', str(d), '-i', frame]
    else:
        inp = ['-ss', str(sg['in']), '-t', str(d * sp), '-i', src]
    run('ffmpeg', '-v', 'error', '-y', *inp, '-an', '-vf', vf, '-t', str(d), '-r', str(FPS),
        '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p', p)

def main(n):
    cfg = json.load(open(f'{HERE}/edit.json'))[str(n)]
    total = sum(sg['dur'] for sg in cfg['segments'])
    if abs(total - cfg['dur']) > 0.05:
        sys.exit(f"reel {n}: сегменти дають {total:.2f} с, а треба {cfg['dur']} с — виправ edit.json")
    for c in {sg['clip'] for sg in cfg['segments']}:
        src = f'{SDR}/{c}.mp4'
        if not os.path.exists(src):
            os.makedirs(SDR, exist_ok=True)
            run('ffmpeg', '-v', 'error', '-y', '-i', f'{RAW}/{c} (1).MOV', '-vf', f'{TONEMAP},scale=1080:1920',
                '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-an', src)
    work = f'{TMP}/r{n}'; shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    os.makedirs(OUT, exist_ok=True)
    parts = []
    for i, sg in enumerate(cfg['segments']):
        p = f'{work}/s{i:02d}.mp4'; segment(sg, f"{SDR}/{sg['clip']}.mp4", p); parts.append(p)
    with open(f'{work}/list.txt', 'w') as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    base = f'{work}/base.mp4'
    run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-c', 'copy', base)
    if os.environ.get('PREVIEW'):  # PREVIEW=t1,t2,... — лише ключові кадри (відео + оверлей) у ads/thumbs/reels/rN/preview.jpg
        ts = os.environ['PREVIEW'].split(',')
        run('node', f'{HERE}/overlay.js', str(n), f'{work}/pv', str(FPS), ','.join(ts))
        for i, t in enumerate(ts):
            png = f"{work}/pv/t{('%g' % float(t)).replace('.', '_')}.png"
            run('ffmpeg', '-v', 'error', '-y', '-ss', t, '-i', base, '-i', png, '-filter_complex',
                f"[0:v][1:v]overlay,drawtext=text='{t}s':x=20:y=20:fontsize=60:fontcolor=red:box=1", '-frames:v', '1', f'{work}/pv/p{i:02d}.jpg')
        run('ffmpeg', '-v', 'error', '-y', '-pattern_type', 'glob', '-i', f'{work}/pv/p*.jpg', '-vf',
            f"scale=360:640,tile={min(6, len(ts))}x{(len(ts) + 5) // 6}", '-frames:v', '1', f'{work}/preview.jpg')
        print('preview', f'{work}/preview.jpg'); return
    run('node', f'{HERE}/overlay.js', str(n), f'{work}/ov', str(FPS))
    out = f'{OUT}/reel-{n}.mp4'
    venc = ['-c:v', 'libx264', '-profile:v', 'high', '-level', '4.1', '-crf', '19', '-preset', 'slow', '-r', str(FPS),
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart']
    vfil = '[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]'
    if cfg.get('voice'):  # тільки голос, без музики; гучність під мобільні -14 LUFS
        run('ffmpeg', '-v', 'error', '-y', '-i', base, '-framerate', str(FPS), '-i', f'{work}/ov/f%05d.png', '-i', f'{HERE}/voice.wav',
            '-filter_complex', f"{vfil};[2:a]adelay={int(cfg.get('voice_at', 0)*1000)}:all=1,apad,"
            f"highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]",
            '-map', '[v]', '-map', '[a]', '-t', str(cfg['dur']), *venc, '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', out)
    else:  # без звуку взагалі
        run('ffmpeg', '-v', 'error', '-y', '-i', base, '-framerate', str(FPS), '-i', f'{work}/ov/f%05d.png',
            '-filter_complex', vfil, '-map', '[v]', '-an', '-t', str(cfg['dur']), *venc, out)
    run('ffmpeg', '-v', 'error', '-y', '-ss', str(cfg.get('cover', 1.0)), '-i', out, '-frames:v', '1', '-q:v', '2', f'{OUT}/reel-{n}-cover.jpg')
    print('done', out)

if __name__ == '__main__':
    for a in sys.argv[1:]: main(int(a))
