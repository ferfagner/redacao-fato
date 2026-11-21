"""Vídeo de fundo (b-roll): corta cada trecho no tamanho certo para a cena e deixa pronto no projeto.

No cenas.json, cada cena pode ter "broll": uma lista de 1 a 3 itens
  {"arquivo": "videos/sp.mp4", "inicio": 2.0, "fonte": "Pexels", "url_origem": "https://...", "licenca": "licenca pexels"}
O tempo da cena é dividido entre os itens (um corte a cada ~2 s, de preferência numa batida da fala).
Foto também serve como item (.jpg/.png/.webp): entra com zoom lento.
"""
from pathlib import Path

from .comum import rodar

VIDEO_EXT = (".mp4", ".mov", ".webm", ".mkv", ".m4v")
FOTO_EXT = (".jpg", ".jpeg", ".png", ".webp")


def _duracao(arq: Path) -> float:
    try:
        r = rodar("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq)
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def _cortes(n, dur, batidas):
    """Divide [0, dur] em n partes; puxa cada corte para a batida mais próxima (até 0,6 s)."""
    cortes = [dur * k / n for k in range(1, n)]
    out = []
    for c in cortes:
        perto = min(batidas or [c], key=lambda b: abs(b - c))
        out.append(perto if abs(perto - c) <= 0.6 else c)
    pontos = [0.0] + sorted(out) + [dur]
    return [(round(a, 3), round(b - a, 3)) for a, b in zip(pontos, pontos[1:]) if b - a > 0.4]


def preparar(pasta: Path, projeto: Path, cenas, tempos):
    """Gera assets/broll/*.mp4|jpg e devolve a lista de trechos com o tempo global de cada um."""
    destino = projeto / "assets" / "broll"
    destino.mkdir(parents=True, exist_ok=True)
    trechos = []
    for s, tp in zip(cenas, tempos):
        itens = s.get("broll") or []
        if not itens:
            continue
        dur = tp["fim"] - tp["ini"]
        partes = _cortes(len(itens), dur, tp.get("batidas", []))
        for k, (it, (ini_local, d)) in enumerate(zip(itens, partes)):
            orig = (pasta / it["arquivo"]).resolve()
            nome = f"c{s['id']:02d}_{k}"
            d_out = d + 0.25   # sobra para o corte nunca mostrar quadro vazio
            if orig.suffix.lower() in FOTO_EXT:
                saida = destino / f"{nome}.jpg"
                rodar("ffmpeg", "-y", "-v", "error", "-i", orig, "-vf",
                      "scale=1188:2112:force_original_aspect_ratio=increase,crop=1188:2112", "-q:v", "3", saida)
                tipo = "foto"
            else:
                saida = destino / f"{nome}.mp4"
                total = _duracao(orig)
                ini = float(it.get("inicio", 0) or 0)
                if total and ini + d_out > total:      # trecho curto: recua o início ou repete
                    ini = max(0.0, total - d_out)
                laco = ["-stream_loop", "-1"] if total and total < d_out else []
                rodar("ffmpeg", "-y", "-v", "error", *laco, "-ss", f"{ini:.3f}", "-i", orig, "-t", f"{d_out:.3f}", "-an",
                      "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1",
                      "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                      saida)
                tipo = "video"
            trechos.append({"id": nome, "tipo": tipo, "src": f"assets/broll/{saida.name}", "cena": s["id"],
                            "ini": round(tp["ini"] + ini_local, 3), "dur": round(d, 3), "k": len(trechos)})
    return trechos


def html(trechos):
    """Elementos do index.html (fora das sub-composições) e o JS do timeline principal: zoom em cada corte."""
    els, js = [], []
    for t in trechos:
        estilo = "position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;z-index:2;"
        if t["tipo"] == "video":
            els.append(f'<video id="br-{t["id"]}" src="{t["src"]}" data-start="{t["ini"]}" data-duration="{t["dur"]}" '
                       f'data-track-index="{6 + t["k"] % 2}" muted playsinline style="{estilo}"></video>')
        else:
            els.append(f'<img id="br-{t["id"]}" class="clip" src="{t["src"]}" alt="" data-start="{t["ini"]}" data-duration="{t["dur"]}" '
                       f'data-track-index="{6 + t["k"] % 2}" style="{estilo}" />')
        # entra com um "soco" de zoom e segue aproximando devagar (alterna o centro do zoom)
        origem = ["50% 40%", "35% 50%", "65% 50%", "50% 60%"][t["k"] % 4]
        js.append(f'tl.set("#br-{t["id"]}", {{transformOrigin: "{origem}"}}, {t["ini"]});'
                  f'tl.fromTo("#br-{t["id"]}", {{scale: 1.16}}, {{scale: 1.03, duration: 0.35, ease: "power3.out"}}, {t["ini"]});'
                  f'tl.to("#br-{t["id"]}", {{scale: 1.10, duration: {max(0.2, t["dur"] - 0.35):.3f}, ease: "none"}}, {t["ini"] + 0.35:.3f});')
    return "\n      ".join(els), "\n      ".join(js)
