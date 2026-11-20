"""As seis famílias de cena. Cada função devolve (html, css, js) de uma cena.

Quadro 1080x1920. Áreas livres do TikTok e dos Reels (as do `hyperframes check`):
y 270 a 840 com x 120 a 960, e y 840 a 1248 com x 120 a 780.
Conteúdo da cena: y 285 a 830, centrado em x = 540. Placa da fonte: y 868. Legenda: y 1090 a 1240.
"""
import html as _h
import json
import math

from .comum import norm
from .validar import _numero

X0, LARG = 120, 840


def esc(s):
    return _h.escape(str(s), quote=True)


def tam_titulo(linhas, maximo, minimo=52, fator=0.80):
    maior = max(len(l) for l in linhas)
    return int(max(minimo, min(maximo, LARG / (fator * max(maior, 1)))))


def titulo_html(p, linhas, destaque, classe="tit", caixa=False):
    """Linhas do título com cada palavra num span (para entrar uma a uma)."""
    dn = norm(destaque.split()[0]) if destaque else None
    out, k = [], 0
    for ln in linhas:
        ws = []
        for w in ln.split():
            hl = dn and norm(w) == dn
            cls = "w" + (" hl" + (" hlbox" if caixa else "") if hl else "")
            ws.append(f'<span id="{p}-w{k}" class="{cls}">{esc(w)}</span>')
            k += 1
        out.append(f'<div class="ln">{" ".join(ws)}</div>')
    return f'<div id="{p}-{classe}" class="{classe}">{"".join(out)}</div>', k


def js_titulo(p, n, t, stagger=0.06):
    if n == 0:
        return ""
    alvos = ",".join('"#%s-w%d"' % (p, i) for i in range(n))
    return (f'tl.fromTo([{alvos}], {{y: 70, opacity: 0}}, '
            f'{{y: 0, opacity: 1, duration: 0.38, ease: "power3.out", stagger: {stagger}}}, {t:.3f});\n')


def js_destaque(p, t):
    if t is None:
        return ""
    return (f'tl.fromTo("#{p}-tit .hl", {{scale: 1}}, {{scale: 1.14, duration: 0.14, ease: "power2.out", immediateRender: false}}, {t:.3f});\n'
            f'tl.to("#{p}-tit .hl", {{scale: 1, duration: 0.25, ease: "power2.inOut"}}, {t + 0.14:.3f});\n')


def placa_fonte(p, fonte):
    if not fonte:
        return "", ""
    return (f'<div id="{p}-fonte" class="fonte"><span class="fk">FONTE</span> {esc(fonte).upper()}</div>',
            f'tl.fromTo("#{p}-fonte", {{x: -30, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.35, ease: "power3.out"}}, 0.15);\n')


# ---------------------------------------------------------------- famílias

def tipo_cinetico(p, s, t, dur):
    linhas = s["titulo"]
    if s["id"] == 1:  # gancho na caixa cobalto, como manda a identidade
        fs = tam_titulo(linhas, 84, fator=0.78 * 1.12)
        tit, n = titulo_html(p, linhas, s.get("destaque"), caixa=True)
        html = (f'<div id="{p}-caixa" class="gancho"><div class="selo">FATO DO DIA</div>{tit}</div>')
        css = (f'#{p}-caixa{{position:absolute;left:{X0}px;width:{LARG}px;top:270px;padding:52px 48px 60px;'
               f'background:var(--cobalto);border-radius:16px;}}'
               f'#{p}-tit{{font-size:{fs}px;line-height:1.02;color:var(--on-cobalto);}}')
        js = (f'tl.fromTo("#{p}-caixa", {{scale: 1.04}}, {{scale: 1, duration: 0.6, ease: "power3.out"}}, 0);\n'
              f'tl.to("#{p}-tit .hl", {{scale: 1.1, duration: 0.18, ease: "power2.out", yoyo: true, repeat: 1}}, 0.9);\n')
        return html, css, js
    fs = tam_titulo(linhas, 108)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    rot = f'<div id="{p}-rot" class="rot">{esc(s["rotulo"]).upper()}</div>' if s.get("rotulo") else ""
    html = f'<div id="{p}-bloco" class="centro">{rot}{tit}<div id="{p}-barra" class="barra"></div></div>'
    css = f'#{p}-tit{{font-size:{fs}px;line-height:1.0;}}'
    js = (f'tl.fromTo("#{p}-rot", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {max(0, t - 0.2):.3f});\n' if rot else "")
    js += js_titulo(p, n, t)
    js += f'tl.fromTo("#{p}-barra", {{scaleX: 0}}, {{scaleX: 1, duration: 0.5, ease: "power3.inOut"}}, {t + 0.25 + 0.06 * n:.3f});\n'
    return html, css, js


