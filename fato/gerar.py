"""Monta o projeto HyperFrames a partir das cenas, dos tempos e da narração."""
import json
import re
import shutil
from pathlib import Path

from .comum import MODELO, norm
from .familias import FUNCOES, esc, js_destaque, placa_fonte
from .mapas import GLOBO_JS, OBJETO_JS, mapa_brasil, mapa_lugar

from .cartoes import CARTOES  # noqa: E402
from .fotos import tratar  # noqa: E402
from . import broll  # noqa: E402
from .narrar import NUMEROS  # noqa: E402

AVISOS = []   # avisos da montagem (ex.: recorte de foto que falhou)

TODAS = dict(FUNCOES, mapa_brasil=mapa_brasil, mapa_lugar=mapa_lugar, **CARTOES)

GSAP = '<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>'

TOKENS = """
:root{--papel:#0f0f17;--elevado:#1a1a26;--linha:#2e2e3d;--tinta:#f4f3ef;--tinta-suave:#a6a5b2;
--cobalto:#2a40f0;--on-cobalto:#ffffff;--cobalto-texto:#8a95ff;--amarelo:#ffd60a;--on-amarelo:#121218;--placa:#121218;}
"""

CSS_CENA = """
#root{position:absolute;inset:0;font-family:'Archivo Black',sans-serif;color:var(--tinta);}
.wrap{position:absolute;inset:0;}
.tit{text-transform:uppercase;letter-spacing:-0.01em;text-align:center;}
.tit .ln{display:block;}
.w{display:inline-block;}
.hl{color:var(--amarelo);}
.hlbox{background:var(--amarelo);color:var(--on-amarelo);border-radius:4px;padding:0 .12em;}
.rot{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:30px;letter-spacing:.12em;color:var(--cobalto-texto);text-align:center;margin-bottom:28px;}
.centro{position:absolute;left:120px;width:840px;top:285px;height:545px;display:flex;flex-direction:column;justify-content:center;align-items:center;}
.col{position:absolute;left:120px;width:840px;top:300px;display:flex;flex-direction:column;align-items:center;}
.col.topo{top:300px;}
.barra{width:200px;height:12px;border-radius:4px;background:var(--amarelo);margin-top:36px;transform-origin:left center;}
.selo{display:inline-block;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:28px;letter-spacing:.14em;background:var(--amarelo);color:var(--on-amarelo);border-radius:4px;padding:6px 14px;margin-bottom:30px;}
.gancho .tit{text-align:left;}
.gancho{transform-origin:center top;}
.numwrap{position:relative;width:840px;height:260px;display:flex;align-items:center;justify-content:center;}
.arco{position:absolute;width:260px;height:260px;left:290px;top:0;}
.aro{fill:none;stroke:var(--linha);stroke-width:6;}
.aroc{fill:none;stroke:var(--cobalto);stroke-width:10;stroke-linecap:round;stroke-dasharray:1760;}
.num{position:relative;color:var(--amarelo);line-height:1;letter-spacing:-0.03em;white-space:nowrap;}
.uni{font-size:40px;text-transform:uppercase;color:var(--tinta);margin-top:6px;text-align:center;}
.lista{width:840px;margin-top:40px;display:flex;flex-direction:column;gap:22px;}
.itopo{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;}
.irot{font-size:30px;text-transform:uppercase;color:var(--tinta-suave);}
.trilho{width:100%;height:44px;border-radius:8px;background:var(--linha);overflow:hidden;}
.fill{height:100%;border-radius:8px;transform-origin:left center;}
.ival{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:36px;color:var(--tinta);}
.palco{position:absolute;left:120px;width:840px;top:470px;height:360px;perspective:1200px;}
.obj{position:absolute;left:420px;top:180px;width:0;height:0;transform-style:preserve-3d;}
.anel{position:absolute;border-radius:50%;border:3px solid var(--cobalto-texto);}
.anel.mer{width:320px;height:320px;margin:-160px 0 0 -160px;}
.anel.par{border-color:var(--cobalto);}
.face{position:absolute;width:280px;height:280px;margin:-140px 0 0 -140px;border:4px solid var(--amarelo);background:rgba(42,64,240,.18);border-radius:8px;}
.card{position:absolute;left:120px;width:840px;top:300px;padding:44px 48px 44px;background:var(--elevado);border-radius:16px;border:2px solid var(--linha);}
.aspas{font-size:160px;line-height:.6;height:70px;color:var(--amarelo);}
.quem{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:30px;letter-spacing:.08em;color:var(--cobalto-texto);margin-top:36px;}
.cta{margin-top:44px;background:var(--cobalto);color:var(--on-cobalto);border-radius:8px;padding:22px 36px;font-size:40px;text-transform:uppercase;text-align:center;}
.logo{margin-top:56px;display:flex;align-items:center;gap:6px;font-size:48px;}
.logo img{width:80px;height:80px;margin-right:18px;}
.logo .news{background:var(--amarelo);color:var(--on-amarelo);border-radius:4px;padding:0 .1em;}
.logo .br{color:var(--cobalto-texto);}
.fonte{position:absolute;left:120px;top:868px;background:var(--placa);border:2px solid var(--linha);border-radius:8px;padding:12px 20px;
  font-family:'JetBrains Mono',monospace;font-weight:500;font-size:28px;letter-spacing:.04em;color:var(--tinta);}
.fonte .fk{color:var(--amarelo);font-weight:700;margin-right:8px;}
.pz{position:absolute;inset:0;transform-origin:540px 430px;}
.palco3d{position:absolute;inset:0;perspective:1600px;perspective-origin:540px 560px;transform-origin:540px 430px;}
.c3d{position:absolute;inset:0;transform-style:preserve-3d;transform-origin:540px 560px;}
.painel{position:absolute;left:84px;width:912px;top:262px;height:590px;border-radius:24px;overflow:hidden;
  background:linear-gradient(160deg,rgba(42,64,240,.22),rgba(26,26,38,.80) 45%,rgba(15,15,23,.88));
  border:2px solid rgba(138,149,255,.35);box-shadow:0 40px 90px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.14);}
.brilho{position:absolute;top:-20%;left:0;width:30%;height:140%;
  background:linear-gradient(100deg,rgba(255,255,255,0),rgba(255,255,255,.10),rgba(255,255,255,0));}
.glbox{position:absolute;}
.painel.vidro{background:linear-gradient(160deg,rgba(42,64,240,.34),rgba(15,15,23,.50) 50%,rgba(15,15,23,.62));-webkit-backdrop-filter:blur(18px) saturate(1.25);backdrop-filter:blur(18px) saturate(1.25);border-color:rgba(255,255,255,.22);}
.c3d .col,.c3d .centro,.c3d .palco,.c3d .glbox{transform:translateZ(60px);}
"""

