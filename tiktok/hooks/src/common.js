// Спільне для сцен TikTok-хуків: таймінг, підписи в стилі TikTok, обертання 3D-фігурок, фінальна картка.
// Сцена задає window.SCENE = {dur, draw(t) → html}; render.js викликає window.draw(t) для кожного кадру.
// Безпечна зона TikTok для текстів: x 60–900, y 200–1500 (праворуч кнопки, знизу підпис).
const IMG = '/papermagic-site/img/', BUILD = '/tiktok/hooks/build/';
const SAFE = { x0: 60, x1: 900, y0: 200, y1: 1500 }, CX = (SAFE.x0 + SAFE.x1) / 2;
const LOGO = `<svg viewBox="0 0 900 860" width="100%" height="100%"><g fill="none" stroke="currentColor" stroke-width="24" stroke-linejoin="round" stroke-linecap="round"><path d="M195 165 L248 525 M195 165 L560 528"/><path d="M25 428 L330 578 M25 428 L305 738 L440 708"/><path d="M290 615 L445 465 L655 628 L650 838 L290 615 Z M290 615 L305 738"/><path d="M445 465 Q470 600 515 640 Q590 740 645 828" stroke-width="12"/><path d="M560 545 L712 290 L772 292 L655 628 M772 292 L860 405 L752 362"/></g><g fill="currentColor"><path d="M453 20 Q467.0 76.0 523 90 Q467.0 104.0 453 160 Q439.0 104.0 383 90 Q439.0 76.0 453 20 Z"/><path d="M648 158 Q657.4 195.6 695 205 Q657.4 214.4 648 252 Q638.6 214.4 601 205 Q638.6 195.6 648 158 Z"/><path d="M523 270 Q531.0 302.0 563 310 Q531.0 318.0 523 350 Q515.0 318.0 483 310 Q515.0 302.0 523 270 Z"/><path d="M825 538 Q836.4 583.6 882 595 Q836.4 606.4 825 652 Q813.6 606.4 768 595 Q813.6 583.6 825 538 Z"/></g></svg>`;

const clamp = v => Math.max(0, Math.min(1, v));
const ease = v => 1 - Math.pow(1 - clamp(v), 3);
const easeIO = v => { v = clamp(v); return v < .5 ? 4 * v * v * v : 1 - Math.pow(-2 * v + 2, 3) / 2; };
// pop: 0 → перехльост ~1.15 → 1 (для «вискакування»)
const pop = v => { v = clamp(v); if (v === 0) return 0; const s = 1.7; v -= 1; return 1 + (s + 1) * v * v * v + s * v * v; };
const seg = (t, a, b) => clamp((t - a) / (b - a));
const inside = (t, a, b) => t >= a && t < b;
const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

// кадр обертання 3D-фігурки (build/spin/NAME, 120 кадрів на оберт); turn — частка оберту
const SPIN_N = 120;
const spinSrc = (name, turn) => `${BUILD}spin/${name}/f${String(((Math.round(turn * SPIN_N) % SPIN_N) + SPIN_N) % SPIN_N).padStart(4, '0')}.png`;
function spin(name, turn, cx, cy, w, s = 1, extra = '') {
  return `<img src="${spinSrc(name, turn)}" style="position:absolute;left:${cx - w / 2}px;top:${cy - w / 2}px;width:${w}px;height:${w}px;transform:scale(${s});${extra}">`;
}

// підпис у стилі TikTok: білі «плашки» під кожним рядком, центр у безпечній зоні
function cap(lines, top, size, o = {}) {
  const s = o.scale ?? 1, bg = o.bg || '#fff', fg = o.fg || 'var(--ink)', rot = o.rot || 0;
  const rows = lines.map(l => `<span style="background:${bg};color:${fg};padding:${size * .1}px ${size * .28}px;border-radius:${size * .26}px;box-decoration-break:clone;-webkit-box-decoration-break:clone">${l}</span>`).join('<br>');
  return `<div class="cap" style="top:${top}px;font-size:${size}px;transform:rotate(${rot}deg) scale(${s});opacity:${o.op ?? 1}">${rows}</div>`;
}

// маленька плашка-стікер (етап, таймер)
function chip(text, x, y, size, o = {}) {
  return `<div style="position:absolute;left:${x}px;top:${y}px;transform:translate(${o.center ? '-50%' : '0'},0) rotate(${o.rot || 0}deg) scale(${o.scale ?? 1});transform-origin:${o.center ? '50%' : '0'} 50%;opacity:${o.op ?? 1}"><span style="display:inline-block;white-space:nowrap;font-weight:900;font-size:${size}px;padding:${size * .22}px ${size * .55}px;border-radius:999px;background:${o.bg || 'var(--violet)'};color:${o.fg || '#fff'};box-shadow:0 12px 30px rgba(42,36,64,.22)">${text}</span></div>`;
}

// конфеті-сплеск з центру (cx, cy) починаючи з t0
function confetti(t, t0, cx, cy, n = 36) {
  const k = t - t0; if (k < 0 || k > 1.6) return '';
  const cols = ['#ff6b5b', '#ffc93c', '#5fd3b5', '#6a4cf0', '#4aa3ff', '#ff8fc7'];
  let h = '';
  for (let i = 0; i < n; i++) {
    const a = rnd(i) * Math.PI * 2, v = 500 + rnd(i + 50) * 700, e = ease(k / 1.1);
    const x = cx + Math.cos(a) * v * e, y = cy + Math.sin(a) * v * e + 600 * k * k;
    const w = 18 + rnd(i + 9) * 16;
    h += `<div style="position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${w * .55}px;background:${cols[i % cols.length]};border-radius:4px;transform:rotate(${rnd(i + 3) * 360 + k * 600}deg);opacity:${1 - seg(k, 1.1, 1.6)}"></div>`;
  }
  return h;
}

// фінал: логотип PaperMagic + «3D-розмальовки · друкуй вдома»; fig — html фігурки поруч
function endCard(t, t0, fig = '') {
  const k = t - t0, lo = pop(k / .45), tx = ease((k - .25) / .4), sub = ease((k - .5) / .4);
  return `<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 40%,#fff 0,#fff3d6 55%,#ffe2a8 100%)"></div>
    ${fig}
    <div style="position:absolute;left:${CX - 170}px;top:330px;width:340px;height:325px;color:var(--violet);transform:scale(${lo}) rotate(${(1 - lo) * -20}deg)">${LOGO}</div>
    <div class="cap" style="top:700px;font-size:132px;font-weight:900;opacity:${tx};transform:translateY(${(1 - tx) * 40}px);letter-spacing:-.02em">PaperMagic</div>
    ${cap(['3D-розмальовки', '· друкуй вдома ·'], 880, 74, { op: sub, scale: .9 + .1 * sub, bg: 'var(--violet)', fg: '#fff' })}`;
}

// кадр: малює сцену; для перевірки в браузері — scene.html?t=СЕКУНДИ
window.draw = t => { document.getElementById('stage').innerHTML = window.SCENE.draw(t); };
window.addEventListener('load', async () => {
  const pre = (window.SCENE.preload || []).map(src => new Promise(r => { const i = new Image(); i.onload = i.onerror = r; i.src = src; }));
  await Promise.all(pre); await document.fonts.load('900 40px Nunito'); await document.fonts.load('800 40px Nunito');
  window.draw(+(new URLSearchParams(location.search).get('t') || 0));
  window.READY = true;
});