def numero_heroi(p, s, t, dur):
    d = s["dado"]
    valor = str(d["valor"])
    alvo = _numero(valor)
    casas = len(valor.split(",")[1]) if "," in valor else 0
    nfs = int(min(200, LARG / (0.70 * max(len(valor), 1))))
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 56)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    rot = esc(d.get("rotulo", "")).upper()
    html = (f'<div id="{p}-bloco" class="col">'
            + (f'<div id="{p}-rot" class="rot">{rot}</div>' if rot else "")
            + f'<div class="numwrap"><svg id="{p}-arco" class="arco" viewBox="0 0 600 600"><circle cx="300" cy="300" r="280" class="aro"/>'
              f'<circle id="{p}-arcoc" cx="300" cy="300" r="280" class="aroc"/></svg>'
              f'<div id="{p}-num" class="num">{esc(valor)}</div></div>'
            + (f'<div id="{p}-uni" class="uni">{esc(d.get("unidade", ""))}</div>' if d.get("unidade") else "")
            + f'{tit}</div>')
    css = f'#{p}-num{{font-size:{nfs}px;}} #{p}-tit{{font-size:{fs}px;line-height:1.04;margin-top:28px;}}'
    t0 = max(0.1, t)
    js = f'tl.fromTo("#{p}-rot", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.3}}, {max(0, t0 - 0.25):.3f});\n' if rot else ""
    js += f'tl.fromTo("#{p}-num", {{scale: 0.6, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.5, ease: "back.out(1.6)"}}, {t0:.3f});\n'
    if alvo is not None:
        js += (f'(function(){{const o={{v:0}};const el=document.getElementById("{p}-num");'
               f'tl.to(o,{{v:{alvo},duration:1.1,ease:"power2.out",onUpdate:()=>{{el.textContent=fmt(o.v,{casas});}}}},{t0:.3f});}})();\n')
    js += f'tl.fromTo("#{p}-arcoc", {{strokeDashoffset: 1760}}, {{strokeDashoffset: 0, duration: 1.3, ease: "power2.inOut"}}, {t0:.3f});\n'
    js += f'tl.fromTo("#{p}-arco", {{rotation: -90}}, {{rotation: 30, duration: {max(dur, 2):.2f}, ease: "none"}}, 0);\n'
    if d.get("unidade"):
        js += f'tl.fromTo("#{p}-uni", {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: 0.35}}, {t0 + 0.6:.3f});\n'
    js += js_titulo(p, n, t0 + 0.8)
    return html, css, js


