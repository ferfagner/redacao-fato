// Globo 3D com a imagem Blue Marble da NASA (domínio público): gira até o lugar, aproxima e marca com um pino.
import * as THREE from "./three.module.min.js";

const suave = (k) => { k = Math.min(1, Math.max(0, k)); return k * k * (3 - 2 * k); };
const easeOut = (k) => 1 - Math.pow(1 - Math.min(1, Math.max(0, k)), 3);

export async function criarGlobo(canvas, o) {
  // o = {lat, lon, t0, cx, cy, raio, textura, rotulo: elemento DOM, rotuloDx}
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(canvas.width, canvas.height, false);
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const W = canvas.width, H = canvas.height;
  const cena = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 100);
  cena.add(new THREE.AmbientLight(0xffffff, 0.35));
  const sol = new THREE.DirectionalLight(0xffffff, 2.4); sol.position.set(-1, 0.6, 1.2); cena.add(sol);

  const tex = await new THREE.TextureLoader().loadAsync(o.textura);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  const terra = new THREE.Mesh(new THREE.SphereGeometry(1, 96, 64), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.9 }));
  cena.add(terra);
  const atm = new THREE.Mesh(new THREE.SphereGeometry(1.06, 64, 48), new THREE.MeshBasicMaterial({ color: 0x2a40f0, transparent: true, opacity: 0.22, side: THREE.BackSide }));
  cena.add(atm);

  const rad = THREE.MathUtils.degToRad;
  const alvo = new THREE.Euler(rad(o.lat), -rad(o.lon) - Math.PI / 2, 0, "XYZ");
  const inicio = new THREE.Euler(rad(o.lat * 0.3), -rad(o.lon + 75) - Math.PI / 2, 0, "XYZ");
  const qA = new THREE.Quaternion().setFromEuler(alvo), qI = new THREE.Quaternion().setFromEuler(inicio);
  // pino preso ao globo, no ponto que fica de frente quando a rotação chega no alvo
  const local = new THREE.Vector3(0, 0, 1).applyQuaternion(qA.clone().invert());
  const pino = new THREE.Group(); terra.add(pino);
  pino.position.copy(local.clone().multiplyScalar(1.0));
  pino.lookAt(local.clone().multiplyScalar(2));
  const bola = new THREE.Mesh(new THREE.SphereGeometry(0.028, 20, 14), new THREE.MeshBasicMaterial({ color: 0xffd60a }));
  bola.position.z = 0.03; pino.add(bola);
  const anel = new THREE.Mesh(new THREE.RingGeometry(0.05, 0.065, 40), new THREE.MeshBasicMaterial({ color: 0xffd60a, transparent: true, side: THREE.DoubleSide }));
  anel.position.z = 0.012; pino.add(anel);

  const q = new THREE.Quaternion();
  const ponto = new THREE.Vector3();
  function render(t) {
    const u = (t - o.t0) / 1.8;
    q.copy(qI).slerp(qA, easeOut(u));
    terra.quaternion.copy(q);
    const zoom = suave((t - o.t0 - 1.2) / 1.4);
    const dist = o.d0 + (o.d1 - o.d0) * zoom;           // aproxima depois de girar
    cam.position.set(0, 0, dist);
    cam.lookAt(0, 0, 0);
    cam.setViewOffset(W, H, W / 2 - o.cx, H / 2 - o.cy, W, H);
    const vp = suave((t - o.t0 - 1.5) / 0.4);           // pino aparece
    pino.scale.setScalar(Math.max(0.001, vp));
    const pulso = ((t - o.t0) * 0.9) % 1;
    anel.scale.setScalar(1 + pulso * 1.8);
    anel.material.opacity = (1 - pulso) * vp;
    renderer.render(cena, cam);
    if (o.rotulo) {
      bola.getWorldPosition(ponto).project(cam);
      const px = (ponto.x * 0.5 + 0.5) * W, py = (-ponto.y * 0.5 + 0.5) * H;
      o.rotulo.style.transform = `translate(${Math.round(px + (o.rotuloDx || 28))}px, ${Math.round(py - 30)}px)`;
      o.rotulo.style.opacity = String(suave((t - o.t0 - 1.7) / 0.3));
    }
  }
  return { render };
}
