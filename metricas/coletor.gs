/**
 * Coletor de métricas do thebestnewsbr (Instagram, Facebook e TikTok) para uma planilha do Google Drive.
 *
 * Vive dentro da planilha "thebestnewsbr - Métricas" (Extensões > Apps Script). Passo a passo em metricas/LEIAME.md.
 * As chaves ficam nas "Propriedades do script" (Configurações do projeto), nunca neste código.
 *
 * Propriedades que o dono preenche:
 *   META_APP_ID, META_APP_SECRET          app da Meta (Instagram + página do Facebook)
 *   TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET app do TikTok (Login Kit + Display API)
 *   REDIRECT_URI                           a URL do app da Web deste script (termina em /exec)
 *   META_CONFIG_ID (opcional)              id da configuração do "Login do Facebook para Empresas"
 *   PAGINA (opcional)                      nome ou id da página do Facebook, se houver mais de uma
 * Propriedades que o script grava sozinho: META_PAGE_ID, META_PAGE_TOKEN, META_IG_ID, TT_REFRESH, TT_OPEN_ID, ESTADO_*.
 */

const META_V = 'v27.0';
const DIAS = 60;            // acompanha posts dos últimos 60 dias
const ABA = 'metricas';     // 1ª aba: uma linha por post (o Analista lê esta)
const ABA_HIST = 'historico';
const ABA_EXEC = 'execucoes';
const COLS = ['rede', 'id', 'data_post', 'link', 'legenda', 'duracao_s', 'views', 'alcance', 'curtidas', 'comentarios',
  'compartilhamentos', 'salvamentos', 'seguidores_ganhos', 'tempo_medio_s', 'pulos_3s_pct', 'views_48h', 'views_7d',
  'atualizado_em'];

const META_ESCOPOS = ['pages_show_list', 'pages_read_engagement', 'read_insights', 'instagram_basic',
  'instagram_manage_insights', 'business_management'];
const TT_ESCOPOS = ['user.info.basic', 'video.list'];

// ---------------------------------------------------------------- menu e agendamento

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Métricas')
    .addItem('Configurar chaves', 'configurarChaves')
    .addItem('Coletar agora', 'coletar')
    .addItem('Ligar a coleta diária (6h)', 'ligarColetaDiaria')
    .addItem('Mostrar link para conectar as redes', 'mostrarLinkConexao')
    .addToUi();
}

const CHAVES = [
  ['TIKTOK_CLIENT_KEY', 'Client key do app do TikTok'],
  ['TIKTOK_CLIENT_SECRET', 'Client secret do app do TikTok'],
  ['META_APP_ID', 'ID do app da Meta'],
  ['META_APP_SECRET', 'Chave secreta do app da Meta'],
  ['META_CONFIG_ID', 'ID da configuração do Login do Facebook para Empresas (opcional)'],
  ['PAGINA', 'Nome da página do Facebook (opcional, só se tiver mais de uma)'],
];

/** Pede cada chave numa janelinha e guarda nas propriedades do script (ninguém mais vê). */
function configurarChaves() {
  const ui = SpreadsheetApp.getUi();
  for (const [k, desc] of CHAVES) {
    const tem = prop(k) ? ' (já preenchida; deixe em branco para manter)' : '';
    const r = ui.prompt('Configurar chaves', desc + tem + ':', ui.ButtonSet.OK_CANCEL);
    if (r.getSelectedButton() !== ui.Button.OK) break;
    const v = r.getResponseText().trim();
    if (v) props().setProperty(k, v);
  }
  ui.alert('Chaves guardadas. Agora use Métricas > Mostrar link para conectar as redes.');
}

/** URL de retorno do login: a do app da Web deste script (ou a da propriedade REDIRECT_URI). */
function retorno() {
  return props().getProperty('REDIRECT_URI') || ScriptApp.getService().getUrl() || '';
}

function ligarColetaDiaria() {
  ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'coletar').forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('coletar').timeBased().everyDays(1).atHour(6).inTimezone('America/Sao_Paulo').create();
  avisar('Coleta diária ligada: todo dia por volta das 6h.');
}

function mostrarLinkConexao() {
  const url = retorno();
  avisar(url ? 'Abra este link no navegador (logado na sua conta Google):\n\n' + url
    : 'O script ainda não foi publicado como app da Web. Veja o passo a passo em metricas/LEIAME.md.');
}

