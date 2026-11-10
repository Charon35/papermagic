// Спільний таймлайн процес-відео: його читають і сцена (police-process.html), і генератор 3D-кадрів (build.sh).
(function (root) {
  const clamp = v => Math.max(0, Math.min(1, v));
  const seg = (t, a, b) => clamp((t - a) / (b - a));
  const easeIO = v => { v = clamp(v); return v < .5 ? 4 * v * v * v : 1 - Math.pow(-2 * v + 2, 3) / 2; };
  const ease = v => 1 - Math.pow(1 - clamp(v), 3);
  const lerp = (a, b, k) => a + (b - a) * k;
  const TL = {
    FPS: 30,
    S1: [0, 2.2],                                   // 1) чистий чорно-білий аркуш
    COLOR: [2.3, 4.2, 6.1], COLOR_D: 1.75,          // 2) розфарбовування трьох деталей
    CUT: [8.4, 10.0, 11.6], CUT_D: 1.45,            // 3) ножиці по контуру, деталь піднімається
    AWAY: [13.2, 14.3],                             //    аркуш їде вниз, деталі лягають «як на столі»
    T3: 14.3,                                       // 4) з цього моменту — 3D: складання й склеювання
    DUR: 23.7,                                      // 5) готова машинка повільно обертається
    PX: 1.679,                                      // пікселів екрана на 1 піксель листа у 3D-виді зверху (dist 2133, fov 30)
  };
  // параметри 3D-кадру в момент t (t ≥ T3)
  TL.cam3d = t => {
    const u = t - TL.T3, c = easeIO(seg(u, .2, 3.6));
    const ramp = x => x < 0 ? 0 : x < 1 ? x * x / 2 : x - .5;      // плавний старт обертання
    return { side: seg(u, .3, 2.3), strip: seg(u, 1.3, 3.4), bar: seg(u, 3.35, 3.9),
      el: lerp(Math.PI / 2 - 1e-4, .34, c), dist: lerp(2133, 1650, c), lookY: lerp(0, 66, c),
      rot: .38 * c + .55 * ramp(u - 3.1) };
  };
  Object.assign(TL, { clamp, seg, easeIO, ease, lerp });
  if (typeof module !== 'undefined') module.exports = TL; else root.TL = TL;
})(this);
