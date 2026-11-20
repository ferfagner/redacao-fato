"""Confere os arquivos que os agentes entregam, antes de gastar voz e render.

Cada erro diz para qual agente volta (Checador, Roteirista ou Diretor).
"""
import re

from .comum import BLOCOS, FAMILIAS, LICENCAS_IMAGEM, POSES, UFS, Falha, erro, norm, palavras, rodar

# faixas de palavras por bloco do roteiro (mínimo, máximo)
FAIXAS = {"gancho": (8, 12), "fato": (26, 32), "mecanismo": (66, 74), "virada": (26, 32),
          "ressalva": (20, 26), "chamada": (8, 12)}
TOTAL = (165, 180)  # ~3 palavras por segundo na voz Antonio a 0%
TOLERANCIA = 2  # palavras de folga por bloco antes de virar erro


def validar_ficha(f):
    e = []
    if not isinstance(f, dict):
        raise Falha("ficha", [erro("Checador", "a ficha precisa ser um objeto JSON")])
    if f.get("vetado"):
        raise Falha("ficha", [erro("Checador", "pauta vetada: " + str(f.get("motivo", "sem motivo")))])
    if not str(f.get("fato", "")).strip():
        e.append(erro("Checador", "falta 'fato' (o fato em uma frase)"))
    fontes = f.get("fontes") or []
    if len(fontes) < 2:
        e.append(erro("Checador", "são necessárias duas fontes independentes em 'fontes'"))
    dominios = set()
    for i, fo in enumerate(fontes, 1):
        for campo in ("url", "instituicao", "ano"):
            if not fo.get(campo):
                e.append(erro("Checador", f"fonte {i}: falta '{campo}'"))
        m = re.match(r"https?://([^/]+)", str(fo.get("url", "")))
        if m:
            dominios.add(m.group(1).lower().removeprefix("www."))
    if len(fontes) >= 2 and len(dominios) < 2:
        e.append(erro("Checador", "as duas fontes têm o mesmo domínio: não são independentes"))
    for i, n in enumerate(f.get("numeros") or [], 1):
        for campo in ("valor", "ano", "instituicao"):
            if not n.get(campo):
                e.append(erro("Checador", f"número {i}: falta '{campo}' (número sem ano e instituição não passa)"))
    if not f.get("fonte_tela"):
        e.append(erro("Checador", "falta 'fonte_tela' (ex.: \"IBGE, 2024\")"))
    if e:
        raise Falha("ficha", e)


def validar_roteiro(r):
    e, av = [], []
    blocos = (r or {}).get("blocos") or []
    ids = [b.get("id") for b in blocos]
    if ids != BLOCOS:
        raise Falha("roteiro", [erro("Roteirista", f"os blocos precisam ser, nesta ordem: {', '.join(BLOCOS)} (veio: {ids})")])
    total = 0
    for b in blocos:
        n = len(palavras(b.get("texto", "")))
        total += n
        lo, hi = FAIXAS[b["id"]]
        if n < lo - TOLERANCIA or n > hi + TOLERANCIA:
            e.append(erro("Roteirista", f"bloco '{b['id']}' tem {n} palavras; o combinado é {lo} a {hi}"))
        elif n < lo or n > hi:
            av.append(f"bloco '{b['id']}' tem {n} palavras (faixa {lo} a {hi})")
        if "(" in b.get("texto", ""):
            e.append(erro("Roteirista", f"bloco '{b['id']}': tire os parênteses, a voz lê tudo o que está escrito"))
        if re.search(r"\d", b.get("texto", "")):
            av.append(f"bloco '{b['id']}' tem algarismos; a voz costuma ler melhor números por extenso")
    if b := blocos[0]:
        if b["texto"].strip().endswith("?"):
            e.append(erro("Roteirista", "o gancho não pode ser uma pergunta"))
    if not (TOTAL[0] - 5 <= total <= TOTAL[1] + 5):
        e.append(erro("Roteirista", f"o roteiro tem {total} palavras; o combinado é {TOTAL[0]} a {TOTAL[1]}"))
    if e:
        raise Falha("roteiro", e, av)
    return av