FMT_JS = ("function fmt(v,c){const s=v.toFixed(c);const [i,d]=s.split('.');"
          "const m=i.replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.');return d?m+','+d:m;}\n")


def _cena_html(cid, s, tempo):
    p = cid
    dur = round(tempo["fim"] - tempo["ini"], 3)
    r = TODAS[s["familia"]](p, s, tempo["ancora"], dur)
    corpo, css, js = r[:3]
    modulo = r[3] if len(r) > 3 else None
    fon_html, fon_js = placa_fonte(p, s.get("fonte"))
    js += fon_js + js_destaque(p, tempo["destaque"])
    # cartão 3D: o conteúdo entra girando em perspectiva e depois flutua até o fim da cena
    painel = s["id"] != 1 and s["familia"] != "citacao_fonte"
    corpo = (f'<div id="{p}-pz" class="pz"><div id="{p}-cam" class="palco3d"><div id="{p}-c3d" class="c3d">'
             + (f'<div class="painel{" vidro" if s.get("broll") else ""}"><div id="{p}-brilho" class="brilho"></div></div>' if painel else "")
             + corpo + '</div></div></div>')
    # câmera: aproxima devagar a cena inteira (nunca fica parado)
    js += f'tl.fromTo("#{p}-cam", {{scale: 1}}, {{scale: 1.06, duration: {dur:.2f}, ease: "none"}}, 0);\n'
    # batidas: "soco" de zoom nas palavras fortes da fala, a cada ~2 s
    for bt in tempo.get("batidas", []):
        js += (f'tl.to("#{p}-pz", {{scale: 1.045, duration: 0.09, ease: "power2.out"}}, {bt:.3f});'
               f'tl.to("#{p}-pz", {{scale: 1, duration: 0.32, ease: "power2.inOut"}}, {bt + 0.09:.3f});\n')
    lado = -1 if s["id"] % 2 else 1
    if s["id"] == 1:   # o gancho já está na tela no quadro 0 (é a capa)
        js += f'tl.fromTo("#{p}-c3d", {{rotationY: -14, rotationX: 8}}, {{rotationY: 0, rotationX: 0, duration: 0.9, ease: "power3.out"}}, 0);\n'
    else:
        js += (f'tl.fromTo("#{p}-c3d", {{rotationY: {32 * lado}, rotationX: 8, z: -120, opacity: 0}}, '
               f'{{rotationY: 0, rotationX: 0, z: 0, opacity: 1, duration: 0.65, ease: "power3.out"}}, 0);\n')
        # transição em chicote: entra de lado com borrão de movimento
        js += (f'tl.fromTo("#{p}-pz", {{x: {260 * lado}, filter: "blur(14px)"}}, '
               f'{{x: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out"}}, 0);\n')
    ti =0.9 if s["id"] == 1 else 0.65
    js += (f'tl.to("#{p}-c3d", {{rotationY: {-5 * lado}, rotationX: 2, duration: {max(0.5, dur - ti - 0.3):.2f}, '
           f'ease: "sine.inOut"}}, {ti});\n')
    if painel:
        js += f'tl.fromTo("#{p}-brilho", {{xPercent: -120}}, {{xPercent: 420, duration: 1.1, ease: "power2.inOut"}}, 0.35);\n'
    # saída: o cartão é empurrado para o lado do próximo e some (a próxima cena entra por cima)
    js += (f'tl.fromTo("#{p}-pz", {{x: 0, filter: "blur(0px)"}}, {{x: {-260 * lado}, filter: "blur(14px)", duration: 0.24, '
           f'ease: "power2.in", immediateRender: false}}, {max(0.3, dur - 0.24):.3f});\n')
    js += f'tl.fromTo("#{p}-wrap", {{opacity: 1}}, {{opacity: 0, duration: 0.2, ease: "power1.in", immediateRender: false}}, {max(0.3, dur - 0.22):.3f});\n'
    extra, tipo = "", ""
    if modulo is not None:  # cena com Three.js: módulo, registra o timeline depois de carregar
        tipo = ' type="module"'
        extra = (OBJETO_JS if modulo.get("_js") == "objeto" else GLOBO_JS).format(dados=json.dumps(modulo), p=p)
    return f"""<template>
  <style>{TOKENS}{CSS_CENA}{css}</style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{p}-wrap" class="wrap">{corpo}{fon_html}</div>
  </div>
  <script{tipo}>
    {FMT_JS}
    const tl = gsap.timeline({{ paused: true }});
    {js}
    {extra}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


def _mascote_html(cenas, tempos, narr):
    """Mascote em cima das cenas e embaixo da legenda: lugar e pose por cena, boca pela fala."""
    total = narr["total"]
    lugares, poses = [], []
    padrao = {"numero_heroi": "aponta", "dado_comparado": "aponta", "mapa_brasil": "aponta", "mapa_lugar": "aponta",
              "citacao_fonte": "pensa", "objeto_profundidade": "fala", "tipo_cinetico": "fala", "foto": "aponta",
              "lista_cards": "aponta", "versus": "surpreso", "linha_tempo": "pensa", "antes_depois": "aponta"}
    for i, (s, tp) in enumerate(zip(cenas, tempos)):
        if i == 0:
            lugar = [0, 540, 850, 0.95]           # grande, embaixo da caixa do gancho
            pose = "surpreso"
        elif i == len(cenas) - 1:
            lugar = [tp["ini"], 540, 975, 0.72]    # fecho
            pose = "comemora"
        else:
            lugar = [tp["ini"], 735, 998, 0.62]    # canto, entre a placa da fonte e a legenda
            pose = padrao.get(s["familia"], "fala")
        pose = (s.get("personagem") or {}).get("pose", pose)
        if not lugares or lugares[-1][1:] != lugar[1:]:
            lugares.append(lugar)
        poses.append([round(tp["ini"] + max(0, tp["ancora"] - 0.1), 3) if i else 0, pose])
    pal = []
    for w in narr["palavras"]:   # [ini, fim, sílabas, vogais] — a boca toma a forma de cada vogal
        vog = "".join(g[0] for g in re.findall(r"[aeiou]+", norm(w["texto"])))
        pal.append([w["ini"], w["fim"], max(1, min(5, len(vog))), vog[:5] or "a"])
    dados = json.dumps({"lugares": lugares, "poses": poses, "palavras": pal})
    return f"""<template>
  <style>
    #root{{position:absolute;inset:0;}}
    #mascote-cv{{position:absolute;left:0;top:0;width:1080px;height:1920px;}}
  </style>
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
"""


def _grupos_legenda(pals, max_pal=5, max_chars=26):
    grupos, atual = [], []
    for k, p in enumerate(pals):
        if atual:
            cand = " ".join(x["texto"] for x in atual + [p])
            pausa = p["ini"] - atual[-1]["fim"]
            if len(atual) >= max_pal or len(cand) > max_chars or (pausa >= 0.15 and len(atual) >= 3) or atual[-1]["bloco"] != p["bloco"]:
                grupos.append(atual); atual = []
        atual.append(p)
        if p["texto"].endswith((".", "!", "?", "…", ":", ";")):
            grupos.append(atual); atual = []
    if atual:
        grupos.append(atual)
    return grupos


def _legenda_html(grupos, total, chaves=None):
    divs, js = [], []
    for g, ws in enumerate(grupos):
        ini = ws[0]["ini"] - 0.05
        fim = grupos[g + 1][0]["ini"] - 0.06 if g + 1 < len(grupos) else min(total - 0.1, ws[-1]["fim"] + 0.6)
        fim = max(fim, ws[-1]["fim"])
        if g + 1 < len(grupos):  # nunca dois grupos na tela: sai antes do próximo entrar
            fim = min(fim, grupos[g + 1][0]["ini"] - 0.051)
        spans = []
        # no máximo uma palavra-chave por linha: a de destaque da cena; senão, o número mais longo
        destaques, numeros = chaves if chaves else (set(), set())
        cand = [k for k, w in enumerate(ws) if norm(w["texto"]) in destaques] or \
               sorted((k for k, w in enumerate(ws) if norm(w["texto"]) in numeros), key=lambda k: -len(ws[k]["texto"]))
        escolhida = cand[0] if cand else None
        for k, w in enumerate(ws):
            prox = ws[k + 1]["ini"] if k + 1 < len(ws) else fim
            if k == escolhida:   # palavra-chave: caixa amarela entra quando é falada, texto fica escuro
                spans.append(f'<span id="lg{g}-{k}" class="lw chave"><span id="lg{g}-{k}-bx" class="cbx"></span>'
                             f'<span id="lg{g}-{k}-t" class="ct">{esc(w["texto"])}</span></span>')
                js.append(f'tl.set("#lg{g}-{k}-bx", {{scaleX: 0, rotation: -2}}, 0);'
                          f'tl.fromTo("#lg{g}-{k}-bx", {{scaleX: 0, rotation: -2}}, {{scaleX: 1, rotation: -2, duration: 0.12, ease: "power2.out", immediateRender: false}}, {w["ini"]:.3f});'
                          f'tl.set("#lg{g}-{k}-t", {{color: "#121218"}}, {w["ini"] + 0.04:.3f});')
                vai = min(0.08, (prox - w["ini"]) * 0.4)
                volta = min(0.2, prox - w["ini"] - vai - 0.01)
                if vai > 0.03 and volta > 0.03:
                    js.append(f'tl.fromTo("#lg{g}-{k}", {{scale: 1}}, {{scale: 1.16, duration: {vai:.3f}, ease: "power2.out", immediateRender: false}}, {w["ini"]:.3f});'
                              f'tl.to("#lg{g}-{k}", {{scale: 1.06, duration: {volta:.3f}, ease: "power2.inOut"}}, {w["ini"] + vai:.3f});')
                continue
            spans.append(f'<span id="lg{g}-{k}" class="lw">{esc(w["texto"])}</span>')
            # palavra falada: acende em amarelo e dá um "pulo" de escala (legenda cinética)
            js.append(f'tl.set("#lg{g}-{k}", {{color: "#ffd60a"}}, {w["ini"]:.3f});'
                      f'tl.set("#lg{g}-{k}", {{color: "#ffffff"}}, {prox:.3f});')
            vai = min(0.08, (prox - w["ini"]) * 0.4)
            volta = min(0.2, prox - w["ini"] - vai - 0.01)
            if vai > 0.03 and volta > 0.03:   # o pulinho termina antes da próxima palavra
                js.append(f'tl.fromTo("#lg{g}-{k}", {{scale: 1}}, {{scale: 1.1, duration: {vai:.3f}, ease: "power2.out", immediateRender: false}}, {w["ini"]:.3f});'
                          f'tl.to("#lg{g}-{k}", {{scale: 1, duration: {volta:.3f}, ease: "power2.inOut"}}, {w["ini"] + vai:.3f});')
        divs.append(f'<div id="lg{g}" class="grupo"><div id="lg{g}-in" class="gin">{" ".join(spans)}</div></div>')
        js.append(f'tl.set("#lg{g}", {{opacity: 1, visibility: "visible"}}, {ini:.3f});'
                  f'tl.fromTo("#lg{g}-in", {{y: 26, scale: 0.86}}, {{y: 0, scale: 1, duration: 0.16, ease: "back.out(2.2)", immediateRender: false}}, {ini:.3f});'
                  f'tl.set("#lg{g}", {{opacity: 0, visibility: "hidden"}}, {fim:.3f});')
    grupos_html = "".join(divs)
    return f"""<template>
  <style>
    @font-face{{font-family:'Archivo Narrow';src:url('assets/fonts/ArchivoNarrow-Bold.woff2') format('woff2');font-weight:700;}}
    #root{{position:absolute;inset:0;}}
    /* centralizada no quadro, perto do pé da tela (base em y = 1600), por escolha do dono */
    .grupo{{position:absolute;left:150px;width:780px;bottom:320px;text-align:center;opacity:0;visibility:hidden;
      font-family:'Archivo Narrow',sans-serif;font-weight:700;font-size:68px;line-height:76px;text-transform:uppercase;
      color:#ffffff;-webkit-text-stroke:12px #000000;paint-order:stroke fill;}}
    .gin{{transform-origin:50% 100%;}}
    .lw{{display:inline-block;transform-origin:50% 80%;margin:0 .05em;}}
    .chave{{position:relative;color:#ffd60a;padding:0 .1em;}}
    .chave .cbx{{position:absolute;left:0;right:0;top:4px;bottom:2px;background:#ffd60a;border-radius:8px;transform-origin:0 50%;
      box-shadow:0 6px 0 #000;}}
    .chave .ct{{position:relative;-webkit-text-stroke:0;}}
  </style>
  <div id="root" data-composition-id="legenda" data-width="1080" data-height="1920">
    {grupos_html}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join(js)}
    window.__timelines["legenda"] = tl;
  </script>
</template>
""", [(" ".join(w["texto"] for w in ws), ws[0]["ini"], ws[-1]["fim"]) for ws in grupos]


def _fundo_html(total):
    return f"""<template>
  <style>{TOKENS}
    #root{{position:absolute;inset:0;background:var(--papel);overflow:hidden;}}
    #fundo-grade{{position:absolute;left:-90px;top:-90px;width:1260px;height:2200px;
      background-image:linear-gradient(var(--linha) 2px,transparent 2px),linear-gradient(90deg,var(--linha) 2px,transparent 2px);
      background-size:90px 90px;opacity:.45;}}
    #fundo-luz{{position:absolute;left:-300px;top:200px;width:1700px;height:1700px;border-radius:50%;
      background:radial-gradient(circle,rgba(42,64,240,.38) 0%,rgba(42,64,240,.10) 38%,rgba(15,15,23,0) 70%);}}
    #fundo-vinheta{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,rgba(15,15,23,0) 45%,rgba(8,8,12,.85) 100%);}}
  </style>
  <div id="root" data-composition-id="fundo" data-width="1080" data-height="1920">
    <div id="fundo-grade"></div><div id="fundo-luz"></div><div id="fundo-vinheta"></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#fundo-grade", {{y: 0}}, {{y: 90 * {max(1, round(total / 6))}, duration: {total}, ease: "none"}}, 0);
    tl.fromTo("#fundo-luz", {{x: -120, y: -80}}, {{x: 160, y: 260, duration: {total}, ease: "sine.inOut"}}, 0);
    window.__timelines["fundo"] = tl;
  </script>
</template>
"""


def _moldura_html(total):
    return f"""<template>
  <style>{TOKENS}
    #root{{position:absolute;inset:0;}}
    #moldura-trilho{{position:absolute;left:120px;width:840px;top:232px;height:6px;border-radius:3px;background:var(--linha);}}
    #moldura-barra{{position:absolute;left:120px;width:840px;top:232px;height:6px;border-radius:3px;background:var(--amarelo);transform-origin:left center;}}
  </style>
  <div id="root" data-composition-id="moldura" data-width="1080" data-height="1920">
    <div id="moldura-trilho"></div><div id="moldura-barra"></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#moldura-barra", {{scaleX: 0}}, {{scaleX: 1, duration: {total}, ease: "none"}}, 0);
    window.__timelines["moldura"] = tl;
  </script>
</template>
"""


def _efeitos_html(total, limites):
    """Camada por cima das cenas: granulado de filme o tempo todo e um efeito em cada troca de cena
    (alterna flash, vazamento de luz e glitch). Tudo no timeline, então é igual em qualquer quadro."""
    js = []
    # granulado: a textura pula de posição 12 vezes por segundo (sorteio fixo, sem Math.random)
    passo, k, semente = 1 / 12, 0, 7
    while k * passo < total:
        semente = (semente * 1103515245 + 12345) % 2147483648
        x, y = semente % 200 - 100, (semente // 200) % 200 - 100
        js.append(f'tl.set("#ef-grao", {{x: {x}, y: {y}}}, {k * passo:.3f});')
        k += 1
    for n, t in enumerate(limites):
        tipo = n % 3
        if tipo == 0:     # flash rápido
            js.append(f'tl.fromTo("#ef-flash", {{opacity: 0}}, {{opacity: 0.55, duration: 0.06, ease: "power1.out", immediateRender: false}}, {max(0, t - 0.04):.3f});'
                      f'tl.to("#ef-flash", {{opacity: 0, duration: 0.22, ease: "power2.in"}}, {t + 0.02:.3f});')
        elif tipo == 1:   # vazamento de luz nas cores da marca
            js.append(f'tl.fromTo("#ef-luz", {{opacity: 0, xPercent: -30}}, {{opacity: 0.85, xPercent: 0, duration: 0.25, ease: "sine.out", immediateRender: false}}, {max(0, t - 0.15):.3f});'
                      f'tl.to("#ef-luz", {{opacity: 0, xPercent: 25, duration: 0.5, ease: "sine.in"}}, {t + 0.1:.3f});')
        else:             # glitch: faixas coloridas deslocadas por poucos quadros
            for q, dx in enumerate((38, -54, 22, 0)):
                js.append(f'tl.set("#ef-glitch", {{opacity: {0 if dx == 0 else 1}, x: {dx}}}, {t - 0.06 + q * 0.045:.3f});')
    return f"""<template>
  <style>
    #root{{position:absolute;inset:0;overflow:hidden;pointer-events:none;}}
    #ef-grao{{position:absolute;left:-150px;top:-150px;width:1380px;height:2220px;opacity:.10;mix-blend-mode:overlay;
      background:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");}}
    #ef-vinheta{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,rgba(0,0,0,0) 55%,rgba(0,0,0,.45) 100%);}}
    #ef-flash{{position:absolute;inset:0;background:#ffffff;opacity:0;}}
    #ef-luz{{position:absolute;inset:-20%;opacity:0;mix-blend-mode:screen;filter:blur(30px);
      background:radial-gradient(ellipse 45% 60% at 20% 40%,rgba(255,214,10,.85),transparent 60%),
                 radial-gradient(ellipse 50% 70% at 80% 60%,rgba(42,64,240,.9),transparent 65%);}}
    #ef-glitch{{position:absolute;inset:0;opacity:0;mix-blend-mode:screen;
      background:linear-gradient(transparent 22%,rgba(0,255,240,.35) 22%,rgba(0,255,240,.35) 26%,transparent 26%,
        transparent 51%,rgba(255,0,140,.35) 51%,rgba(255,0,140,.35) 57%,transparent 57%,
        transparent 74%,rgba(255,214,10,.30) 74%,rgba(255,214,10,.30) 76%,transparent 76%);}}
  </style>
  <div id="root" data-composition-id="efeitos" data-width="1080" data-height="1920">
    <div id="ef-vinheta"></div><div id="ef-luz"></div><div id="ef-glitch"></div><div id="ef-flash"></div><div id="ef-grao"></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.set("#ef-grao", {{x: 0}}, 0);
    {chr(10).join(js)}
    tl.to({{}}, {{duration: {total}}}, 0);
    window.__timelines["efeitos"] = tl;
  </script>
