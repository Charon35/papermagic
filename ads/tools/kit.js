// Спільне для сцен ads/*/scene.html: час кадру, анімації, логотип, фігурки.
// Кадр за часом: scene.html?t=СЕКУНДИ. Підключати після ../../instagram/src/figs.js.
const T = +(new URLSearchParams(location.search).get('t') || 0);
const IMG = '../../papermagic-site/img/';
const LOGO = `<svg viewBox="0 0 900 860" width="100%" height="100%"><g fill="none" stroke="#2a2440" stroke-width="24" stroke-linejoin="round" stroke-linecap="round"><path d="M195 165 L248 525 M195 165 L560 528"/><path d="M25 428 L330 578 M25 428 L305 738 L440 708"/><path d="M290 615 L445 465 L655 628 L650 838 L290 615 Z M290 615 L305 738"/><path d="M445 465 Q470 600 515 640 Q590 740 645 828" stroke-width="12"/><path d="M560 545 L712 290 L772 292 L655 628 M772 292 L860 405 L752 362"/></g></svg>`;

const clamp = v => Math.max(0, Math.min(1, v));
const ease = v => 1 - Math.pow(1 - clamp(v), 3);
const pop = v => { v = clamp(v); return v === 0 ? 0 : 1 + 0.12 * Math.sin(v * Math.PI) * (1 - v) + (ease(v) - 1); };
const fade = (a, b) => clamp((T - a) / (b - a));
const vis = (a, b, f = .35) => Math.min(fade(a, a + f), 1 - fade(b - f, b));   // видимість сцени [a, b]
const vis0 = (b, f = .35) => 1 - fade(b - f, b);                                // перша сцена: видно з кадру 0

// назви, аркуші й тло — як у PRODUCTS на сайті (papermagic-site/index.html)
const SITE = {
  police:  ['Поліцейське авто', 3, 99],          racer: ['Гоночна «Блискавка 95»', 8, 99],
  shark:   ['Весела акула', 5, 89],              cupcake: ['Фудтрак «Кекс»', 2, 99],
  hippie:  ['Хіпі-фургон', 1, 99],               bus: ['Мікроавтобус «Жабенята»', 7, 99],
  truck:   ['Вантажівка PaperMagic', 6, 89],     dog: ['Песик Шнауцер', 4, 99],
};
const HERO = { blyskavka: 'kapitan-blyskavka', zirka: 'divchynka-zirka', sonyashnyk: 'super-sonyashnyk', khvylia: 'kapitan-khvylia', misiachna: 'misiachna-tin' };
Object.assign(BG, { blyskavka: '#e6efff', zirka: '#f3e9ff', sonyashnyk: '#fff6d6', khvylia: '#e0f5f8', misiachna: '#ebeaf7' });

const svgCache = {};
// фігурка id у прямокутнику w×(w·260/320), масштаб s від низу, прозорість o
function fig(id, x, y, w, s = 1, o = 1, extra = '') {
  const inner = HERO[id] ? `<img src="${IMG}hero-${HERO[id]}.svg" style="width:100%;height:100%;object-fit:contain">`
    : (svgCache[id] = svgCache[id] || FIGS[id]());
  return `<div class="abs fig" style="left:${x}px;top:${y}px;width:${w}px;height:${w * 260 / 320}px;transform:scale(${s});transform-origin:50% 90%;opacity:${o};${extra}">${inner}</div>`;
}
const sheet = id => `${IMG}sheet-${SITE[id] ? SITE[id][1] : 'hero-' + HERO[id]}.jpg`;

// логотип у безпечній зоні (y 250–1570), над заголовком
const logo = (o = 1) => `<div class="abs" style="left:0;right:0;top:262px;display:flex;justify-content:center;align-items:center;gap:16px;opacity:${o}"><div style="width:76px;height:73px">${LOGO}</div><div style="font-weight:900;font-size:44px">PaperMagic</div></div>`;
