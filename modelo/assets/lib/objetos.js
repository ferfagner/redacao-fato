// Acervo de objetos 3D das cenas (Three.js). Cada objeto é uma função que monta a peça e devolve
// anima(t). Tudo é função do tempo t: o render é determinístico.
import * as THREE from "./three.module.min.js";

const COR = { cobalto: 0x2a40f0, cobaltoEsc: 0x1c2bb0, cobaltoClaro: 0x8a95ff, amarelo: 0xffd60a, branco: 0xffffff,
  linha: 0x2e2e3d, tela: 0x10101a, vermelho: 0xff5a45, verde: 0x2ee59d };
const cl = (k) => Math.min(1, Math.max(0, k));
const easeOut = (k) => 1 - Math.pow(1 - cl(k), 3);
const back = (k) => { k = cl(k); const c = 1.7; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
const sc = (m, k) => m.scale.setScalar(Math.max(0.001, k));

function forma(w, h, r) {
  const s = new THREE.Shape(), x = -w / 2, y = -h / 2;
  r = Math.min(r, w / 2, h / 2);
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  return s;
}
const placa = (w, h, r, d, mat, bisel = 0.04) => {
  const g = new THREE.ExtrudeGeometry(forma(w, h, r), { depth: d, bevelEnabled: true, bevelThickness: bisel, bevelSize: bisel, bevelSegments: 4, curveSegments: 10 });
  g.translate(0, 0, -d / 2);
  return new THREE.Mesh(g, mat);
};

// ------------------------------------------------------------------ catálogo
// cada entrada: (ctx) => anima(t). ctx = {g (grupo), M (material), o (dados), anc (âncoras de rótulo), sombra}
const OBJ = {};

OBJ.moedas = ({ g, M, o }) => {
  const moedas = [], geo = new THREE.CylinderGeometry(0.62, 0.62, 0.11, 48);
  const mat = M(COR.amarelo, { metalness: 0.55, roughness: 0.3, emissive: 0x3a2a00, emissiveIntensity: 0.4 });
  for (let i = 0; i < 12; i++) {
    const m = new THREE.Mesh(geo, mat);
    const borda = new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.025, 8, 40), M(0xffe680, { metalness: 0.5 }));
    borda.rotation.x = Math.PI / 2; borda.position.y = 0.056; m.add(borda);
    g.add(m); moedas.push(m);
  }
  return (t) => moedas.forEach((m, i) => {
    const k = easeOut((t - o.t0 - i * 0.07) / 0.35);
    m.position.set(Math.sin(i * 2.1) * 0.04, 0.06 + i * 0.115 + (1 - k) * 3.2, Math.cos(i * 1.7) * 0.04);
    m.rotation.y = i * 0.6 + t * 0.4; m.visible = t >= o.t0 + i * 0.07 - 0.01;
  });
};

OBJ.podio = ({ g, M, o, anc }) => {
  const alturas = [0.85, 1.25, 0.6], xs = [-1.15, 0, 1.15], ordem = [1, 0, 2];
  const blocos = [0, 1, 2].map((j) => {
    const b = new THREE.Mesh(new THREE.BoxGeometry(1.05, 1, 1.0), M(j === 1 ? COR.amarelo : COR.cobalto));
    b.position.x = xs[j]; g.add(b); anc.push(new THREE.Vector3(xs[j], 0, 0)); return b;
  });
  o._ordemRot = [1, 0, 2];   // rótulos: 1º no centro, 2º à esquerda, 3º à direita
  return (t) => blocos.forEach((b, j) => {
    const h = Math.max(0.001, alturas[j] * back((t - o.t0 - ordem[j] * 0.18) / 0.55));
    b.scale.y = h; b.position.y = h / 2; anc[j].set(xs[j], h + 0.32, 0.5);
  });
};

OBJ.barras = ({ g, M, o, anc }) => {
  const it = o.itens || [], vals = it.map((x) => x.valor), vmax = Math.max(...vals) || 1, n = it.length;
  const passo = Math.min(2.1, 4.4 / n), x0 = -passo * (n - 1) / 2;
  const bs = it.map((x, j) => {
    const b = new THREE.Mesh(new THREE.BoxGeometry(passo * 0.62, 1, 0.7), M(x.valor === vmax ? COR.amarelo : COR.cobalto));
    b.position.x = x0 + j * passo; g.add(b); anc.push(new THREE.Vector3(b.position.x, 0, 0.35)); return b;
  });
  return (t) => bs.forEach((b, j) => {
    const h = Math.max(0.001, (0.15 + 1.2 * vals[j] / vmax) * easeOut((t - o.t0 - j * 0.15) / 0.8));
    b.scale.y = h; b.position.y = h / 2; anc[j].y = h + 0.14;
  });
};

