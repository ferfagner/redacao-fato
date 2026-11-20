// Mascote 3D do thebestnewsbr: o quadro da logo ganha olhos, boca (a barra amarela) e braços.
// Tudo é função do tempo t (render determinístico): poses, posição, piscadas e boca vêm de dados.
import * as THREE from "./three.module.min.js";

const COR = { cobalto: 0x2a40f0, cobaltoEsc: 0x1f2fb8, branco: 0xffffff, amarelo: 0xffd60a, vermelho: 0xff5a45, tinta: 0x121218 };

// pose = ângulos em graus e ajustes do rosto
const POSES = {
  fala:     { armL: 18, armR: -18, tilt: 0, rotY: -12, lookX: 0, lookY: 0, eye: 1.0, lift: 0 },
  aponta:   { armL: 18, armR: 135, tilt: -6, rotY: -22, lookX: -0.6, lookY: 0.7, eye: 1.0, lift: 6 },
  surpreso: { armL: 70, armR: -70, tilt: 0, rotY: 0, lookX: 0, lookY: 0.2, eye: 1.35, lift: 18 },
  pensa:    { armL: 18, armR: 100, tilt: 9, rotY: -18, lookX: 0.5, lookY: 0.8, eye: 0.85, lift: 0 },
  comemora: { armL: 150, armR: -150, tilt: 0, rotY: 0, lookX: 0, lookY: 0.3, eye: 1.1, lift: 14 },
  nega:     { armL: 30, armR: -30, tilt: 0, rotY: 0, lookX: 0, lookY: -0.2, eye: 0.9, lift: 0 },
};

function arredondado(w, h, r) {
  const s = new THREE.Shape(), x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  return s;
}
function placa(w, h, r, prof, bisel, mat) {
  const g = new THREE.ExtrudeGeometry(arredondado(w, h, r), { depth: prof, bevelEnabled: true, bevelThickness: bisel, bevelSize: bisel, bevelSegments: 4, curveSegments: 10 });
  g.translate(0, 0, -prof / 2);
  return new THREE.Mesh(g, mat);
}
const lerp = (a, b, k) => a + (b - a) * k;
const suave = (k) => { k = Math.min(1, Math.max(0, k)); return k * k * (3 - 2 * k); };
const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

// valor de uma lista de chaves [[t, ...]] com transição de `dur` segundos
function chave(keys, t, dur) {
  let i = 0;
  while (i + 1 < keys.length && keys[i + 1][0] <= t) i++;
  const atual = keys[i], ant = keys[Math.max(0, i - 1)];
  const k = i === 0 ? 1 : suave((t - atual[0]) / dur);
  return { atual, ant, k, desde: t - atual[0] };
}