function avisar(msg) {
  try { SpreadsheetApp.getUi().alert(msg); } catch (e) { console.log(msg); }
}

// ---------------------------------------------------------------- conexão (OAuth), feita uma vez

function doGet(e) {
  const p = (e && e.parameter) || {};
  try {
    if (p.code && p.state) return pagina(callback(p));
    if (p.error) return pagina('A rede recusou a conexão: ' + seguro(p.error_description || p.error));
    return pagina(inicio());
  } catch (err) {
    return pagina('Deu erro: ' + seguro(err.message));
  }
}

function pagina(html) {
  return HtmlService.createHtmlOutput('<div style="font:16px/1.5 sans-serif;max-width:560px;margin:32px auto">' + html + '</div>')
    .setTitle('Métricas thebestnewsbr');
}

function inicio() {
  const red = retorno();
  if (!red) return 'Não achei a URL deste app da Web (terminada em /exec); preencha a propriedade <b>REDIRECT_URI</b>.';
  const links = [];
  if (prop('META_APP_ID')) {
    const q = { client_id: prop('META_APP_ID'), redirect_uri: red, state: novoEstado('meta'), response_type: 'code' };
    if (prop('META_CONFIG_ID')) q.config_id = prop('META_CONFIG_ID'); else q.scope = META_ESCOPOS.join(',');
    links.push(botao('https://www.facebook.com/' + META_V + '/dialog/oauth?' + qs(q), 'Conectar Instagram e Facebook'));
  }
  if (prop('TIKTOK_CLIENT_KEY')) {
    const q = { client_key: prop('TIKTOK_CLIENT_KEY'), scope: TT_ESCOPOS.join(','), response_type: 'code',
      redirect_uri: red, state: novoEstado('tiktok') };
    links.push(botao('https://www.tiktok.com/v2/auth/authorize/?' + qs(q), 'Conectar TikTok'));
  }
  const st = [];
  st.push('Instagram/Facebook: ' + (prop('META_PAGE_TOKEN') ? 'conectado' : 'não conectado'));
  st.push('TikTok: ' + (prop('TT_REFRESH') ? 'conectado' : 'não conectado'));
  return '<h2>Conectar as redes</h2><p>' + st.join('<br>') + '</p>' +
    (links.length ? links.join('') : '<p>Preencha primeiro as propriedades META_APP_ID e/ou TIKTOK_CLIENT_KEY.</p>');
}

function botao(href, txt) {
  return '<p><a target="_top" href="' + href + '" style="display:inline-block;padding:12px 18px;background:#2a40f0;color:#fff;' +
    'border-radius:8px;text-decoration:none">' + txt + '</a></p>';
}

function novoEstado(rede) {
  const n = Utilities.getUuid();
  props().setProperty('ESTADO_' + rede, n);
  return rede + ':' + n;
}

function callback(p) {
  const [rede, n] = String(p.state).split(':');
  if (!n || prop('ESTADO_' + rede) !== n) throw new Error('link vencido ou de outra origem; abra a página de conexão de novo');
  props().deleteProperty('ESTADO_' + rede);
  return rede === 'meta' ? conectarMeta(p.code) : conectarTikTok(p.code);
}

function conectarMeta(code) {
  const G = 'https://graph.facebook.com/' + META_V;
  const curto = jget(G + '/oauth/access_token', { client_id: prop('META_APP_ID'), client_secret: prop('META_APP_SECRET'),
    redirect_uri: retorno(), code: code });
  const longo = jget(G + '/oauth/access_token', { grant_type: 'fb_exchange_token', client_id: prop('META_APP_ID'),
    client_secret: prop('META_APP_SECRET'), fb_exchange_token: curto.access_token });
  // a chave da página tirada de uma chave longa de usuário não vence
  const contas = jget(G + '/me/accounts', { fields: 'id,name,access_token,instagram_business_account{id,username}',
    limit: 100, access_token: longo.access_token }).data || [];
  if (!contas.length) throw new Error('nenhuma página do Facebook voltou; marque a página na tela de permissões');
  const alvo = prop('PAGINA');
  const pag = (alvo && contas.find(c => c.id === alvo || c.name === alvo)) ||
    contas.find(c => c.instagram_business_account) || contas[0];
  props().setProperties({ META_PAGE_ID: pag.id, META_PAGE_TOKEN: pag.access_token,
    META_IG_ID: pag.instagram_business_account ? pag.instagram_business_account.id : '' });
  const ig = pag.instagram_business_account ? '@' + pag.instagram_business_account.username
    : '<b>nenhum Instagram ligado a esta página</b> (ligue o Instagram à página e conecte de novo)';
  return '<h2>Pronto</h2><p>Página do Facebook: <b>' + seguro(pag.name) + '</b><br>Instagram: ' + ig + '</p>' +
    '<p>Pode fechar esta aba. Na planilha, use o menu Métricas &gt; Coletar agora.</p>';
}

