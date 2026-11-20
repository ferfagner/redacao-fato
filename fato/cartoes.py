"""Cartões 3D: lista, versus, linha do tempo e antes/depois. Cada função devolve (html, css, js)."""
from .familias import esc, js_titulo, tam_titulo, titulo_html
from .validar import _numero


def _topo(linhas, fs):
    return int(300 + len(linhas) * fs * 1.04 + 28)


def lista_cards(p, s, t, dur):
    """Ranking ou lista: cartões que chegam um a um em profundidade (3D), com número e valor."""
    itens = s["itens"]
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 56)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    top = _topo(linhas, fs)
    gap = 12
    h = int(min(92, (840 - top - gap * (len(itens) - 1)) / len(itens)))
    cards, js = [], js_titulo(p, n, max(0.1, t - 0.3))
    for k, it in enumerate(itens):
        val = f'<span class="lv">{esc(it.get("valor", ""))}{esc(it.get("unidade", ""))}</span>' if it.get("valor") else ""
        cards.append(f'<div id="{p}-l{k}" class="lcard{" lprim" if k == 0 else ""}" style="top:{top + k * (h + gap)}px;height:{h}px">'
                     f'<span class="ln">{k + 1}</span><span class="lt">{esc(it["rotulo"]).upper()}</span>{val}</div>')
        tk = max(0.2, t) + 0.15 + 0.3 * k
        js += (f'tl.fromTo("#{p}-l{k}", {{rotationX: -70, z: -260, y: 60, opacity: 0}}, '
               f'{{rotationX: 0, z: 0, y: 0, opacity: 1, duration: 0.5, ease: "back.out(1.4)"}}, {tk:.3f});\n')
    html = f'<div id="{p}-bloco" class="col topo">{tit}</div><div class="lpalco">{"".join(cards)}</div>'
    fsl = max(30, min(44, int(h * 0.46)))
    css = (f'#{p}-tit{{font-size:{fs}px;line-height:1.04;}}'
           '.lpalco{position:absolute;inset:0;perspective:1100px;perspective-origin:540px 600px;}'
           '.lcard{position:absolute;left:150px;width:780px;display:flex;align-items:center;gap:22px;padding:0 26px;'
           'background:linear-gradient(100deg,rgba(42,64,240,.32),rgba(26,26,38,.92));border:2px solid rgba(138,149,255,.4);'
           'border-radius:14px;box-shadow:0 18px 40px rgba(0,0,0,.5);transform-origin:50% 0%;}'
           '.lprim{border-color:#ffd60a;background:linear-gradient(100deg,rgba(255,214,10,.22),rgba(26,26,38,.92));}'
           f'.ln{{font-size:{fsl + 6}px;color:#ffd60a;min-width:48px;}}'
           f'.lt{{flex:1;font-size:{fsl}px;color:#f4f3ef;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}'
           f'.lv{{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:{fsl - 2}px;color:#ffd60a;}}')
    return html, css, js


