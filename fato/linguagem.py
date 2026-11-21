"""Linguagem para todo público: revisão obrigatória pelo Gemini e índice de facilidade de leitura."""
import re
from pathlib import Path

from . import plataformas
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


def validar_revisao(pasta: Path, roteiro=None):
    """Exige o registro da revisão de linguagem feita pelo Gemini."""
    arq = pasta / "revisao_linguagem.json"
    if not arq.exists():
        raise Falha("linguagem", [erro("Coordenador", "falta revisao_linguagem.json: passe o roteiro, os títulos e a legenda do post "
                                                      "pelo Gemini (seção \"Revisão de linguagem\" do AGENTS.md)")])
    r = ler_json(arq)
    e = []
    if str(r.get("ferramenta", "")).lower() != "gemini":
        e.append(erro("Coordenador", "a revisão de linguagem precisa ser feita pelo Gemini ('ferramenta': 'gemini')"))
    revisados = set(r.get("textos_revisados") or [])
    if "legenda_post" in revisados:   # nome antigo
        revisados.add("publicacao")
    faltam = [t for t in ("roteiro", "titulos", "publicacao") if t not in revisados]
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
    if roteiro is not None:
        e += _chamada_autentica(r, roteiro)
    if e:
        raise Falha("linguagem", e)
    return {"nota_clareza": nota, "mudancas": len(r.get("mudancas") or [])}


# frases dos exemplos do manual: servem de modelo, nunca para copiar
CHAMADAS_DO_MANUAL = [
    "Segue a página pra um fato novo por dia e comenta o que você acha do Brasil envelhecer.",
    "Quer entender o Brasil pelos números? Segue a página. E pra você, um país mais velho preocupa ou não?",
    "Segue pra entender o dinheiro sem complicação. E aí, juro alto assim pesa no seu bolso?",
    "Tem mais curiosidade de games chegando, então segue a gente. Qual jogo antigo você queria ver de volta?",
]
PALAVRAS_VAZIAS = {"a", "o", "as", "os", "de", "do", "da", "dos", "das", "e", "que", "pra", "para", "um", "uma", "voce",
                   "aqui", "no", "na", "nos", "se", "com", "em", "me", "te", "eu", "seu", "sua", "isso", "esse", "essa"}
SIMILAR_MAX = 0.6   # fração de palavras em comum acima da qual a chamada conta como repetida


def _palavras_chave(t):
    return {w for w in re.findall(r"\w+", plataformas._plano(t)) if w not in PALAVRAS_VAZIAS}


def similaridade(a, b):
    pa, pb = _palavras_chave(a), _palavras_chave(b)
    return len(pa & pb) / len(pa | pb) if pa and pb else 0.0


def _chamada_autentica(r, roteiro):
    """A chamada final é escrita para cada vídeo (Gemini propõe opções) e não repete as últimas nem o exemplo do manual."""
    e = []
    chamada = next((b["texto"] for b in roteiro["blocos"] if b["id"] == "chamada"), "")
    opcoes = [str(x) for x in (r.get("chamada_opcoes") or []) if str(x).strip()]
    if len(opcoes) < 3:
        e.append(erro("Coordenador", "faltam as opções de chamada do Gemini: 'chamada_opcoes' precisa de pelo menos 3 "
                                     "(seção \"Revisão de linguagem\" do AGENTS.md)"))
    if "chamadas_recentes" not in r:
        e.append(erro("Coordenador", "falta 'chamadas_recentes' (as chamadas dos últimos 10 vídeos, da coluna 'chamada' do "
                                     "log.csv; lista vazia se ainda não houver)"))
    for velha in list(r.get("chamadas_recentes") or []) + CHAMADAS_DO_MANUAL:
        s = similaridade(chamada, velha)
        if s >= SIMILAR_MAX:
            e.append(erro("Roteirista", f"a chamada final está parecida demais com \"{str(velha)[:80]}\" ({s:.0%} das palavras): "
                                        "escreva uma nova, ligada ao assunto deste vídeo (o Gemini propõe opções)"))
            break
    return e


# hashtags genéricas que não ajudam (ou que as plataformas tratam como spam): não use
HASHTAGS_VAZIAS = {"#fyp", "#foryou", "#foryoupage", "#parati", "#paravoce", "#viral", "#viralvideo", "#explore",
                   "#explorepage", "#trending", "#followme", "#follow", "#like", "#likeforlike", "#l4l", "#f4f", "#tiktok",
                   "#reels", "#instagram", "#xyzbca", "#fy"}