OBJ.planeta = ({ g, M, o, sombra }) => {
  const p = new THREE.Mesh(new THREE.IcosahedronGeometry(1.0, 3), M(COR.cobaltoClaro, { flatShading: true, roughness: 0.6 }));
  p.position.y = 1.0; g.add(p);
  const anel = new THREE.Mesh(new THREE.RingGeometry(1.35, 1.75, 96), new THREE.MeshStandardMaterial({ color: COR.amarelo, side: THREE.DoubleSide, roughness: 0.4, transparent: true, opacity: 0.9 }));
  anel.rotation.x = Math.PI / 2.4; anel.position.y = 1.0; g.add(anel);
  const lua = new THREE.Mesh(new THREE.SphereGeometry(0.16, 24, 16), M(COR.branco)); g.add(lua);
  sombra.visible = false;
  return (t) => {
    const k = back((t - o.t0) / 0.7); sc(p, k); sc(anel, k);
    p.rotation.y = t * 0.5; anel.rotation.z = t * 0.15;
    const a = t * 1.3; lua.position.set(Math.cos(a) * 2.2, 1.0 + Math.sin(a) * 0.35, Math.sin(a) * 2.2); lua.visible = k > 0.5;
  };
};

// pizza: fatias proporcionais aos valores de "comparacao" (a maior em amarelo)
OBJ.pizza = ({ g, M, o, anc }) => {
  const it = o.itens || [], tot = it.reduce((s, x) => s + x.valor, 0) || 1, vmax = Math.max(...it.map((x) => x.valor));
  const cores = [COR.cobalto, COR.cobaltoClaro, COR.cobaltoEsc, 0x5468ff];
  let a0 = Math.PI / 2;
  const fatias = it.map((x, j) => {
    const ang = (x.valor / tot) * Math.PI * 2;
    const s = new THREE.Shape(); s.moveTo(0, 0); s.absarc(0, 0, 1.45, a0, a0 + ang, false); s.lineTo(0, 0);
    const geo = new THREE.ExtrudeGeometry(s, { depth: 0.35, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 2, curveSegments: 48 });
    const m = new THREE.Mesh(geo, M(x.valor === vmax ? COR.amarelo : cores[j % cores.length]));
    m.rotation.x = -Math.PI / 2;
    const meio = a0 + ang / 2; m.userData = { meio, dx: Math.cos(meio), dz: -Math.sin(meio) };
    anc.push(new THREE.Vector3(Math.cos(meio) * 1.95, 0.45, -Math.sin(meio) * 1.95));
    a0 += ang; g.add(m); return m;
  });
  return (t) => fatias.forEach((m, j) => {
    const k = back((t - o.t0 - j * 0.12) / 0.5); m.scale.set(Math.max(0.001, k), Math.max(0.001, k), 1);
    const sai = m.userData.meio && it[j].valor === vmax ? 0.18 * easeOut((t - o.t0 - 0.9) / 0.4) : 0;
    m.position.set(m.userData.dx * sai, 0.05, m.userData.dz * sai);
  });
};

// linha: pontos ligados por uma "fita" 3D, um por item de "comparacao"
OBJ.linha = ({ g, M, o, anc }) => {
  const it = o.itens || [], n = Math.max(2, it.length), vals = it.map((x) => x.valor);
  const vmin = Math.min(...vals), vmax = Math.max(...vals), larg = 4.2;
  const pts = it.map((x, j) => new THREE.Vector3(-larg / 2 + larg * j / (n - 1), 0.3 + 1.6 * (x.valor - vmin) / ((vmax - vmin) || 1), 0));
  const curva = new THREE.CatmullRomCurve3(pts);
  const tubo = new THREE.Mesh(new THREE.TubeGeometry(curva, 120, 0.06, 12), M(COR.amarelo, { emissive: 0x3a2a00, emissiveIntensity: 0.5 }));
  g.add(tubo);
  const bolas = pts.map((p) => { const b = new THREE.Mesh(new THREE.SphereGeometry(0.13, 20, 14), M(COR.branco)); b.position.copy(p); g.add(b); anc.push(p.clone().add(new THREE.Vector3(0, 0.22, 0))); return b; });
  const base = new THREE.Mesh(new THREE.BoxGeometry(larg + 0.6, 0.06, 0.8), M(COR.cobaltoEsc)); base.position.y = 0.0; g.add(base);
  const idx = tubo.geometry.index; const total = idx ? idx.count : 0;
  return (t) => {
    const k = easeOut((t - o.t0) / 1.0);
    if (idx) tubo.geometry.setDrawRange(0, Math.floor(total * k / 6) * 6);
    bolas.forEach((b, j) => sc(b, back((t - o.t0 - 0.9 * j / (n - 1)) / 0.3)));
  };
};

