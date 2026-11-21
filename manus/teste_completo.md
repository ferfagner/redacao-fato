# Teste completo no Manus: pesquisa real, sem publicar

Cole o bloco entre as linhas numa tarefa nova do Manus. Ele roda o fluxo inteiro de um dia (Radar, Checador, Roteirista, Diretor, Revisor e render) e salva o vídeo e a descrição numa pasta nova do seu Google Drive com uma pauta real. Ele **não publica**, não cria perfis, não mexe no Trello e não agenda nada. No fim, entrega o vídeo e tudo o que foi produzido para você avaliar.

---

Quero um teste completo do meu pipeline de vídeo com uma pauta real. **Não publique nada em nenhuma rede.** Não crie perfis, grupos, quadros nem agendamentos. Você mesmo faz o papel de cada etapa, na ordem abaixo, seguindo as regras do repositório.

## 0. Preparar

1. Clone o repositório privado `https://github.com/ferfagner/redacao-fato`. Se precisar de acesso ao GitHub e aparecer um cartão de autorização, pare e me mostre.
2. Rode `bash setup.sh`. Se faltar algo (Python 3.10+, Node 22+, FFmpeg ou o Chrome do HyperFrames), instale pelo gerenciador de pacotes. Se não der, pare e me diga o que faltou.
3. **Leia o `AGENTS.md` inteiro antes de seguir.** Ele tem o formato exato da `ficha.json`, do `roteiro.json` e do `cenas.json`, as famílias de cena, os objetos 3D e as regras que o validador confere. Em caso de dúvida, vale o `AGENTS.md`.
4. Crie a pasta `pautas/teste-AAAA-MM-DD/`, com a data de hoje. É nela que ficam os três arquivos.

## 1. Radar (pesquisa real)

Pesquise **no navegador** as publicações das últimas 24 a 48 horas: busca do Google, Google Notícias e YouTube, abertos como páginas comuns, sem conector e sem login. Use o Gemini sempre que ajudar a resumir, agrupar, comparar ou traduzir. Toda pauta, porém, precisa de uma URL de origem que você abriu.

As categorias e as fontes que valem como origem:

| categoria | fontes |
|---|---|
| `ciencia` (ciência e espaço) | Nature, Science, NASA, ESA, Smithsonian, universidades, Agência FAPESP |
| `brasil` (Brasil em números) | IBGE, Agência Brasil, Banco Central, INPE, ministérios, G1 |
| `tecnologia` | anúncios oficiais das empresas, Reuters, Associated Press, BBC |
| `games` | blogs oficiais (PlayStation, Xbox, Nintendo, Steam), Newzoo, lançamentos confirmados |
| `mundo` | Reuters, Associated Press, BBC Brasil, Our World in Data, Pew Research, ONU |

O YouTube serve para medir o interesse (vídeos em alta e visualizações sobre o tema nas últimas 24 a 48 horas). **Ele não é fonte do fato.** Não baixe nem use trechos, imagens ou áudio. Se uma página pedir login, conteúdo pago ou CAPTCHA, pule e use outra fonte.

Dê nota de 0 a 5 em cada critério:

| critério | peso |
|---|---|
| novidade | 25 |
| vira número, gráfico, mapa ou objeto 3D | 20 |
| curiosidade (inclusive o interesse no YouTube e no Google) | 20 |
| durabilidade | 15 |
| segurança editorial | 10 |
| originalidade | 10 |

A nota final vai de 0 a 100: some (nota × peso) e divida por 5.

**Variedade:** entre as 8, pelo menos 3 categorias diferentes.

Descarte:
- política partidária;
- tragédia, morte e doença de uma pessoa;
- promessa de investimento;
- celebridade em situação vexatória;
- teoria da conspiração;
- em games, boato, vazamento e "insider".

Monte a lista das 8 melhores, cada uma com título, categoria, veículo, URL, data e hora, nota e sinal de interesse. **Escolha a de maior nota para produzir.** Se ela for vetada no passo 2, passe para a próxima da lista.

## 2. Checador

Confirme o fato central em **duas fontes independentes, de domínios diferentes**, de preferência primárias (estudo, relatório oficial, dado de órgão público). Duas matérias que citam a mesma nota não contam como duas fontes. Todo número precisa de valor, ano e instituição.

Grave `ficha.json` no formato do `AGENTS.md`, com a `categoria` da pauta escolhida (ela define a trilha musical). Se o fato não fechar, registre o motivo e volte ao passo 1 com a próxima pauta, no máximo 3 tentativas.

## 3. Roteirista

Escreva `roteiro.json` com os 6 blocos e as faixas de palavras do `AGENTS.md` (total de 165 a 180 palavras):
- português do Brasil falado, frases curtas, sem jargão;
- gancho sem pergunta;
- números por extenso, como serão falados, sem parênteses;
- retenção: o gancho abre uma pergunta que só se responde na virada, e o `mecanismo` e a `virada` começam com uma frase-ponte verdadeira que reabre a curiosidade ("Mas tem um detalhe.");
- só o que está na ficha.

## 4. Diretor

