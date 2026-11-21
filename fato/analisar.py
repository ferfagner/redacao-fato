"""Análise das métricas para o Analista: liga cada post ao vídeo do log.csv e mede o que funciona.

Uso:  python3 -m fato.analisar metricas.csv log.csv [saida.json]
- metricas.csv: a aba "metricas" da planilha "thebestnewsbr - Métricas" exportada como CSV.
- log.csv: o log de produção (uma linha por vídeo).

Nota de desempenho de cada post (1,0 = mediana da própria rede):
  40% alcance  (views em 7 dias ÷ mediana da rede)
  40% retenção (tempo médio assistido ÷ duração, ÷ mediana da rede; só Instagram e Facebook informam)
  20% valor    ((compartilhamentos + salvamentos) ÷ views, ÷ mediana da rede)
A nota do vídeo é a média dos seus posts. Grupo com menos de 3 vídeos não vira conclusão.
"""
import csv
import json
import re
import statistics
import sys
import unicodedata
from datetime import datetime, timedelta

MIN_GRUPO = 3
MIN_AJUSTE = 10      # abaixo disso o Analista só coleta (fase "coleta")
PESOS = {"alcance": 0.4, "retencao": 0.4, "valor": 0.2}


def _n(v):
    try:
        s = str(v).strip().replace(",", ".")
        return float(s) if s not in ("", "nan") else None
    except ValueError:
        return None


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def _data(v):
    s = str(v or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(s[:19], fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _ler(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _parecido(a, b):
    """Fração das primeiras palavras da descrição que aparecem no começo da legenda."""
    pa, pb = _norm(a)[:12], set(_norm(b)[:30])
    return sum(1 for w in pa if w in pb) / len(pa) if pa else 0.0


def ligar(posts, videos):
    """Cada post vai para o vídeo com a descrição mais parecida, postado de 0 a 4 dias depois da produção."""
    for p in posts:
        dp = _data(p.get("data_post"))
        melhor, nota = None, 0.0
        for v in videos:
            dv = _data(v.get("data"))
            if dp and dv and not (dv - timedelta(days=1) <= dp <= dv + timedelta(days=4)):
                continue
            s = _parecido(v.get("descricao_inicio") or v.get("tema"), p.get("legenda"))
            if s > nota:
                melhor, nota = v, s
        p["_video"] = melhor if nota >= 0.5 else None
    return posts


def notas(posts):
    por_rede = {}
    for p in posts:
        views7 = _n(p.get("views_7d"))
        if views7 is None:
            continue    # só conta post com 7 dias de vida
        dur = _n(p.get("duracao_s")) or (_n(p["_video"].get("duracao_s")) if p.get("_video") else None)
        tm = _n(p.get("tempo_medio_s"))
        views = _n(p.get("views")) or 0
        val = ((_n(p.get("compartilhamentos")) or 0) + (_n(p.get("salvamentos")) or 0)) / views if views else None
        p["_m"] = {"alcance": views7, "retencao": tm / dur if tm and dur else None, "valor": val}
        por_rede.setdefault(p["rede"], []).append(p)
    medianas = {}
    for rede, ps in por_rede.items():
        med = {}
        for k in PESOS:
            vals = [p["_m"][k] for p in ps if p["_m"][k]]
            med[k] = statistics.median(vals) if vals else None
        medianas[rede] = med
        for p in ps:
            soma = peso = 0.0
            for k, w in PESOS.items():
                if p["_m"][k] is not None and med[k]:
                    soma += w * p["_m"][k] / med[k]; peso += w
            p["_nota"] = round(soma / peso, 3) if peso else None
    return medianas


def _faixa_dur(d):
    d = _n(d)
    return "" if d is None else ("até 55 s" if d <= 55 else "56 a 65 s" if d <= 65 else "mais de 65 s")


def _hora(p):
    d = _data(p.get("data_post"))
    return "" if not d else ("manhã" if 5 <= d.hour < 12 else "tarde" if d.hour < 18 else "noite")


def analisar(metricas_csv, log_csv):
    posts = ligar(_ler(metricas_csv), _ler(log_csv))
    medianas = notas(posts)
    vids = {}
    for p in posts:
        if p.get("_nota") is None or not p.get("_video"):
            continue
        v = p["_video"]
        chave = v.get("card") or v.get("tema")
        vids.setdefault(chave, {"video": v, "notas": [], "horas": []})
        vids[chave]["notas"].append(p["_nota"])
        vids[chave]["horas"].append(_hora(p))
    linhas = []
    for chave, x in vids.items():
        v = x["video"]
        linhas.append({"video": chave, "nota": round(sum(x["notas"]) / len(x["notas"]), 3), "categoria": v.get("categoria", ""),
                       "gancho_tipo": v.get("gancho_tipo", ""), "familias": [f.strip() for f in re.split(r"[;|,]", v.get("familias", "")) if f.strip()],
                       "duracao": _faixa_dur(v.get("duracao_s")), "horario": max(set(x["horas"]), key=x["horas"].count)})
    grupos = {}
    for dim in ("categoria", "gancho_tipo", "duracao", "horario", "familias"):
        g = {}
        for l in linhas:
            valores = l[dim] if isinstance(l[dim], list) else [l[dim]]
            for val in valores:
                if val:
                    g.setdefault(val, []).append(l["nota"])
        grupos[dim] = {k: {"videos": len(v), "nota_media": round(sum(v) / len(v), 2), "conclusivo": len(v) >= MIN_GRUPO}
                       for k, v in sorted(g.items(), key=lambda kv: -sum(kv[1]) / len(kv[1]))}
    linhas.sort(key=lambda l: -l["nota"])
    sem_par = [{"rede": p["rede"], "link": p.get("link"), "legenda": (p.get("legenda") or "")[:60]} for p in posts if not p.get("_video")]
    return {
        "fase": "ajuste" if len(linhas) >= MIN_AJUSTE else "coleta",
        "videos_com_nota": len(linhas),
        "posts_lidos": len(posts),
        "posts_sem_video_no_log": sem_par[:20],
        "medianas_por_rede": medianas,
        "grupos": grupos,
        "melhores": linhas[:3],
        "piores": linhas[-3:][::-1] if len(linhas) > 3 else [],
        "como_ler": "nota 1,0 = mediana da rede; acima de 1,2 é bom, abaixo de 0,8 é fraco. "
                    "Só tire conclusão de grupo com conclusivo=true (3 vídeos ou mais).",
    }


def main():
    if len(sys.argv) not in (3, 4):
        print(__doc__)
        sys.exit(2)
    r = analisar(sys.argv[1], sys.argv[2])
    txt = json.dumps(r, ensure_ascii=False, indent=2, default=str)
    if len(sys.argv) == 4:
        open(sys.argv[3], "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