BANCOS_PROIBIDOS = ("gettyimages", "shutterstock", "alamy", "apimages", "reuters.com", "afp.com", "istockphoto",
                    "dreamstime", "123rf", "depositphotos", "adobestock", "stock.adobe", "google.com/imgres", "pinterest")
TIPOS_IMAGEM = ("pessoa", "jogo", "lugar", "objeto", "evento")


def validar_imagem(i, im, pasta):
    """Foto só entra com licença que permite o uso, crédito na tela e origem rastreável."""
    e = []
    if not isinstance(im, dict):
        return [erro("Diretor", "foto precisa de 'imagem' com arquivo, credito, licenca, url_origem e tipo", i)]
    for campo in ("arquivo", "credito", "licenca", "url_origem", "tipo"):
        if not str(im.get(campo, "")).strip():
            e.append(erro("Diretor", f"imagem sem '{campo}'", i))
    lic = norm(str(im.get("licenca", "")))
    if im.get("licenca") and not any(lic.startswith(norm(x)) for x in LICENCAS_IMAGEM):
        e.append(erro("Diretor", f"licença '{im.get('licenca')}' não serve; use só: {', '.join(LICENCAS_IMAGEM)}", i))
    url = str(im.get("url_origem", "")).lower()
    if url and not url.startswith(("http://", "https://")):
        e.append(erro("Diretor", "url_origem precisa ser o link da página da imagem", i))
    if any(b in url for b in BANCOS_PROIBIDOS):
        e.append(erro("Diretor", "imagem de banco pago, agência ou buscador não pode; procure no Wikimedia Commons ou no kit de imprensa oficial", i))
    if im.get("tipo") and im["tipo"] not in TIPOS_IMAGEM:
        e.append(erro("Diretor", f"tipo de imagem '{im['tipo']}' não existe ({', '.join(TIPOS_IMAGEM)})", i))
    if len(str(im.get("credito", ""))) > 80:
        e.append(erro("Diretor", "o crédito passa de 80 caracteres; resuma (ex.: \"Foto: Nome / Wikimedia Commons, CC BY-SA 4.0\")", i))
    if len(str(im.get("nome", ""))) > 26:
        e.append(erro("Diretor", "o nome na foto passa de 26 caracteres", i))
    if pasta is not None and im.get("arquivo"):
        arq = (pasta / im["arquivo"]).resolve()
        if not arq.exists():
            e.append(erro("Diretor", f"arquivo de imagem não encontrado: {im['arquivo']}", i))
        elif arq.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            e.append(erro("Diretor", "a imagem precisa ser JPG, PNG ou WEBP", i))
        elif arq.stat().st_size > 12 * 1024 * 1024:
            e.append(erro("Diretor", "a imagem passa de 12 MB; baixe uma versão menor", i))
        else:
            try:
                r = rodar("ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", arq)
                w, h = (int(x) for x in r.stdout.strip().split(",")[:2])
                if max(w, h) < 600:
                    e.append(erro("Diretor", f"imagem pequena demais ({w}x{h}); o mínimo é 600 px no lado maior", i))
            except Exception:
                e.append(erro("Diretor", "não consegui ler a imagem (arquivo corrompido?)", i))
    return e