def dado_comparado(p, s, t, dur):
    itens = s["comparacao"]
    vals = [_numero(i["valor"]) for i in itens]
    vmax = max(vals) or 1
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 58)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    linhas_html, js = [], js_titulo(p, n, max(0.1, t - 0.3))
    for k, (it, v) in enumerate(zip(itens, vals)):
        cor = "var(--amarelo)" if v == vmax else "var(--cobalto)"
        casas = len(str(it["valor"]).split(",")[1]) if "," in str(it["valor"]) else 0
        larg = max(0.06, v / vmax)
        linhas_html.append(
            f'<div class="item"><div class="itopo"><div class="irot">{esc(it["rotulo"]).upper()}</div>'
            f'<div id="{p}-v{k}" class="ival">{esc(it["valor"])}{esc(it.get("unidade", ""))}</div></div>'
            f'<div class="trilho"><div id="{p}-b{k}" class="fill" style="width:{larg * 100:.1f}%;background:{cor}"></div></div></div>')
        tk = max(0.2, t) + 0.35 + 0.22 * k
        js += f'tl.fromTo("#{p}-b{k}", {{scaleX: 0}}, {{scaleX: 1, duration: 0.8, ease: "power3.out"}}, {tk:.3f});\n'
        js += (f'(function(){{const o={{v:0}};const el=document.getElementById("{p}-v{k}");'
               f'tl.to(o,{{v:{v},duration:0.8,ease:"power3.out",onUpdate:()=>{{el.textContent=fmt(o.v,{casas})+{json.dumps(it.get("unidade", ""))};}}}},{tk:.3f});}})();\n')
    html = f'<div id="{p}-bloco" class="col topo">{tit}<div class="lista">{"".join(linhas_html)}</div></div>'
    css = f'#{p}-tit{{font-size:{fs}px;line-height:1.04;}}'
    return html, css, js


def objeto_profundidade(p, s, t, dur):
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 64)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    obj = s.get("objeto", "globo")
    if obj in OBJETOS_3D:
        return _objeto_three(p, s, t, dur, tit, n, fs, obj)
    faces = []
    if obj == "cubo":
        for tr in ("rotateY(0deg)", "rotateY(90deg)", "rotateY(180deg)", "rotateY(270deg)", "rotateX(90deg)", "rotateX(-90deg)"):
            faces.append(f'<div class="face" style="transform:{tr} translateZ(140px)"></div>')
    elif obj == "aneis":
        for k, (sz, rx) in enumerate(((320, 70), (240, 20), (170, -40))):
            faces.append(f'<div class="anel" style="width:{sz}px;height:{sz}px;margin:{-sz / 2}px 0 0 {-sz / 2}px;'
                         f'transform:rotateX({rx}deg) rotateY({k * 35}deg)"></div>')
    else:  # globo: meridianos + paralelos
        for k in range(9):
            faces.append(f'<div class="anel mer" style="transform:rotateY({k * 20}deg)"></div>')
        for lat in (-60, -30, 0, 30, 60):
            r = 160 * math.cos(math.radians(lat))
            y = -160 * math.sin(math.radians(lat))
            faces.append(f'<div class="anel par" style="width:{2 * r:.0f}px;height:{2 * r:.0f}px;margin:{-r:.0f}px 0 0 {-r:.0f}px;'
                         f'transform:translateY({y:.0f}px) rotateX(90deg)"></div>')
    html = (f'<div id="{p}-bloco" class="col topo">{tit}</div>'
            f'<div class="palco"><div id="{p}-obj" class="obj">{"".join(faces)}</div></div>')
    css = f'#{p}-tit{{font-size:{fs}px;line-height:1.04;}}'
    js = js_titulo(p, n, max(0.1, t - 0.2))
    js += f'tl.fromTo("#{p}-obj", {{scale: 0.5, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.7, ease: "power3.out"}}, 0.05);\n'
    js += f'tl.fromTo("#{p}-obj", {{rotationY: -20, rotationX: 16}}, {{rotationY: {-20 + 40 * dur:.0f}, rotationX: 22, duration: {dur:.2f}, ease: "none"}}, 0);\n'
    return html, css, js


OBJETOS_3D = ("moedas", "podio", "planeta", "barras")
OBJETOS = ("globo", "cubo", "aneis") + OBJETOS_3D


