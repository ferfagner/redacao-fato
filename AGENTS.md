# Manual dos agentes: Redação Fato (thebestnewsbr)

Este repositório transforma três arquivos JSON num vídeo vertical de 60 s. Os agentes decidem o conteúdo. O código faz a voz, a montagem, a checagem e o render. **Nenhum agente escreve HTML, mexe no modelo ou improvisa outro renderizador.** Se algo falhar, devolva a quem o relatório indica.

## Pasta da pauta

Cada vídeo tem uma pasta própria, por exemplo `pautas/2026-11-21-censo/`, com três arquivos:

| arquivo | quem escreve | conteúdo |
|---|---|---|
| `ficha.json` | Checador | o fato, os números e as duas fontes |
| `roteiro.json` | Roteirista | a narração em 6 blocos |
| `cenas.json` | Diretor | de 9 a 11 cenas |

Veja o exemplo completo em `exemplos/teste-acervo/`.

## Comandos

Rode sempre na raiz do repositório:

```bash
python -m fato validar pautas/2026-11-21-censo   # segundos: confere os três arquivos
python -m fato revisar pautas/2026-11-21-censo   # cerca de 1 min: voz, projeto, checagem e folha de quadros
python -m fato render  pautas/2026-11-21-censo   # cerca de 3 min: vídeo final e conferência
```

Cada comando grava `saida/relatorio.json` e termina com um destes códigos:

| código | significado | o que fazer |
|---|---|---|
| 0 | ok | seguir |
| 2 | volta para um agente | cada item de `erros` tem `para` (Checador, Roteirista ou Diretor), a `msg` e, quando for o caso, a `cena`. Mande só esses itens para quem corrige. |
| 1 | falha técnica | não é culpa de nenhum agente. Leia `falha_tecnica`, rode de novo uma vez e, se repetir, mova o card para "Precisa de você". |

O que fica em `saida/`:
- `narracao.wav`
- `legendas.srt`
- `tempos.json`
- `projeto/` (o projeto HyperFrames, que abre no Studio com `npx hyperframes preview`)
- `folha.png` e `quadros/cenaNN.png`
- `check.json`
- `video.mp4`
- `entrega/`: os dois arquivos que vão para o Google Drive (`<pasta>.mp4` e `<pasta>.txt`)

## Fluxo

1. O **Checador** grava `ficha.json`.
2. O **Roteirista** grava `roteiro.json`.
3. O **Diretor** grava `cenas.json`.
4. O **Roteirista** grava `publicacao.json`, com a descrição do post, as hashtags em alta e as palavras-chave. Veja a seção "Publicação".
5. **Revisão de linguagem pelo Gemini** (obrigatória): o roteiro, os títulos das cenas e a publicação passam pelo Gemini, e o resultado fica em `revisao_linguagem.json`. Veja a seção "Revisão de linguagem".
6. Rode `validar`. Se der código 2, devolva os erros e rode de novo, no máximo duas vezes por agente.
7. **Revisor, etapa A:** lê a ficha, o roteiro e as cenas.
8. Rode `revisar`. Se der código 2, devolva os erros (por exemplo, a narração ficou longa ou uma cena ficou curta).
9. **Revisor, etapa B:** abre `saida/folha.png` (uma imagem por cena, já com legenda e fonte) e `saida/legendas.srt`, e responde "aprovado" ou uma lista numerada de correções por cena.
10. Só depois do "aprovado" da etapa B, rode `render`. Se `ok` vier `false`, os `problemas` dizem o que conferir: duração, resolução, áudio ou volume.
11. **Não publique em rede nenhuma.** O `render` deixa em `saida/entrega/` só dois arquivos: o vídeo (`<pasta>.mp4`) e a descrição com as hashtags (`<pasta>.txt`). Salve os dois numa pasta nova do Google Drive (`thebestnewsbr/videos/AAAA-MM-DD - <tema>`).

## Publicação: descrição, hashtags e palavras-chave (Roteirista)

TikTok e Instagram funcionam como buscadores. A descrição e as hashtags decidem para quem o vídeo aparece e se ele é achado na busca. O Roteirista grava `publicacao.json`, que passa pelo Gemini junto com o roteiro.

