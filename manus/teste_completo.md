# Teste completo no Manus: pesquisa real, sem publicar

Cole o bloco entre as linhas numa tarefa nova do Manus. Ele roda o fluxo inteiro de um dia (Radar, Checador, Roteirista, Diretor, Revisor e render) com uma pauta real. Ele **não publica**, não cria perfis, não mexe no Trello e não agenda nada. No fim, entrega o vídeo e tudo o que foi produzido para você avaliar.

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

Grave `ficha.json` no formato do `AGENTS.md`. Se o fato não fechar, registre o motivo e volte ao passo 1 com a próxima pauta, no máximo 3 tentativas.

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
- **use de 2 a 4 cenas com objeto 3D ou mapa** e escolha o objeto que conta a história: `podio` para ranking, `barras` para comparação, `moedas` para dinheiro, `planeta` para espaço, `mapa_brasil` para estados e `mapa_lugar` para um lugar;
- se fizer sentido, escolha a pose do mascote em `personagem`;
- **fotos:** se o assunto for uma pessoa pública, um jogo, um filme ou um lugar, procure uma foto no navegador, só no Wikimedia Commons ou no kit de imprensa oficial, e salve em `imagens/`. Use a família `foto`, com `licenca`, `credito` e `url_origem`, como manda a seção "Fotos" do `AGENTS.md`. Foto do Google Imagens, de rede social, de jornal ou de banco de imagens é proibida. Se não achar foto liberada, siga sem foto.

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
- nada fica cortado ou sobreposto;
- a legenda bate com a fala.

Se precisar corrigir, ajuste e rode `revisar` de novo, no máximo 2 rodadas.

## 7. Render

Rode `python3 -m fato render pautas/teste-AAAA-MM-DD` e anote o tempo. Se `ok` vier `false`, me mostre os `problemas`.

## 8. Não publique. Me entregue:

1. A lista das 8 pautas do Radar, com notas, e qual foi escolhida e por quê.
2. A ficha do Checador, com as duas URLs.
3. O roteiro (texto dos 6 blocos) e a lista de cenas com as famílias usadas. Se usou fotos, o link de origem e a licença de cada uma.
4. Os arquivos `saida/video.mp4`, `saida/folha.png` e `saida/legendas.srt`.
5. O `saida/relatorio.json` do `revisar` e o do `render`.
6. Quantas rodadas de correção houve em cada etapa e o que foi corrigido.
7. Os tempos de `setup.sh`, `revisar` e `render`.
8. Uma sugestão de legenda para o post, neste molde (no máximo um emoji, nunca no começo):

```
{gancho}

{fato em uma frase}, segundo {fonte1}.

Fontes: {fonte1}; {fonte2}
Salva pra mostrar pra alguém 👀
#curiosidades #fatos #thebestnewsbr #{tema_hashtag}
```

Não edite nada fora de `pautas/`, não escreva HTML e não troque de renderizador. Nenhuma senha ou chave pode aparecer na resposta.

---