export async function criarMascote(canvas, dados) {
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(1080, 1920, false);
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;

  const cena = new THREE.Scene();
  const cam = new THREE.OrthographicCamera(0, 1080, 0, -1920, -2000, 2000);
  cam.position.z = 1000;
  cena.add(new THREE.AmbientLight(0xffffff, 0.55));
  const key = new THREE.DirectionalLight(0xfff1dc, 2.2); key.position.set(-0.6, 0.8, 1); cena.add(key);
  const rim = new THREE.DirectionalLight(0x8a95ff, 1.6); rim.position.set(0.9, 0.3, -0.6); cena.add(rim);

  const M = (cor, extra) => new THREE.MeshStandardMaterial({ color: cor, roughness: 0.42, metalness: 0.05, ...extra });
  const raiz = new THREE.Group(); cena.add(raiz);      // posição/escala na tela
  const corpo = new THREE.Group(); raiz.add(corpo);     // gira e respira
  corpo.add(placa(220, 220, 52, 70, 12, M(COR.cobalto)));
  const zF = 48;
  // olhos (brancos) e pupilas
  const olhos = [], pupilas = [];
  for (const sx of [-1, 1]) {
    const o = placa(44, 58, 20, 6, 3, M(COR.branco, { roughness: 0.3 }));
    o.position.set(sx * 46, 34, zF); corpo.add(o); olhos.push(o);
    const p = new THREE.Mesh(new THREE.CircleGeometry(11, 24), new THREE.MeshBasicMaterial({ color: COR.tinta }));
    p.position.set(sx * 46, 30, zF + 7); corpo.add(p); pupilas.push(p);
  }
  // boca = segunda linha da logo (barra amarela + barra branca)
  const boca = placa(104, 22, 11, 6, 2, M(COR.amarelo, { roughness: 0.35 }));
  boca.position.set(-26, -52, zF); corpo.add(boca);
  const bocaB = placa(52, 22, 11, 6, 2, M(COR.branco, { roughness: 0.35 }));
  bocaB.position.set(62, -52, zF); corpo.add(bocaB);
  // ponto de "no ar"
  const luz = new THREE.Mesh(new THREE.SphereGeometry(15, 24, 16), M(COR.vermelho, { emissive: COR.vermelho, emissiveIntensity: 0.6 }));
  luz.position.set(74, 76, zF - 4); corpo.add(luz);
  // braços: ombro -> braço -> mão
  const bracos = [];
  for (const sx of [-1, 1]) {
    const ombro = new THREE.Group(); ombro.position.set(sx * 118, -18, 34); corpo.add(ombro);
    const b = new THREE.Mesh(new THREE.CapsuleGeometry(13, 70, 6, 12), M(COR.cobaltoEsc));
    b.position.set(0, -42, 0); ombro.add(b);
    const mao = new THREE.Mesh(new THREE.SphereGeometry(20, 20, 14), M(COR.branco, { roughness: 0.35 }));
    mao.position.set(0, -90, 0); ombro.add(mao);
    bracos.push(ombro);
  }
  // sombra no chão (fica parada quando ele pula)
  const sombra = new THREE.Mesh(new THREE.CircleGeometry(100, 40), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35 }));
  sombra.scale.set(1, 0.22, 1); raiz.add(sombra);

  const poses = dados.poses, lugares = dados.lugares, palavras = dados.palavras;
  const rad = THREE.MathUtils.degToRad;

  function boca_aberta(t) {
    for (const [a, b, sil] of palavras) {
      if (t >= a && t < b) {
        const u = (t - a) / Math.max(0.05, b - a);
        return Math.abs(Math.sin(Math.PI * sil * u));
      }
    }
    return 0;
  }
  function piscada(t) {
    for (let k = 0; k < 40; k++) {
      const tb = 1.4 + k * 3.2 + hash(k) * 0.9, d = t - tb;
      if (d >= 0 && d < 0.14) return 1 - Math.sin(Math.PI * d / 0.14) * 0.92;
    }
    return 1;
  }

  function render(t) {
    // lugar na tela
    const L = chave(lugares, t, 0.45);
    const x = lerp(L.ant[1], L.atual[1], L.k), y = lerp(L.ant[2], L.atual[2], L.k), s = lerp(L.ant[3], L.atual[3], L.k);
    raiz.position.set(x, -y, 0);
    const pop = suave(t / 0.35);                        // entra com um pop no começo
    raiz.scale.setScalar(s * (0.6 + 0.4 * pop));
    raiz.visible = s > 0.01;
    // pose
    const P = chave(poses, t, 0.32);
    const a = POSES[P.ant[1]] || POSES.fala, b = POSES[P.atual[1]] || POSES.fala, k = P.k;
    const v = {}; for (const n in b) v[n] = lerp(a[n], b[n], k);
    let pulo = v.lift * Math.sin(Math.PI * Math.min(1, P.desde / 0.45)) * (P.desde < 0.45 ? 1 : 0);
    let giro = 0;
    if (P.atual[1] === "nega" && P.desde < 1.0) giro = 16 * Math.sin(P.desde * Math.PI * 6) * (1 - P.desde);
    if (P.atual[1] === "comemora") pulo += 10 * Math.abs(Math.sin(P.desde * Math.PI * 2.2));
    const resp = Math.sin(t * Math.PI * 0.9);
    corpo.position.y = pulo + resp * 3;
    corpo.scale.set(1 + resp * 0.008, 1 - resp * 0.012, 1);
    corpo.rotation.set(rad(4 + Math.sin(t * 0.7) * 2), rad(v.rotY + giro + Math.sin(t * 0.5) * 4), rad(v.tilt));
    bracos[0].rotation.z = rad(-v.armL + Math.sin(t * 1.3) * 3);
    bracos[1].rotation.z = rad(-v.armR - Math.sin(t * 1.1) * 3);
    const pis = piscada(t);
    for (let i = 0; i < 2; i++) {
      olhos[i].scale.set(1, v.eye * pis, 1);
      pupilas[i].position.x = (i ? 46 : -46) + v.lookX * 9;
      pupilas[i].position.y = 30 + v.lookY * 10;
      pupilas[i].scale.set(1, Math.max(0.1, pis), 1);
    }
    const ab = boca_aberta(t);
    boca.scale.set(1 - ab * 0.12, 1 + ab * 1.6, 1);
    boca.position.y = -52 - ab * 8;
    luz.material.emissiveIntensity = 0.4 + 0.6 * (0.5 + 0.5 * Math.sin(t * Math.PI * 2 * 0.8));
    sombra.position.set(0, -165, -60);
    sombra.material.opacity = 0.32 - Math.min(0.15, pulo / 120);
    renderer.render(cena, cam);
  }
  return { render };
}