def versus(p, s, t, dur):
    """Dois cartões frente a frente com o selo VS; o maior valor ganha borda amarela."""
    a, b = s["comparacao"][:2]
    va, vb = _numero(a.get("valor")), _numero(b.get("valor"))
    ganha = 0 if (va or 0) >= (vb or 0) else 1
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 56)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    top = _topo(linhas, fs)
    h = min(380, 820 - top)
    cards = []
    for k, it in enumerate((a, b)):
        x = 150 if k == 0 else 560
        cards.append(f'<div id="{p}-v{k}" class="vcard{" vgan" if k == ganha else ""}" style="left:{x}px;top:{top}px;height:{h}px">'
                     f'<div class="vrot">{esc(it["rotulo"]).upper()}</div>'
                     f'<div class="vval">{esc(it.get("valor", ""))}</div><div class="vuni">{esc(it.get("unidade", "")).upper()}</div></div>')
    selo = f'<div id="{p}-vs" class="vs" style="top:{top + h // 2 - 56}px">VS</div>'
    t0 = max(0.2, t)
    js = js_titulo(p, n, max(0.1, t - 0.3))
    js += f'tl.fromTo("#{p}-v0", {{rotationY: -95, opacity: 0}}, {{rotationY: 8, opacity: 1, duration: 0.55, ease: "back.out(1.3)"}}, {t0:.3f});\n'
    js += f'tl.fromTo("#{p}-v1", {{rotationY: 95, opacity: 0}}, {{rotationY: -8, opacity: 1, duration: 0.55, ease: "back.out(1.3)"}}, {t0 + 0.25:.3f});\n'
    js += f'tl.fromTo("#{p}-vs", {{scale: 0, rotation: -40}}, {{scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2.2)"}}, {t0 + 0.55:.3f});\n'
    js += f'tl.to("#{p}-v{ganha}", {{scale: 1.05, duration: 0.3, ease: "power2.out", yoyo: true, repeat: 1}}, {t0 + 1.1:.3f});\n'
    html = f'<div id="{p}-bloco" class="col topo">{tit}</div><div class="vpalco">{"".join(cards)}{selo}</div>'
    css = (f'#{p}-tit{{font-size:{fs}px;line-height:1.04;}}'
           '.vpalco{position:absolute;inset:0;perspective:1200px;perspective-origin:540px 600px;}'
           '.vcard{position:absolute;width:370px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;'
           'background:linear-gradient(170deg,rgba(42,64,240,.35),rgba(26,26,38,.95));border:3px solid rgba(138,149,255,.45);'
           'border-radius:18px;box-shadow:0 22px 50px rgba(0,0,0,.55);text-align:center;padding:20px;}'
           '.vgan{border-color:#ffd60a;box-shadow:0 0 40px rgba(255,214,10,.35),0 22px 50px rgba(0,0,0,.55);}'
           '.vrot{font-size:34px;color:#f4f3ef;text-transform:uppercase;line-height:1.05;}'
           '.vval{font-size:92px;color:#ffd60a;line-height:1;letter-spacing:-0.02em;}'
           '.vuni{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:28px;color:#a6a5b2;}'
           '.vs{position:absolute;left:484px;width:112px;height:112px;border-radius:56px;background:#ffd60a;color:#121218;'
           'font-size:48px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 8px #0f0f17;}')
    return html, css, js


def linha_tempo(p, s, t, dur):
    """Datas numa linha vertical em perspectiva; cada ponto acende e mostra o que aconteceu."""
    itens = s["itens"]
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 56)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    top = _topo(linhas, fs) + 10
    passo = int(min(120, (830 - top) / len(itens)))
    pts, js = [], js_titulo(p, n, max(0.1, t - 0.3))
    t0 = max(0.2, t)
    js += f'tl.fromTo("#{p}-trilho", {{scaleY: 0}}, {{scaleY: 1, duration: {0.35 * len(itens) + 0.3:.2f}, ease: "none"}}, {t0:.3f});\n'
    for k, it in enumerate(itens):
        y = top + k * passo
        pts.append(f'<div id="{p}-p{k}" class="tp" style="top:{y}px"><div class="tdot{" tult" if k == len(itens) - 1 else ""}"></div>'
                   f'<div class="tano">{esc(it["rotulo"])}</div><div class="ttxt">{esc(it.get("texto", "")).upper()}</div></div>')
        tk = t0 + 0.2 + 0.35 * k
        js += f'tl.fromTo("#{p}-p{k}", {{x: 80, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.4, ease: "power3.out"}}, {tk:.3f});\n'
    html = (f'<div id="{p}-bloco" class="col topo">{tit}</div>'
            f'<div class="tpalco"><div class="tcol"><div id="{p}-trilho" class="trilhot" style="top:{top + 18}px;height:{passo * (len(itens) - 1)}px"></div>'
            f'{"".join(pts)}</div></div>')
    css = (f'#{p}-tit{{font-size:{fs}px;line-height:1.04;}}'
           '.tpalco{position:absolute;inset:0;perspective:1300px;perspective-origin:540px 600px;}'
           '.tcol{position:absolute;inset:0;transform:rotateY(14deg);transform-origin:200px 600px;}'
           '.trilhot{position:absolute;left:208px;width:6px;background:#8a95ff;border-radius:3px;transform-origin:50% 0;}'
           '.tp{position:absolute;left:190px;width:740px;display:flex;align-items:center;gap:22px;}'
           '.tdot{width:42px;height:42px;border-radius:21px;background:#2a40f0;border:5px solid #8a95ff;flex:none;}'
           '.tult{background:#ffd60a;border-color:#fff3b0;}'
           '.tano{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:40px;color:#ffd60a;min-width:130px;}'
           '.ttxt{font-size:32px;color:#f4f3ef;text-transform:uppercase;line-height:1.05;}')
    return html, css, js


