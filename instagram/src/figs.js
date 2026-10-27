/* ================= 3D-ish figure renderer =================
   Simple oblique projection: x = length (to the right), y = up, z = depth (goes up-right). */
const KX = 0.6, KY = 0.36, STROKE = '#2a2440';

function shade(hex, f){
  const n = parseInt(hex.slice(1),16); let r=n>>16, g=(n>>8)&255, b=n&255;
  if (f > 1){ const t=f-1; r+= (255-r)*t; g+=(255-g)*t; b+=(255-b)*t; } else { r*=f; g*=f; b*=f; }
  return '#'+[r,g,b].map(v=>Math.round(Math.max(0,Math.min(255,v))).toString(16).padStart(2,'0')).join('');
}

function Scene(ox, oy){
  let out = '';
  const P = (x,y,z=0) => [ox + x + z*KX, oy - y - z*KY];
  const pts = a => a.map(p=>p.map(v=>v.toFixed(1)).join(',')).join(' ');
  const S = `stroke="${STROKE}" stroke-width="2.4" stroke-linejoin="round" vector-effect="non-scaling-stroke"`;
  const api = {
    P, S,
    add(s){ out += s; return api; },
    poly(a, fill, extra=''){ out += `<polygon points="${pts(a)}" fill="${fill}" ${S} ${extra}/>`; return api; },
    // extrude a convex profile (CCW, y up) from z0 to z1
    prism(profile, z0, z1, color){
      const n = profile.length;
      for (let i=0;i<n;i++){
        const p = profile[i], q = profile[(i+1)%n];
        const dx = q[0]-p[0], dy = q[1]-p[1];
        if (dy*KX - dx*KY <= 0.01) continue;
        const up = -dx > Math.abs(dy)*0.7;
        api.poly([P(p[0],p[1],z0),P(q[0],q[1],z0),P(q[0],q[1],z1),P(p[0],p[1],z1)], shade(color, up?1.18:0.8));
      }
      api.poly(profile.map(p=>P(p[0],p[1],z0)), color);
      return api;
    },
    box(x0,x1,y0,y1,z0,z1,c){ return api.prism([[x0,y0],[x1,y0],[x1,y1],[x0,y1]], z0, z1, c); },
    // groups whose local coordinates live on a plane (y up)
    side(z, inner){ out += `<g transform="matrix(1,0,0,-1,${ox+z*KX},${oy-z*KY})">${inner}</g>`; return api; },
    endX(x, inner){ out += `<g transform="matrix(${KX},${-KY},0,-1,${ox+x},${oy})">${inner}</g>`; return api; },
    // local u in [0,1] along edge p->q, v = depth z
    face(p, q, inner){ out += `<g transform="matrix(${q[0]-p[0]},${-(q[1]-p[1])},${KX},${-KY},${ox+p[0]},${oy-p[1]})">${inner}</g>`; return api; },
    // decal drawn in normal screen orientation, centered at a 3D point
    at(x,y,z, inner){ const [sx,sy]=P(x,y,z); out += `<g transform="translate(${sx.toFixed(1)},${sy.toFixed(1)})">${inner}</g>`; return api; },
    wheel(x,y,z,r,rim='#d9dde6'){
      const [sx,sy] = P(x,y,z), [bx,by] = P(x,y,z+7);
      out += `<circle cx="${bx}" cy="${by}" r="${r}" fill="#1d1a2b" ${S}/>`+
             `<circle cx="${sx}" cy="${sy}" r="${r}" fill="#34304a" ${S}/>`+
             `<circle cx="${sx}" cy="${sy}" r="${r*0.55}" fill="${rim}" ${S}/>`+
             `<circle cx="${sx}" cy="${sy}" r="${r*0.18}" fill="#8b8fa3"/>`;
      return api;
    },
    shadow(cx, cy, rx, ry){ out += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="#2a2440" opacity=".1"/>`; return api; },
    svg(label){ return `<svg viewBox="0 0 320 260" role="img" aria-label="${label}">${out}</svg>`; }
  };
  return api;
}
const R = (x,y,w,h,fill,extra='') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${STROKE}" stroke-width="2" vector-effect="non-scaling-stroke" ${extra}/>`;
const PG = (a,fill,extra='') => `<polygon points="${a.map(p=>p.join(',')).join(' ')}" fill="${fill}" stroke="${STROKE}" stroke-width="2" stroke-linejoin="round" vector-effect="non-scaling-stroke" ${extra}/>`;
const C = (x,y,r,fill,extra='') => `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" ${extra}/>`;
const GLASS = '#9fd8ff', GLASS_D = '#2f4e73';
const flower = (r, c) => [0,72,144,216,288].map(a=>C((Math.cos(a*Math.PI/180)*r*.9).toFixed(1),(Math.sin(a*Math.PI/180)*r*.9).toFixed(1),r*.7,c,`stroke="${STROKE}" stroke-width="1.6"`)).join('')+C(0,0,r*.55,'#ffe14d',`stroke="${STROKE}" stroke-width="1.6"`);

const FIGS = {
  police(){
    const s = Scene(30,222), D=78;
    s.shadow(165,224,150,16);
    s.wheel(46,19,D,19).wheel(162,19,D,19);
    s.prism([[0,18],[206,18],[206,50],[196,58],[10,58],[0,50]],0,D,'#f3f5fa');
    s.prism([[42,58],[160,58],[138,92],[64,92]],6,D-6,'#f3f5fa');
    s.side(0, R(30,26,150,22,'#23356b'));
    s.at(105,37,0,`<text x="0" y="5" text-anchor="middle" font-family="Nunito" font-weight="900" font-size="13" fill="#fff" letter-spacing="1">ПОЛІЦІЯ</text>`);
    s.side(6, PG([[54,62],[98,62],[98,87],[70,87]],GLASS)+PG([[104,62],[150,62],[134,87],[104,87]],GLASS));
    s.face([160,58],[138,92], PG([[.1,12],[.9,12],[.9,D-12],[.1,D-12]],GLASS));
    s.endX(206, R(6,36,14,8,'#ffe14d')+R(D-20,36,14,8,'#ffe14d')+R(26,26,D-52,14,'#c9cfdc'));
    s.box(86,101,92,101,26,52,'#ff4b4b').box(101,116,92,101,26,52,'#3b82ff');
    s.side(0, `<line x1="103" y1="50" x2="103" y2="88" stroke="${STROKE}" stroke-width="1.6" vector-effect="non-scaling-stroke"/>`);
    s.wheel(46,19,0,19).wheel(162,19,0,19);
    return s.svg('Поліцейське авто');
  },
  racer(){
    const s = Scene(28,222), D=74;
    s.shadow(165,224,150,15);
    s.wheel(42,17,D,18,'#ff4b4b').wheel(168,17,D,18,'#ff4b4b');
    s.box(4,10,55,66,10,20,'#c42420').box(4,10,55,66,D-20,D-10,'#c42420');
    s.prism([[0,15],[210,15],[210,38],[195,48],[150,55],[20,60],[0,55]],0,D,'#e8342f');
    s.prism([[58,58],[142,55],[120,80],[82,80]],12,D-12,'#e8342f');
    s.side(12, PG([[70,60],[132,58],[116,77],[86,77]],'#29324a'));
    s.face([142,55],[120,80], PG([[.08,14],[.92,14],[.92,D-26],[.08,D-26]],GLASS)
      + `<ellipse cx=".5" cy="22" rx=".22" ry="7" fill="#fff" stroke="${STROKE}" stroke-width="1.5" vector-effect="non-scaling-stroke"/><ellipse cx=".5" cy="38" rx=".22" ry="7" fill="#fff" stroke="${STROKE}" stroke-width="1.5" vector-effect="non-scaling-stroke"/>`
      + `<ellipse cx=".45" cy="23" rx=".11" ry="3.5" fill="#3c7bd6"/><ellipse cx=".45" cy="39" rx=".11" ry="3.5" fill="#3c7bd6"/>`);
    s.side(0, PG([[14,36],[58,44],[54,36],[96,46],[50,26],[54,34]],'#ffd23f'));
    s.at(136,34,0,`<text x="0" y="9" text-anchor="middle" font-family="Nunito" font-style="italic" font-weight="900" font-size="28" fill="#ffd23f" stroke="${STROKE}" stroke-width="1.5" paint-order="stroke">95</text>`);
    s.endX(210, R(8,24,12,8,'#ffe14d')+R(D-20,24,12,8,'#ffe14d')+`<path d="M24 20 Q37 14 50 20" fill="none" stroke="${STROKE}" stroke-width="2" vector-effect="non-scaling-stroke"/>`);
    s.box(0,22,66,71,0,D,'#c42420');
    s.wheel(42,17,0,18,'#ff4b4b').wheel(168,17,0,18,'#ff4b4b');
    return s.svg('Гоночна машинка «Блискавка 95»');
  },
  shark(){
    const sk = STROKE;
    return `<svg viewBox="0 0 320 260" role="img" aria-label="Весела акула">
      <ellipse cx="160" cy="236" rx="120" ry="12" fill="#2a2440" opacity=".1"/>
      <path d="M140 92 L176 26 L210 96 Z" fill="#4a7bb5" stroke="${sk}" stroke-width="2.4" stroke-linejoin="round"/>
      <path d="M70 120 L20 70 L34 140 L14 196 L72 150 Z" fill="#4a7bb5" stroke="${sk}" stroke-width="2.4" stroke-linejoin="round"/>
      <path d="M304 140 Q256 84 166 90 Q104 94 62 122 L64 150 Q120 182 196 180 Q268 176 304 140 Z" fill="#5d8fc9" stroke="${sk}" stroke-width="2.4" stroke-linejoin="round"/>
      <path d="M304 140 Q266 172 196 180 Q128 182 66 150 Q150 160 214 152 Q270 146 304 140 Z" fill="#f3f7fb" stroke="${sk}" stroke-width="2.4" stroke-linejoin="round"/>
      <path d="M166 90 L196 180 M110 104 L196 180 M236 100 L196 180" stroke="${sk}" stroke-width="1.4" stroke-dasharray="4 4" opacity=".45"/>
      <path d="M298 144 Q266 166 222 160 Q246 146 298 144 Z" fill="#8c2333" stroke="${sk}" stroke-width="2.2" stroke-linejoin="round"/>
      <path d="M232 156 l6 -9 l5 9 Z M246 154 l6 -9 l5 9 Z M260 152 l6 -9 l5 9 Z M274 150 l6 -8 l5 8 Z M250 162 l5 -7 l5 7Z" fill="#fff" stroke="${sk}" stroke-width="1.3"/>
      <circle cx="262" cy="122" r="10" fill="#fff" stroke="${sk}" stroke-width="2.2"/><circle cx="265" cy="122" r="5" fill="${sk}"/><circle cx="267" cy="120" r="1.6" fill="#fff"/>
      <path d="M212 120 q-6 14 0 28 M222 118 q-6 14 0 28 M232 118 q-6 12 0 24" fill="none" stroke="${sk}" stroke-width="2" stroke-linecap="round"/>
      <path d="M176 166 L150 214 L214 172 Z" fill="#4a7bb5" stroke="${sk}" stroke-width="2.4" stroke-linejoin="round"/>
      <g fill="none" stroke="#5d8fc9" stroke-width="2"><circle cx="292" cy="96" r="6"/><circle cx="302" cy="74" r="4"/><circle cx="288" cy="58" r="3"/></g>
    </svg>`;
  },
  cupcake(){
    const s = Scene(30,226), D=80;
    s.shadow(160,228,150,15);
    s.wheel(42,20,D,20).wheel(152,20,D,20);
    s.prism([[0,16],[196,16],[196,58],[184,66],[166,100],[0,100]],0,D,'#8fe0cf');
    let drips = R(0,86,166,14,'#ff8fbf','stroke="none"');
    [[16,8],[48,13],[82,7],[112,15],[144,9]].forEach(([x,h])=>drips+=`<rect x="${x-6}" y="${86-h}" width="12" height="${h+2}" rx="6" fill="#ff8fbf"/>`);
    s.side(0, drips + `<line x1="0" y1="100" x2="166" y2="100" stroke="${STROKE}" stroke-width="2.4" vector-effect="non-scaling-stroke"/>`);
    s.side(0, R(56,36,84,34,'#fff7e0') + [0,1,2,3,4,5].map(i=>R(52+i*15,70,15,9,i%2?'#fff':'#ff5b6e')).join('') + PG([[148,60],[176,60],[164,88],[148,88]],GLASS));
    s.face([184,66],[166,100], PG([[.12,10],[.88,10],[.88,D-10],[.12,D-10]],GLASS));
    s.endX(196, R(8,28,14,8,'#ffe14d')+R(D-22,28,14,8,'#ffe14d'));
    s.wheel(42,20,0,20).wheel(152,20,0,20);
    // cupcake on the roof
    const [cx,cy] = s.P(84,100,D/2);
    let pleats=''; for(let i=-3;i<=3;i++) pleats+=`<line x1="${i*9}" y1="0" x2="${i*12}" y2="-34" stroke="${STROKE}" stroke-width="1.4"/>`;
    let spr=''; [[-28,-58,'#ff5b6e'],[-10,-70,'#5aa9f5'],[12,-62,'#ffe14d'],[26,-50,'#5fd3b5'],[-20,-46,'#6a4cf0'],[4,-48,'#ff5b6e'],[-2,-80,'#5fd3b5']].forEach(([x,y,c])=>spr+=`<rect x="${x}" y="${y}" width="7" height="3" rx="1.5" fill="${c}" transform="rotate(${(x*7)%60} ${x} ${y})"/>`);
    s.add(`<g transform="translate(${cx},${cy})">
      <line x1="10" y1="-70" x2="34" y2="-112" stroke="#ff5b6e" stroke-width="6" stroke-linecap="round"/>
      <line x1="10" y1="-70" x2="34" y2="-112" stroke="#fff" stroke-width="6" stroke-dasharray="4 6" stroke-linecap="round"/>
      <path d="M-34 0 L34 0 L44 -34 L-44 -34 Z" fill="#ffb3d1" stroke="${STROKE}" stroke-width="2.4" stroke-linejoin="round"/>${pleats}
      <path d="M-50 -34 Q-56 -52 -36 -56 Q-36 -78 -12 -76 Q0 -96 18 -80 Q42 -80 38 -58 Q56 -52 50 -34 Z" fill="#8a5a3c" stroke="${STROKE}" stroke-width="2.4" stroke-linejoin="round"/>${spr}
      <circle cx="-6" cy="-90" r="8" fill="#e8342f" stroke="${STROKE}" stroke-width="2"/><path d="M-6 -98 q2 -8 8 -10" fill="none" stroke="${STROKE}" stroke-width="2"/>
    </g>`);
    return s.svg('Фудтрак «Кекс»');
  },
  hippie(){
    const s = Scene(28,224), D=80;
    s.shadow(160,226,150,15);
    s.wheel(45,22,D,22).wheel(155,22,D,22);
    s.prism([[0,16],[200,16],[200,62],[188,74],[164,112],[8,114],[0,104]],0,D,'#4cc3c8');
    s.side(0, R(0,16,200,24,'#a5d649') + R(14,70,48,32,GLASS_D,'rx="4"') + R(70,70,70,32,GLASS_D,'rx="4"') + PG([[148,72],[180,72],[161,104],[148,104]],GLASS_D)
      + `<line x1="144" y1="18" x2="144" y2="108" stroke="${STROKE}" stroke-width="1.6" vector-effect="non-scaling-stroke"/>`);
    s.face([188,74],[164,112], PG([[.12,8],[.88,8],[.88,D-8],[.12,D-8]],GLASS_D) + PG([[.3,16],[.7,16],[.6,26],[.2,26]],'#ffffff55','stroke="none"'));
    s.endX(200, C(14,42,7,'#ffe14d',`stroke="${STROKE}" stroke-width="2" vector-effect="non-scaling-stroke"`)+C(D-14,42,7,'#ffe14d',`stroke="${STROKE}" stroke-width="2" vector-effect="non-scaling-stroke"`)+R(28,30,D-56,8,'#a5d649'));
    s.at(36,54,0,flower(9,'#ff8a3d')).at(106,52,0,flower(11,'#ff5b9a')).at(176,50,0,flower(8,'#ff8a3d')).at(124,26,0,flower(6,'#fff'));
    s.wheel(45,22,0,22).wheel(155,22,0,22);
    return s.svg('Хіпі-фургон');
  },
  bus(){
    const s = Scene(28,224), D=80;
    s.shadow(160,226,150,15);
    s.wheel(44,20,D,20).wheel(160,20,D,20);
    s.prism([[0,18],[202,18],[202,74],[186,116],[0,116]],0,D,'#ffcf3f');
    s.side(0, R(0,18,202,18,'#57b947') + [12,54,96,138].map(x=>R(x,76,36,30,GLASS,'rx="3"')).join('') + PG([[178,78],[198,78],[190,104],[178,104]],GLASS));
    const frog = `<ellipse cx="0" cy="0" rx="19" ry="12" fill="#7bd36b" stroke="${STROKE}" stroke-width="2"/>`+
      `<circle cx="-9" cy="-11" r="7" fill="#7bd36b" stroke="${STROKE}" stroke-width="2"/><circle cx="9" cy="-11" r="7" fill="#7bd36b" stroke="${STROKE}" stroke-width="2"/>`+
      `<circle cx="-9" cy="-11" r="3.4" fill="${STROKE}"/><circle cx="9" cy="-11" r="3.4" fill="${STROKE}"/>`+
      `<path d="M-8 2 Q0 9 8 2" fill="none" stroke="${STROKE}" stroke-width="2" stroke-linecap="round"/><circle cx="-13" cy="3" r="2.6" fill="#ff9ec4"/><circle cx="13" cy="3" r="2.6" fill="#ff9ec4"/>`;
    s.at(50,52,0,frog).at(124,52,0,`<g transform="scale(.8)">${frog}</g>`);
    s.face([202,74],[186,116], PG([[.1,8],[.9,8],[.9,D-8],[.1,D-8]],GLASS));
    s.endX(202, C(14,32,6,'#fff',`stroke="${STROKE}" stroke-width="2" vector-effect="non-scaling-stroke"`)+C(D-14,32,6,'#fff',`stroke="${STROKE}" stroke-width="2" vector-effect="non-scaling-stroke"`)+R(26,22,D-52,12,'#57b947'));
    s.wheel(44,20,0,20).wheel(160,20,0,20);
    return s.svg('Мікроавтобус «Жабенята»');
  },
  truck(){
    const s = Scene(26,224), D=84;
    s.shadow(160,226,150,15);
    s.wheel(42,19,D,19).wheel(172,19,D,19);
    s.box(0,206,16,26,4,D-4,'#3d3f52');
    s.box(0,140,26,122,0,D,'#ffd84d');
    s.side(0, R(10,36,120,76,'#fffaf0','rx="6"'));
    s.at(70,74,0,`<text x="0" y="6" text-anchor="middle" font-family="Nunito" font-weight="900" font-size="19" fill="#6a4cf0">PaperMagic</text>`);
    s.prism([[144,26],[206,26],[206,70],[194,100],[144,100]],4,D-4,'#ef5148');
    s.side(4, PG([[154,68],[190,68],[183,92],[154,92]],GLASS) + `<line x1="150" y1="30" x2="150" y2="96" stroke="${STROKE}" stroke-width="1.6" vector-effect="non-scaling-stroke"/>`);
    s.face([206,70],[194,100], PG([[.1,10],[.9,10],[.9,D-14],[.1,D-14]],GLASS));
    s.endX(206, R(14,36,D-32,16,'#c9cfdc') + R(6,30,12,8,'#ffe14d') + R(D-22,30,12,8,'#ffe14d'));
    s.wheel(42,19,0,19).wheel(172,19,0,19);
    return s.svg('Вантажівка PaperMagic');
  },
  dog(){
    const s = Scene(40,226), G='#9fa9c4', W='#f4f1ea';
    s.shadow(150,228,130,14);
    s.box(38,58,0,42,52,68,W).box(142,162,0,42,52,68,W);
    const [tx,ty] = s.P(30,92,40);
    s.add(`<path d="M${tx} ${ty} C${tx-40} ${ty-10} ${tx-46} ${ty-70} ${tx-8} ${ty-74} C${tx+22} ${ty-76} ${tx+20} ${ty-44} ${tx} ${ty-44} C${tx-14} ${ty-44} ${tx-14} ${ty-58} ${tx-4} ${ty-58}" fill="none" stroke="${STROKE}" stroke-width="14" stroke-linecap="round"/>`+
           `<path d="M${tx} ${ty} C${tx-40} ${ty-10} ${tx-46} ${ty-70} ${tx-8} ${ty-74} C${tx+22} ${ty-76} ${tx+20} ${ty-44} ${tx} ${ty-44} C${tx-14} ${ty-44} ${tx-14} ${ty-58} ${tx-4} ${ty-58}" fill="none" stroke="${G}" stroke-width="9" stroke-linecap="round"/>`);
    s.box(28,170,40,96,14,70,G);
    let fur=''; for(let i=0;i<9;i++){ const x=40+i*14; fur+=`<path d="M${x} 52 l4 8 l3 -8 l4 8" fill="none" stroke="${W}" stroke-width="2" vector-effect="non-scaling-stroke"/>`; }
    s.side(14, fur);
    s.box(38,58,0,42,14,30,W).box(142,162,0,42,14,30,W);
    s.box(144,152,66,82,6,78,'#ff5b6e');
    s.box(150,214,72,140,8,76,G);
    s.box(158,178,140,152,10,26,'#6c7598').box(158,178,140,152,58,74,'#6c7598');
    const st = `stroke="${STROKE}" stroke-width="2" vector-effect="non-scaling-stroke"`;
    s.endX(214, PG([[0,72],[68,72],[68,98],[54,90],[34,98],[16,90],[0,98]],W)
      + C(20,118,10,'#fff',st) + C(48,118,10,'#fff',st) + C(22,117,5,STROKE) + C(50,117,5,STROKE)
      + PG([[8,128],[32,128],[30,136],[10,134]],W) + PG([[36,128],[60,128],[58,134],[38,136]],W)
      + `<ellipse cx="34" cy="100" rx="9" ry="6" fill="${STROKE}"/>` + `<ellipse cx="34" cy="80" rx="6" ry="5" fill="#ff8fa3" stroke="${STROKE}" stroke-width="1.6" vector-effect="non-scaling-stroke"/>`);
    return s.svg('Песик Шнауцер');
  }
};
const BG = {police:'#e8eeff', racer:'#ffe8e3', shark:'#e3f1ff', cupcake:'#ffeaf3', hippie:'#e2f7f4', bus:'#fff4d6', truck:'#fff1e0', dog:'#eef0f4'};

