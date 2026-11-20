# Manual dos agentes: Redação Fato (thebestnewsbr)

Este repositório transforma três arquivos JSON num vídeo vertical de 60 s. Os agentes decidem o conteúdo. O código faz a voz, a montagem, a checagem e o render. **Nenhum agente escreve HTML, mexe no modelo ou improvisa outro renderizador.** Se algo falhar, devolva a quem o relatório indica.

## Pasta da pauta

Cada vídeo tem uma pasta própria, por exemplo `pautas/2026-11-21-censo/`, com três arquivos:

| arquivo | quem escreve | conteúdo |
|---|---|---|
| `ficha.json` | Checador | o fato, os números e as duas fontes |
| `roteiro.json` | Roteirista | a narração em 6 blocos |
| `cenas.json` | Diretor | de 9 a 11 cenas |

Veja o exemplo completo em `exemplos/censo-2022/`.

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

## Fluxo

1. O **Checador** grava `ficha.json`.
2. O **Roteirista** grava `roteiro.json`.
3. O **Diretor** grava `cenas.json`.
4. Rode `validar`. Se der código 2, devolva os erros e rode de novo, no máximo duas vezes por agente.
5. **Revisor, etapa A:** lê a ficha, o roteiro e as cenas.
6. Rode `revisar`. Se der código 2, devolva os erros (por exemplo, a narração ficou longa ou uma cena ficou curta).
7. **Revisor, etapa B:** abre `saida/folha.png` (uma imagem por cena, já com legenda e fonte) e `saida/legendas.srt`, e responde "aprovado" ou uma lista numerada de correções por cena.
8. Só depois do "aprovado" da etapa B, rode `render`. Se `ok` vier `false`, os `problemas` dizem o que conferir: duração, resolução, áudio ou volume.
9. Publique `saida/video.mp4`.

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
  "fonte_tela": "IBGE, Censo 2022"
}
```

- Pauta vetada: `{"vetado": true, "motivo": "uma linha"}`.
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
| `objeto_profundidade` | objeto 3D com o título | `objeto`, que pode ser:<br>• `moedas`: pilha de moedas caindo (dinheiro, preço, economia)<br>• `podio`: 1º, 2º e 3º lugar (ranking), com exatamente 3 itens em `comparacao`, cada um com `rotulo` de até 16 caracteres<br>• `barras`: barras 3D com valores, com 2 a 4 itens em `comparacao` (`rotulo`, `valor` numérico, `unidade`)<br>• `planeta`: planeta com anel e lua (espaço, ciência)<br>• `globo`, `cubo` e `aneis`: formas de linha, para quando nada acima combina |
| `citacao_fonte` | cartão com aspas e a fonte | o título é a citação |
| `fecho_chamada` | chamada, botão e logo | `chamada` (texto do botão, opcional) |
| `mapa_brasil` | estados acendendo por valor, um em destaque | `mapa: {valores: {"SP": "44,4", …}, unidade, destaque: "SP", legenda}` ou `mapa: {destaques: ["CE", "PE"]}`. Use as siglas das UFs. Com `valores`, a `fonte` é obrigatória. |
| `mapa_lugar` | globo da NASA girando até o lugar, com pino | `lugar: {nome, lat, lon}` em graus decimais, com o nome em até 24 caracteres |
| `foto` | foto de pessoa, jogo, lugar, objeto ou evento num cartão, com nome e crédito | `imagem: {arquivo, tipo, nome, credito, licenca, url_origem}`, conforme a seção "Fotos" |

### Ritmo (automático)

O código garante uma mudança visual a cada 2 a 3 segundos, sempre ligada à fala:
- **batidas:** um "soco" de zoom nas palavras fortes (números e palavras longas), com um tique sonoro discreto;
- **câmera:** aproxima devagar durante toda a cena;
- **troca de cena:** o cartão é empurrado para o lado e o próximo entra girando;
- **legenda cinética:** centralizada embaixo, a palavra falada acende em amarelo e dá um pulinho.

O Diretor contribui com cenas curtas, de 3 a 6 s.

### Cartões 3D

Toda cena entra como um cartão de vidro em perspectiva: gira, aproxima e depois flutua até o fim, alternando o lado a cada cena. Isso é automático.

O que depende do Diretor é usar **de 2 a 4 cenas com objeto 3D ou mapa por vídeo** (`objeto_profundidade`, `mapa_brasil` ou `mapa_lugar`). O validador avisa quando há menos de 2. Escolha o objeto que conta a história: ranking vira `podio`, comparação de valores vira `barras`, dinheiro vira `moedas`, espaço vira `planeta`, um lugar vira `mapa_lugar`.

### Fotos (pessoas, jogos, lugares)

Use foto quando o assunto for uma pessoa pública, um jogo, um filme, um lugar ou um objeto que o público precisa **ver**: um jogador, um ator, a capa de um jogo, um prédio. O Diretor procura a foto no navegador, salva em `pautas/<pasta>/imagens/` e usa a família `foto`.

**Só vale foto com licença que permita o uso, sempre com crédito na tela.** O validador recusa qualquer outra.

| de onde | licença (campo `licenca`) | exemplo de crédito |
|---|---|---|
| [Wikimedia Commons](https://commons.wikimedia.org): pessoas, lugares, eventos, objetos | `CC0`, `dominio publico`, `CC BY` ou `CC BY-SA` (copie a versão, ex.: `CC BY-SA 4.0`) | `Foto: Nome do autor / Wikimedia Commons, CC BY-SA 4.0` |
| kit de imprensa oficial (páginas "press", "media" ou "newsroom" do estúdio, da editora de games, do clube ou da empresa) | `kit de imprensa oficial` | `Imagem: Nintendo (kit de imprensa)` |

Proibido:
- foto do Google Imagens, do Pinterest, de redes sociais ou de matérias de jornal;
- bancos pagos e agências (Getty, Shutterstock, Alamy, AP, Reuters, AFP);
- foto de pessoa comum, sem vida pública;
- foto de criança;
- foto editada ou montada para parecer outra coisa;
- usar a foto de alguém de um jeito que pareça que a pessoa apoia o perfil ou um produto.

Como baixar do Wikimedia Commons: abra a página do arquivo, confira a licença e o autor e baixe a versão reduzida, de 1280 px. O link é `https://upload.wikimedia.org/wikipedia/commons/thumb/<a>/<ab>/<Arquivo>/1280px-<Arquivo>`. O original costuma dar erro 429 (pedidos demais).

