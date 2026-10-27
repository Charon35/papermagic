"""Збирає рекламу: python3 -I build.py N
Бере сегменти з edit.json (кліп, початок, тривалість, швидкість, кадрування), склеює у 1080×1920@30,
накладає анімований оверлей з ads.html (кадри з overlay.js), додає власну музику з music.py."""
import json, os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ADS = os.path.dirname(HERE)
RAW = os.environ.get('RAW', f'{ADS}/raw')
OUT = os.environ.get('OUT', f'{ADS}/out')
TMP = f'{ADS}/thumbs/build'
FPS = 30

def run(*a): subprocess.run(a, check=True)

def main(n):
    cfg = json.load(open(f'{HERE}/edit.json'))[str(n)]
    total = sum(sg['dur'] for sg in cfg['segments'])
    if abs(total - cfg['dur']) > 0.05:
        sys.exit(f"ad {n}: сегменти дають {total:.2f} с, а треба {cfg['dur']} с — виправ edit.json")
    work = f'{TMP}/ad{n}'; shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    os.makedirs(OUT, exist_ok=True)
    # 1. сегменти → однаковий формат
    parts = []
    for i, sg in enumerate(cfg['segments']):
        sp = sg.get('speed', 1.0)
        # crop: [x, y, w, h] у частках кадру (після автоповороту); потім заповнення 1080×1920
        cx, cy, cw, ch = sg.get('crop', [0, 0, 1, 1])
        vf = (f"crop=iw*{cw}:ih*{ch}:iw*{cx}:ih*{cy},scale=1080:1920:force_original_aspect_ratio=increase,"
              f"crop=1080:1920,setsar=1,setpts=PTS/{sp},fps={FPS},"
              f"eq=saturation={sg.get('sat', 1.12)}:contrast=1.04:brightness={sg.get('bright', 0.02)}")
        if sg.get('zoom'):  # повільний наїзд для динаміки
            z = sg['zoom']; d = sg['dur']
            vf += f",zoompan=z='1+{z}*on/({d}*{FPS})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={FPS}"
        p = f'{work}/s{i:02d}.mp4'
        run('ffmpeg', '-v', 'error', '-y', '-ss', str(sg['in']), '-t', str(sg['dur'] * sp), '-i', f"{RAW}/{sg['clip']}",
            '-an', '-vf', vf, '-t', str(sg['dur']), '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p', p)
        parts.append(p)
    with open(f'{work}/list.txt', 'w') as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    base = f'{work}/base.mp4'
    run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-c', 'copy', base)
    # 2. оверлей
    run('node', f'{HERE}/overlay.js', str(n), f'{work}/ov', str(FPS))
    # 3. музика
    run('python3', '-I', f'{HERE}/music.py', f'{work}/music.wav', str(cfg.get('music', n)), str(cfg['dur']))
    # 4. фінал
    run('ffmpeg', '-v', 'error', '-y', '-i', base, '-framerate', str(FPS), '-i', f'{work}/ov/f%05d.png', '-i', f'{work}/music.wav',
        '-filter_complex', f"[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v];[2:a]volume=0.9,loudnorm=I=-14:TP=-1.5:LRA=9[a]",
        '-map', '[v]', '-map', '[a]', '-t', str(cfg['dur']), '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.1',
        '-crf', '19', '-preset', 'slow', '-r', str(FPS), '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        '-movflags', '+faststart', f'{OUT}/ad-{n}.mp4')
    # 5. обкладинка
    run('ffmpeg', '-v', 'error', '-y', '-ss', str(cfg.get('cover', 1.2)), '-i', f'{OUT}/ad-{n}.mp4', '-frames:v', '1', '-q:v', '2', f'{OUT}/ad-{n}-cover.jpg')
    print('done', f'{OUT}/ad-{n}.mp4')

if __name__ == '__main__':
    for a in sys.argv[1:]: main(int(a))
