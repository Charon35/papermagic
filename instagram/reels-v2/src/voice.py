"""Закадровий голос для рілса 3 (жіночий голос Tetiana, модель robinhad/ukrainian-tts v6, MIT; датасет Apache-2.0).
1) синтез (потрібне окреме venv з espnet==202301, torch, kaldiio, soundfile і файли моделі в MODEL):
     VENV/bin/python -I voice.py synth MODEL OUTDIR
   ваги вантажимо torch.load(weights_only=True) — тільки тензори, без виконання коду з pickle.
2) збірка доріжки з пауз і таймінгів (звичайний python3 + ffmpeg):
     python3 -I voice.py mix OUTDIR   → voice.wav, voice.json і voice.js (для reels.html) поруч зі скриптом
Наголоси розставлені вручну: «+» перед наголошеною голосною."""
import json, os, subprocess, sys, wave
HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = 'tetiana'
TEMPO = 1.07   # трохи живіший темп
LEAD = 0.25    # тиша на початку
# (текст для моделі з наголосами, субтитр, пауза після, с)
LINES = [
    ('х+очете год+ину сп+окою, і без ж+одного екр+ана?', 'Хочете годину спокою —<br>і без жодного екрана?', 0.25),
    ('+ось н+аш секр+ет.', 'Ось наш секрет 🤫', 0.30),
    ('друк+уєте розмаль+овку на зв+ичайному арк+уші.', 'Друкуєте розмальовку<br>на звичайному аркуші 🖨️', 0.20),
    ('дит+ина розмаль+овує, вир+ізає, скл+еює,', 'Дитина розмальовує,<br>вирізає, склеює…', 0.05),
    ('і в н+еї нов+а +іграшка, зр+облена сво+їми рук+ами!', '…і в неї нова іграшка,<br>зроблена своїми руками!', 0.30),
    ('ц+е і мот+орика, і фант+азія.', 'Це і моторика,<br>і фантазія ✨', 0.25),
    ('а друкув+ати м+ожна ск+ільки завг+одно.', 'А друкувати можна<br>скільки завгодно 🔁', 0.25),
    ('від вісімдес+яти дев\'ят+и гр+ивень. пос+илання в пр+офілі!', 'Від 89 ₴.<br>Посилання в профілі 👆', 0.0),
]

def synth(model, out):
    import soundfile as sf, torch
    from espnet2.bin.tts_inference import Text2Speech
    from kaldiio import load_ark
    tts = Text2Speech(train_config=f'{model}/config.yaml', model_file=None, device='cpu', noise_scale=0.333, noise_scale_dur=0.333)
    tts.model.load_state_dict(torch.load(f'{model}/model.pth', map_location='cpu', weights_only=True)); tts.model.eval()
    xv = {k: v for k, v in load_ark(f'{model}/spk_xvector.ark')}
    torch.manual_seed(1)
    os.makedirs(out, exist_ok=True)
    for i, (txt, _, _) in enumerate(LINES):
        with torch.no_grad(): wav = tts(txt, spembs=xv[VOICE][0])['wav']
        sf.write(f'{out}/l{i}.wav', wav.view(-1).numpy(), tts.fs, 'PCM_16')

def mix(out):
    SR = 48000; pcm = b''; t = 0.0; cues = []
    def silence(s): return b'\0\0' * int(round(s * SR))
    pcm += silence(LEAD); t += LEAD
    for i, (_, sub, gap) in enumerate(LINES):
        tmp = f'{out}/t{i}.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{out}/l{i}.wav', '-af', f'atempo={TEMPO},aresample={SR}',
                        '-ac', '1', '-c:a', 'pcm_s16le', tmp], check=True)
        with wave.open(tmp) as w: data = w.readframes(w.getnframes())
        d = len(data) / 2 / SR
        cues.append({'a': round(t, 3), 'b': round(t + d, 3), 'text': sub})
        pcm += data + silence(gap); t += d + gap
    with wave.open(f'{HERE}/voice.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)
    data = json.dumps({'dur': round(t, 3), 'cues': cues}, ensure_ascii=False, indent=1)
    open(f'{HERE}/voice.json', 'w').write(data + '\n')
    open(f'{HERE}/voice.js', 'w').write(f'// згенеровано voice.py mix — таймінги субтитрів\nconst VOICE = {data};\n')
    print(f'voice {t:.2f} s')

if __name__ == '__main__':
    if sys.argv[1] == 'synth': synth(sys.argv[2], sys.argv[3])
    else: mix(sys.argv[2])