OBJ.trofeu = ({ g, M, o }) => {
  const ouro = M(COR.amarelo, { metalness: 0.7, roughness: 0.25, emissive: 0x2a1e00, emissiveIntensity: 0.4 });
  const t1 = new THREE.Group(); g.add(t1);
  const copa = new THREE.Mesh(new THREE.LatheGeometry([0, 0.2, 0.55, 0.7, 0.72, 0.7].map((r, i) => new THREE.Vector2(r, i * 0.22)), 48), ouro);
  copa.position.y = 1.0; t1.add(copa);
  for (const s of [-1, 1]) { const a = new THREE.Mesh(new THREE.TorusGeometry(0.28, 0.06, 12, 32, Math.PI), ouro); a.position.set(s * 0.72, 1.55, 0); a.rotation.z = s * -Math.PI / 2; t1.add(a); }
  const haste = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.16, 0.5, 24), ouro); haste.position.y = 0.75; t1.add(haste);
  const base = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.35, 0.9), M(COR.cobaltoEsc)); base.position.y = 0.32; t1.add(base);
  const placaT = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.14, 0.02), ouro); placaT.position.set(0, 0.32, 0.46); t1.add(placaT);
  return (t) => { const k = back((t - o.t0) / 0.6); sc(t1, k); t1.rotation.y = (1 - k) * 2 + Math.sin(t * 0.8) * 0.2; };
};

OBJ.medalha = ({ g, M, o }) => {
  const m1 = new THREE.Group(); g.add(m1);
  const disco = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 0.12, 64), M(COR.amarelo, { metalness: 0.7, roughness: 0.25 }));
  disco.rotation.x = Math.PI / 2; disco.position.y = 1.1; m1.add(disco);
  const estrela = new THREE.Shape();
  for (let i = 0; i < 10; i++) { const r = i % 2 ? 0.22 : 0.5, a = Math.PI / 2 + i * Math.PI / 5; i ? estrela.lineTo(Math.cos(a) * r, Math.sin(a) * r) : estrela.moveTo(Math.cos(a) * r, Math.sin(a) * r); }
  const est = new THREE.Mesh(new THREE.ExtrudeGeometry(estrela, { depth: 0.06, bevelEnabled: false }), M(COR.branco)); est.position.set(0, 1.1, 0.07); m1.add(est);
  for (const s of [-1, 1]) { const f = new THREE.Mesh(new THREE.BoxGeometry(0.32, 1.2, 0.03), M(s < 0 ? COR.cobalto : COR.vermelho)); f.position.set(s * 0.22, 2.15, -0.05); f.rotation.z = s * 0.28; m1.add(f); }
  return (t) => { const k = back((t - o.t0) / 0.6); sc(m1, k); m1.rotation.y = Math.sin(t * 1.4) * 0.5; m1.position.y = (1 - k) * 1.2 - 0.3; };
};

OBJ.foguete = ({ g, M, o, sombra }) => {
  const f = new THREE.Group(); g.add(f);
  const corpo = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 1.3, 32), M(COR.branco)); corpo.position.y = 0.65; f.add(corpo);
  const bico = new THREE.Mesh(new THREE.ConeGeometry(0.32, 0.6, 32), M(COR.vermelho)); bico.position.y = 1.6; f.add(bico);
  const janela = new THREE.Mesh(new THREE.CircleGeometry(0.13, 24), M(COR.cobaltoClaro, { emissive: COR.cobalto, emissiveIntensity: 0.6 })); janela.position.set(0, 0.95, 0.321); f.add(janela);
  for (let i = 0; i < 3; i++) { const a = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.45, 0.4), M(COR.cobalto)); const ang = i * Math.PI * 2 / 3; a.position.set(Math.sin(ang) * 0.34, 0.2, Math.cos(ang) * 0.34); a.rotation.y = ang; f.add(a); }
  const fogo = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.7, 24), new THREE.MeshBasicMaterial({ color: COR.amarelo, transparent: true, opacity: 0.85 }));
  fogo.rotation.x = Math.PI; fogo.position.y = -0.35; f.add(fogo);
  sombra.visible = false;
  return (t) => {
    const k = easeOut((t - o.t0) / 1.2);
    f.position.y = -1.6 + 2.0 * k + Math.sin(t * 9) * 0.015; f.rotation.y = t * 0.6;
    fogo.scale.set(1, 0.8 + 0.4 * Math.abs(Math.sin(t * 23)), 1);
  };
};

