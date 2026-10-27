// node overlay.js AD OUTDIR [FPS=30] [t1,t2,...]  — кадри оверлею (PNG з альфою) з ads.html
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [ad, out, fpsArg, times] = process.argv.slice(2);
  const fps = +(fpsArg || 30);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const url = 'file://' + path.resolve(__dirname, 'ads.html');
  const P = 6, pages = [];
  for (let i = 0; i < P; i++) {
    const pg = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    await pg.goto(url); await pg.evaluate(() => document.fonts.ready);
    pages.push(pg);
  }
  const dur = await pages[0].evaluate(a => window.AD_DUR(a), +ad);
  const list = times ? times.split(',').map(Number).map((t, i) => [t, `${out}/t${String(t).replace('.', '_')}.png`])
                     : Array.from({ length: Math.round(dur * fps) }, (_, i) => [i / fps, `${out}/f${String(i).padStart(5, '0')}.png`]);
  let next = 0;
  await Promise.all(pages.map(async pg => {
    while (next < list.length) {
      const [t, file] = list[next++];
      await pg.evaluate(([a, t]) => window.renderFrame(a, t), [+ad, t]);
      await pg.screenshot({ path: file, omitBackground: true });
    }
  }));
  await browser.close();
  console.log(`ad ${ad}: ${list.length} frames, dur ${dur}s`);
})();