function conectarTikTok(code) {
  const r = jpost('https://open.tiktokapis.com/v2/oauth/token/', { client_key: prop('TIKTOK_CLIENT_KEY'),
    client_secret: prop('TIKTOK_CLIENT_SECRET'), code: code, grant_type: 'authorization_code',
    redirect_uri: retorno() });
  if (!r.refresh_token) throw new Error('o TikTok não devolveu a chave: ' + seguro(r.error_description || r.error || ''));
  const falta = TT_ESCOPOS.filter(s => String(r.scope || '').indexOf(s) < 0);
  props().setProperties({ TT_REFRESH: r.refresh_token, TT_OPEN_ID: r.open_id || '' });
  return '<h2>Pronto</h2><p>TikTok conectado.' + (falta.length ? ' <b>Faltou a permissão: ' + falta.join(', ') + '</b>' : '') +
    '</p><p>A conexão vale por 1 ano; o script renova sozinho a cada coleta.</p>';
}

// ---------------------------------------------------------------- coleta

function coletar() {
  const t0 = Date.now();
  const linhas = [], erros = [];
  [['instagram', coletarInstagram], ['facebook', coletarFacebook], ['tiktok', coletarTikTok]].forEach(([rede, f]) => {
    try { linhas.push(...f()); } catch (e) { erros.push(rede + ': ' + seguro(e.message)); }
  });
  gravar(linhas);
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ex = aba(ss, ABA_EXEC, ['quando', 'posts', 'erros', 'segundos']);
  ex.appendRow([new Date(), linhas.length, erros.join(' | '), Math.round((Date.now() - t0) / 1000)]);
  if (erros.length) console.log('erros: ' + erros.join(' | '));
  return { posts: linhas.length, erros: erros };
}

function desde() { return Date.now() - DIAS * 86400000; }

function coletarInstagram() {
  const ig = prop('META_IG_ID'), tk = prop('META_PAGE_TOKEN');
  if (!ig || !tk) return [];
  const G = 'https://graph.facebook.com/' + META_V;
  const out = [];
  let url = G + '/' + ig + '/media?' + qs({ fields: 'id,caption,media_product_type,media_type,permalink,timestamp', limit: 50, access_token: tk });
  while (url) {
    const r = jget(url);
    let velho = false;
    (r.data || []).forEach(m => {
      if (Date.parse(m.timestamp) < desde()) { velho = true; return; }
      if (m.media_product_type !== 'REELS' && m.media_type !== 'VIDEO') return;
      const v = insights(G + '/' + m.id + '/insights', tk,
        ['views', 'reach', 'likes', 'comments', 'shares', 'saved', 'ig_reels_avg_watch_time', 'reels_skip_rate']);
      out.push({ rede: 'instagram', id: m.id, data_post: new Date(m.timestamp), link: m.permalink, legenda: m.caption || '',
        duracao_s: '', views: v.views, alcance: v.reach, curtidas: v.likes, comentarios: v.comments,
        compartilhamentos: v.shares, salvamentos: v.saved, seguidores_ganhos: '',
        tempo_medio_s: num(v.ig_reels_avg_watch_time) === '' ? '' : v.ig_reels_avg_watch_time / 1000,
        pulos_3s_pct: v.reels_skip_rate });
    });
    url = !velho && r.paging && r.paging.next ? r.paging.next : null;
  }
  return out;
}

