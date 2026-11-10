// node check.js SCENE.html — перевіряє, що всі тексти (.cap і плашки) в безпечній зоні TikTok у кожному 0.1 с
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs'), http = require('http');
const ROOT = path.resolve(__dirname, '../../..');
(async () => {
  const scene = process.argv[2];
  const srv = http.createServer((q, r) => fs.readFile(path.join(ROOT, decodeURIComponent(q.url.split('?')[0])), (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.end(d); })).listen(0, '127.0.0.1');
  await new Promise(r => srv.on('listening', r));
  const b = await chromium.launch(), pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto(`http://127.0.0.1:${srv.address().port}/${path.relative(ROOT, path.resolve(scene))}?t=0`); await pg.waitForFunction(() => window.READY);
  const dur = await pg.evaluate(() => SCENE.dur); let bad = 0;
  for (let t = 0; t < dur; t += .1) {
    const r = await pg.evaluate(t => { draw(t); const o = [];
      document.querySelectorAll('#stage span').forEach(e => { if (!e.textContent.trim()) return; const q = e.getBoundingClientRect(); if (q.width) o.push([e.textContent.slice(0, 24), q.left, q.top, q.right, q.bottom]); });
      return o; }, t);
    for (const [txt, l, tp, rt, bt] of r) if (l < 55 || rt > 905 || tp < 195 || bt > 1505) { bad++; console.log(t.toFixed(1), JSON.stringify(txt), [l, tp, rt, bt].map(Math.round).join(' ')); }
  }
  console.log(scene, bad ? `${bad} порушень` : 'усі тексти в безпечній зоні');
  await b.close(); srv.close();
})();
