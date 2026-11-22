Produza o vídeo vertical de 60 s do thebestnewsbr a partir do quadro Trello "Redação Fato" (https://trello.com/b/llcZddqR). Você não posta em rede nenhuma: entrega no Google Drive e, no fim, dispara uma vez o cenário do Make que publica. O AGENTS.md do repositório manda em tudo: contratos, comandos, códigos de saída e "Regras das plataformas".

0. Se houver card em "Precisa de você" com "retomar na revisão de linguagem", retome ele primeiro, com a pasta de thebestnewsbr/pendentes/ no Drive.
1. Card mais antigo de "Aprovado" vai para "Em produção". Se "Aprovado" estiver vazio, pegue o de maior nota de "Pauta do dia", só com 85 ou mais, e marque "auto". Se nenhum tiver 85, não produza e me avise.
2. git clone --depth 1 https://github.com/ferfagner/redacao-fato && cd redacao-fato && bash setup.sh; mkdir -p pautas/AAAA-MM-DD-slug. Leia estrategia/estrategia.json (não edite).
3. Checador grava ficha.json, com duas fontes de domínios diferentes. Se vetar, comente, mova para "Vetado" e pegue o próximo card.
4. Roteirista grava roteiro.json: 165 a 180 palavras, seis blocos.
   - Nada de isca ("manda pra", "compartilha", "marca", "comenta SIM", "salva").
   - Notícia não pode parecer oferta de vaga, renda ou benefício.
5. Diretor grava cenas.json: 11 a 13 cenas de até 6 s, de 2 a 4 com 3D ou mapa, pelo menos 1 foto e vídeo de fundo baixado em 4 trechos ou mais.
6. Roteirista grava publicacao.json: hashtags pesquisadas no navegador e, se couber, avisos_postagem.
7. Gemini revisa o roteiro, os títulos e a publicação e grava revisao_linguagem.json.
   - 503 ou 429: troque de modelo (3.5-flash → 3.8-flash → 3.5-flash-lite) e insista por até 30 min, como no AGENTS.md. Nunca use 2.x.
   - Mande ao Gemini as 10 últimas chamadas da coluna "chamada" do log.csv.
   - O Gemini propõe 3 chamadas finais próprias deste vídeo (seguir a página + opinião sobre um ponto concreto). Escolha uma.
8. validar, Revisor etapa A, revisar, Revisor etapa B.
   - Código 2 volta ao papel indicado, com no máximo duas correções por papel.
   - Só siga com "aprovado".
9. render. Se ok vier false, pare.
10. Crie uma pasta nova em thebestnewsbr/videos/ (1jIPmzVlm2d5oAlTZ2FPlWkdqjReRvHx8) com o nome "AAAA-MM-DD - <título>" e coloque nela os dois arquivos de saida/entrega/.
11. Mova o card para "No Drive" e comente o link e os avisos_postagem.
12. Acrescente uma linha no log.csv com estas colunas: data, card, categoria, tema, familias, fonte1, fonte2, duracao_s, rodadas_revisao, tempo_render_min, link_drive, status, gancho_tipo, n_cenas, n_broll, descricao_inicio, teste_da_semana, chamada.
    - descricao_inicio: as 80 primeiras letras do .txt.
    - chamada: o texto do bloco chamada.

13. Make: no fim, rode uma vez o cenário "Drive → Facebook, Instagram, TikTok e YouTube (thebestnewsbr)" (id 7127775) pelo conector do Make e espere terminar. Só rode se o vídeo e o .txt já estiverem na pasta do Drive e a linha do log.csv estiver gravada. Deu certo: o próprio cenário publica, move a pasta para publicados e o card para "Publicado"; confira e mande o resumo. Deu erro: não rode de novo (pode postar duas vezes); comente o erro no card e me avise.

Se travar, mova o card para "Precisa de você" com folha.png e relatorio.json, e me avise.
