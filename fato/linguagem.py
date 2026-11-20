"""Linguagem para todo público: revisão obrigatória pelo Gemini e índice de facilidade de leitura."""
import re
from pathlib import Path

from .comum import Falha, erro, ler_json, norm

IFL_MIN_TOTAL = 60     # abaixo disso o roteiro volta para o Roteirista
IFL_MIN_BLOCO = 50     # abaixo disso, aviso
FRASE_MAX = 20         # palavras por frase (acima, aviso)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]")


def _silabas(w):
    return max(1, len(re.findall(r"[aeiou]+", norm(w))))


def ifl(texto):
    """Índice de Facilidade de Leitura (Flesch adaptado ao português, Martins et al., 1996).
    Acima de 75: muito fácil; 50 a 75: fácil; 25 a 50: difícil; abaixo de 25: muito difícil."""
    frases = [f for f in re.split(r"[.!?…:;]+", texto) if f.strip()]
    ws = [w for w in texto.split() if norm(w)]
    if not ws:
        return 100.0, []
    asl = len(ws) / max(1, len(frases))
    asw = sum(_silabas(w) for w in ws) / len(ws)
    longas = [f.strip() for f in frases if len([w for w in f.split() if norm(w)]) > FRASE_MAX]
    return round(248.835 - 1.015 * asl - 84.6 * asw, 1), longas


def legibilidade(roteiro):
    e, av = [], []
    tudo = " ".join(b["texto"] for b in roteiro["blocos"])
    total, _ = ifl(tudo)
    if total < IFL_MIN_TOTAL:
        e.append(erro("Roteirista", f"texto difícil para o público geral (facilidade de leitura {total}, mínimo {IFL_MIN_TOTAL}): "
                                    "use frases mais curtas e palavras do dia a dia"))
    for b in roteiro["blocos"]:
        v, longas = ifl(b["texto"])
        if v < IFL_MIN_BLOCO:
            av.append(f"bloco '{b['id']}' está difícil (facilidade {v}); vale simplificar")
        for f in longas:
            av.append(f"bloco '{b['id']}': frase com mais de {FRASE_MAX} palavras: \"{f[:70]}…\"")
    return e, av, total


def validar_revisao(pasta: Path):
    """Exige o registro da revisão de linguagem feita pelo Gemini."""
    arq = pasta / "revisao_linguagem.json"
    if not arq.exists():
        raise Falha("linguagem", [erro("Coordenador", "falta revisao_linguagem.json: passe o roteiro, os títulos e a legenda do post "
                                                      "pelo Gemini (seção \"Revisão de linguagem\" do AGENTS.md)")])
    r = ler_json(arq)
    e = []
    if str(r.get("ferramenta", "")).lower() != "gemini":
        e.append(erro("Coordenador", "a revisão de linguagem precisa ser feita pelo Gemini ('ferramenta': 'gemini')"))
    faltam = [t for t in ("roteiro", "titulos", "legenda_post") if t not in (r.get("textos_revisados") or [])]
    if faltam:
        e.append(erro("Coordenador", f"a revisão do Gemini não cobriu: {', '.join(faltam)}"))
    try:
        nota = float(r.get("nota_clareza"))
    except (TypeError, ValueError):
        nota = None
    if nota is None or not 1 <= nota <= 10:
        e.append(erro("Coordenador", "'nota_clareza' (de 1 a 10, dada pelo Gemini) está faltando ou inválida"))
    elif nota < 7:
        e.append(erro("Roteirista", f"o Gemini deu nota {nota:g} de clareza; reescreva para ficar mais simples e revise de novo"))
    leg = str(r.get("legenda_post", "")).strip()
    if not leg:
        e.append(erro("Coordenador", "falta 'legenda_post' (a legenda do post, já revisada pelo Gemini)"))
    else:
        if len(leg) > 2200:
            e.append(erro("Roteirista", "a legenda do post passa de 2.200 caracteres"))
        emojis = EMOJI.findall(leg)
        if len(emojis) > 1:
            e.append(erro("Roteirista", "a legenda do post tem mais de um emoji"))
        if emojis and EMOJI.match(leg):
            e.append(erro("Roteirista", "a legenda do post não pode começar com emoji"))
    if e:
        raise Falha("linguagem", e)
    return {"nota_clareza": nota, "mudancas": len(r.get("mudancas") or []), "legenda_post": leg}