OBJ.lampada = ({ g, M, o }) => {
  const l = new THREE.Group(); g.add(l);
  const vidro = new THREE.Mesh(new THREE.SphereGeometry(0.7, 40, 30), new THREE.MeshPhysicalMaterial({ color: COR.amarelo, emissive: COR.amarelo, emissiveIntensity: 0, roughness: 0.1, transmission: 0.2, transparent: true, opacity: 0.92 }));
  vidro.position.y = 1.45; l.add(vidro);
  const rosca = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.26, 0.55, 24), M(0xb8bcc8, { metalness: 0.8, roughness: 0.3 })); rosca.position.y = 0.6; l.add(rosca);
  const raios = new THREE.Group(); l.add(raios);
  for (let i = 0; i < 8; i++) { const r = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.32, 0.06), new THREE.MeshBasicMaterial({ color: COR.amarelo })); const a = i * Math.PI / 4; r.position.set(Math.cos(a) * 1.05, 1.45 + Math.sin(a) * 1.05, 0); r.rotation.z = a - Math.PI / 2; raios.add(r); }
  return (t) => {
    const k = back((t - o.t0) / 0.5); sc(l, k);
    const acende = cl((t - o.t0 - 0.6) / 0.15); vidro.material.emissiveIntensity = 0.9 * acende;
    raios.visible = acende > 0.5; raios.scale.setScalar(1 + 0.08 * Math.sin(t * 6));
  };
};

OBJ.relogio = ({ g, M, o }) => {
  const r = new THREE.Group(); r.position.y = 1.15; g.add(r);
  r.add(new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0, 0.2, 64).rotateX(Math.PI / 2), M(COR.cobalto)));
  const face = new THREE.Mesh(new THREE.CircleGeometry(0.88, 64), M(COR.branco)); face.position.z = 0.11; r.add(face);
  for (let i = 0; i < 12; i++) { const m = new THREE.Mesh(new THREE.BoxGeometry(0.05, i % 3 ? 0.1 : 0.18, 0.02), M(COR.tela)); const a = i * Math.PI / 6; m.position.set(Math.sin(a) * 0.74, Math.cos(a) * 0.74, 0.12); m.rotation.z = -a; r.add(m); }
  const pH = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.45, 0.02).translate(0, 0.2, 0), M(COR.tela)); pH.position.z = 0.13; r.add(pH);
  const pM = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.68, 0.02).translate(0, 0.32, 0), M(COR.vermelho)); pM.position.z = 0.14; r.add(pM);
  return (t) => { const k = back((t - o.t0) / 0.5); sc(r, k); pM.rotation.z = -t * 2.4; pH.rotation.z = -t * 0.2; };
};

OBJ.ampulheta = ({ g, M, o }) => {
  const a = new THREE.Group(); g.add(a);
  const vidro = new THREE.MeshPhysicalMaterial({ color: 0xdfe4ff, roughness: 0.05, transparent: true, opacity: 0.35 });
  const perfil = [0.05, 0.45, 0.6, 0.55, 0.3, 0.08, 0.3, 0.55, 0.6, 0.45, 0.05].map((r, i) => new THREE.Vector2(r, i * 0.2));
  const v = new THREE.Mesh(new THREE.LatheGeometry(perfil, 40), vidro); v.position.y = 0.15; a.add(v);
  const areiaC = new THREE.Mesh(new THREE.ConeGeometry(0.45, 0.6, 32), M(COR.amarelo)); areiaC.position.y = 1.55; areiaC.rotation.x = Math.PI; a.add(areiaC);
  const areiaB = new THREE.Mesh(new THREE.ConeGeometry(0.5, 0.6, 32), M(COR.amarelo)); areiaB.position.y = 0.45; a.add(areiaB);
  for (const y of [0.1, 2.25]) { const tampa = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.75, 0.12, 40), M(COR.cobalto)); tampa.position.y = y; a.add(tampa); }
  return (t) => {
    const k = back((t - o.t0) / 0.5); sc(a, k);
    const u = cl((t - o.t0 - 0.4) / Math.max(1, (o.dur || 4) - 1));
    areiaC.scale.set(Math.max(0.05, 1 - u), Math.max(0.05, 1 - u), Math.max(0.05, 1 - u));
    areiaB.scale.set(Math.max(0.05, 0.3 + 0.7 * u), Math.max(0.05, 0.3 + 0.7 * u), Math.max(0.05, 0.3 + 0.7 * u));
  };
};

