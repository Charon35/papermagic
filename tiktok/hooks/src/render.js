// node render.js SCENE.html OUTDIR DUR FPS [t1,t2,...]  — кадри сцени за ?t= (1080×1920, PNG)
// Без списку часів рендерить усі кадри f0000.png… з кроком 1/FPS; зі списком — лише ці моменти (t1.png…).
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs'), http = require('http');
const ROOT = path.resolve(__dirname, '../../..');
const TYPES = { '.js': 'text/javascript', '.html': 'text/html', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.css': 'text/css', '.woff2': 'font/woff2', '.json': 'application/json' };
(async () => {
  const [scene, out, dur, fps, list] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const srv = http.createServer((q, r) => {
    const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
    fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); }
      r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'max-age=3600' }); r.end(d); });
  }).listen(0, '127.0.0.1');
  await new Promise(r => srv.on('listening', r));
  const url = `http://127.0.0.1:${srv.address().port}/${path.relative(ROOT, path.resolve(scene))}`;
  const jobs = list ? list.split(',').map(t => ({ t: +t, name: t }))
    : Array.from({ length: Math.round(+dur * +fps) }, (_, i) => ({ t: i / +fps, name: 'f' + String(i).padStart(4, '0') }));
  const browser = await chromium.launch();
  const P = Math.min(6, jobs.length);
  let next = 0;
  await Promise.all(Array.from({ length: P }, async () => {
    const pg = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    pg.on('console', m => { if (m.type() === 'error') console.error('page:', m.text()); });
    pg.on('pageerror', e => console.error('page:', e.message));
    await pg.goto(url + '?t=0'); await pg.waitForFunction(() => window.READY);
    while (next < jobs.length) { const j = jobs[next++];
      await pg.evaluate(t => window.draw(t), j.t);
      await pg.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => {}))).then(() => document.fonts.ready));
      await pg.screenshot({ path: `${out}/${j.name}.png` }); }
  }));
  await browser.close(); srv.close();
  console.log('rendered', jobs.length, 'frames →', out);
})();