def antes_depois(p, s, t, dur):
    """Um cartão que gira no meio da cena: frente = ANTES, verso = DEPOIS."""
    a, b = s["comparacao"][:2]
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 56)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    top = _topo(linhas, fs)
    h = min(400, 820 - top)

    def face(it, cls, selo):
        return (f'<div class="adf {cls}"><div class="adselo">{selo}</div><div class="adrot">{esc(it["rotulo"]).upper()}</div>'
                f'<div class="adval">{esc(it.get("valor", ""))}</div><div class="aduni">{esc(it.get("unidade", "")).upper()}</div></div>')
    t0 = max(0.2, t)
    vira = max(t0 + 1.2, min(dur - 1.4, t0 + (dur - t0) * 0.5))
    js = js_titulo(p, n, max(0.1, t - 0.3))
    js += f'tl.fromTo("#{p}-ad", {{rotationY: -40, opacity: 0, scale: 0.85}}, {{rotationY: 0, opacity: 1, scale: 1, duration: 0.5, ease: "power3.out"}}, {t0:.3f});\n'
    js += f'tl.to("#{p}-ad", {{rotationY: 180, duration: 0.7, ease: "back.inOut(1.4)"}}, {vira:.3f});\n'
    html = (f'<div id="{p}-bloco" class="col topo">{tit}</div><div class="adpalco">'
            f'<div id="{p}-ad" class="adcard" data-layout-allow-overlap style="top:{top}px;height:{h}px">{face(a, "adfr", "ANTES")}{face(b, "adve", "DEPOIS")}</div></div>')
    css = (f'#{p}-tit{{font-size:{fs}px;line-height:1.04;}}'
           '.adpalco{position:absolute;inset:0;perspective:1400px;perspective-origin:540px 600px;}'
           '.adcard{position:absolute;left:190px;width:700px;transform-style:preserve-3d;}'
           '.adf{position:absolute;inset:0;backface-visibility:hidden;border-radius:20px;display:flex;flex-direction:column;'
           'align-items:center;justify-content:center;gap:10px;box-shadow:0 24px 60px rgba(0,0,0,.55);}'
           '.adfr{background:linear-gradient(170deg,#2e2e3d,#1a1a26);border:3px solid #55545e;}'
           '.adve{background:linear-gradient(170deg,rgba(42,64,240,.55),#1a1a26);border:3px solid #ffd60a;transform:rotateY(180deg);}'
           '.adselo{font-family:"JetBrains Mono",monospace;font-weight:700;letter-spacing:.14em;background:#ffd60a;font-size:28px;'
           'color:#121218;border-radius:4px;padding:4px 14px;}'
           '.adfr .adselo{background:#a6a5b2;}'
           '.adrot{font-size:38px;color:#f4f3ef;text-transform:uppercase;}'
           '.adval{font-size:120px;color:#ffd60a;line-height:1;}'
           '.adfr .adval{color:#f4f3ef;}'
           '.aduni{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:28px;color:#a6a5b2;}')
    return html, css, js


CARTOES = {"lista_cards": lista_cards, "versus": versus, "linha_tempo": linha_tempo, "antes_depois": antes_depois}