OBJ.celular = ({ g, M, o }) => {
  const c = new THREE.Group(); c.position.y = 1.2; g.add(c);
  c.add(placa(1.1, 2.1, 0.18, 0.1, M(COR.tela)));
  const tela = placa(0.96, 1.9, 0.12, 0.01, M(COR.cobalto, { emissive: COR.cobalto, emissiveIntensity: 0.6 }), 0.005); tela.position.z = 0.07; c.add(tela);
  const icones = [];
  for (let i = 0; i < 9; i++) { const ic = placa(0.2, 0.2, 0.05, 0.01, M(i === 4 ? COR.amarelo : COR.branco, { emissive: i === 4 ? COR.amarelo : 0x555577, emissiveIntensity: 0.4 }), 0.005); ic.position.set(-0.28 + (i % 3) * 0.28, 0.45 - Math.floor(i / 3) * 0.32, 0.09); c.add(ic); icones.push(ic); }
  return (t) => {
    const k = back((t - o.t0) / 0.5); sc(c, k); c.rotation.y = -0.3 + Math.sin(t * 0.9) * 0.25;
    icones.forEach((ic, i) => sc(ic, back((t - o.t0 - 0.3 - i * 0.05) / 0.3)));
  };
};

OBJ.controle = ({ g, M, o }) => {
  const c = new THREE.Group(); c.position.y = 1.0; g.add(c);
  const corpo = placa(2.2, 0.9, 0.42, 0.35, M(COR.tela)); c.add(corpo);
  for (const s of [-1, 1]) { const p = new THREE.Mesh(new THREE.SphereGeometry(0.42, 24, 18), M(COR.tela)); p.scale.set(1, 1.15, 0.5); p.position.set(s * 0.82, -0.35, 0); c.add(p); }
  const cruz = new THREE.Group(); cruz.position.set(-0.62, 0.05, 0.25); c.add(cruz);
  cruz.add(new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.11, 0.06), M(COR.cobaltoClaro))); cruz.add(new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.36, 0.06), M(COR.cobaltoClaro)));
  const botoes = [[0.62, 0.17, COR.amarelo], [0.78, 0.03, COR.vermelho], [0.62, -0.11, COR.verde], [0.46, 0.03, COR.cobaltoClaro]].map(([x, y, cor]) => {
    const b = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.07, 20).rotateX(Math.PI / 2), M(cor, { emissive: cor, emissiveIntensity: 0.3 })); b.position.set(x, y, 0.22); c.add(b); return b;
  });
  for (const s of [-1, 1]) { const a = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.08, 20).rotateX(Math.PI / 2), M(COR.cobalto)); a.position.set(s * 0.25, -0.22, 0.22); c.add(a); }
  return (t) => {
    const k = back((t - o.t0) / 0.5); sc(c, k); c.rotation.x = -0.35; c.rotation.y = Math.sin(t * 0.8) * 0.3;
    botoes.forEach((b, i) => { b.position.z = 0.22 - 0.03 * (Math.floor(t * 3) % 4 === i ? 1 : 0); });
  };
};

OBJ.predios = ({ g, M, o }) => {
  const hs = [1.2, 2.0, 1.5, 2.6, 1.1, 1.8, 1.4], ps = [];
  hs.forEach((h, j) => {
    const p = new THREE.Mesh(new THREE.BoxGeometry(0.5, 1, 0.5), M(j === 3 ? COR.amarelo : (j % 2 ? COR.cobalto : COR.cobaltoEsc)));
    p.position.set(-1.65 + j * 0.55, 0, (j % 3) * 0.25 - 0.25); p.userData.h = h; g.add(p); ps.push(p);
    for (let a = 0; a < Math.floor(h / 0.35); a++) { const jan = new THREE.Mesh(new THREE.PlaneGeometry(0.3, 0.08), new THREE.MeshBasicMaterial({ color: (a + j) % 3 ? 0xfff1b0 : 0x404060 })); jan.position.set(0, 0, 0.255); jan.userData.y = 0.2 + a * 0.35; p.add(jan); }
  });
  return (t) => ps.forEach((p, j) => {
    const h = Math.max(0.001, p.userData.h * easeOut((t - o.t0 - j * 0.08) / 0.6));
    p.scale.y = h; p.position.y = h / 2;
    p.children.forEach((jan) => { jan.position.y = (jan.userData.y - h / 2) / h; jan.scale.y = 1 / h; jan.visible = jan.userData.y < h - 0.1; });
  });
};

