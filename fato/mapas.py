"""Famílias de mapa: mapa_brasil (estados do IBGE) e mapa_lugar (globo NASA Blue Marble)."""
import json
import math
from functools import lru_cache

from .comum import MODELO
from .familias import esc, js_titulo, tam_titulo, titulo_html
from .validar import _numero

UFS_ARQ = MODELO / "assets" / "mapas" / "ufs.json"
MALHA_ARQ = MODELO / "assets" / "mapas" / "br-uf.geojson"


@lru_cache(None)
def ufs():
    """{'SP': {'id': '35', 'nome': 'São Paulo'}, ...}"""
    return {u["sigla"]: {"id": str(u["id"]), "nome": u["nome"]} for u in json.loads(UFS_ARQ.read_text(encoding="utf-8"))}


@lru_cache(None)
def caminhos(larg=450, alt=450):
    """Caminhos SVG de cada UF, projetados numa caixa larg x alt. Devolve ({sigla: d}, {sigla: (cx, cy)})."""
    g = json.loads(MALHA_ARQ.read_text(encoding="utf-8"))
    por_id = {v["id"]: k for k, v in ufs().items()}
    k = math.cos(math.radians(15))
    polis = {}
    for f in g["features"]:
        sig = por_id[f["properties"]["codarea"]]
        geo = f["geometry"]
        lst = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        polis[sig] = [[(lon * k, -lat) for lon, lat in anel] for poli in lst for anel in poli]
    xs = [x for p in polis.values() for a in p for x, _ in a]
    ys = [y for p in polis.values() for a in p for _, y in a]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    esc_ = min(larg / (x1 - x0), alt / (y1 - y0))
    ox, oy = (larg - (x1 - x0) * esc_) / 2, (alt - (y1 - y0) * esc_) / 2
    d, cen = {}, {}
    for sig, aneis in polis.items():
        partes, sx, sy, n = [], 0, 0, 0
        for a in aneis:
            pts = [((x - x0) * esc_ + ox, (y - y0) * esc_ + oy) for x, y in a]
            partes.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
            for x, y in pts:
                sx += x; sy += y; n += 1
        d[sig] = "".join(partes)
        cen[sig] = (sx / n, sy / n)
    return d, cen


def _cor(k):
    """escala de #1d2250 (menor) a #8a95ff (maior), passando pelo cobalto"""
    paradas = [(0, (0x1d, 0x22, 0x50)), (0.55, (0x2a, 0x40, 0xf0)), (1, (0x8a, 0x95, 0xff))]
    for (a, ca), (b, cb) in zip(paradas, paradas[1:]):
        if k <= b:
            u = (k - a) / (b - a)
            return "#%02x%02x%02x" % tuple(round(x + (y - x) * u) for x, y in zip(ca, cb))
    return "#8a95ff"