def _objeto_three(p, s, t, dur, tit, n, fs, obj):
    """Objeto em Three.js (objetos.js), com rótulos HTML que seguem o objeto."""
    W, H, top = 840, 470, 380
    itens = []
    for it in s.get("comparacao") or []:
        itens.append({"rotulo": str(it.get("rotulo", "")), "valor": _numero(it.get("valor")) or 0,
                      "txt": f'{it.get("valor", "")}{it.get("unidade", "")}'})
    rot_html = ""
    if obj in ("barras", "podio"):
        for k, it in enumerate(itens[:4 if obj == "barras" else 3]):
            cab = f'<b>{k + 1}º</b> ' if obj == "podio" else ""
            val = f'<span class="ov">{esc(it["txt"])}</span>' if obj == "barras" else ""
            rot_html += f'<div id="{p}-r{k}" class="orot">{val}{cab}{esc(it["rotulo"]).upper()}</div>'
    html = (f'<div id="{p}-bloco" class="col topo">{tit}</div>'
            f'<div class="glbox" style="left:120px;top:{top}px;width:{W}px;height:{H}px">'
            f'<canvas id="{p}-cv" width="{W}" height="{H}" data-layout-ignore></canvas>{rot_html}</div>')
    css = (f'#{p}-tit{{font-size:{fs}px;line-height:1.04;}}'
           '.glbox canvas{position:absolute;left:0;top:0;}'
           '.orot{position:absolute;left:0;top:0;opacity:0;white-space:nowrap;text-align:center;font-size:28px;'
           'color:#f4f3ef;text-transform:uppercase;text-shadow:0 2px 8px rgba(0,0,0,.8);}'
           '.orot b{color:#ffd60a;}'
           '.orot .ov{display:block;font-family:"JetBrains Mono",monospace;font-weight:700;font-size:30px;color:#ffd60a;}')
    js = js_titulo(p, n, max(0.1, t - 0.3))
    modulo = {"_js": "objeto", "tipo": obj, "t0": round(max(0.15, t), 3), "dur": dur, "itens": itens,
              "n_rotulos": rot_html.count('class="orot"')}
    return html, css, js, modulo


def citacao_fonte(p, s, t, dur):
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 60, minimo=44, fator=0.80 * 1.2)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    html = (f'<div id="{p}-card" class="card"><div class="aspas">&ldquo;</div>{tit}'
            f'<div id="{p}-quem" class="quem">— {esc(s.get("fonte", "")).upper()}</div></div>')
    css = f'#{p}-tit{{font-size:{fs}px;line-height:1.06;text-align:left;}}'
    js = f'tl.fromTo("#{p}-card", {{y: 80, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.55, ease: "power3.out"}}, 0.05);\n'
    js += js_titulo(p, n, max(0.25, t))
    js += f'tl.fromTo("#{p}-quem", {{opacity: 0}}, {{opacity: 1, duration: 0.35}}, {max(0.25, t) + 0.06 * n + 0.3:.3f});\n'
    return html, css, js


def fecho_chamada(p, s, t, dur):
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 84)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    cta = esc(s.get("chamada") or "SALVA E MANDA PRA ALGUÉM").upper()
    html = (f'<div id="{p}-bloco" class="col topo">{tit}'
            f'<div id="{p}-cta" class="cta">{cta}</div>'
            f'<div id="{p}-logo" class="logo"><img src="assets/marca.svg" alt=""/>'
            f'<span>thebest</span><span class="news">news</span><span class="br">br</span></div></div>')
    css = f'#{p}-tit{{font-size:{fs}px;line-height:1.0;}}'
    js = js_titulo(p, n, max(0.1, t - 0.1))
    js += f'tl.fromTo("#{p}-cta", {{scale: 0.7, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.45, ease: "back.out(1.8)"}}, {max(0.1, t) + 0.5:.3f});\n'
    js += f'tl.to("#{p}-cta", {{scale: 1.06, duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: {max(1, int((dur - 1.5) / 0.4))}}}, {max(0.1, t) + 1.0:.3f});\n'
    js += f'tl.fromTo("#{p}-logo", {{y: 30, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.4}}, {max(0.1, t) + 0.8:.3f});\n'
    return html, css, js


FUNCOES = {"tipo_cinetico": tipo_cinetico, "numero_heroi": numero_heroi, "dado_comparado": dado_comparado,
           "objeto_profundidade": objeto_profundidade, "citacao_fonte": citacao_fonte, "fecho_chamada": fecho_chamada}
