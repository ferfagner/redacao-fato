// Mascote 3D do thebestnewsbr (v2). O quadro cobalto da logo vira um personagem:
// tela escura no rosto (olhos, sobrancelhas e boca amarela que muda por vogal), antena com o ponto
// vermelho de "no ar", braços com mãos, pés no chão. Tudo é função do tempo t: o render é determinístico.
//
// Atuação (princípios de animação):
// - toda pose nova tem antecipação (agacha um pouco), movimento com exagero (passa do ponto e volta)
//   e partes defasadas: o corpo lidera, os braços chegam depois e a antena balança por último;
// - o pulo agacha antes, estica no ar e amassa ao pousar;
// - na fala, a boca toma a forma de cada vogal, a cabeça acompanha as sílabas e as palavras longas
//   ganham um gesto de braço;
// - parado, ele respira, olha em volta e pisca (às vezes duas vezes).
import * as THREE from "./three.module.min.js";

const COR = { cobalto: 0x2a40f0, cobaltoEsc: 0x1c2bb0, tela: 0x10101a, branco: 0xffffff, amarelo: 0xffd60a,
  vermelho: 0xff5a45, sobrancelha: 0x8a95ff, pupila: 0x121218 };

// alvos de cada pose. braços em graus (0 = caído, positivo = levanta para fora, negativo = cruza o corpo)
const POSES = {
  fala:     { bE: 12, bD: 12, incl: 0, giro: -14, olhoX: 0, olhoY: 0, abre: 1.0, sobY: 0, sobR: 0, sobAsim: 0, boca: "barra", feliz: 0 },
  aponta:   { bE: 148, bD: 14, incl: -7, giro: -24, olhoX: -0.75, olhoY: 0.7, abre: 1.05, sobY: 4, sobR: 0, sobAsim: 0, boca: "sorriso", feliz: 0 },
  surpreso: { bE: 75, bD: 75, incl: 0, giro: -6, olhoX: 0, olhoY: 0.15, abre: 1.32, sobY: 11, sobR: -6, sobAsim: 0, boca: "o", feliz: 0 },
  pensa:    { bE: 10, bD: -56, incl: 8, giro: -18, olhoX: 0.6, olhoY: 0.85, abre: 0.9, sobY: 2, sobR: 0, sobAsim: 9, boca: "lado", feliz: 0 },
  comemora: { bE: 162, bD: 162, incl: 0, giro: -8, olhoX: 0, olhoY: 0.2, abre: 1.0, sobY: 7, sobR: -4, sobAsim: 0, boca: "riso", feliz: 1 },
  nega:     { bE: 10, bD: 105, incl: 0, giro: -10, olhoX: 0, olhoY: -0.15, abre: 0.92, sobY: -3, sobR: 14, sobAsim: 0, boca: "reta", feliz: 0 },
};
// formato da boca em repouso (largura, altura) e por vogal na fala
const BOCA = { barra: [74, 15], sorriso: [78, 20], o: [40, 44], lado: [32, 13], riso: [86, 34], reta: [54, 10] };
const VOGAL = { a: [64, 52], e: [80, 30], i: [78, 22], o: [46, 46], u: [36, 36] };

const cl = (k) => Math.min(1, Math.max(0, k));
const lerp = (a, b, k) => a + (b - a) * k;
const suave = (k) => { k = cl(k); return k * k * (3 - 2 * k); };
const passa = (k, s) => { k = cl(k); s = s == null ? 1.7 : s; return 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2); };
const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const rad = (g) => g * Math.PI / 180;

function forma(w, h, r) {
  const s = new THREE.Shape(), x = -w / 2, y = -h / 2;
  r = Math.min(r, w / 2, h / 2);
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  return s;
}
function placa(w, h, r, prof, bisel, mat) {
  const g = new THREE.ExtrudeGeometry(forma(w, h, r), { depth: prof, bevelEnabled: bisel > 0, bevelThickness: bisel, bevelSize: bisel, bevelSegments: 5, curveSegments: 12 });
  g.translate(0, 0, -prof / 2);
  return new THREE.Mesh(g, mat);
}

