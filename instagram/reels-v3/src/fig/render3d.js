// node render3d.js MODEL.json OUTDIR W H FRAMES.json  — рендер кадрів 3D-фігурки (PNG з альфою)
// FRAMES.json: [{name, rot, el, az, dist, fov, lookY, x, y, z, scale}, ...]
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs'), http = require('http');
(async () => {
  const [modelF, out, W, H, framesF] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const srv = http.createServer((q, r) => {
    const f = decodeURIComponent(q.url.split('?')[0]);
    fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); }
      r.writeHead(200, { 'Content-Type': f.endsWith('.js') ? 'text/javascript' : f.endsWith('.html') ? 'text/html' : f.endsWith('.png') ? 'image/png' : 'application/octet-stream' }); r.end(d); });
  }).listen(0, '127.0.0.1');
  await new Promise(r => srv.on('listening', r));
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const model = JSON.parse(fs.readFileSync(modelF));
  const extra = fs.existsSync(modelF.replace('.json', '.extra.json')) ? JSON.parse(fs.readFileSync(modelF.replace('.json', '.extra.json'))) : {};
  Object.assign(model, extra);
  const frames = JSON.parse(fs.readFileSync(framesF));
  const P = Math.min(4, frames.length), pages = [];
  for (let i = 0; i < P; i++) {
    const pg = await browser.newPage({ viewport: { width: +W, height: +H } });
    pg.on('console', m => { if (m.type() === 'error') console.error('page:', m.text()); });
    await pg.goto(`http://127.0.0.1:${port}${path.resolve(__dirname, 'fig3d.html')}`);
    await pg.waitForFunction(() => window.READY);
    await pg.evaluate(c => window.setup(c), { model, w: +W, h: +H, base: `http://127.0.0.1:${port}${path.dirname(path.resolve(modelF))}/`, ...(model.render || {}) });
    pages.push(pg);
  }
  let next = 0;
  await Promise.all(pages.map(async pg => { while (next < frames.length) { const f = frames[next++];
    await pg.evaluate(o => window.frame(o), f);
    await pg.screenshot({ path: `${out}/${f.name}.png`, omitBackground: true }); } }));
  await browser.close(); srv.close();
  console.log('rendered', frames.length);
})();