OBJ.dinheiro = ({ g, M, o }) => {
  const notas = [];
  for (let i = 0; i < 10; i++) {
    const n = new THREE.Group(); g.add(n);
    const papel = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.03, 0.8), M(COR.verde, { roughness: 0.8 })); n.add(papel);
    const faixa = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.032, 0.82), M(0x1c8f61)); n.add(faixa);
    notas.push(n);
  }
  return (t) => notas.forEach((n, i) => {
    const k = easeOut((t - o.t0 - i * 0.08) / 0.4);
    n.position.set(Math.sin(i * 1.7) * 0.05, 0.02 + i * 0.035 + (1 - k) * 2.6, Math.cos(i * 2.3) * 0.05);
    n.rotation.y = i * 0.12 + (1 - k) * 1.5; n.visible = t >= o.t0 + i * 0.08 - 0.01;
  });
};

OBJ.coracao = ({ g, M, o }) => {
  const s = new THREE.Shape();
  s.moveTo(0, -0.9); s.bezierCurveTo(-1.2, -0.1, -1.1, 0.9, -0.5, 0.9); s.bezierCurveTo(-0.15, 0.9, 0, 0.6, 0, 0.45);
  s.bezierCurveTo(0, 0.6, 0.15, 0.9, 0.5, 0.9); s.bezierCurveTo(1.1, 0.9, 1.2, -0.1, 0, -0.9);
  const c = new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth: 0.4, bevelEnabled: true, bevelThickness: 0.12, bevelSize: 0.1, bevelSegments: 6, curveSegments: 32 }), M(COR.vermelho, { emissive: 0x401010, emissiveIntensity: 0.4 }));
  c.geometry.center(); c.position.y = 1.15; g.add(c);
  return (t) => { const k = back((t - o.t0) / 0.5); const bate = 1 + 0.08 * Math.max(0, Math.sin(t * 7)) * (k > 0.9 ? 1 : 0); sc(c, k * bate); c.rotation.y = Math.sin(t * 0.7) * 0.35; };
};

OBJ.atomo = ({ g, M, o, sombra }) => {
  const a = new THREE.Group(); a.position.y = 1.15; g.add(a);
  const nucleo = new THREE.Mesh(new THREE.IcosahedronGeometry(0.32, 2), M(COR.amarelo, { emissive: 0x3a2a00, emissiveIntensity: 0.5 })); a.add(nucleo);
  const orbs = [0, 1, 2].map((i) => {
    const o2 = new THREE.Group(); o2.rotation.set(Math.PI / 2, i * Math.PI / 3, 0); a.add(o2);
    o2.add(new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.02, 8, 96), M(COR.cobaltoClaro)));
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 12), M(COR.branco, { emissive: COR.branco, emissiveIntensity: 0.5 })); o2.add(e);
    return e;
  });
  sombra.visible = false;
  return (t) => { const k = back((t - o.t0) / 0.6); sc(a, k); a.rotation.y = t * 0.4; orbs.forEach((e, i) => { const ang = t * (2.2 + i * 0.4) + i * 2; e.position.set(Math.cos(ang) * 1.15, Math.sin(ang) * 1.15, 0); }); };
};

OBJ.dna = ({ g, M, o, sombra }) => {
  const d = new THREE.Group(); d.position.y = 0.1; g.add(d);
  const n = 18;
  for (let i = 0; i < n; i++) {
    const y = i * 0.13, a = i * 0.55;
    for (const s of [0, Math.PI]) { const b = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 10), M(s ? COR.amarelo : COR.cobaltoClaro)); b.position.set(Math.cos(a + s) * 0.6, y, Math.sin(a + s) * 0.6); d.add(b); }
    const ligacao = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.2, 8), M(COR.branco)); ligacao.position.y = y; ligacao.rotation.set(0, -a, Math.PI / 2); d.add(ligacao);
  }
  sombra.visible = false;
  return (t) => { d.rotation.y = t * 0.8; d.children.forEach((c, i) => { c.visible = t > o.t0 + (i / d.children.length) * 0.9; }); };
};