Escreva `cenas.json`, com 11 a 13 cenas curtas (3 a 6 s cada; o mínimo aceito é 9 e o máximo 14):
- a cena 1 é `tipo_cinetico` do gancho e a última é `fecho_chamada`;
- títulos em caixa alta, com até 3 linhas de até 4 palavras e 22 caracteres, e no máximo 9 palavras;
- toda cena com número leva `fonte`;
- cada cena tem uma `ancora`, que é uma palavra do mesmo bloco da narração;
- **use de 2 a 4 cenas de 3D:** um objeto do acervo (28 desenhados ou 54 modelos realistas, como `modelo:astronauta`; prefira o realista quando combinar), um mapa ou um cartão 3D (`lista_cards`, `versus`, `linha_tempo`, `antes_depois`), escolhendo o que conta a história (veja o `AGENTS.md`);
- se fizer sentido, escolha a pose do mascote em `personagem`;
- **fotos (obrigatório, pelo menos 1):** procure no navegador na ordem da seção "Fotos" do `AGENTS.md` (Wikimedia Commons, Openverse, Agência Brasil, Fotos Públicas, NASA/ESA, kit de imprensa, Unsplash/Pexels/Pixabay e, em último caso, ilustração de IA, nunca de pessoa real). Salve em `imagens/`, use a família `foto` com `licenca`, `credito`, `url_origem` e `tratamento` (`recorte` para pessoas).
- **cenas de até 6 s:** cena longa perde ritmo; divida em duas com outra âncora.
- **vídeo de fundo (obrigatório, pelo menos 4 trechos):** para cada cena, menos a `foto`, procure de 1 a 3 trechos que combinem com a frase falada (Pexels Videos com filtro vertical primeiro; depois Pixabay, Mixkit, NASA ou kit de imprensa). Baixe a versão HD em `videos/` e preencha `broll` com `arquivo`, `inicio`, `fonte`, `url_origem` e `licenca`, como na seção "Vídeo de fundo" do `AGENTS.md`. Para fotos, use também o Openverse (openverse.org).

## 4a. Descrição e hashtags do post

Siga a seção "Publicação" do `AGENTS.md`:
1. Pesquise **no navegador, sem login**, as hashtags em alta: TikTok Creative Center (Hashtags populares, Brasil, 7 dias), a busca do TikTok e do Instagram, e o Google Trends (Brasil, 7 dias).
2. Escolha de 3 a 6 hashtags: `#thebestnewsbr`, mais as do assunto e da categoria, e no máximo uma em alta com relação direta. Nada de `#fyp`, `#viral` e similares.
3. Escreva a descrição: primeira linha com o gancho e uma palavra-chave, de 2 a 3 frases simples com o dado, uma chamada para comentar ou salvar e as fontes no fim.
4. Escolha de 3 a 6 palavras-chave de busca.
5. Grave tudo em `publicacao.json`.

## 4b. Revisão de linguagem pelo Gemini (obrigatória)

Mande ao Gemini, pela conexão da conta, o prompt da seção "Revisão de linguagem" do `AGENTS.md`, com o roteiro, os títulos das cenas e o `publicacao.json` colados no fim. O objetivo é que qualquer pessoa entenda de primeira, do adolescente ao idoso.

Aplique as mudanças em `roteiro.json`, `cenas.json` e `publicacao.json`, descartando as que mudarem fatos, números ou limites, e grave `revisao_linguagem.json` no formato do `AGENTS.md`. Sem esse arquivo, o `validar` não passa.

## 5. Validar e Revisor, etapa A

Rode `python3 -m fato validar pautas/teste-AAAA-MM-DD`. Se der código 2, corrija o arquivo indicado em cada erro e rode de novo, no máximo 3 vezes.

Depois, como Revisor, confira:
- os números da tela batem com a ficha;
- toda cena com dado tem fonte;
- não há erro de português;
- o gancho promete o que o vídeo entrega.

Anote as correções que fizer.

## 6. Revisar e Revisor, etapa B

Rode `python3 -m fato revisar pautas/teste-AAAA-MM-DD`.
- **Código 2:** o `saida/relatorio.json` diz quem corrige o quê (por exemplo, a narração ficou longa ou uma cena ficou curta). Ajuste e rode de novo, no máximo 2 rodadas.
- **Código 1:** falha técnica. Rode de novo uma vez e, se repetir, pare e me mostre o erro.

Então abra `saida/folha.png` e `saida/legendas.srt` e, como Revisor, confira:
- a leitura de cada cena está clara;
- toda foto mostra mesmo a pessoa ou a coisa certa, e o crédito está visível;
- o vídeo de fundo de cada cena combina com a frase falada e não mostra logo, marca ou criança em destaque;
- nada fica cortado ou sobreposto;
- a legenda bate com a fala.

Se precisar corrigir, ajuste e rode `revisar` de novo, no máximo 2 rodadas.

## 7. Render

Rode `python3 -m fato render pautas/teste-AAAA-MM-DD` e anote o tempo. Se `ok` vier `false`, me mostre os `problemas`.

## 8. Salve no Google Drive (sem publicar)

O `render` deixa em `pautas/teste-AAAA-MM-DD/saida/entrega/` exatamente dois arquivos:
- o vídeo, `teste-AAAA-MM-DD.mp4`;
- a descrição pronta para colar, com as hashtags no fim, `teste-AAAA-MM-DD.txt`.

1. Habilite o conector do **Google Drive** com `connector ensure`. Se aparecer um cartão de autorização, pare e me mostre.
2. No meu Drive, crie uma **pasta nova** dentro de `thebestnewsbr/videos/`, com o nome `AAAA-MM-DD - <tema do vídeo>`. Crie `thebestnewsbr/videos/` se ainda não existir.
3. Envie para essa pasta **só esses dois arquivos**, nada mais.
4. Me responda só com o link da pasta. Se algo falhar, mostre o erro.

Não edite nada fora de `pautas/`, não escreva HTML e não troque de renderizador. Nenhuma senha ou chave pode aparecer na resposta.

---
