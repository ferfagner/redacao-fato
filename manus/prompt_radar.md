Monte a pauta do dia do perfil thebestnewsbr no quadro "Redação Fato" do Trello.

Quadro: ari:cloud:trello::board/workspace/605e32a1d7d89361be15ef1f/6b0084f98920334867315334
Lista de destino: "Pauta do dia" (6b00850386ece6c280483af0)

O que procurar

Pesquise no navegador, sem conector e sem login. Use páginas comuns: a busca do Google, o Google Notícias e o YouTube. Procure nas últimas 24 a 48 horas, nestas cinco categorias:

• ciencia (ciência e espaço): Nature, Science, NASA, ESA, Smithsonian, universidades, Agência FAPESP.
• brasil (Brasil em números): IBGE, Agência Brasil, Banco Central, INPE, ministérios, G1.
• tecnologia: anúncios oficiais das empresas, Reuters, Associated Press, BBC.
• games: blogs oficiais (PlayStation, Xbox, Nintendo, Steam), números de publishers e da Newzoo, lançamentos confirmados.
• mundo (notícias gerais e curiosidades): Reuters, Associated Press, BBC Brasil, Our World in Data, Pew Research, ONU.

O YouTube mede o interesse do público, mas não é fonte do fato:
• veja os vídeos em alta, as buscas por categoria e as visualizações nas últimas 24 a 48 horas;
• nunca baixe nem use trechos, imagens ou áudio de vídeos.

O Google serve para achar a origem: a matéria, o comunicado ou o estudo. Toda pauta e todo número precisam de uma URL de origem que você mesmo abriu no navegador.

Se uma página pedir login, cookie pago ou CAPTCHA, pule e siga com outra fonte. Não crie conta.

Nota

Dê nota de 0 a 5 em seis critérios:
• novidade (peso 25);
• vira número, gráfico, mapa, objeto 3D ou foto licenciada (peso 20);
• curiosidade, medida também pelo interesse no YouTube e no Google (peso 20);
• durabilidade (peso 15);
• segurança editorial (peso 10);
• originalidade frente ao log.csv dos últimos 30 dias (peso 10).

A nota final vai de 0 a 100: some (nota × peso) e divida por 5.

Pesos do Analista:
• leia estrategia/estrategia.json no repositório github.com/ferfagner/redacao-fato, sem editar;
• multiplique a nota final pelo peso da categoria em "categorias" (de 0,7 a 1,3), limitando a 100;
• se não conseguir ler o arquivo, use peso 1.

Variedade: entre as oito pautas, pelo menos três categorias diferentes e no máximo três da mesma categoria.

Descarte:
• política partidária;
• tragédia, morte e doença de uma pessoa;
• promessa de investimento;
• celebridade em situação vexatória;
• teoria da conspiração;
• em games, boato, vazamento e "insider";
• tema que já está no quadro ou no log.csv (veja "Não repetir").

Regras das plataformas:
• o ângulo sugerido nunca é isca de engajamento ("manda pra quem…", "marca alguém");
• notícia de emprego, renda, crédito ou benefício nunca é tratada como oferta ("vagas abertas", "dinheiro esquecido", "quem procura emprego");
• fale do dado, não com quem precisa.

Não repetir (antes de pesquisar)

• Liste os cards do quadro dos últimos 30 dias, de todas as listas, inclusive Vetado e arquivados, e as linhas do log.csv do mesmo período.
• Anote de cada um o assunto, os números e as URLs.
• Uma pauta nova é repetida quando tem a mesma URL, o mesmo estudo, anúncio ou evento, ou o mesmo número sobre o mesmo assunto, mesmo que vinda de outro veículo ou com outro título.
• Na dúvida, mande ao Gemini a lista anotada e as pautas novas, e descarte as que ele disser que são o mesmo fato.
• Só vale de novo se houver um fato novo de verdade (número atualizado, resultado final) e o card disser "atualiza o card X".
• Sem pautas novas suficientes, crie menos cards. Nunca complete as oito com repetição.

Antes de criar os cards

Passe os títulos e as descrições pelo Gemini para deixá-los simples e claros, sem mudar os fatos. Qualquer pessoa precisa entender de primeira, do adolescente ao idoso.

Cards

Crie no máximo oito cards na lista "Pauta do dia", em ordem decrescente de nota.

• Título: o fato em até 60 caracteres, sem ponto final.
• Descrição:
  – o fato em uma frase;
  – a nota (e o peso do Analista, se for diferente de 1);
  – o veículo, a data e a hora;
  – as URLs;
  – uma linha de ângulo sugerido.
  – uma linha "chave:" com assunto | número principal | URL principal, para as próximas rodadas acharem repetição.
• Checklist: duas fontes independentes; número com ano e instituição; fora da lista de veto.
• Etiquetas: a da categoria e "nota alta" quando a nota passar de 85.

Limites

Não escreva roteiro, não mova cards e não publique em rede nenhuma. No fim, envie um resumo com as notas e o link do quadro (https://trello.com/b/llcZddqR).