OBJ.cadeado = ({ g, M, o }) => {
  const c = new THREE.Group(); c.position.y = 0.8; g.add(c);
  c.add(placa(1.3, 1.0, 0.18, 0.5, M(COR.amarelo, { metalness: 0.5, roughness: 0.3 })));
  const arco = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.09, 16, 40, Math.PI), M(0xb8bcc8, { metalness: 0.8, roughness: 0.25 })); c.add(arco);
  for (const s of [-1, 1]) { const h = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.4, 16), arco.material); h.position.set(s * 0.42, 0.55, 0); h.userData.s = s; c.add(h); }
  const furo = new THREE.Mesh(new THREE.CircleGeometry(0.1, 20), M(COR.tela)); furo.position.set(0, 0.05, 0.3); c.add(furo);
  return (t) => { const k = back((t - o.t0) / 0.5); sc(c, k); const fecha = easeOut((t - o.t0 - 0.6) / 0.3); arco.position.y = 0.75 + 0.3 * (1 - fecha); c.children.forEach((h) => { if (h.userData.s) h.position.y = 0.55 + 0.3 * (1 - fecha); }); c.rotation.y = Math.sin(t * 0.7) * 0.3; };
};

OBJ.alvo = ({ g, M, o }) => {
  const a = new THREE.Group(); a.position.y = 1.15; g.add(a);
  [1.1, 0.85, 0.6, 0.35, 0.12].forEach((r, i) => { const d = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 0.12, 48).rotateX(Math.PI / 2), M(i % 2 ? COR.branco : (i === 4 ? COR.amarelo : COR.vermelho))); d.position.z = i * 0.015; a.add(d); });
  const flecha = new THREE.Group(); a.add(flecha);
  const haste = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.4, 10).rotateX(Math.PI / 2), M(COR.cobaltoEsc)); haste.position.z = 0.7; flecha.add(haste);
  const pena = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.3, 4).rotateX(-Math.PI / 2), M(COR.amarelo)); pena.position.z = 1.35; flecha.add(pena);
  return (t) => { const k = back((t - o.t0) / 0.5); sc(a, k); const u = easeOut((t - o.t0 - 0.5) / 0.35); flecha.position.z = 4 * (1 - u); flecha.visible = t > o.t0 + 0.5; a.rotation.y = -0.4 + Math.sin(t * 0.6) * 0.15; };
};

OBJ.termometro = ({ g, M, o, anc }) => {
  const th = new THREE.Group(); g.add(th);
  const vidro = new THREE.MeshPhysicalMaterial({ color: 0xdfe4ff, roughness: 0.05, transparent: true, opacity: 0.3 });
  const tubo = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 2.2, 24), vidro); tubo.position.y = 1.4; th.add(tubo);
  const bulbo = new THREE.Mesh(new THREE.SphereGeometry(0.36, 24, 18), M(COR.vermelho, { emissive: 0x401010, emissiveIntensity: 0.4 })); bulbo.position.y = 0.3; th.add(bulbo);
  const coluna = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 1, 20).translate(0, 0.5, 0), bulbo.material); coluna.position.y = 0.45; th.add(coluna);
  const it = o.itens || [];
  const nivel = it.length ? cl(it[it.length - 1].valor / (Math.max(...it.map((x) => x.valor)) || 1)) : 0.8;
  anc.push(new THREE.Vector3(0.45, 0, 0));
  return (t) => { const k = back((t - o.t0) / 0.5); sc(th, k); const h = Math.max(0.01, 2.0 * nivel * easeOut((t - o.t0 - 0.4) / 1.0)); coluna.scale.y = h; anc[0].set(0.45, 0.45 + h, 0); };
};

OBJ.calendario = ({ g, M, o }) => {
  const c = new THREE.Group(); c.position.y = 1.15; g.add(c);
  c.add(placa(1.7, 1.8, 0.12, 0.12, M(COR.branco)));
  const topo = placa(1.7, 0.45, 0.1, 0.13, M(COR.vermelho)); topo.position.y = 0.68; c.add(topo);
  for (const s of [-1, 1]) { const a = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.03, 8, 20), M(0xb8bcc8, { metalness: 0.8 })); a.position.set(s * 0.45, 0.92, 0.0); c.add(a); }
  const dias = [];
  for (let i = 0; i < 20; i++) { const d = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.18, 0.02), M(i === 13 ? COR.amarelo : 0xd6d9e6)); d.position.set(-0.6 + (i % 5) * 0.3, 0.25 - Math.floor(i / 5) * 0.26, 0.14); c.add(d); dias.push(d); }
  return (t) => { const k = back((t - o.t0) / 0.5); sc(c, k); c.rotation.y = -0.25 + Math.sin(t * 0.7) * 0.2; dias.forEach((d, i) => sc(d, back((t - o.t0 - 0.3 - i * 0.025) / 0.25))); };
};

