# Métricas automáticas (Instagram, Facebook e TikTok) numa planilha do Drive

Uma planilha do Google com um script (Apps Script) consulta as APIs oficiais todo dia, por volta das 6h, e grava as métricas de cada post. O agente Analista do Manus lê essa planilha toda segunda.

**Segurança:** as chaves ficam nas "Propriedades do script", que só você vê. Não cole chave no chat, no Trello nem no repositório. A senha de cada rede você digita só na tela de login da própria rede.

Leva uns 30 a 40 minutos, uma vez só. Faça na ordem.

> Dica: faça tudo numa janela do navegador logada **só** na sua conta Google do thebestnewsbr (ou numa janela anônima). Com várias contas Google abertas, o Apps Script costuma dar erro de "não foi possível abrir o arquivo".

---

## Parte 1: a planilha e o script (10 min)

1. No Google Drive, abra a pasta `thebestnewsbr` e crie uma planilha chamada **`thebestnewsbr - Métricas`**. O nome precisa ser exatamente esse, porque o Analista procura por ele.
2. Na planilha: **Extensões > Apps Script**.
3. Apague o que estiver no editor, cole todo o conteúdo de `metricas/coletor.gs` e clique em **Salvar**. Dê ao projeto o nome "Métricas".
4. **Implantar > Nova implantação**. Na engrenagem, escolha **App da Web**:
   - Executar como: **Eu**.
   - Quem pode acessar: **Somente eu**.
   - Clique em **Implantar** e autorize com a sua conta. O Google mostra "app não verificado": clique em **Avançado > Acessar Métricas**. É o seu próprio script.
   - Copie a **URL do app da Web**, que termina em `/exec`. Ela é a sua **URL de retorno**.
5. Volte ao editor, clique na engrenagem (**Configurações do projeto**), desça até **Propriedades do script** e adicione:
   - `REDIRECT_URI`: a URL de retorno do passo 4.

---

## Parte 2: app da Meta, que cobre Instagram e Facebook (15 min)

**Antes:** o Instagram do thebestnewsbr precisa estar **ligado à página do Facebook**. Na página do Facebook, vá em **Configurações > Contas vinculadas > Instagram** e conecte. Se já estiver ligado, pule.

1. Entre em **developers.facebook.com** com a conta que administra a página e clique em **Meus apps > Criar app**.
   - Se perguntar o caso de uso, escolha **Outro** e depois o tipo **Empresa** (Business).
   - Nome: `thebestnewsbr metricas`.
2. No painel do app, adicione o produto de login. Pode aparecer como **"Login do Facebook para Empresas"** ou como **"Login do Facebook"**, conforme o tipo de app.
   - Em **Configurações** desse produto, campo **URIs de redirecionamento do OAuth válidos**: cole a URL de retorno e salve.
   - Se for **"Login do Facebook para Empresas"**, crie uma **Configuração** do tipo "token de acesso do usuário" com estas permissões: `pages_show_list`, `pages_read_engagement`, `read_insights`, `instagram_basic`, `instagram_manage_insights` e `business_management`. Copie o **ID da configuração**.
3. Em **Configurações do app > Básico**, copie o **ID do app** e a **Chave secreta do app**. Ela aparece ao clicar em "Mostrar" e pede a sua senha do Facebook.
4. Nas **Propriedades do script** (Parte 1, passo 5), adicione:
   - `META_APP_ID`: o ID do app.
   - `META_APP_SECRET`: a chave secreta.
   - `META_CONFIG_ID`: o ID da configuração, só se você criou uma no passo 2.
   - `PAGINA`: o nome exato da página do Facebook. Só é preciso se você administra mais de uma página.

O app pode ficar em **modo de desenvolvimento**. Como você é o administrador, ele lê as métricas da sua própria página e do seu Instagram sem precisar da revisão da Meta.

---

## Parte 3: app do TikTok (10 min)

1. Entre em **developers.tiktok.com** com a conta do thebestnewsbr e vá em **Manage apps > Connect an app**. Use um app novo, separado do app do O Preço Vale.
   - Nome: `thebestnewsbr metricas`.
2. Em **Products**, adicione o **Login Kit**. Se aparecer como produto separado, adicione também a **Display API**. Os escopos necessários são `user.info.basic` e `video.list`.
3. Ative o **Sandbox**:
   - crie um sandbox;
   - em **Target users**, adicione a sua conta do TikTok e aceite o convite no app do TikTok.

   Assim o app funciona sem passar pela auditoria do TikTok.
4. No **Login Kit**, em **Redirect URI** (Web), cole a URL de retorno e salve.
5. Copie o **Client key** e o **Client secret** do sandbox e adicione nas **Propriedades do script**:
   - `TIKTOK_CLIENT_KEY`
   - `TIKTOK_CLIENT_SECRET`

---

## Parte 4: conectar e ligar (5 min)

1. Abra a URL de retorno no navegador. Aparece a página **"Conectar as redes"**.
2. Clique em **Conectar Instagram e Facebook**:
   - entre com a conta que administra a página;
   - marque a página do thebestnewsbr e o Instagram;
   - aceite.

   A tela final mostra o nome da página e o @ do Instagram. Se aparecer "nenhum Instagram ligado a esta página", volte ao "Antes" da Parte 2.
3. Volte à URL de retorno e clique em **Conectar TikTok**. Entre na conta e aceite.
4. Na planilha, recarregue a página. Aparece o menu **Métricas**.
   - Clique em **Métricas > Coletar agora**. Na primeira vez o Google pede autorização de novo.
   - Confira a aba `metricas`: deve aparecer uma linha por vídeo dos últimos 60 dias. A aba `execucoes` mostra quantos posts foram lidos e os erros, se houver.
5. Clique em **Métricas > Ligar a coleta diária (6h)**. Pronto.

---

## Se der problema

| sinal | o que fazer |
|---|---|
| A aba `execucoes` mostra `instagram: ...(código 10)` ou `(código 200)` | Falta permissão. Conecte de novo pela URL de retorno e marque todas as opções. |
| Instagram ou Facebook pararam de vir depois de uma troca de senha | A Meta derruba a conexão quando a senha muda. Conecte de novo. |
| `tiktok: ... conecte o TikTok de novo` | A conexão do TikTok vence em 1 ano, ou caiu. Clique em "Conectar TikTok" de novo. |
| O TikTok recusa a URL de retorno | Me avise. Dá para usar outra página de retorno. |
| Alguma coluna vem vazia (ex.: `tempo_medio_s` no TikTok) | Normal: o TikTok não entrega tempo assistido pela API. As outras métricas seguem. |

**Ao postar, não apague o começo da descrição** que vai no `.txt`. É por ele que o Analista descobre qual post é de qual vídeo.
