// Рендер сцен у хмарі (Linux, Playwright + Chromium):
//   кадри відео: node ads/render.js --frames ads/heroes-set/scene.html 1080 1920 FRAMES_DIR 24 12
//                ffmpeg -framerate 24 -i FRAMES_DIR/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -an OUT.mp4
//   банери:      node ads/render.js ads/statics/statics.html 1080 1350 - 'v=1|ads/statics/papermagic-static-1.png' ...
const { chromium } = require('playwright');
(async () => {
  const a = process.argv.slice(2);
  const frames = a[0] === '--frames'; if (frames) a.shift();
  const [file, w, h, out] = a; const rest = a.slice(4);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  const go = async (q, o) => {
    await p.goto('file://' + require('path').resolve(file) + '?' + q);
    await p.evaluate(() => document.fonts.ready);
    await p.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => i.onload = i.onerror = r))));
    await p.screenshot({ path: o });
  };
  if (frames) {
    const [fps, dur] = rest.map(Number);
    for (let i = 0; i < fps * dur; i++) await go('t=' + (i / fps).toFixed(4), `${out}/f${String(i).padStart(4, '0')}.png`);
  } else for (const q of rest) await go(q.split('|')[0], q.split('|')[1]);
  await b.close();
})();