**1. Pesquise as hashtags em alta no navegador, sem login:**
- **TikTok Creative Center → Hashtags populares:** https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/pt, com região **Brasil** e período de **7 dias**. Veja as que têm a ver com o assunto e com a categoria.
- **Busca do TikTok e do Instagram:** digite o assunto, veja as hashtags que os vídeos com mais visualizações usam e quantos posts cada uma tem.
- **Google Trends** (https://trends.google.com.br, Brasil, 7 dias): mostra como o público escreve o assunto. Isso alimenta as palavras-chave.

**2. Monte de 3 a 6 hashtags, nesta mistura:**
- `#thebestnewsbr`, sempre;
- 1 ou 2 do **assunto específico** (`#censo2022`, `#minecraft`, `#jameswebb`);
- 1 ou 2 da **categoria**, com volume médio (`#curiosidades`, `#ciencia`, `#games`, `#brasil`);
- no máximo 1 **em alta**, só se tiver relação direta com o assunto.

Proibido:
- hashtag em alta sem relação com o vídeo (engana o público e as plataformas punem);
- hashtag genérica que não ajuda: `#fyp`, `#foryou`, `#parati`, `#viral`, `#explore`, `#trending` e similares. O validador recusa.

**3. Escreva a descrição:**
1. **Primeira linha**, com até 125 caracteres, que é o que aparece antes do "mais": o gancho com uma palavra-chave.
2. **De 2 a 3 frases curtas** contando o fato em linguagem simples, com o dado principal.
3. **Uma pergunta ou chamada** que puxe comentário ou salvamento, sem prometer o que o vídeo não entrega.
4. **`Fontes: …`** no fim.

Use no máximo um emoji, nunca no começo, e sem hashtag no meio do texto.

**4. Palavras-chave:** de 3 a 6 termos que as pessoas digitam na busca (`"censo 2022"`, `"população do brasil"`). Pelo menos uma precisa aparecer na descrição.

```json
{
  "descricao": "O Brasil nunca cresceu tão devagar, e o Censo 2022 mostra o porquê.

Somos 203 milhões de pessoas, só 6,5% a mais que em 2010. As famílias encolheram e o país está envelhecendo.

Você sabia disso? Salva pra mostrar pra alguém 👀

Fontes: IBGE; Agência Brasil",
  "hashtags": ["#thebestnewsbr", "#censo2022", "#ibge", "#curiosidades", "#brasil"],
  "palavras_chave": ["censo 2022", "população do brasil", "ibge"],
  "fonte_hashtags": "TikTok Creative Center (Brasil, 7 dias) e busca do TikTok, 21/11/2026",
  "por_plataforma": {
    "tiktok": {"hashtags": ["#thebestnewsbr", "#censo2022", "#curiosidades", "#aprendanotiktok"]}
  }
}
```

`por_plataforma` é opcional e serve para quando uma rede pede hashtags ou texto diferentes. O que não estiver nele usa `descricao` e `hashtags`.

O validador confere:
- a descrição tem de 80 a 2.200 caracteres, cita as fontes, usa uma palavra-chave e tem no máximo um emoji, fora do começo;
- são de 3 a 6 hashtags, com `#thebestnewsbr`, sem as genéricas proibidas e sem repetição;
- são de 3 a 6 palavras-chave;
- `fonte_hashtags` informa onde e quando as hashtags foram pesquisadas.

## Revisão de linguagem (Gemini, obrigatória)

Todo texto que o público vai ler ou ouvir passa pelo Gemini antes de virar vídeo: a narração (`roteiro.json`), os títulos e rótulos das cenas (`cenas.json`) e a legenda do post. O objetivo é que **qualquer pessoa entenda de primeira, ouvindo uma vez só**: do adolescente ao idoso, com qualquer escolaridade.

**Como fazer:** mande ao Gemini, pela conexão da conta, o prompt abaixo com os textos colados no fim. Aplique as mudanças nos arquivos e grave `revisao_linguagem.json` na pasta da pauta. Se o Gemini sugerir algo que quebre uma regra (mudar um número, inventar um fato, passar do limite de palavras), descarte a sugestão e registre o motivo.

```text
Você revisa a linguagem de vídeos curtos de fatos para o público geral brasileiro: de adolescentes a idosos, com qualquer escolaridade. A pessoa vai OUVIR a narração uma vez só, no celular, e ler títulos curtos na tela.

Reescreva o que for preciso para que qualquer pessoa entenda de primeira:
- troque palavra difícil, técnica, estrangeira ou sigla por palavra do dia a dia; se o termo for essencial, explique em poucas palavras;
- frases de até 15 palavras na narração, uma ideia por frase, na voz ativa;
- sem gíria regional ou de nicho, sem ironia que possa ser mal entendida e sem duplo sentido;
- números do jeito que se fala ("duzentos e três milhões"), sem parênteses;
- não acrescente nem retire fatos, números, nomes, datas ou fontes;
- mantenha o número de palavras de cada bloco da narração (no máximo 3 a mais ou a menos);
- títulos com no máximo 4 palavras por linha, até 3 linhas e 9 palavras no total, em caixa alta;
- descrição do post: primeira linha com o gancho e uma palavra-chave (até 125 caracteres), frases curtas, no máximo um emoji e nunca no começo, fontes no fim;
- hashtags e palavras-chave: diga se alguma não tem relação com o assunto ou é genérica demais (não invente hashtags novas).

Responda só com JSON, neste formato:
{"roteiro": {"gancho": "...", "fato": "...", "mecanismo": "...", "virada": "...", "ressalva": "...", "chamada": "..."},
 "titulos": [{"cena": 1, "titulo": ["...", "..."]}],
 "publicacao": {"descricao": "...", "hashtags_sem_relacao": []},
 "mudancas": [{"onde": "roteiro.mecanismo", "antes": "...", "depois": "...", "motivo": "..."}],
 "nota_clareza": 9}

TEXTOS:
<cole aqui o roteiro (6 blocos), os títulos de cada cena e o publicacao.json>
```

**`revisao_linguagem.json`** (o validador confere):

```json
{
  "ferramenta": "gemini",
  "data": "2026-11-21",
  "textos_revisados": ["roteiro", "titulos", "publicacao"],
  "nota_clareza": 9,
  "mudancas": [{"onde": "roteiro.mecanismo", "antes": "taxa de fecundidade", "depois": "número de filhos por mulher", "motivo": "termo técnico"}],
  "descartadas": [{"sugestao": "...", "motivo": "mudava o número da ficha"}]
}
```

O validador confere:
- **Revisão registrada:** `ferramenta` é `gemini`, e `textos_revisados` inclui `roteiro`, `titulos` e `publicacao`.
- **Nota de clareza:** `nota_clareza` vai de 1 a 10. Abaixo de 7, volta para o Roteirista reescrever.
- **Narração:** o próprio validador mede a facilidade de leitura (índice Flesch adaptado ao português). Frase com mais de 20 palavras gera aviso, e texto difícil volta para o Roteirista.

## ficha.json (Checador)

```json
{
  "fato": "o fato em uma frase",
  "numeros": [{"valor": "203,1", "unidade": "milhões de habitantes", "ano": 2022, "instituicao": "IBGE"}],
  "fontes": [
    {"url": "https://…", "instituicao": "IBGE", "ano": 2023},
    {"url": "https://… (outro domínio)", "instituicao": "…", "ano": 2023}
  ],
  "confianca": "alto",
  "fonte_tela": "IBGE, Censo 2022",
  "categoria": "brasil"
}
```

- Pauta vetada: `{"vetado": true, "motivo": "uma linha"}`.
- `categoria` é uma destas: `ciencia`, `brasil`, `tecnologia`, `games` ou `mundo`. Ela vem do Radar e define a trilha musical do vídeo.
- As duas fontes precisam ser de domínios diferentes.
- Todo número precisa de valor, ano e instituição.

## roteiro.json (Roteirista)

São seis blocos, nesta ordem e com estes ids. O total vai de 165 a 180 palavras, o que dá de 58 a 65 s na voz `pt-BR-AntonioNeural`.

| id | palavras | conteúdo |
|---|---|---|
| `gancho` | 8 a 12 | promessa concreta, nunca uma pergunta |
| `fato` | 26 a 32 | o dado, com a instituição |
| `mecanismo` | 66 a 74 | o porquê |
| `virada` | 26 a 32 | o que quase ninguém sabe |
| `ressalva` | 20 a 26 | o limite do dado |
| `chamada` | 8 a 12 | pedido para enviar ou salvar |

```json
{"blocos": [{"id": "gancho", "texto": "…"}, {"id": "fato", "texto": "…"}, {"id": "mecanismo", "texto": "…"},
            {"id": "virada", "texto": "…"}, {"id": "ressalva", "texto": "…"}, {"id": "chamada", "texto": "…"}]}
```

- Escreva como se fala: os números vão por extenso ("duzentos e três milhões"), sem parênteses nem siglas soletradas.
- **Retenção.** O vídeo precisa prender até o fim:
  - o gancho abre uma pergunta que só se responde na virada (um "loop aberto");
  - o `mecanismo` e a `virada` começam com uma frase-ponte que reabre a curiosidade, por volta de 15 s e de 35 s. Exemplos: "Mas tem um detalhe.", "E aqui vem a parte estranha.", "Só que ninguém conta isso.";
  - a frase-ponte nunca pode mentir: o que ela promete aparece logo depois.
- A voz começa na velocidade normal. Se o vídeo passar de 65 s, ela acelera até +20%. Se ainda assim não couber, o relatório pede o corte e diz quantas palavras tirar.

## cenas.json (Diretor)

```json
{
  "tema": "título interno do vídeo",
  "cenas": [
    {"id": 1, "bloco": "gancho", "familia": "tipo_cinetico", "titulo": ["O BRASIL NUNCA", "CRESCEU TÃO", "DEVAGAR"], "destaque": "DEVAGAR"},
    {"id": 2, "bloco": "fato", "familia": "numero_heroi", "titulo": ["NO ÚLTIMO CENSO"],
     "dado": {"valor": "203", "unidade": "milhões de pessoas", "rotulo": "População em 2022"},
     "fonte": "IBGE, Censo 2022", "ancora": "Censo"}
  ]
}
```

Regras que o validador confere:
- De 9 a 14 cenas (ideal: **11 a 13**, de 3 a 6 s cada), com ids 1, 2, 3… e na ordem dos blocos. Todo bloco tem pelo menos uma cena. Cena acima de 6,5 s gera aviso, e acima de 9 s volta para o Diretor.
- A cena 1 é `gancho` + `tipo_cinetico`: aparece na caixa azul já no primeiro quadro, que é a capa do vídeo. A última cena é `fecho_chamada`.
- `titulo`: lista de até 3 linhas, cada uma com até 4 palavras e 22 caracteres, e no máximo 9 palavras no total. Escreva em caixa alta.
- `destaque`: uma palavra do título, que fica em amarelo e pulsa quando é falada.
- `ancora`: a palavra (ou palavras) da narração, do mesmo bloco, em que a cena começa. É obrigatória a partir da cena 2. Cada cena fica com 1,6 a 9 s; se ficar fora disso, o relatório pede para trocar a âncora ou dividir a cena.
- `fonte` é obrigatória em toda cena com `dado`, com `comparacao` ou da família `citacao_fonte`. Aparece na placa "FONTE".

As famílias e seus campos extras:

| família | uso | campos extras |
|---|---|---|
| `tipo_cinetico` | frase forte, palavra a palavra | `rotulo` (opcional) |
| `numero_heroi` | um número grande que conta até o valor | `dado: {valor, unidade, rotulo}` |
| `dado_comparado` | 2 a 4 barras | `comparacao: [{rotulo, valor, unidade}]`, com `valor` numérico ("190,8") |
| `objeto_profundidade` | objeto 3D com o título | `objeto`: um dos 28 desenhados em código (tabela "Acervo de objetos 3D") **ou** um dos 54 modelos realistas, com `"modelo:<nome>"` (tabela "Modelos 3D realistas") |
| `citacao_fonte` | cartão com aspas e a fonte | o título é a citação |
| `fecho_chamada` | chamada, botão e logo | `chamada` (texto do botão, opcional) |
| `mapa_brasil` | estados acendendo por valor, um em destaque | `mapa: {valores: {"SP": "44,4", …}, unidade, destaque: "SP", legenda}` ou `mapa: {destaques: ["CE", "PE"]}`. Use as siglas das UFs. Com `valores`, a `fonte` é obrigatória. |
| `mapa_lugar` | globo da NASA girando até o lugar, com pino | `lugar: {nome, lat, lon}` em graus decimais, com o nome em até 24 caracteres |
| `foto` | foto de pessoa, jogo, lugar, objeto ou evento num cartão, com nome e crédito | `imagem: {arquivo, tipo, nome, credito, licenca, url_origem}`, conforme a seção "Fotos" |
| `lista_cards` | ranking ou lista: cartões que chegam um a um em profundidade | `itens`: de 3 a 5 `{rotulo, valor, unidade}`, com `rotulo` de até 24 caracteres; `valor` é opcional e, se houver, exige `fonte` |
| `versus` | dois cartões frente a frente com o selo VS; o maior ganha borda amarela | `comparacao`: exatamente 2 `{rotulo, valor, unidade}`, com `valor` de até 7 caracteres |
| `linha_tempo` | datas numa linha vertical em perspectiva, que acendem uma a uma | `itens`: de 3 a 5 `{rotulo, texto}`, com `rotulo` (a data) de até 10 caracteres e `texto` de até 26 |
| `antes_depois` | cartão que gira no meio da cena: frente ANTES, verso DEPOIS | `comparacao`: exatamente 2 (o primeiro é o antes), com `valor` de até 7 caracteres |

### Ritmo (automático)

O código garante uma mudança visual a cada 2 a 3 segundos, sempre ligada à fala:
- **batidas:** um "soco" de zoom nas palavras fortes (números e palavras longas), com um tique sonoro discreto;
- **câmera:** aproxima devagar durante toda a cena;
- **troca de cena:** o cartão é empurrado para o lado e o próximo entra girando;
- **legenda cinética:** centralizada embaixo, a palavra falada acende em amarelo e dá um pulinho.

O Diretor contribui com cenas curtas, de 3 a 6 s.

### Acervo de objetos 3D (`objeto_profundidade`)

| objeto | use para | dados extras |
|---|---|---|
| `barras` | comparar de 2 a 4 valores | `comparacao` com valor numérico |
| `pizza` | partes de um todo (fatias) | `comparacao` com de 2 a 4 fatias |
| `linha` | evolução no tempo | `comparacao` com de 3 a 6 pontos (ex.: anos) |
| `podio` | ranking top 3 | `comparacao` com exatamente 3 |
| `termometro` | temperatura, nível ou índice subindo | `comparacao` (o último valor vira o nível) |
| `moedas`, `dinheiro` | dinheiro, preço, economia, salário | nenhum |
| `trofeu`, `medalha` | vitória, recorde, prêmio, campeão | nenhum |
| `foguete`, `planeta`, `atomo` | espaço, lançamento, ciência, física | nenhum |
| `dna` | biologia, saúde, genética | nenhum |
| `lampada` | ideia, descoberta, invenção | nenhum |
| `relogio`, `ampulheta`, `calendario` | tempo, prazo, data, espera | nenhum |
| `celular` | apps, redes sociais, tecnologia | nenhum |
| `controle` | games | nenhum |
| `predios` | cidades, economia, imóveis, população | nenhum |
| `coracao` | saúde, amor, coração | nenhum |
| `cadeado`, `escudo` | segurança, privacidade, proteção | nenhum |
| `alvo` | meta, objetivo, precisão | nenhum |
| `bola` | esportes, futebol | nenhum |
| `globo`, `cubo`, `aneis` | formas de linha, para quando nada acima combina | nenhum |

Para ver todos animados, rode `python ferramentas/bancada_objetos.py`, que gera a folha em `ferramentas/saida_objetos/`.

### Modelos 3D realistas (`"objeto": "modelo:<nome>"`)

São 54 modelos fotorrealistas, com luz de estúdio de verdade (HDRI). A origem e a licença de cada um estão em `modelo/assets/modelos3d/LICENCAS.md`. **Prefira um modelo realista quando ele combinar com o assunto**: fica mais crível que o objeto desenhado em código.

| tema | modelos |
|---|---|
| espaço (NASA) | `astronauta`, `traje_espacial`, `hubble`, `james_webb`, `estacao_espacial`, `perseverance`, `ingenuity`, `saturno_v`, `onibus_espacial`, `modulo_lunar`, `cassini`, `juno`, `antena_70m`, `crawler` |
| tecnologia e games | `console`, `notebook`, `televisao`, `placa_circuito`, `camera_video`, `camera_seguranca`, `radio`, `toca_fitas`, `relogio_pulso`, `lampada_led`, `micro_ondas` |
| ciência | `microscopio`, `quimica`, `bico_bunsen`, `instrumento_espacial`, `binoculo`, `multimetro`, `lampada_antiga` |
| economia e trabalho | `caixa_registradora`, `caixa_papelao`, `caixote`, `martelo`, `chave_inglesa`, `trena`, `mala`, `caderno`, `lousa` |
| comida | `maca`, `bananas`, `abacate`, `batata_doce`, `limao`, `bolo` |
| casa e cultura | `relogio_parede`, `xadrez`, `busto`, `planta`, `ventilador`, `botas`, `mascara_gas` |

Exemplo: `{"familia": "objeto_profundidade", "objeto": "modelo:james_webb", "titulo": ["O TELESCÓPIO", "MAIS POTENTE"], ...}`.

Os modelos da NASA flutuam (sem chão) e giram devagar; os outros ficam apoiados e entram com um pulo. Para ver todos, rode `python ferramentas/bancada_objetos.py --modelos`, que gera `ferramentas/saida_objetos/folha_modelos.png`.

### Cartões 3D

Toda cena entra como um cartão de vidro em perspectiva: chega de lado com borrão de movimento (chicote), gira, aproxima e depois flutua até o fim, alternando o lado a cada cena. Quando a cena tem vídeo de fundo, o cartão vira vidro fosco, desfocando o vídeo atrás. Na troca de cena entra um efeito (flash, vazamento de luz ou glitch, alternando) e o vídeo inteiro tem granulado de filme. Tudo isso é automático.

O que depende do Diretor é usar **de 2 a 4 cenas de 3D por vídeo**, entre `objeto_profundidade`, `mapa_brasil`, `mapa_lugar`, `lista_cards`, `versus`, `linha_tempo` e `antes_depois`, variando de um vídeo para o outro. O validador avisa quando há menos de 2. Escolha o objeto que conta a história: ranking vira `podio`, comparação de valores vira `barras`, dinheiro vira `moedas`, espaço vira `planeta`, um lugar vira `mapa_lugar`.

### Vídeo de fundo (b-roll, obrigatório)

É o que mais deixa o vídeo "profissional": atrás de quase toda cena roda um vídeo real ligado à frase, trocando a cada ~2 s, e o cartão fica por cima. **Regra: pelo menos 4 trechos por vídeo** (o validador recusa menos) e, de preferência, em todas as cenas menos a `foto`.

No `cenas.json`, a cena ganha `broll`, uma lista de **1 a 3 trechos**. O código divide o tempo da cena entre eles, corta na batida da fala, enquadra em 1080x1920, dá um "soco" de zoom em cada corte e escurece de leve para o texto continuar legível.

```json
{"id": 4, "familia": "objeto_profundidade", "objeto": "modelo:relogio_parede", "titulo": ["AS FAMÍLIAS", "ENCOLHERAM"],
 "broll": [{"arquivo": "videos/familia-sala.mp4", "inicio": 0, "fonte": "Pexels", "url_origem": "https://www.pexels.com/video/9690678/", "licenca": "licenca pexels"},
           {"arquivo": "videos/familia-cozinha.mp4", "inicio": 2, "fonte": "Pexels", "url_origem": "https://www.pexels.com/video/12751539/", "licenca": "licenca pexels"}],
 "ancora": "famílias"}
```

- `inicio`: em que segundo do vídeo original o trecho começa (pule aberturas paradas ou com logo).
- **Onde buscar, na ordem:**
  1. **Pexels Videos**: busque em inglês, com o filtro de orientação vertical, por exemplo `https://www.pexels.com/search/videos/crowd%20brazil/?orientation=portrait`.
  2. **Pixabay Videos**.
  3. **Mixkit**.
  4. **NASA** (images.nasa.gov) para espaço.
  5. **Kit de imprensa oficial** (trailer de jogo ou filme), para games e lançamentos.
  6. Wikimedia Commons (vídeos `CC`).
- **Licenças aceitas:** `licenca pexels`, `licenca pixabay`, `licenca mixkit`, `dominio publico`, `CC0`, `CC BY`, `CC BY-SA` e `kit de imprensa oficial`.
- **Como baixar do Pexels:** o link de download é `https://www.pexels.com/download/video/<id>/`. Ele redireciona para o arquivo em `videos.pexels.com`, que baixa normalmente por script. **Prefira a versão HD (1080x1920)**, não a 4K; o validador recusa arquivo acima de 150 MB.
- **Proibido:** YouTube, TikTok, Instagram, telejornal, bancos pagos e agências.
- **O vídeo precisa combinar com a frase falada naquele momento.** Por exemplo: "as famílias encolheram" pede família em casa; "203 milhões" pede multidão na rua. Prefira imagem do Brasil quando o assunto for o Brasil.
- **Evite:** gente olhando para a câmera por muito tempo, marcas e logos em destaque, criança como assunto principal (bebê de costas ou mãos e pés serve) e qualquer coisa que pareça mostrar a pessoa do assunto sem ser ela.
- Uma foto (`.jpg`, `.png` ou `.webp`) também serve como trecho: entra com zoom lento.
- Salve os arquivos em `pautas/<pasta>/videos/`.

### Fotos (obrigatório: pelo menos 1 por vídeo)

**Regra: todo vídeo tem pelo menos uma cena `foto`.** O validador recusa vídeo sem foto. O Diretor procura no navegador, salva em `pautas/<pasta>/imagens/` e usa a família `foto`.

**Ordem de busca.** Comece pela primeira linha e desça até achar:

| # | onde | bom para | `licenca` |
|---|---|---|---|
| 1 | **Wikimedia Commons** (commons.wikimedia.org) | pessoas públicas, atletas, atores, lugares, eventos | `CC0`, `dominio publico`, `CC BY` ou `CC BY-SA` (com a versão) |
| 1b | **Openverse** (openverse.org): buscador de mais de 800 milhões de imagens com licença livre (Flickr, museus, Wikimedia). Filtre por "uso comercial" | quase tudo: pessoas, lugares, objetos, eventos | a CC que aparece na imagem (`CC BY`, `CC BY-SA`, `CC0`) |
| 2 | **Agência Brasil** (agenciabrasil.ebc.com.br): as fotos são CC BY | política, economia, esporte e eventos no Brasil | `CC BY` |
| 3 | **Fotos Públicas** (fotospublicas.com) e Flickr oficiais de governos, clubes e órgãos públicos com licença livre | eventos, autoridades, obras, esportes | `fotos publicas` ou a CC do Flickr |
| 4 | **NASA, ESA, NOAA** (imagens oficiais) | espaço, clima, ciência | `dominio publico` (NASA) ou `CC BY` (ESA) |
| 5 | **Kit de imprensa oficial** (páginas press, media ou newsroom de estúdios, editoras de games, ligas, empresas) | jogos, filmes, produtos, lançamentos | `kit de imprensa oficial` |
| 6 | **Unsplash, Pexels e Pixabay** | foto do **tema**, quando não houver do assunto exato (um estádio, um celular, uma cidade, comida) | `licenca unsplash`, `licenca pexels` ou `licenca pixabay` |
| 7 | **Ilustração gerada por IA** (Gemini ou outra ferramenta da conta) | último recurso, só para objeto, lugar genérico ou conceito | `ilustracao ia`, com crédito "Ilustração gerada por IA" |

**Por que não "qualquer imagem da internet":** no Brasil toda foto tem direito autoral automaticamente, mesmo sem aviso no site. Quem fotografou pode pedir a remoção ao TikTok ou ao Instagram, e várias remoções derrubam o perfil. Por isso a regra é o contrário: **vale tudo que declara uso livre** (a tabela acima já cobre quase tudo); o resto fica de fora.

**Continua proibido**, porque dá derrubada de vídeo ou processo:
- Google Imagens, Pinterest, redes sociais e fotos de matérias de jornal;
- bancos pagos e agências (Getty, Shutterstock, Alamy, AP, Reuters, AFP);
- foto do Unsplash+ (é paga).

**Editar não muda a licença.** Recortar ou mudar a cor de uma foto da Getty continua sendo uso de foto da Getty.

Também proibido:
- ilustração de IA mostrando **pessoa real** ou que pareça foto de um fato;
- foto de criança;
- foto de pessoa sem vida pública;
- montagem enganosa;
- usar alguém de um jeito que pareça que a pessoa apoia o perfil.

**Tratamento automático** (campo `tratamento`; o código aplica antes de entrar no vídeo):
- `natural` (padrão): ajusta tamanho, contraste, cor e nitidez;
- `marca`: duotone nas cores do thebestnewsbr, bom para foto de banco, com cores fracas ou de estilo diferente;
- `recorte`: tira o fundo da pessoa ou do objeto e põe sobre o brilho da marca, "saindo" do cartão. É o melhor para **pessoas**: atleta, ator, cientista.

Como baixar do Wikimedia Commons: use a versão reduzida, de 1280 px (`https://upload.wikimedia.org/wikipedia/commons/thumb/<a>/<ab>/<Arquivo>/1280px-<Arquivo>`). O original costuma dar erro 429.

```json
{"id": 9, "bloco": "virada", "familia": "foto", "titulo": ["O MENOR DESDE", "O CENSO DE 1872"], "destaque": "1872",
 "imagem": {"arquivo": "imagens/dom-pedro-ii.jpg", "tipo": "pessoa", "nome": "Dom Pedro II", "tratamento": "recorte",
            "credito": "Foto: Hermann Witte, c. 1887 / Wikimedia Commons, domínio público",
            "licenca": "dominio publico", "url_origem": "https://commons.wikimedia.org/wiki/File:Dom_Pedro_II_circa_1887.jpg"},
 "fonte": "IBGE", "ancora": "primeiro"}
```

Regras do validador:
- **Arquivo:** JPG, PNG ou WEBP, com até 12 MB e pelo menos 600 px no lado maior.
- **Tipo:** `pessoa`, `jogo`, `lugar`, `objeto` ou `evento`.
- **Textos:** `nome` com até 26 caracteres e `credito` com até 80.
- **Origem:** `url_origem` é a página da imagem, exceto na ilustração de IA.
- **Tratamento:** `natural`, `marca` ou `recorte`.

O Revisor confere na folha de quadros se **a foto é mesmo da pessoa ou da coisa certa**.

### Personagem (mascote)

O mascote do thebestnewsbr é o quadro da logo com olhos, boca e braços. Ele narra o vídeo inteiro, mexendo a boca no tempo da fala.
- Na cena 1 ele aparece grande e surpreso, logo abaixo da caixa do gancho.
- Nas cenas do meio ele fica pequeno, entre a placa da fonte e a legenda.
- No fecho ele comemora.

A pose de cada cena é automática e muda na âncora: aponta para números e mapas, pensa nas citações e fala nas demais. Para trocar, use `"personagem": {"pose": "…"}`, com uma destas poses: `fala`, `aponta`, `surpreso`, `pensa`, `comemora` ou `nega`.

### Som

O código mistura sozinho:
- a narração;
- os efeitos sonoros: woosh nos cortes, pop quando um número ou pino aparece, clique nas barras e sino no fecho;
- a trilha, escolhida pela `categoria` da ficha entre as faixas licenciadas de `modelo/assets/trilhas/` (veja o `LICENCAS.md`). Ela abaixa quando a voz fala.

O volume final fica em −16 LUFS. Os agentes não escolhem som.

## Métricas e estratégia (Analista)

As métricas chegam sozinhas, todo dia, na planilha `thebestnewsbr/thebestnewsbr - Métricas` do Drive. O coletor (`metricas/coletor.gs`) lê as APIs oficiais do Instagram, do Facebook e do TikTok. A aba `metricas` tem uma linha por post: views, alcance, curtidas, comentários, compartilhamentos, salvamentos, tempo médio assistido (Instagram e Facebook), pulos nos 3 primeiros segundos (Instagram), além de views com 48 h e com 7 dias. O TikTok não informa tempo assistido pela API.

Toda segunda, o Analista exporta essa aba como CSV, baixa `thebestnewsbr/log.csv` e roda:

```bash
python3 -m fato.analisar metricas.csv log.csv analise.json
```

Ele liga cada post ao vídeo do log pelo começo da descrição e pela data, e dá uma nota a cada vídeo. A nota 1,0 é a mediana da rede: acima de 1,2 é bom e abaixo de 0,8 é fraco. Os resultados saem agrupados por categoria, tipo de gancho, família de cena, duração e horário. Um grupo com menos de 3 vídeos sai com `conclusivo: false`.

O que ele muda fica em `thebestnewsbr/estrategia.json` no Drive, que o Radar, o Roteirista e o Diretor leem antes de trabalhar:

```json
{
  "atualizado_em": "2026-11-23",
  "fase": "coleta",
  "categorias": {"ciencia": 1.0, "brasil": 1.0, "tecnologia": 1.0, "games": 1.0, "mundo": 1.0},
  "ganchos": {"preferir": [], "evitar": []},
  "cenas": {"preferir": [], "evitar": []},
  "teste_da_semana": {"variavel": "gancho_tipo", "a": "numero", "b": "contraste", "como": "Roteirista alterna: dias pares a, ímpares b"},
  "aprendizados": ["frases curtas, uma por linha, com o número de vídeos que sustenta cada uma"]
}
```

Limites, para a estratégia não ficar pulando:
- **Pesos de categoria:** entre 0,7 e 1,3, e cada um anda no máximo 0,1 por semana. O Radar multiplica a nota da pauta pelo peso.
- **Fase "coleta"** (menos de 10 vídeos com nota): não mude pesos nem preferências.
- **Conclusões:** só de grupos com `conclusivo: true`.
- **Testes:** um por semana, com uma variável só.
- **Regras deste manual** (licenças, Gemini, formato, segurança editorial): a estratégia nunca muda. Mudança grande (parar uma categoria, mudar a duração alvo, mudar o horário) vira um card em "Precisa de você", não uma alteração.

## O que o código garante, e o Revisor não precisa medir

- **Formato:** 1080×1920, 30 fps, H.264 e AAC, com a narração em −16 LUFS.
- **Posição na tela:** texto dentro das áreas livres do TikTok e dos Reels. O `hyperframes check` mede, e qualquer aviso aparece em `check_avisos`.
- **Legenda:** queimada no vídeo, com a palavra falada acesa em amarelo, e também entregue em `legendas.srt`.
- **Identidade thebestnewsbr:** fundo `#0f0f17`, cobalto `#2a40f0`, amarelo `#ffd60a`, Archivo Black, Archivo Narrow e JetBrains Mono.
