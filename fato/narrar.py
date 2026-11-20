"""Narração: edge-tts por bloco, corte de silêncio, -16 LUFS, ajuste de velocidade,
tempo de cada palavra e tempo de cada cena (pela âncora)."""
import asyncio
import time
from pathlib import Path

import edge_tts

from .comum import Falha, duracao, erro, norm, rodar

VOZ = "pt-BR-AntonioNeural"
INICIO = 0.35        # a voz começa um pouco depois do quadro 0
PAUSA = 0.30         # entre blocos
CAUDA = 1.6          # depois da última palavra
DUR_MIN, DUR_MAX = 58.0, 65.0
CENA_MIN = 1.6       # cena mais curta aceitável
CENA_MAX = 9.0       # vertical pede uma mudança a cada poucos segundos
ANTES_ANCORA = 0.25  # a cena começa um pouco antes da palavra-âncora


async def _tts(texto, rate, mp3: Path):
    try:
        com = edge_tts.Communicate(texto, VOZ, rate=rate, boundary="WordBoundary")
    except TypeError:
        com = edge_tts.Communicate(texto, VOZ, rate=rate)
    pals = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                ini = ch["offset"] / 1e7
                pals.append([ch["text"], round(ini, 3), round(ini + ch["duration"] / 1e7, 3)])
    if not pals:
        raise RuntimeError("edge-tts não devolveu o tempo das palavras")
    return pals


def _pontuar(pals, texto):
    """O edge-tts devolve as palavras sem pontuação; recupera do texto original."""
    tokens, out, j = texto.split(), [], 0
    for w, a, b in pals:
        alvo, k = norm(w), j
        while k < len(tokens) and alvo not in norm(tokens[k]):
            k += 1
        if k < len(tokens):
            out.append([tokens[k], a, b])
            j = k + 1
        else:
            out.append([w, a, b])
    return out


def _bloco(bid, texto, rate, pasta: Path):
    mp3, wav = pasta / f"{bid}.mp3", pasta / f"{bid}.wav"
    # o serviço de voz é online: tenta 4 vezes, com espera crescente, antes de desistir
    for tentativa in range(4):
        try:
            pals = asyncio.run(_tts(texto, rate, mp3))
            break
        except Exception as ex:  # rede, limite de requisições ou resposta vazia
            if tentativa == 3:
                raise RuntimeError(f"voz (edge-tts) falhou 4 vezes no bloco '{bid}': {type(ex).__name__}: {ex}")
            time.sleep(3 * (tentativa + 1))
    lead = max(0.0, pals[0][1] - 0.05)
    pals = [[w, round(a - lead, 3), round(b - lead, 3)] for w, a, b in pals]
    rodar("ffmpeg", "-y", "-v", "error", "-i", mp3, "-af",
          f"atrim=start={lead},asetpts=PTS-STARTPTS,areverse,"
          "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse,"
          "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", "-ac", "1", "-ar", "48000", wav)
    return wav, duracao(wav), _pontuar(pals, texto)


def narrar(roteiro, pasta_audio: Path, saida_wav: Path):
    """Gera os blocos e a trilha. Devolve {rate, total, fim_voz, palavras:[{texto,ini,fim,bloco}], blocos:[...]}."""
    pasta_audio.mkdir(parents=True, exist_ok=True)
    blocos = roteiro["blocos"]
    cache = {}

    def tenta(pct):
        if pct not in cache:
            rate = f"{pct:+d}%"
            res = [(b["id"], *_bloco(b["id"], b["texto"], rate, pasta_audio)) for b in blocos]
            cache[pct] = (rate, res, INICIO + sum(r[2] for r in res) + PAUSA * (len(res) - 1))
        return cache[pct]

    # velocidade normal primeiro; acelera se passar de 65 s, desacelera um pouco se ficar curta
    pct = 0
    rate, res, fim_voz = tenta(0)
    while fim_voz + CAUDA > DUR_MAX and pct < 20:
        pct += 5
        rate, res, fim_voz = tenta(pct)
    while fim_voz + CAUDA < DUR_MIN and -10 < pct <= 0:
        r2 = tenta(pct - 5)
        if r2[2] + CAUDA > DUR_MAX:
            break
        pct -= 5
        rate, res, fim_voz = r2
    if fim_voz + CAUDA > DUR_MAX:
        excesso = fim_voz + CAUDA - DUR_MAX
        longos = sorted(res, key=lambda r: -r[2])[:2]
        raise Falha("narracao", [erro("Roteirista",
            f"mesmo a +20% a narração passa {excesso:.1f} s do limite de {DUR_MAX:.0f} s; "
            f"corte uns {int(excesso * 3.4) + 3} palavras, de preferência em: " + ", ".join(r[0] for r in longos))])
    total = round(max(DUR_MIN, fim_voz + CAUDA), 2)
    avisos = []
    if total - fim_voz > 4:
        raise Falha("narracao", [erro("Roteirista",
            f"a narração ficou com {fim_voz:.0f} s mesmo na voz mais lenta; acrescente uns {int((total - fim_voz - CAUDA) * 2.9) + 3} palavras no mecanismo ou na virada")])
    if total - fim_voz > 2.5:
        avisos.append(f"narração curta ({fim_voz:.1f} s): a última cena fica parada {total - fim_voz:.1f} s")

    # trilha única
    entradas, filtros, t, pal_glob, info_blocos = [], [], INICIO, [], []
    for k, (bid, wav, d, pals) in enumerate(res):
        entradas += ["-i", wav]
        filtros.append(f"[{k}]adelay={int(round(t * 1000))}:all=1[a{k}]")
        for w, a, b in pals:
            pal_glob.append({"texto": w, "ini": round(t + a, 3), "fim": round(t + b, 3), "bloco": bid})
        info_blocos.append({"id": bid, "ini": round(t, 3), "fim": round(t + d, 3)})
        t += d + PAUSA
    mix = "".join(f"[a{k}]" for k in range(len(res)))
    filtros.append(f"{mix}amix=inputs={len(res)}:normalize=0:dropout_transition=0,apad,atrim=0:{total}[out]")
    saida_wav.parent.mkdir(parents=True, exist_ok=True)
    rodar("ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex", ";".join(filtros),
          "-map", "[out]", "-ar", "48000", "-ac", "2", saida_wav)
    return {"voz": VOZ, "rate": rate, "total": total, "fim_voz": round(fim_voz, 3),
            "blocos": info_blocos, "palavras": pal_glob, "avisos": avisos}