def mapa_brasil(p, s, t, dur):
    m = s["mapa"]
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 54)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    leg_h = 58 if m.get("legenda") else 0
    topo = int(300 + leg_h + len(linhas) * fs * 1.04 + 26)   # o mapa começa depois do título
    L = max(300, min(440, 830 - topo))
    esq = 540 - L // 2
    d, cen = caminhos(L, L)
    valores = {k.upper(): _numero(v) for k, v in (m.get("valores") or {}).items()}
    dest = [x.upper() for x in (m.get("destaques") or ([m["destaque"]] if m.get("destaque") else []))]
    if valores:
        vmin, vmax = min(valores.values()), max(valores.values())
        ordem = sorted(valores, key=lambda u: valores[u])
    else:
        ordem = sorted(d)
    paths, js = [], js_titulo(p, n, max(0.1, t - 0.3))
    t0 = max(0.2, t) + 0.15
    for i, sig in enumerate(ordem if valores else sorted(d)):
        if valores:
            cor = "#ffd60a" if sig in dest else _cor((valores.get(sig, vmin) - vmin) / ((vmax - vmin) or 1))
        else:
            cor = "#ffd60a" if sig in dest else "#2a40f0"
        paths.append(f'<path id="{p}-uf-{sig}" d="{d[sig]}" class="uf"/>')
        ti = t0 + 0.9 * i / max(1, len(ordem) - 1)
        js += f'tl.fromTo("#{p}-uf-{sig}", {{fill: "#2e2e3d"}}, {{fill: "{cor}", duration: 0.35, ease: "power2.out"}}, {ti:.3f});\n'
    # estados sem valor ficam na cor da linha
    for sig in d:
        if valores and sig not in valores:
            paths.append(f'<path id="{p}-uf-{sig}" d="{d[sig]}" class="uf"/>')
    cal = ""
    if dest:
        sig = dest[0]
        cx, cy = cen[sig]
        txt = ufs()[sig]["nome"].upper()
        if valores.get(sig) is not None:
            v = m["valores"].get(sig) if sig in (m.get("valores") or {}) else m["valores"].get(sig.lower())
            txt += f' · {esc(v)}{esc(m.get("unidade", ""))}'
        # o rótulo fica do lado com mais espaço
        lado_dir = cx < L / 2
        lx = esq + cx + (34 if lado_dir else -34)
        cal = (f'<div id="{p}-cal" class="calout {"dir" if lado_dir else "esq"}" '
               f'style="left:{lx:.0f}px;top:{topo + cy - 26:.0f}px">{esc(txt)}</div>')
        tc = t0 + 1.05
        js += f'tl.fromTo("#{p}-uf-{sig}", {{scale: 1}}, {{scale: 1.08, duration: 0.25, ease: "power2.out", yoyo: true, repeat: 1, transformOrigin: "50% 50%", immediateRender: false}}, {tc:.3f});\n'
        xp = 0 if lado_dir else -100
        js += f'tl.fromTo("#{p}-cal", {{opacity: 0, y: 12, xPercent: {xp}}}, {{opacity: 1, y: 0, xPercent: {xp}, duration: 0.3, ease: "power3.out"}}, {tc + 0.1:.3f});\n'
    leg = f'<div id="{p}-leg" class="rot">{esc(m.get("legenda", "")).upper()}</div>' if m.get("legenda") else ""
    if leg:
        js += f'tl.fromTo("#{p}-leg", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {max(0, t - 0.4):.3f});\n'
    html = (f'<div id="{p}-bloco" class="col topo">{leg}{tit}</div>'
            f'<svg id="{p}-mapa" class="mapa" viewBox="0 0 {L} {L}" width="{L}" height="{L}" '
            f'style="left:{esq}px;top:{topo}px">{"".join(paths)}</svg>{cal}')
    css = (f'#{p}-tit{{font-size:{fs}px;line-height:1.04;}}'
           f'.mapa{{position:absolute;overflow:visible;}}'
           f'.uf{{fill:#2e2e3d;stroke:#0f0f17;stroke-width:1.2;}}'
           f'.calout{{position:absolute;background:#ffd60a;color:#121218;font-size:30px;padding:8px 14px;border-radius:4px;white-space:nowrap;text-transform:uppercase;}}')
    return html, css, js


def mapa_lugar(p, s, t, dur):
    lg = s["lugar"]
    linhas = s["titulo"]
    fs = tam_titulo(linhas, 60)
    tit, n = titulo_html(p, linhas, s.get("destaque"))
    W, H, top = 840, 420, 415
    t0 = max(0.0, t - 0.2)
    html = (f'<div id="{p}-bloco" class="col topo">{tit}</div>'
            f'<div class="glbox" style="left:120px;top:{top}px;width:{W}px;height:{H}px">'
            f'<canvas id="{p}-cv" width="{W}" height="{H}" data-layout-ignore></canvas>'
            f'<div id="{p}-lugar" class="lugar">{esc(lg["nome"]).upper()}</div>'
            f'<div class="credito" data-layout-ignore>IMAGEM: NASA BLUE MARBLE</div></div>')
    css = (f'#{p}-tit{{font-size:{fs}px;line-height:1.04;}}'
           '.glbox{position:absolute;}'
           '.glbox canvas{position:absolute;left:0;top:0;}'
           '.lugar{position:absolute;left:0;top:0;opacity:0;background:#ffd60a;color:#121218;font-size:32px;padding:8px 14px;border-radius:4px;white-space:nowrap;}'
           '.credito{position:absolute;right:6px;bottom:4px;font-family:"JetBrains Mono",monospace;font-size:16px;color:#a6a5b2;opacity:.8;}')
    js = js_titulo(p, n, max(0.1, t - 0.3))
    modulo = {"lat": float(lg["lat"]), "lon": float(lg["lon"]), "t0": round(t0, 3), "cx": W / 2, "cy": H / 2,
              "d0": 6.2, "d1": 4.1, "textura": "./assets/mapas/terra.jpg", "dur": dur}
    return html, css, js, modulo


GLOBO_JS = """
import {{ criarGlobo }} from "./assets/lib/globo.js";
const o = {dados};
o.rotulo = document.getElementById("{p}-lugar");
const g = await criarGlobo(document.getElementById("{p}-cv"), o);
const st = {{ t: 0 }};
tl.to(st, {{ t: o.dur, duration: o.dur, ease: "none", onUpdate: () => g.render(st.t) }}, 0);
g.render(0);
"""
