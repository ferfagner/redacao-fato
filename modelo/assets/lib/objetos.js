// Objetos 3D das cenas (Three.js): moedas, podio, planeta e barras. Tudo é função de t.
import * as THREE from "./three.module.min.js";

const COR = { cobalto: 0x2a40f0, cobaltoClaro: 0x8a95ff, amarelo: 0xffd60a, branco: 0xffffff, linha: 0x2e2e3d };
const cl = (k) => Math.min(1, Math.max(0, k));
const easeOut = (k) => 1 - Math.pow(1 - cl(k), 3);
const back = (k) => { k = cl(k); const c = 1.7; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };

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
  cam.lookAt(0, 0.55, 0);
  cena.add(new THREE.HemisphereLight(0xdfe4ff, 0x14141f, 1.1));
  const key = new THREE.DirectionalLight(0xfff1dc, 2.4); key.position.set(-3, 5, 4); cena.add(key);
  const rim = new THREE.DirectionalLight(0x8a95ff, 2.0); rim.position.set(4, 2, -3); cena.add(rim);
  const M = (cor, extra) => new THREE.MeshStandardMaterial({ color: cor, roughness: 0.38, metalness: 0.15, ...extra });
  const grupo = new THREE.Group(); cena.add(grupo);
  // chão: sombra suave
  const sombra = new THREE.Mesh(new THREE.CircleGeometry(2.4, 48), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35 }));
  sombra.rotation.x = -Math.PI / 2; sombra.position.y = -0.01; grupo.add(sombra);

  const itens = o.itens || [];
  const ancoras = [];   // pontos 3D onde ficam os rótulos DOM
  let anima = () => {};

  if (o.tipo === "moedas") {
    const moedas = [], n = 12;
    const geo = new THREE.CylinderGeometry(0.62, 0.62, 0.11, 48);
    const mat = M(COR.amarelo, { metalness: 0.55, roughness: 0.3, emissive: 0x3a2a00, emissiveIntensity: 0.4 });
    for (let i = 0; i < n; i++) {
      const m = new THREE.Mesh(geo, mat);
      const borda = new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.025, 8, 40), M(0xffe680, { metalness: 0.5 }));
      borda.rotation.x = Math.PI / 2; borda.position.y = 0.056; m.add(borda);
      grupo.add(m); moedas.push(m);
    }
    anima = (t) => {
      moedas.forEach((m, i) => {
        const k = easeOut((t - o.t0 - i * 0.07) / 0.35);
        m.position.set(Math.sin(i * 2.1) * 0.04, 0.06 + i * 0.115 + (1 - k) * 3.2, Math.cos(i * 1.7) * 0.04);
        m.rotation.y = i * 0.6 + t * 0.4;
        m.visible = t >= o.t0 + i * 0.07 - 0.01;
      });
    };
  } else if (o.tipo === "podio") {
    const alturas = [0.85, 1.25, 0.6], xs = [-1.15, 0, 1.15], ordem = [1, 0, 2];
    const blocos = [];
    for (let j = 0; j < 3; j++) {
      const b = new THREE.Mesh(new THREE.BoxGeometry(1.05, 1, 1.0), M(j === 1 ? COR.amarelo : COR.cobalto));
      b.position.x = xs[j]; grupo.add(b); blocos.push(b);
      const topo = new THREE.Vector3(xs[j], 0, 0); ancoras.push(topo);
    }
    anima = (t) => {
      blocos.forEach((b, j) => {
        const k = back((t - o.t0 - ordem[j] * 0.18) / 0.55);
        const h = Math.max(0.001, alturas[j] * k);
        b.scale.y = h; b.position.y = h / 2;
        ancoras[j].set(xs[j], h + 0.32, 0.5);
      });
    };
    // rótulos na ordem esquerda, centro, direita = 2º, 1º, 3º
    o._ordemRot = [1, 0, 2];
  } else if (o.tipo === "barras") {
    const vals = itens.map((x) => x.valor), vmax = Math.max(...vals) || 1, n = itens.length;
    const passo = Math.min(2.1, 4.4 / n), x0 = -passo * (n - 1) / 2;
    const barras = itens.map((it, j) => {
      const b = new THREE.Mesh(new THREE.BoxGeometry(passo * 0.62, 1, 0.7), M(it.valor === vmax ? COR.amarelo : COR.cobalto));
      b.position.x = x0 + j * passo; grupo.add(b);
      ancoras.push(new THREE.Vector3(b.position.x, 0, 0.35));
      return b;
    });
    anima = (t) => {
      barras.forEach((b, j) => {
        const alvo = 0.15 + 1.2 * vals[j] / vmax;
        const h = Math.max(0.001, alvo * easeOut((t - o.t0 - j * 0.15) / 0.8));
        b.scale.y = h; b.position.y = h / 2;
        ancoras[j].y = h + 0.14;
      });
    };
  } else { // planeta
    const p = new THREE.Mesh(new THREE.IcosahedronGeometry(1.0, 3), M(COR.cobaltoClaro, { flatShading: true, roughness: 0.6 }));
    p.position.y = 1.0; grupo.add(p);
    const anel = new THREE.Mesh(new THREE.RingGeometry(1.35, 1.75, 96), new THREE.MeshStandardMaterial({ color: COR.amarelo, side: THREE.DoubleSide, roughness: 0.4, transparent: true, opacity: 0.9 }));
    anel.rotation.x = Math.PI / 2.4; anel.position.y = 1.0; grupo.add(anel);
    const lua = new THREE.Mesh(new THREE.SphereGeometry(0.16, 24, 16), M(COR.branco));
    grupo.add(lua);
    sombra.visible = false;
    anima = (t) => {
      const k = back((t - o.t0) / 0.7);
      p.scale.setScalar(Math.max(0.001, k)); anel.scale.setScalar(Math.max(0.001, k));
      p.rotation.y = t * 0.5;
      anel.rotation.z = t * 0.15;
      const a = t * 1.3;
      lua.position.set(Math.cos(a) * 2.2, 1.0 + Math.sin(a) * 0.35, Math.sin(a) * 2.2);
      lua.visible = k > 0.5;
    };
  }

  const v = new THREE.Vector3();
  function render(t) {
    grupo.rotation.y = -0.35 + 0.22 * Math.sin((t - o.t0) * 0.6);
    anima(t);
    renderer.render(cena, cam);
    (o.rotulos || []).forEach((el, j) => {
      const idx = o._ordemRot ? o._ordemRot[j] : j;
      const a = ancoras[idx];
      if (!el || !a) return;
      v.copy(a).applyMatrix4(grupo.matrixWorld).project(cam);
      el.style.transform = `translate(${Math.round((v.x * 0.5 + 0.5) * W)}px, ${Math.round((-v.y * 0.5 + 0.5) * H)}px) translate(-50%, -100%)`;
      el.style.opacity = String(cl((t - o.t0 - 0.6 - j * 0.12) / 0.3));
    });
  }
  return { render };
}