def tempos_cenas(cenas, narr):
    """Liga cada cena à sua palavra-âncora. Devolve lista de (ini, fim, t_ancora_local, t_destaque_local)."""
    pals, e = narr["palavras"], []
    nrm = [norm(p["texto"]) for p in pals]
    inicios, ancoras, cursor = [], [], 0
    for s in cenas:
        if s["id"] == 1:
            inicios.append(0.0); ancoras.append(INICIO); continue
        alvo = [norm(w) for w in s["ancora"].split()]
        achou = None
        for i in range(cursor, len(pals) - len(alvo) + 1):
            if pals[i]["bloco"] == s["bloco"] and nrm[i:i + len(alvo)] == alvo:
                achou = i; break
        if achou is None:
            for i in range(cursor, len(pals) - len(alvo) + 1):
                if nrm[i:i + len(alvo)] == alvo:
                    achou = i; break
        if achou is None:
            e.append(erro("Diretor", f"a âncora \"{s['ancora']}\" não foi achada na fala depois da cena anterior", s["id"]))
            inicios.append(inicios[-1] + CENA_MIN); ancoras.append(inicios[-1]); continue
        cursor = achou + len(alvo)
        ta = pals[achou]["ini"]
        inicios.append(round(max(0.0, ta - ANTES_ANCORA), 3)); ancoras.append(ta)
    fins = inicios[1:] + [narr["total"]]
    out = []
    for s, a, b, ta in zip(cenas, inicios, fins, ancoras):
        if b - a > CENA_MAX:
            e.append(erro("Diretor", f"a cena dura {b - a:.1f} s (máximo {CENA_MAX:.0f} s): divida em duas, com uma âncora no meio da fala", s["id"]))
        if b - a < CENA_MIN:
            e.append(erro("Diretor", f"a cena fica com só {b - a:.1f} s (mínimo {CENA_MIN} s); troque a âncora desta cena ou da seguinte", s["id"]))
        # quando a palavra em destaque é falada dentro da cena
        td = None
        if s.get("destaque"):
            dn = norm(s["destaque"].split()[0])
            for p in pals:
                if a <= p["ini"] < b and norm(p["texto"]) == dn:
                    td = round(p["ini"] - a, 3); break
        out.append({"ini": round(a, 3), "fim": round(b, 3), "ancora": round(max(0.0, ta - a), 3), "destaque": td})
    if e:
        raise Falha("tempos", e)
    return out


NUMEROS = {"zero", "um", "uma", "dois", "duas", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze",
           "doze", "treze", "quatorze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove", "vinte",
           "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa", "cem", "cento", "duzentos",
           "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos", "mil",
           "milhao", "milhoes", "bilhao", "bilhoes", "trilhao", "trilhoes", "metade", "dobro", "triplo"}


def batidas(tempos, narr, passo=2.2, minimo=1.8):
    """Momentos de "soco" visual dentro de cada cena (tempo relativo à cena), a cada ~2 s,
    sempre numa palavra forte da fala (número ou palavra longa), para a tela nunca ficar parada."""
    pals = narr["palavras"]
    for tp in tempos:
        a, b = tp["ini"] + tp["ancora"] + 1.0, tp["fim"] - 0.6
        dentro = [p for p in pals if a <= p["ini"] <= b]
        escolhidos, prox = [], a
        while True:
            janela = [p for p in dentro if prox <= p["ini"] <= prox + 1.2]
            if not janela:
                depois = [p for p in dentro if p["ini"] >= prox]
                if not depois:
                    break
                janela = depois[:1]
            forte = lambda p: (norm(p["texto"]) in NUMEROS) * 3 + (len(norm(p["texto"])) >= 8) * 2 + (len(norm(p["texto"])) >= 6)
            p = max(janela, key=forte)
            escolhidos.append(round(p["ini"] - tp["ini"], 3))
            prox = p["ini"] + max(minimo, passo - 0.4)
        tp["batidas"] = escolhidos
    return tempos