</template>
"""


def _srt(linhas):
    def t(s):
        ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000)
        return f"{h:02}:{m:02}:{s_:02},{ms:03}"
    out = []
    for n, (txt, a, b) in enumerate(linhas, 1):
        out += [str(n), f"{t(a)} --> {t(b)}", txt, ""]
    return "\n".join(out)


def gerar(projeto: Path, cenas, tempos, narr, wav: Path, titulo="", pasta: Path = None):
    # limpa o conteúdo, mas não a pasta: o `hyperframes check` deixa um processo aquecido usando ela
    projeto.mkdir(parents=True, exist_ok=True)
    for item in projeto.iterdir():
        if item.name == ".hyperframes":
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    (projeto / "compositions").mkdir(parents=True)
    # o acervo de modelos realistas é grande: copia só os que esta pauta usa
    shutil.copytree(MODELO / "assets", projeto / "assets", ignore=shutil.ignore_patterns("modelos3d"))
    (projeto / "assets" / "modelos3d").mkdir(exist_ok=True)
    for s_ in cenas:
        ob = str(s_.get("objeto", ""))
        if ob.startswith("modelo:"):
            shutil.copy(MODELO / "assets" / "modelos3d" / f"{ob[7:]}.glb", projeto / "assets" / "modelos3d" / f"{ob[7:]}.glb")
    shutil.copy(MODELO / "hyperframes.json", projeto / "hyperframes.json")
    shutil.copy(wav, projeto / "assets" / "narracao.wav")
    total = narr["total"]
    hosts = []

    def host(cid, ini, dur, z, kind="graphics", faixa=1):
        hosts.append(f'<div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
                     f'data-start="{ini}" data-duration="{dur}" data-track-index="{faixa}" data-track-kind="{kind}" '
                     f'data-width="1080" data-height="1920" style="z-index:{z}"></div>')

    (projeto / "compositions" / "fundo.html").write_text(_fundo_html(total), encoding="utf-8")
    host("fundo", 0, total, 1, faixa=0)
    for s, tp in zip(cenas, tempos):
        cid = f"c{s['id']:02d}"
        if s["familia"] == "foto" and pasta is not None:   # a foto vai para dentro do projeto
            orig = (pasta / s["imagem"]["arquivo"]).resolve()
            nome_arq, trat, aviso = tratar(orig, projeto / "assets" / "fotos", cid,
                                           s["imagem"].get("tratamento", "natural"), cwd=projeto)
            if aviso:
                AVISOS.append(f"cena {s['id']}: {aviso}")
            s = dict(s, _foto_src=f"assets/fotos/{nome_arq}", _tratamento=trat)
        (projeto / "compositions" / f"{cid}.html").write_text(_cena_html(cid, s, tp), encoding="utf-8")
        host(cid, tp["ini"], round(tp["fim"] - tp["ini"], 3), 4, faixa=1)
    (projeto / "compositions" / "mascote.html").write_text(_mascote_html(cenas, tempos, narr), encoding="utf-8")
    host("mascote", 0, total, 5, faixa=5)
    limites = [tp["ini"] for tp in tempos[1:]]
    (projeto / "compositions" / "efeitos.html").write_text(_efeitos_html(total, limites), encoding="utf-8")
    host("efeitos", 0, total, 6, faixa=8)
    # palavras-chave da legenda: números falados e as palavras de destaque das cenas
    destaques = {norm(w) for s_ in cenas for w in str(s_.get("destaque", "")).split() if not w.isdigit()}
    numeros = set(NUMEROS) - {"um", "uma"}
    leg_html, leg_linhas = _legenda_html(_grupos_legenda(narr["palavras"]), total, (destaques, numeros))
    (projeto / "compositions" / "legenda.html").write_text(leg_html, encoding="utf-8")
    host("legenda", 0, total, 7, kind="captions", faixa=2)
    (projeto / "compositions" / "moldura.html").write_text(_moldura_html(total), encoding="utf-8")
    host("moldura", 0, total, 8, faixa=3)
    hosts_txt = "\n      ".join(hosts)
    # vídeo de fundo (b-roll): fica embaixo das cenas, com um véu escuro para o texto continuar legível
    trechos = broll.preparar(pasta, projeto, cenas, tempos) if pasta is not None else []
    br_els, br_js = broll.html(trechos)
    for t in trechos:
        br_js += (f'\n      tl.set("#veu", {{opacity: 1}}, {t["ini"]});'
                  f'tl.set("#veu", {{opacity: 0}}, {t["ini"] + t["dur"]:.3f});')
    (projeto / "index.html").write_text(f"""<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{esc(titulo)}</title>
    {GSAP}
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0f0f17; }}
      #root {{ width: 100%; height: 100%; position: relative; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
      {hosts_txt}
      {br_els}
      <div id="veu" style="position:absolute;inset:0;z-index:3;opacity:0;background:linear-gradient(180deg,rgba(10,10,16,.72) 0%,rgba(10,10,16,.30) 22%,rgba(10,10,16,.25) 50%,rgba(10,10,16,.55) 72%,rgba(10,10,16,.85) 100%);"></div>
      <audio id="narracao" class="clip" src="assets/narracao.wav" data-start="0" data-duration="{total}" data-track-index="4" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {br_js}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""", encoding="utf-8")
    return _srt(leg_linhas)
