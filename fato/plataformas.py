"""Regras do TikTok e do Instagram para o que o público lê ou ouve (narração, títulos, chamada e descrição).

As duas plataformas tiram do "Para você"/"Explorar" (e recusam como anúncio) o que:
- pede interação de forma explícita para ganhar alcance ("isca de engajamento": manda pra alguém, compartilha,
  marca um amigo, comenta SIM, curte se...);
- parece oferta de emprego, renda, crédito ou benefício sem dizer qual é, quanto paga e como se inscreve
  (a política de anúncios de Meta e TikTok trata isso como "oportunidade irreal/enganosa");
- usa manchete que o vídeo não sustenta (URGENTE, CHOCANTE, "ninguém te conta").
Detalhes e fontes na seção "Regras das plataformas" do AGENTS.md.
"""
import re
import unicodedata

# (padrão, motivo). Erro: volta para o agente corrigir.
ISCA = [
    (r"\bmand(a|e|em)\b (isso|esse video|este video|o video|esse|este|(pra|para) (alguem|quem|seus?|suas?|um amigo|uma amiga|amig[oa]s|familia|galera|todo mundo))\b",
     "pede para mandar o vídeo a alguém"),
    (r"\b(compartilh|encaminh|repost)\w* (esse video|este video|o video|isso|com (alguem|quem|seus?|suas?|um amigo|uma amiga|amig[oa]s|familia|a galera|todo mundo))\b",
     "pede para compartilhar"),
    (r"\b(marca|marque|marquem) (ai |aqui )?(alguem|um amigo|uma amiga|amig[oa]s|quem|aquele|aquela|seu amigo|sua amiga|o amigo|a amiga)\b", "pede para marcar alguém"),
    (r"\b(curt(a|e|am)\b.{0,10}\b(se|esse|este|o video|ai|aqui)\b|deix(a|e) (seu|o|um) like|\bda (um )?like)",
     "pede curtida"),
    (r"\b(coment(a|e|em)|digit(a|e)|escrev(a|e))\b.{0,25}\b(sim|nao|eu quero|quero|\d+|um emoji|um coracao)\b",
     "pede comentário com palavra combinada"),
    (r"\bsalv(a|e|em)\b.{0,25}\b(pra|para|esse|este|o video|ai|depois)\b", "pede para salvar"),
    (r"\b(segue|siga|sigam)\b.{0,20}\b(parte \d|parte dois|pra saber o resto|para saber o resto)\b",
     "promete continuação para ganhar seguidor"),
    (r"\blink na bio\b", "manda para link na bio (o vídeo não tem link)"),
]
OPORTUNIDADE = [
    (r"\bquem (procura|busca|esta procurando|esta buscando|precisa de|quer|esta sem)\b.{0,15}"
     r"\b(emprego|trabalho|vaga|renda|dinheiro|credito|emprestimo|beneficio)\b",
     "fala com quem procura emprego/renda como se o vídeo oferecesse a oportunidade"),
    (r"\b(vagas? abertas?|esta contratando|estao contratando|inscricoes abertas|inscreva-?se ja|ganhe dinheiro|"
     r"renda extra|dinheiro gratis|dinheiro esquecido|saque (ja|agora|hoje)|receba (ja|agora|hoje|ate)|garanta (ja|o seu|a sua))\b",
     "parece anúncio de vaga, renda ou benefício"),
]
# Aviso: o Revisor confere se o vídeo sustenta.
SENSACIONALISMO = [
    (r"\b(urgente|chocante|bomba|absurdo|inacreditavel|ninguem te conta|ninguem fala|a midia esconde|"
     r"querem esconder|acabou de sair|100% garantido)\b", "termo sensacionalista"),
]


def _plano(s):
    s = unicodedata.normalize("NFD", str(s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^\w%\- ]+", " ", s)).strip()


def checar(texto, onde):
    """Devolve (erros, avisos) em texto simples para o trecho `onde`."""
    t = _plano(texto)
    erros, avisos = [], []
    for lista, saida in ((ISCA, erros), (OPORTUNIDADE, erros), (SENSACIONALISMO, avisos)):
        for padrao, motivo in lista:
            m = re.search(padrao, t)
            if m:
                saida.append(f"{onde}: {motivo} (\"{m.group(0)}\"). Regras das plataformas no AGENTS.md")
    return erros, avisos


# palavras que não dizem de qual parte do vídeo se pede a opinião
VAGAS = {"de", "do", "da", "dos", "das", "sobre", "disso", "isso", "tudo", "aqui", "ai", "nos", "comentarios", "video",
         "esse", "este", "assunto", "noticia", "o", "a", "os", "as", "que", "voce", "acha", "pensa"}


def chamada_completa(texto):
    """A chamada final precisa convidar a seguir a página e pedir a opinião sobre um ponto do vídeo.
    Devolve a lista do que falta (vazia = ok)."""
    t = _plano(texto)
    falta = []
    if not re.search(r"\b(segue|siga|sigam|seguir|seguindo)\b", t):
        falta.append("o convite para seguir a página")
    # opinião: "comenta/conta/diz o que você acha/pensa de X" ou uma pergunta (com "?") sobre um ponto concreto
    pedidos = [m.groups()[-1] for m in re.finditer(r"\b(coment(a|e|em)|conta|diz)\b.{0,30}\b(acha|pensa|opiniao)\b(.*)", t)]
    pedidos += [_plano(q) for q in re.findall(r"[^.!?]*\?", str(texto or ""))]
    if not pedidos:
        falta.append("o pedido de opinião (uma pergunta ao público ou \"comenta o que você acha de…\")")
    elif not any(len([w for w in re.findall(r"\w+", p) if w not in VAGAS]) >= 2 for p in pedidos):
        falta.append("o assunto da opinião: diga de qual parte do vídeo (\"o que você acha disso\" é vago)")
    return falta
