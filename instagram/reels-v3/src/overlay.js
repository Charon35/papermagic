// node overlay.js N OUTDIR [FPS=30] [t1,t2,...]  — кадри оверлею (PNG з альфою) з reels.html
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [n, out, fpsArg, times] = process.argv.slice(2);
  const fps = +(fpsArg || 30);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const url = 'file://' + path.resolve(__dirname, 'reels.html');
  const P = 6, pages = [];
  for (let i = 0; i < P; i++) {
    const pg = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    await pg.goto(url);
    await pg.evaluate(async () => { document.getElementById('stage').innerHTML =
      '<span style="font-family:Lora">аA</span><span style="font-family:Lora;font-style:italic">аA</span><span style="font-family:Caveat">аA</span><span style="font-family:Manrope;font-weight:800">аA</span><span style="font-family:Manrope;font-weight:700">аA</span>';
      await document.fonts.ready; });
    pages.push(pg);
  }
  const dur = await pages[0].evaluate(a => window.REEL_DUR(a), +n);
  const list = times ? times.split(',').map(Number).map(t => [t, `${out}/t${('' + t).replace('.', '_')}.png`])
                     : Array.from({ length: Math.round(dur * fps) }, (_, i) => [i / fps, `${out}/f${String(i).padStart(5, '0')}.png`]);
  let next = 0;
  await Promise.all(pages.map(async pg => {
    while (next < list.length) {
      const [t, file] = list[next++];
      await pg.evaluate(([a, t]) => window.renderFrame(a, t), [+n, t]);
      await pg.screenshot({ path: file, omitBackground: true });
    }
  }));
  await browser.close();
  console.log(`reel ${n}: ${list.length} frames, dur ${dur}s`);
})();
