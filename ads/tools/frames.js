// node frames.js SCENE.html OUTDIR SECONDS [FPS]   — усі кадри frame-00000.png… (Playwright + Chromium)
// node frames.js SCENE.html OUT.png --t T           — один кадр у момент T
const path = require('path');
const { chromium } = require('playwright');
const [scene, out, a, b] = process.argv.slice(2);
const url = t => 'file://' + path.resolve(scene).split(path.sep).map(encodeURIComponent).join('/') + '?t=' + t;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const shot = async (t, file) => {
    await page.goto(url(t), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: file });
  };
  if (a === '--t') await shot(+b, out);
  else {
    const fps = +(b || 24), n = Math.round(+a * fps);
    for (let i = 0; i < n; i++) await shot((i / fps).toFixed(4), path.join(out, `frame-${String(i).padStart(5, '0')}.png`));
  }
  await browser.close();
})();