OBJ.bola = ({ g, M, o }) => {
  const geo = new THREE.IcosahedronGeometry(0.9, 1).toNonIndexed();
  const cores = [], b = new THREE.Color(0xffffff), p = new THREE.Color(0x121218);
  for (let f = 0; f < geo.attributes.position.count / 3; f++) { const c = f % 4 === 0 ? p : b; for (let k = 0; k < 3; k++) cores.push(c.r, c.g, c.b); }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(cores, 3));
  const bola = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, roughness: 0.5 })); g.add(bola);
  return (t) => { const u = t - o.t0; const k = back(u / 0.4); sc(bola, k); const q = Math.abs(Math.sin(u * 3.2)) * Math.exp(-u * 0.6); bola.position.y = 0.9 + 1.2 * q; bola.rotation.x = u * 3; bola.rotation.z = u * 1.3; };
};

OBJ.escudo = ({ g, M, o }) => {
  const s = new THREE.Shape(); s.moveTo(0, 1); s.lineTo(0.85, 0.7); s.lineTo(0.75, -0.2); s.quadraticCurveTo(0.5, -0.8, 0, -1.05); s.quadraticCurveTo(-0.5, -0.8, -0.75, -0.2); s.lineTo(-0.85, 0.7); s.lineTo(0, 1);
  const e = new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth: 0.25, bevelEnabled: true, bevelThickness: 0.08, bevelSize: 0.08, bevelSegments: 4 }), M(COR.cobalto)); e.geometry.center(); e.position.y = 1.15; g.add(e);
  const ck = new THREE.Shape(); ck.moveTo(-0.38, 0.02); ck.lineTo(-0.12, -0.25); ck.lineTo(0.42, 0.32); ck.lineTo(0.32, 0.42); ck.lineTo(-0.12, -0.05); ck.lineTo(-0.28, 0.12);
  const v = new THREE.Mesh(new THREE.ExtrudeGeometry(ck, { depth: 0.08, bevelEnabled: false }), M(COR.amarelo, { emissive: 0x3a2a00, emissiveIntensity: 0.5 })); v.position.set(0, 1.15, 0.2); g.add(v);
  return (t) => { const k = back((t - o.t0) / 0.5); sc(e, k); sc(v, back((t - o.t0 - 0.5) / 0.35)); e.rotation.y = v.rotation.y = Math.sin(t * 0.8) * 0.3; };
};

export const TIPOS = Object.keys(OBJ);

export async function criarObjeto(canvas, o) {
  // o = {tipo, t0, dur, itens:[{rotulo, valor, txt}], rotulos:[elementos DOM]}
  const W = canvas.width, H = canvas.height;
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(W, H, false);
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const cena = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(32, W / H, 0.1, 100);
  cam.position.set(0, 1.7, 7.2);
  cam.lookAt(0, 0.95, 0);
  cena.add(new THREE.HemisphereLight(0xdfe4ff, 0x14141f, 1.1));
  const key = new THREE.DirectionalLight(0xfff1dc, 2.4); key.position.set(-3, 5, 4); cena.add(key);
  const rim = new THREE.DirectionalLight(0x8a95ff, 2.0); rim.position.set(4, 2, -3); cena.add(rim);
  const M = (cor, extra) => new THREE.MeshStandardMaterial({ color: cor, roughness: 0.38, metalness: 0.15, ...extra });
  const g = new THREE.Group(); cena.add(g);
  const sombra = new THREE.Mesh(new THREE.CircleGeometry(2.4, 48), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35 }));
  sombra.rotation.x = -Math.PI / 2; sombra.position.y = -0.01; g.add(sombra);
  const anc = [];
  const anima = (OBJ[o.tipo] || OBJ.planeta)({ g, M, o, anc, sombra });

  const v = new THREE.Vector3();
  function render(t) {
    g.rotation.y = -0.35 + 0.22 * Math.sin((t - o.t0) * 0.6);
    anima(t);
    renderer.render(cena, cam);
    (o.rotulos || []).forEach((el, j) => {
      const a = anc[o._ordemRot ? o._ordemRot[j] : j];
      if (!el || !a) return;
      v.copy(a).applyMatrix4(g.matrixWorld).project(cam);
      el.style.transform = `translate(${Math.round((v.x * 0.5 + 0.5) * W)}px, ${Math.round((-v.y * 0.5 + 0.5) * H)}px) translate(-50%, -100%)`;
      el.style.opacity = String(cl((t - o.t0 - 0.6 - j * 0.12) / 0.3));
    });
  }
  return { render };
}