// pulo: agacha (0,1 s), sobe e desce (dur), amassa ao pousar (0,18 s). Devolve [y, escalaX, escalaY]
function pulo(t, t0, dur, h) {
  if (t < t0 - 0.1 || t > t0 + dur + 0.18) return [0, 1, 1];
  if (t < t0) { const a = (t - (t0 - 0.1)) / 0.1; return [0, 1 + 0.08 * a, 1 - 0.12 * a]; }
  if (t < t0 + dur) { const u = (t - t0) / dur, e = Math.sin(Math.PI * u); return [h * 4 * u * (1 - u), 1 - 0.05 * e, 1 + 0.09 * e]; }
  const a = Math.sin(Math.PI * (t - t0 - dur) / 0.18); return [0, 1 + 0.08 * a, 1 - 0.11 * a];
}

export async function criarMascote(canvas, dados) {
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(1080, 1920, false);
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;

  // câmera em perspectiva leve, calibrada para 1 unidade = 1 pixel no plano z = 0
  const cena = new THREE.Scene();
  const FOV = 20, D = 960 / Math.tan(rad(FOV / 2));
  const cam = new THREE.PerspectiveCamera(FOV, 1080 / 1920, 10, D * 3);
  cam.position.set(540, -960, D); cam.lookAt(540, -960, 0);
  cena.add(new THREE.HemisphereLight(0xdfe4ff, 0x101020, 1.0));
  const luzC = new THREE.DirectionalLight(0xfff1dc, 2.3); luzC.position.set(-0.7, 0.9, 1); cena.add(luzC);
  const luzR = new THREE.DirectionalLight(0x8a95ff, 2.2); luzR.position.set(1, 0.4, -0.8); cena.add(luzR);
  const luzF = new THREE.DirectionalLight(0xffffff, 0.45); luzF.position.set(0, -0.2, 1); cena.add(luzF);

  const plast = (cor, extra) => new THREE.MeshPhysicalMaterial({ color: cor, roughness: 0.34, metalness: 0.0, clearcoat: 0.6, clearcoatRoughness: 0.25, ...extra });
  const brilha = (cor, k) => new THREE.MeshStandardMaterial({ color: cor, emissive: cor, emissiveIntensity: k, roughness: 0.4 });

  const raiz = new THREE.Group(); cena.add(raiz);          // lugar na tela e escala
  const sombra = new THREE.Mesh(new THREE.CircleGeometry(110, 48), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.38 }));
  sombra.scale.set(1, 0.2, 1); sombra.position.set(0, -2, -40); raiz.add(sombra);
  const salto = new THREE.Group(); raiz.add(salto);        // pulo e amassa (origem nos pés)
  const pes = [];
  for (const sx of [-1, 1]) {
    const p = new THREE.Mesh(new THREE.SphereGeometry(24, 24, 16), plast(COR.cobaltoEsc));
    p.scale.set(1.35, 0.6, 1.4); p.position.set(sx * 50, 12, 46); salto.add(p); pes.push(p);
  }
  const corpo = new THREE.Group(); corpo.position.y = 30; salto.add(corpo);   // gira e inclina a partir da base
  const C = new THREE.Group(); C.position.y = 98; corpo.add(C);               // centro do corpo
  C.add(placa(210, 192, 56, 100, 18, plast(COR.cobalto)));
  const zF = 68;                                                               // frente do corpo
  const tela = placa(170, 138, 40, 6, 3, plast(COR.tela, { roughness: 0.15, clearcoat: 1 }));
  tela.position.set(0, 6, zF); C.add(tela);
  const zT = zF + 7;                                                           // frente da tela

  // olhos: branco + pupila com brilho (a pupila vive dentro do olho e pisca junto)
  const olhos = [], pupilas = [];
  for (const sx of [-1, 1]) {
    const g = new THREE.Group(); g.position.set(sx * 38, 24, zT); C.add(g);
    g.add(placa(40, 52, 20, 3, 1.5, brilha(COR.branco, 0.25)));
    const pg = new THREE.Group(); pg.position.z = 6; g.add(pg);
    pg.add(new THREE.Mesh(new THREE.CircleGeometry(11.5, 28), new THREE.MeshBasicMaterial({ color: COR.pupila })));
    const b = new THREE.Mesh(new THREE.CircleGeometry(3.6, 16), new THREE.MeshBasicMaterial({ color: COR.branco }));
    b.position.set(4, 4.5, 0.5); pg.add(b);
    // tampa da cor da tela que sobe por baixo: o olho vira um arco feliz
    const tampa = new THREE.Mesh(new THREE.CircleGeometry(30, 32), tela.material);   // mesma luz da tela: some nela
    tampa.position.set(0, -24, 7); tampa.visible = false; g.add(tampa); g.userData.tampa = tampa;
    olhos.push(g); pupilas.push(pg);
  }
  // sobrancelhas
  const sobs = [];
  for (const sx of [-1, 1]) {
    const s = placa(34, 8, 4, 3, 1, brilha(COR.sobrancelha, 0.35));
    s.position.set(sx * 38, 60, zT); C.add(s); sobs.push(s);
  }
  // boca: amarela por fora, escura por dentro quando abre
  const bocaG = new THREE.Group(); bocaG.position.set(0, -34, zT); C.add(bocaG);
  const bocaFora = placa(60, 40, 14, 3, 1, brilha(COR.amarelo, 0.22)); bocaG.add(bocaFora);
  const bocaDentro = placa(60, 40, 14, 2, 0, new THREE.MeshBasicMaterial({ color: 0x3a1020 })); bocaDentro.position.z = 2.6; bocaG.add(bocaDentro);
  // antena com o ponto de "no ar"
  const antena = new THREE.Group(); antena.position.set(62, 104, 0); C.add(antena);
  const haste = new THREE.Mesh(new THREE.CylinderGeometry(4, 5, 46, 12), plast(COR.cobaltoEsc)); haste.position.y = 23; antena.add(haste);
  const luz = new THREE.Mesh(new THREE.SphereGeometry(13, 24, 16), new THREE.MeshStandardMaterial({ color: COR.vermelho, emissive: COR.vermelho, emissiveIntensity: 0.6, roughness: 0.3 }));
  luz.position.y = 50; antena.add(luz);
  // braços: ombro (pivô) -> braço -> mão
  const bracos = [];
  for (const sx of [-1, 1]) {
    const o = new THREE.Group(); o.position.set(sx * 126, -8, 22); C.add(o);
    const b = new THREE.Mesh(new THREE.CapsuleGeometry(14, 54, 6, 14), plast(COR.cobaltoEsc)); b.position.y = -40; o.add(b);
    const m = new THREE.Mesh(new THREE.SphereGeometry(21, 22, 16), plast(COR.branco)); m.scale.set(1, 0.92, 0.85); m.position.y = -82; o.add(m);
    bracos.push(o);
  }

  const poses = dados.poses, lugares = dados.lugares;
  // palavras: [ini, fim, sílabas, vogais]
  const palavras = dados.palavras.map((p) => ({ a: p[0], b: p[1], n: Math.max(1, p[2]), v: p[3] || "a" }));

  function poseEm(t) {
    let i = 0;
    while (i + 1 < poses.length && poses[i + 1][0] <= t) i++;
    return { i, t0: poses[i][0], nome: poses[i][1], ant: poses[Math.max(0, i - 1)][1] };
  }
  function valores(P, t, atraso) {
    const a = POSES[P.ant] || POSES.fala, b = POSES[P.nome] || POSES.fala;
    const k = P.i === 0 ? 1 : passa((t - P.t0 - atraso) / 0.42, 1.6);
    const v = {};
    for (const n in b) v[n] = typeof b[n] === "number" ? lerp(a[n], b[n], k) : b[n];
    return v;
  }
  function falaEm(t) {
    for (let j = 0; j < palavras.length; j++) {
      const w = palavras[j];
      if (t >= w.a && t < w.b) {
        const u = (t - w.a) / Math.max(0.05, w.b - w.a) * w.n;
        const s = Math.min(w.n - 1, Math.floor(u));
        return { abre: Math.pow(Math.sin(Math.PI * (u - s)), 0.7), vogal: w.v[Math.min(s, w.v.length - 1)] || "a", j, w,
                 gesto: w.n >= 3 ? Math.sin(Math.PI * cl((t - w.a) / (w.b - w.a))) : 0 };
      }
    }
    return null;
  }
  function piscada(t) {
    for (let k = 0; k < 60; k++) {
      const tb = 1.2 + k * 2.9 + hash(k) * 1.1;
      for (const off of hash(k + 99) < 0.18 ? [0, 0.22] : [0]) {
        const d = t - tb - off;
        if (d >= 0 && d < 0.13) return 1 - 0.95 * Math.sin(Math.PI * d / 0.13);
      }
    }
    return 1;
  }

  function render(t) {
    // ---- lugar na tela (com pulinho quando muda de lugar)
    let li = 0;
    while (li + 1 < lugares.length && lugares[li + 1][0] <= t) li++;
    const L1 = lugares[li], L0 = lugares[Math.max(0, li - 1)];
    const kL = li === 0 ? 1 : suave((t - L1[0]) / 0.55);
    const x = lerp(L0[1], L1[1], kL), yTela = lerp(L0[2], L1[2], kL), s = lerp(L0[3], L1[3], kL);
    const arco = li === 0 ? 0 : 90 * Math.sin(Math.PI * cl((t - L1[0]) / 0.55));
    const entrada = lugares[0][0] > 0 ? passa((t - lugares[0][0]) / 0.45) : 1;
    raiz.position.set(x, -(yTela + 128 * s) + arco, 0);                      // yTela = centro do corpo (120 acima dos pés)
    raiz.scale.setScalar(Math.max(0.001, s * entrada));

    // ---- pose (corpo lidera; braços chegam 0,06 s depois)
    const P = poseEm(t);
    const v = valores(P, t, 0), vb = valores(P, t, 0.06);
    const dt = t - P.t0;
    const antec = P.i > 0 && dt >= 0 && dt < 0.08 ? Math.sin(Math.PI * dt / 0.08) : 0;   // agacha antes de mudar

    // ---- pulos
    let py = 0, sx = 1, sy = 1;
    const soma = (r) => { py += r[0]; sx *= r[1]; sy *= r[2]; };
    if (P.nome === "surpreso") soma(pulo(t, P.t0 + 0.1, 0.38, 70));
    if (P.nome === "comemora") { soma(pulo(t, P.t0 + 0.12, 0.34, 55)); soma(pulo(t, P.t0 + 0.62, 0.34, 45)); }
    if (li > 0) { const kk = (t - L1[0]) / 0.55; if (kk > 1 && kk < 1.35) { const a = Math.sin(Math.PI * (kk - 1) / 0.35); sx *= 1 + 0.07 * a; sy *= 1 - 0.1 * a; } }

    // ---- fala
    const F = falaEm(t);
    const fAbre = F ? F.abre : 0;
    const resp = Math.sin(t * Math.PI * 0.9);
    salto.position.y = py + (F ? 2.5 * fAbre : 0);
    salto.scale.set(sx * (1 + 0.05 * antec) * (1 + resp * 0.006), sy * (1 - 0.07 * antec) * (1 - resp * 0.01), 1);
    sombra.scale.set(1 - Math.min(0.35, py / 260), 0.2 * (1 - Math.min(0.35, py / 260)), 1);
    sombra.material.opacity = 0.38 - Math.min(0.16, py / 300);

    // giro e inclinação (+ balanço de "não" e ondulação lenta)
    let giro = v.giro + Math.sin(t * 0.45) * 3;
    if (P.nome === "nega" && dt < 1.3) giro += 20 * Math.sin(dt * Math.PI * 5.2) * Math.exp(-2.2 * dt);
    corpo.rotation.set(rad(3 + (F ? -2.5 * fAbre : 0) + Math.sin(t * 0.7) * 1.5), rad(giro), rad(v.incl));

    // braços (com balanço de comemoração, aceno do "não" e gesto em palavra longa)
    let bE = vb.bE, bD = vb.bD;
    if (P.nome === "comemora") { bE += 14 * Math.sin(dt * 9); bD += 14 * Math.sin(dt * 9 + Math.PI); }
    if (P.nome === "nega" && dt < 1.4) bD += 18 * Math.sin(dt * Math.PI * 5.2) * Math.exp(-1.6 * dt);
    if (P.nome === "surpreso") { bE += 3 * Math.sin(t * 40) * Math.exp(-3 * dt); bD += 3 * Math.sin(t * 43) * Math.exp(-3 * dt); }
    if (F && F.gesto && P.nome === "fala") { if (F.j % 2) bD += 32 * F.gesto; else bE += 32 * F.gesto; }
    bE -= 6 * antec; bD -= 6 * antec;
    bracos[0].rotation.z = -rad(bE + Math.sin(t * 1.3) * 2.5);
    bracos[1].rotation.z = rad(bD + Math.sin(t * 1.1 + 1) * 2.5);
    bracos[1].rotation.x = P.nome === "pensa" ? rad(-62 * cl(dt / 0.4)) : 0;   // mão ao queixo, na frente do rosto

    // olhos: alvo da pose no começo, depois olha em volta / para a câmera ao falar
    let ox = v.olhoX, oy = v.olhoY;
    const segura = P.nome === "pensa" ? 99 : (P.nome === "aponta" ? 1.4 : 0.7);
    if (dt > segura) {
      const k = Math.floor(t / 2.3), u = cl((t - k * 2.3) / 0.12);
      const alvoX = F ? 0 : (hash(k) - 0.5) * 0.7, alvoY = F ? 0 : (hash(k + 7) - 0.5) * 0.5;
      const antX = F ? 0 : (hash(k - 1) - 0.5) * 0.7, antY = F ? 0 : (hash(k + 6) - 0.5) * 0.5;
      const kr = cl((dt - segura) / 0.25);
      ox = lerp(ox, lerp(antX, alvoX, u), kr); oy = lerp(oy, lerp(antY, alvoY, u), kr);
    }
    const pis = piscada(t);
    for (let i = 0; i < 2; i++) {
      olhos[i].scale.set(1, Math.max(0.06, v.abre * pis), 1);
      olhos[i].position.y = 24 + (P.nome === "comemora" ? 6 * cl(dt / 0.3) : 0);
      pupilas[i].position.set(ox * 9, oy * 11, 6);
      pupilas[i].scale.setScalar(Math.max(0.001, 1 - v.feliz));
      olhos[i].userData.tampa.visible = v.feliz > 0.02;
      olhos[i].userData.tampa.scale.set(Math.max(0.001, v.feliz), 0.75 * Math.max(0.001, v.feliz), 1);
      // sobrancelhas: altura, inclinação espelhada e assimetria (uma sobe ao pensar)
      const lado = i ? 1 : -1;
      sobs[i].position.y = 60 + v.sobY + (i === 0 ? v.sobAsim : 0) + (F && F.w.n >= 3 && F.abre > 0.5 ? 3 : 0) - 4 * antec;
      sobs[i].rotation.z = rad(lado * v.sobR + (i === 0 ? v.sobAsim * 0.8 : 0));
    }

    // boca: forma de repouso da pose misturada com a vogal falada
    const rep = BOCA[v.boca] || BOCA.barra, vg = VOGAL[F ? F.vogal : "a"] || VOGAL.a;
    const w = lerp(rep[0], vg[0], fAbre), h = lerp(rep[1], vg[1], fAbre);
    bocaFora.scale.set(w / 60, h / 40, 1);
    bocaDentro.visible = h > 18;
    bocaDentro.scale.set(Math.max(0.01, (w - 12) / 60), Math.max(0.01, (h - 12) / 40), 1);
    bocaG.position.x = v.boca === "lado" ? 16 * (1 - fAbre) : 0;
    bocaG.position.y = -34 - 9 * v.feliz;

    // antena: balança atrasada (acompanha o pulo e a fala)
    const vel = py - (P.nome === "surpreso" ? pulo(t - 0.06, P.t0 + 0.1, 0.38, 70)[0] : P.nome === "comemora" ? pulo(t - 0.06, P.t0 + 0.12, 0.34, 55)[0] : py);
    antena.rotation.z = rad(-6 + Math.sin(t * 2.1) * 4 + vel * 0.5 + fAbre * 3 - giro * 0.15);
    luz.material.emissiveIntensity = 0.45 + 0.55 * (0.5 + 0.5 * Math.sin(t * Math.PI * 1.6));

    renderer.render(cena, cam);
  }
  return { render };
}
