"""Bancada do mascote: um projeto HyperFrames curto só com ele, grande, passando por todas as poses e falando.

Uso (na raiz do repositório):
  python ferramentas/bancada_mascote.py              # gera a bancada e a folha com cada pose
  python ferramentas/bancada_mascote.py --video      # também renderiza o vídeo da bancada

Saída em ferramentas/saida_bancada/ (folha.png, quadros/, video.mp4).
"""
import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from fato.comum import MODELO, norm, npx_hf, rodar  # noqa: E402
from fato.gerar import GSAP  # noqa: E402

POSES = ["fala", "aponta", "surpreso", "pensa", "comemora", "nega"]
FRASE = "olha só que coisa incrível aconteceu hoje no Brasil e ninguém esperava".split()
SEG = 3.0


def main():
    out = RAIZ / "ferramentas" / "saida_bancada"
    proj = out / "projeto"
    if proj.exists():
        for item in proj.iterdir():
            if item.name != ".hyperframes":
                shutil.rmtree(item) if item.is_dir() else item.unlink()
    (proj / "compositions").mkdir(parents=True, exist_ok=True)
    shutil.copytree(MODELO / "assets", proj / "assets", dirs_exist_ok=True)
    shutil.copy(MODELO / "hyperframes.json", proj / "hyperframes.json")
    total = 0.6 + SEG * len(POSES) + SEG  # última parte: troca de lugar (grande -> canto)
    poses = [[0, "fala"]] + [[0.6 + i * SEG, p] for i, p in enumerate(POSES)]
    lugares = [[0, 540, 820, 2.0], [0.6 + SEG * len(POSES) + 0.5, 690, 985, 0.6]]
    palavras, t = [], 0.9
    for i in range(len(POSES) + 1):          # fala um pedaço em cada pose
        for w in FRASE[(i * 3) % 9:(i * 3) % 9 + 4]:
            d = 0.12 + 0.07 * len(w)
            vog = "".join(g[0] for g in re.findall(r"[aeiou]+", norm(w)))
            palavras.append([round(t, 3), round(t + d, 3), max(1, len(vog)), vog or "a"])
            t += d + 0.05
        t = 0.6 + SEG * (i + 1) + 0.3
    dados = json.dumps({"lugares": lugares, "poses": poses, "palavras": palavras})
    (proj / "compositions" / "mascote.html").write_text(f"""<template>
  <style>#root{{position:absolute;inset:0;}} #mascote-cv{{position:absolute;left:0;top:0;width:1080px;height:1920px;}}</style>
  <div id="root" data-composition-id="mascote" data-width="1080" data-height="1920">
    <canvas id="mascote-cv" width="1080" height="1920" data-layout-ignore></canvas>
  </div>
  <script type="module">
    import {{ criarMascote }} from "./assets/lib/mascote.js";
    const m = await criarMascote(document.getElementById("mascote-cv"), {dados});
    const tl = gsap.timeline({{ paused: true }});
    const st = {{ t: 0 }};
    tl.to(st, {{ t: {total}, duration: {total}, ease: "none", onUpdate: () => m.render(st.t) }}, 0);
    m.render(0);
    window.__timelines["mascote"] = tl;
  </script>
</template>
""", encoding="utf-8")
    (proj / "index.html").write_text(f"""<!doctype html>
<html lang="pt-BR" data-resolution="portrait"><head><meta charset="UTF-8" />{GSAP}
<style>*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:1080px;height:1920px;overflow:hidden;background:#0f0f17}}
#root{{width:100%;height:100%;position:relative;background:radial-gradient(circle at 50% 45%,#1d2250,#0f0f17 70%)}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
<div id="mascote" data-composition-id="mascote" data-composition-src="compositions/mascote.html" data-start="0" data-duration="{total}"
 data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div></div>
<script>const tl = gsap.timeline({{ paused: true }}); window.__timelines["main"] = tl;</script></body></html>
""", encoding="utf-8")
    # quadros: antecipação, pico e repouso de cada pose
    ts = []
    for i in range(len(POSES)):
        a = 0.6 + i * SEG
        ts += [a + 0.06, a + 0.35, a + 1.2, a + 2.4]
    ts += [0.6 + SEG * len(POSES) + 0.75, total - 0.3]
    quad = out / "quadros"
    if quad.exists():
        shutil.rmtree(quad)
    npx_hf("snapshot", "--at", ",".join(f"{x:.2f}" for x in ts), "--no-end", "--output", quad, cwd=proj, check=False)
    pngs = sorted(quad.glob("*.png"), key=lambda p: float(re.sub(r"[^\d.]", "", p.stem.split("at-")[-1]) or 0))
    for k, p in enumerate(pngs):
        p.rename(quad / f"q{k:02d}.png")
    rodar("ffmpeg", "-y", "-v", "error", "-i", quad / "q%02d.png", "-vf",
          "crop=1080:1080:0:300,scale=300:-1,tile=4x7:padding=6:color=0x333333", "-frames:v", "1", out / "folha.png")
    print("folha:", out / "folha.png", "| poses por linha:", ", ".join(POSES), "+ troca de lugar")
    if "--video" in sys.argv:
        npx_hf("render", "--quality", "draft", "--output", out / "video.mp4", "--quiet", cwd=proj, check=False)
        print("vídeo:", out / "video.mp4")


if __name__ == "__main__":
    main()