function coletarFacebook() {
  const pg = prop('META_PAGE_ID'), tk = prop('META_PAGE_TOKEN');
  if (!pg || !tk) return [];
  const G = 'https://graph.facebook.com/' + META_V;
  const out = [];
  let url = G + '/' + pg + '/video_reels?' + qs({ fields: 'id,description,created_time,permalink_url,length', limit: 50, access_token: tk });
  while (url) {
    const r = jget(url);
    let velho = false;
    (r.data || []).forEach(m => {
      if (m.created_time && Date.parse(m.created_time) < desde()) { velho = true; return; }
      const v = insights(G + '/' + m.id + '/video_insights', tk,
        ['blue_reels_play_count', 'post_impressions_unique', 'post_video_avg_time_watched', 'post_video_followers',
          'post_video_likes_by_reaction_type', 'post_video_social_actions']);
      const soc = v.post_video_social_actions;
      out.push({ rede: 'facebook', id: m.id, data_post: m.created_time ? new Date(m.created_time) : '',
        link: m.permalink_url ? (String(m.permalink_url).indexOf('http') === 0 ? m.permalink_url : 'https://www.facebook.com' + m.permalink_url) : '',
        legenda: m.description || '', duracao_s: m.length || '', views: v.blue_reels_play_count,
        alcance: v.post_impressions_unique, curtidas: soma(v.post_video_likes_by_reaction_type),
        comentarios: parte(soc, 'COMMENT'), compartilhamentos: parte(soc, 'SHARE'), salvamentos: '',
        seguidores_ganhos: v.post_video_followers,
        tempo_medio_s: num(v.post_video_avg_time_watched) === '' ? '' : v.post_video_avg_time_watched / 1000, pulos_3s_pct: '' });
    });
    url = !velho && r.paging && r.paging.next ? r.paging.next : null;
  }
  return out;
}

function coletarTikTok() {
  const refresh = prop('TT_REFRESH');
  if (!refresh) return [];
  const tok = jpost('https://open.tiktokapis.com/v2/oauth/token/', { client_key: prop('TIKTOK_CLIENT_KEY'),
    client_secret: prop('TIKTOK_CLIENT_SECRET'), grant_type: 'refresh_token', refresh_token: refresh });
  if (!tok.access_token) throw new Error('não renovou a conexão (' + seguro(tok.error_description || tok.error || '') + '); conecte o TikTok de novo');
  if (tok.refresh_token) props().setProperty('TT_REFRESH', tok.refresh_token);
  const campos = 'id,title,video_description,create_time,duration,share_url,view_count,like_count,comment_count,share_count';
  const out = [];
  let cursor = null, mais = true, voltas = 0;
  while (mais && voltas++ < 20) {
    const corpo = { max_count: 20 };
    if (cursor) corpo.cursor = cursor;
    const r = UrlFetchApp.fetch('https://open.tiktokapis.com/v2/video/list/?fields=' + campos, {
      method: 'post', contentType: 'application/json', payload: JSON.stringify(corpo),
      headers: { Authorization: 'Bearer ' + tok.access_token }, muteHttpExceptions: true });
    const j = JSON.parse(r.getContentText() || '{}');
    if (j.error && j.error.code && j.error.code !== 'ok') throw new Error(j.error.code + ': ' + seguro(j.error.message || ''));
    const d = j.data || {};
    let velho = false;
    (d.videos || []).forEach(v => {
      if (v.create_time * 1000 < desde()) { velho = true; return; }
      out.push({ rede: 'tiktok', id: v.id, data_post: new Date(v.create_time * 1000), link: v.share_url || '',
        legenda: v.video_description || v.title || '', duracao_s: v.duration || '', views: v.view_count, alcance: '',
        curtidas: v.like_count, comentarios: v.comment_count, compartilhamentos: v.share_count, salvamentos: '',
        seguidores_ganhos: '', tempo_medio_s: '', pulos_3s_pct: '' });
    });
    mais = !!d.has_more && !velho;
    cursor = d.cursor;
  }
  return out;
}

/** Pede todas as métricas de uma vez; se a API recusar alguma (métrica nova ou "em desenvolvimento"), pede uma a uma. */
function insights(base, tk, metricas) {
  const ler = j => {
    const o = {};
    (j.data || []).forEach(x => { o[x.name] = x.values && x.values.length ? x.values[x.values.length - 1].value : x.total_value ? x.total_value.value : ''; });
    return o;
  };
  const r = jgetSemErro(base + '?' + qs({ metric: metricas.join(','), access_token: tk }));
  if (!r.error) return ler(r);
  const o = {};
  metricas.forEach(m => {
    const u = jgetSemErro(base + '?' + qs({ metric: m, access_token: tk }));
    if (!u.error) Object.assign(o, ler(u));
  });
  return o;
}