HASHTAG_OK = re.compile(r"^#[0-9a-zà-öø-ÿ_]{2,40}$")


def _hashtags(lista, onde, e, av, minimo=3, maximo=6):
    tags = [str(h).strip().lower() for h in (lista or [])]
    if not minimo <= len(tags) <= maximo:
        e.append(erro("Roteirista", f"{onde}: são {len(tags)} hashtags; o combinado é de {minimo} a {maximo}"))
    if "#thebestnewsbr" not in tags:
        e.append(erro("Roteirista", f"{onde}: falta a hashtag da marca, #thebestnewsbr"))
    for h in tags:
        if not HASHTAG_OK.match(h):
            e.append(erro("Roteirista", f"{onde}: hashtag inválida \"{h}\" (sem espaço, sem acento estranho, começando com #)"))
        if h in HASHTAGS_VAZIAS:
            e.append(erro("Roteirista", f"{onde}: \"{h}\" é genérica e não ajuda o vídeo a ser achado; troque por uma do assunto"))
    if len(set(tags)) != len(tags):
        e.append(erro("Roteirista", f"{onde}: hashtag repetida"))
    return tags


def _descricao(txt, onde, chaves, e, av):
    txt = str(txt or "").strip()
    if not 80 <= len(txt) <= 2200:
        e.append(erro("Roteirista", f"{onde}: a descrição tem {len(txt)} caracteres; o combinado é de 80 a 2.200"))
        return
    pe, pa = plataformas.checar(txt, onde)
    e += [erro("Roteirista", m) for m in pe]
    av += pa
    primeira = txt.splitlines()[0]
    if len(primeira) > 125:
        av.append(f"{onde}: a primeira linha passa de 125 caracteres; ela é o que aparece antes do \"mais\"")
    if chaves and not any(norm(k) in norm(txt) for k in chaves):
        e.append(erro("Roteirista", f"{onde}: a descrição não usa nenhuma das palavras-chave (é o que faz o vídeo aparecer na busca)"))
    if "fonte" not in txt.lower():
        e.append(erro("Roteirista", f"{onde}: a descrição precisa citar as fontes (\"Fontes: ...\")"))
    emojis = EMOJI.findall(txt)
    if len(emojis) > 1:
        e.append(erro("Roteirista", f"{onde}: mais de um emoji (identidade thebestnewsbr: no máximo um)"))
    if emojis and EMOJI.match(txt):
        e.append(erro("Roteirista", f"{onde}: a descrição não pode começar com emoji"))
    if "#" in txt:
        av.append(f"{onde}: há hashtag dentro da descrição; elas vão no campo 'hashtags'")


def validar_publicacao(pasta: Path):
    """Descrição, hashtags e palavras-chave do post (revisados pelo Gemini)."""
    arq = pasta / "publicacao.json"
    if not arq.exists():
        raise Falha("publicacao", [erro("Roteirista", "falta publicacao.json (descrição, hashtags e palavras-chave do post; "
                                                      "veja a seção \"Publicação\" do AGENTS.md)")])
    p = ler_json(arq)
    e, av = [], []
    chaves = [str(k) for k in (p.get("palavras_chave") or [])]
    if not 3 <= len(chaves) <= 6:
        e.append(erro("Roteirista", f"são {len(chaves)} palavras-chave; o combinado é de 3 a 6"))
    _descricao(p.get("descricao"), "descrição", chaves, e, av)
    tags = _hashtags(p.get("hashtags"), "hashtags", e, av)
    if not str(p.get("fonte_hashtags", "")).strip():
        e.append(erro("Roteirista", "falta 'fonte_hashtags' (onde as hashtags em alta foram pesquisadas, com data)"))
    for plat, v in (p.get("por_plataforma") or {}).items():
        if plat not in ("tiktok", "instagram", "facebook"):
            e.append(erro("Roteirista", f"plataforma desconhecida em por_plataforma: {plat}"))
            continue
        if v.get("descricao"):
            _descricao(v["descricao"], f"descrição do {plat}", chaves, e, av)
        if v.get("hashtags"):
            _hashtags(v["hashtags"], f"hashtags do {plat}", e, av)
    if e:
        raise Falha("publicacao", e, av)
    return {"hashtags": tags, "palavras_chave": chaves, "avisos": av}
