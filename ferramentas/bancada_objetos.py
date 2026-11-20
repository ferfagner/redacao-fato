"""Bancada do acervo de objetos 3D: mostra cada objeto do objetos.js já animado, numa folha só.

Uso (na raiz do repositório):
  python ferramentas/bancada_objetos.py            # objetos desenhados em código
  python ferramentas/bancada_objetos.py --modelos  # modelos realistas (.glb)
Saída: ferramentas/saida_objetos/folha.png (ou folha_modelos.png)
"""
import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from fato.comum import MODELO, OBJETOS_3D, modelos_reais, npx_hf, rodar  # noqa: E402
from fato.gerar import GSAP  # noqa: E402

SEG = 2.6
ITENS = [{"rotulo": "2019", "valor": 30, "txt": "30%"}, {"rotulo": "2021", "valor": 45, "txt": "45%"},
         {"rotulo": "2023", "valor": 38, "txt": "38%"}, {"rotulo": "2025", "valor": 62, "txt": "62%"}]


def projeto(dest: Path, tipos):
    if dest.exists():
        for item in dest.iterdir():
            if item.name != ".hyperframes":
                shutil.rmtree(item) if item.is_dir() else item.unlink()
    (dest / "compositions").mkdir(parents=True, exist_ok=True)
    shutil.copytree(MODELO / "assets", dest / "assets", dirs_exist_ok=True, ignore=shutil.ignore_patterns("modelos3d"))
    (dest / "assets" / "modelos3d").mkdir(exist_ok=True)
    for tp in tipos:
        if tp.startswith("modelo:"):
            shutil.copy(MODELO / "assets" / "modelos3d" / f"{tp[7:]}.glb", dest / "assets" / "modelos3d")
    shutil.copy(MODELO / "hyperframes.json", dest / "hyperframes.json")
    hosts = []
    for i, tipo in enumerate(tipos):
        cid = f"o{i:02d}"
        itens = ITENS[:3] if tipo == "podio" else ITENS
        dados = json.dumps({"tipo": tipo, "t0": 0.1, "dur": SEG, "itens": itens, "n_rotulos": 0})
        (dest / "compositions" / f"{cid}.html").write_text(f"""<template>
  <style>#root{{position:absolute;inset:0;background:#0f0f17;}} #{cid}-cv{{position:absolute;left:120px;top:500px;}}
  .nm{{position:absolute;left:0;width:1080px;top:380px;text-align:center;font:900 64px 'Archivo Black',sans-serif;color:#ffd60a;}}</style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div class="nm">{tipo.replace("modelo:", "").upper()}</div>
    <canvas id="{cid}-cv" width="840" height="470" data-layout-ignore></canvas>
  </div>
  <script type="module">
    import {{ criarObjeto }} from "./assets/lib/objetos.js";
    const o = {dados};
    const g = await criarObjeto(document.getElementById("{cid}-cv"), o);
    const tl = gsap.timeline({{ paused: true }});
    const st = {{ t: 0 }};
    tl.to(st, {{ t: o.dur, duration: o.dur, ease: "none", onUpdate: () => g.render(st.t) }}, 0);
    g.render(0);
    window.__timelines["{cid}"] = tl;
  </script>
</template>
""", encoding="utf-8")
        hosts.append(f'<div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{i * SEG}" '
                     f'data-duration="{SEG}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>')
    total = SEG * len(tipos)
    (dest / "index.html").write_text(f"""<!doctype html><html lang="pt-BR" data-resolution="portrait"><head><meta charset="UTF-8" />{GSAP}
<style>*{{margin:0;padding:0}} html,body{{width:1080px;height:1920px;overflow:hidden;background:#0f0f17}} #root{{width:100%;height:100%;position:relative}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">{''.join(hosts)}</div>
<script>const tl = gsap.timeline({{ paused: true }}); window.__timelines["main"] = tl;</script></body></html>""", encoding="utf-8")
    return [round(i * SEG + 1.9, 2) for i in range(len(tipos))]


def main():
    out = RAIZ / "ferramentas" / "saida_objetos"
    quad = out / ("quadros_modelos" if "--modelos" in sys.argv else "quadros")
    if quad.exists():
        shutil.rmtree(quad)
    quad.mkdir(parents=True)
    modelos = "--modelos" in sys.argv
    tipos, n = ([f"modelo:{m}" for m in modelos_reais()] if modelos else list(OBJETOS_3D)), 0
    for lote in range(0, len(tipos), 9):          # até 9 objetos 3D por página (limite de contextos WebGL)
        dest = out / f"lote{lote // 9}{'m' if modelos else ''}"
        ts = projeto(dest, tipos[lote:lote + 9])
        snap = out / f"snap{lote // 9}{'m' if modelos else ''}"
        if snap.exists():
            shutil.rmtree(snap)
        npx_hf("snapshot", "--at", ",".join(map(str, ts)), "--no-end", "--output", snap, cwd=dest, check=False)
        for p in sorted(snap.glob("*.png"), key=lambda p: float(re.sub(r"[^\d.]", "", p.stem.split("at-")[-1]) or 0)):
            p.rename(quad / f"q{n:02d}.png"); n += 1
    rodar("ffmpeg", "-y", "-v", "error", "-i", quad / "q%02d.png", "-vf",
          f"crop=1080:760:0:340,scale=216:-1,tile=7x{(n + 6) // 7}:padding=6:color=0x333333", "-frames:v", "1",
          out / ("folha_modelos.png" if modelos else "folha.png"))
    print("folha:", out / ("folha_modelos.png" if modelos else "folha.png"), f"({n} objetos)")


if __name__ == "__main__":
    main()