```json
{"id": 9, "bloco": "virada", "familia": "foto", "titulo": ["O MENOR DESDE", "O CENSO DE 1872"], "destaque": "1872",
 "imagem": {"arquivo": "imagens/dom-pedro-ii.jpg", "tipo": "pessoa", "nome": "Dom Pedro II",
            "credito": "Foto: Hermann Witte, c. 1887 / Wikimedia Commons, domínio público",
            "licenca": "dominio publico", "url_origem": "https://commons.wikimedia.org/wiki/File:Dom_Pedro_II_circa_1887.jpg"},
 "fonte": "IBGE", "ancora": "primeiro"}
```

Regras do validador:
- `arquivo` em JPG, PNG ou WEBP, com até 12 MB e pelo menos 600 px no lado maior;
- `tipo` é um destes: `pessoa`, `jogo`, `lugar`, `objeto` ou `evento`. Com `pessoa`, o enquadramento prioriza o rosto;
- `nome` com até 26 caracteres;
- `credito` com até 80 caracteres;
- `url_origem` é a página da imagem, não o link direto do arquivo.

O Revisor confere na folha de quadros se **a foto é mesmo da pessoa ou da coisa certa**. Errar o rosto de alguém é o pior erro possível.

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
- uma trilha, se houver alguma em `modelo/assets/trilhas/`. Ela abaixa quando a voz fala.

O volume final fica em −16 LUFS. Os agentes não escolhem som.

## O que o código garante, e o Revisor não precisa medir

- **Formato:** 1080×1920, 30 fps, H.264 e AAC, com a narração em −16 LUFS.
- **Posição na tela:** texto dentro das áreas livres do TikTok e dos Reels. O `hyperframes check` mede, e qualquer aviso aparece em `check_avisos`.
- **Legenda:** queimada no vídeo, com a palavra falada acesa em amarelo, e também entregue em `legendas.srt`.
- **Identidade thebestnewsbr:** fundo `#0f0f17`, cobalto `#2a40f0`, amarelo `#ffd60a`, Archivo Black, Archivo Narrow e JetBrains Mono.