def validar_cenas(c, roteiro, ficha, pasta=None):
    e, av = [], []
    cenas = (c or {}).get("cenas") or []
    if not 9 <= len(cenas) <= 14:
        e.append(erro("Diretor", f"são {len(cenas)} cenas; o combinado é de 9 a 14 (ideal: 11 a 13)"))
    texto_bloco = {b["id"]: " ".join(norm(w) for w in palavras(b["texto"])) for b in roteiro["blocos"]}
    numeros_ficha = " ".join(str(n.get("valor", "")) for n in ficha.get("numeros") or [])
    ultimo_bloco = 0
    for i, s in enumerate(cenas, 1):
        cid = s.get("id")
        if cid != i:
            e.append(erro("Diretor", f"a cena na posição {i} tem id {cid}; os ids vão de 1 em 1", i))
        fam, bloco = s.get("familia"), s.get("bloco")
        if fam not in FAMILIAS:
            e.append(erro("Diretor", f"família '{fam}' não existe ({', '.join(FAMILIAS)})", i))
        if bloco not in BLOCOS:
            e.append(erro("Diretor", f"bloco '{bloco}' não existe", i))
            continue
        bi = BLOCOS.index(bloco)
        if bi < ultimo_bloco:
            e.append(erro("Diretor", "as cenas precisam seguir a ordem dos blocos do roteiro", i))
        ultimo_bloco = bi
        tit = s.get("titulo")
        if isinstance(tit, str):
            tit = [tit]
        if not tit or not all(isinstance(x, str) and x.strip() for x in tit):
            e.append(erro("Diretor", "falta 'titulo' (lista de linhas)", i))
            continue
        if len(tit) > 3:
            e.append(erro("Diretor", f"título com {len(tit)} linhas; o máximo é 3", i))
        for ln in tit:
            if len(ln.split()) > 4:
                e.append(erro("Diretor", f"a linha \"{ln}\" tem mais de 4 palavras", i))
            if len(ln) > 22:
                e.append(erro("Diretor", f"a linha \"{ln}\" tem {len(ln)} caracteres; o máximo é 22", i))
        npal = sum(len(ln.split()) for ln in tit)
        if npal > 9:
            e.append(erro("Diretor", f"título com {npal} palavras; o máximo é 9", i))
        dest = s.get("destaque")
        if dest and norm(dest) not in [norm(w) for ln in tit for w in ln.split()] and norm(dest) not in norm(" ".join(tit)):
            e.append(erro("Diretor", f"o destaque \"{dest}\" não está no título", i))
        tem_dado = bool(s.get("dado")) or bool(s.get("comparacao"))
        if fam == "numero_heroi" and not (s.get("dado") or {}).get("valor"):
            e.append(erro("Diretor", "numero_heroi precisa de 'dado' com 'valor'", i))
        if fam == "dado_comparado":
            comp = s.get("comparacao") or []
            if not 2 <= len(comp) <= 4:
                e.append(erro("Diretor", "dado_comparado precisa de 2 a 4 itens em 'comparacao'", i))
            for it in comp:
                if not it.get("rotulo") or _numero(it.get("valor")) is None:
                    e.append(erro("Diretor", "cada item de 'comparacao' precisa de 'rotulo' e 'valor' numérico", i))
        if fam == "mapa_brasil":
            m = s.get("mapa") or {}
            vals, dests = m.get("valores") or {}, m.get("destaques") or ([m["destaque"]] if m.get("destaque") else [])
            if not vals and not dests:
                e.append(erro("Diretor", "mapa_brasil precisa de 'mapa' com 'valores' (UF: número) ou 'destaques' (lista de UFs)", i))
            ruins = [u for u in list(vals) + list(dests) if str(u).upper() not in UFS]
            if ruins:
                e.append(erro("Diretor", f"UF desconhecida no mapa: {', '.join(map(str, ruins))}", i))
            if any(_numero(v) is None for v in vals.values()):
                e.append(erro("Diretor", "todo valor do mapa precisa ser numérico (ex.: \"44,4\")", i))
            if vals:
                tem_dado = True
        if fam == "mapa_lugar":
            lg = s.get("lugar") or {}
            try:
                ok = lg.get("nome") and -90 <= float(lg["lat"]) <= 90 and -180 <= float(lg["lon"]) <= 180
            except (KeyError, TypeError, ValueError):
                ok = False
            if not ok:
                e.append(erro("Diretor", "mapa_lugar precisa de 'lugar' com 'nome', 'lat' e 'lon' (graus decimais)", i))
            elif len(str(lg["nome"])) > 24:
                e.append(erro("Diretor", "o nome do lugar passa de 24 caracteres", i))
        if fam == "foto":
            e += validar_imagem(i, s.get("imagem"), pasta)
        if fam == "objeto_profundidade":
            obj = s.get("objeto", "globo")
            objetos = ("globo", "cubo", "aneis", "moedas", "podio", "planeta", "barras")
            if obj not in objetos:
                e.append(erro("Diretor", f"objeto '{obj}' não existe ({', '.join(objetos)})", i))
            comp = s.get("comparacao") or []
            if obj == "barras" and not (2 <= len(comp) <= 4 and all(_numero(x.get("valor")) is not None and x.get("rotulo") for x in comp)):
                e.append(erro("Diretor", "objeto 'barras' precisa de 2 a 4 itens em 'comparacao', com 'rotulo' e 'valor' numérico", i))
            if obj == "podio" and not (len(comp) == 3 and all(x.get("rotulo") for x in comp)):
                e.append(erro("Diretor", "objeto 'podio' precisa de exatamente 3 itens em 'comparacao' (1º, 2º e 3º), com 'rotulo'", i))
            if obj == "podio":
                for x in comp:
                    if len(str(x.get("rotulo", ""))) > 16:
                        e.append(erro("Diretor", f"rótulo do pódio \"{x.get('rotulo')}\" passa de 16 caracteres", i))
        pers = s.get("personagem")
        if pers and (pers.get("pose") not in POSES):
            e.append(erro("Diretor", f"pose do personagem desconhecida: {pers.get('pose')} ({', '.join(POSES)})", i))
        if (tem_dado or fam == "citacao_fonte") and not s.get("fonte"):
            e.append(erro("Diretor", "cena com dado ou citação precisa de 'fonte'", i))
        if s.get("dado") and s["dado"].get("valor"):
            dig = re.sub(r"\D", "", str(s["dado"]["valor"]))
            if dig and dig not in re.sub(r"\D", "", numeros_ficha):
                av.append(f"cena {i}: o número {s['dado']['valor']} não aparece na ficha do Checador")
        anc = s.get("ancora")
        if i > 1:
            if not anc:
                e.append(erro("Diretor", "falta 'ancora' (a palavra falada em que a cena entra)", i))
            elif norm(" ".join(anc.split())) and not all(norm(w) in texto_bloco[bloco].split() for w in anc.split()):
                e.append(erro("Diretor", f"a âncora \"{anc}\" não está no bloco '{bloco}' do roteiro", i))
    if cenas:
        if cenas[0].get("bloco") != "gancho" or cenas[0].get("familia") != "tipo_cinetico":
            e.append(erro("Diretor", "a cena 1 precisa ser do bloco 'gancho' e da família 'tipo_cinetico'", 1))
        if cenas[-1].get("familia") != "fecho_chamada":
            e.append(erro("Diretor", "a última cena precisa ser da família 'fecho_chamada'", len(cenas)))
        usados = {s.get("bloco") for s in cenas}
        falta = [b for b in BLOCOS if b not in usados]
        if falta:
            e.append(erro("Diretor", f"nenhuma cena para o(s) bloco(s): {', '.join(falta)}"))
        n3d = sum(1 for s in cenas if s.get("familia") in ("objeto_profundidade", "mapa_brasil", "mapa_lugar"))
        if n3d < 2:
            av.append(f"só {n3d} cena(s) com objeto 3D ou mapa; o combinado é de 2 a 4 por vídeo")
    if e:
        raise Falha("cenas", e, av)
    return av


def _numero(v):
    """'1.234,5' -> 1234.5 ; '99' -> 99 ; texto -> None"""
    s = str(v or "").strip().replace(" ", "")
    if not re.fullmatch(r"[\d.,]+", s):
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") >= 1 and all(len(p) == 3 for p in s.split(".")[1:]):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None