// ---------------------------------------------------------------- planilha

function gravar(linhas) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = aba(ss, ABA, COLS, 0);
  const dados = sh.getDataRange().getValues();
  const idx = {};
  for (let i = 1; i < dados.length; i++) idx[dados[i][0] + '|' + dados[i][1]] = i;
  const agora = new Date();
  const hist = [];
  linhas.forEach(l => {
    const k = l.rede + '|' + l.id;
    let linha = idx[k] !== undefined ? dados[idx[k]] : null;
    const idade = l.data_post ? (agora - l.data_post) / 3600000 : 0;
    const v48 = linha ? linha[COLS.indexOf('views_48h')] : '';
    const v7 = linha ? linha[COLS.indexOf('views_7d')] : '';
    l.views_48h = v48 !== '' ? v48 : (idade >= 48 ? num(l.views) : '');
    l.views_7d = v7 !== '' ? v7 : (idade >= 168 ? num(l.views) : '');
    l.atualizado_em = agora;
    const nova = COLS.map(c => (l[c] === undefined || l[c] === null) ? '' : (typeof l[c] === 'object' && !(l[c] instanceof Date) ? JSON.stringify(l[c]) : l[c]));
    if (linha) dados[idx[k]] = nova; else { idx[k] = dados.length; dados.push(nova); }
    hist.push([agora, l.rede, l.id, num(l.views), num(l.curtidas), num(l.compartilhamentos), num(l.salvamentos), num(l.tempo_medio_s)]);
  });
  if (dados.length > 1) sh.getRange(1, 1, dados.length, COLS.length).setValues(dados.map(r => r.slice(0, COLS.length)));
  const h = aba(ss, ABA_HIST, ['quando', 'rede', 'id', 'views', 'curtidas', 'compartilhamentos', 'salvamentos', 'tempo_medio_s']);
  if (hist.length) h.getRange(h.getLastRow() + 1, 1, hist.length, hist[0].length).setValues(hist);
}

function aba(ss, nome, cabecalho, posicao) {
  let sh = ss.getSheetByName(nome);
  if (!sh) {
    sh = ss.insertSheet(nome, posicao === undefined ? ss.getSheets().length : posicao);
    sh.appendRow(cabecalho);
    sh.setFrozenRows(1);
  }
  return sh;
}

// ---------------------------------------------------------------- utilidades

function props() { return PropertiesService.getScriptProperties(); }
function prop(k) { return props().getProperty(k) || ''; }
function qs(o) { return Object.keys(o).map(k => encodeURIComponent(k) + '=' + encodeURIComponent(o[k])).join('&'); }
function num(v) { const n = Number(v); return v === '' || v === undefined || v === null || isNaN(n) ? '' : n; }
function soma(v) {
  if (v && typeof v === 'object') return Object.keys(v).reduce((a, k) => a + (Number(v[k]) || 0), 0);
  return num(v);
}
function parte(v, chave) {
  if (v && typeof v === 'object') { const k = Object.keys(v).find(x => x.toUpperCase() === chave); return k ? num(v[k]) : 0; }
  return '';
}
/** nunca deixa chave aparecer em mensagem de erro */
function seguro(s) { return String(s || '').replace(/(access_token|client_secret|refresh_token|code)=[^&\s]+/gi, '$1=***').slice(0, 300); }

function jgetSemErro(url, params) {
  const r = UrlFetchApp.fetch(params ? url + '?' + qs(params) : url, { muteHttpExceptions: true });
  try { return JSON.parse(r.getContentText() || '{}'); } catch (e) { return { error: { message: 'resposta inválida (' + r.getResponseCode() + ')' } }; }
}

function jget(url, params) {
  const j = jgetSemErro(url, params);
  if (j.error) throw new Error((j.error.message || JSON.stringify(j.error)) + (j.error.code ? ' (código ' + j.error.code + ')' : ''));
  return j;
}

function jpost(url, form) {
  const r = UrlFetchApp.fetch(url, { method: 'post', payload: form, muteHttpExceptions: true,
    contentType: 'application/x-www-form-urlencoded' });
  try { return JSON.parse(r.getContentText() || '{}'); } catch (e) { return { error: 'resposta inválida (' + r.getResponseCode() + ')' }; }
}
