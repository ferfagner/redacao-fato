#!/usr/bin/env bash
# Prepara o ambiente para o pipeline (Linux do Manus ou máquina local). Pode rodar de novo sem problema.
set -uo pipefail
cd "$(dirname "$0")"

SUDO=""
if [ "$(id -u)" != "0" ] && command -v sudo >/dev/null 2>&1; then SUDO="sudo"; fi
tem() { command -v "$1" >/dev/null 2>&1; }
apt_instala() {   # instala um pacote por vez: um nome que não existe nesta versão não derruba os outros
  tem apt-get || return 0
  for p in "$@"; do $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$p" >/dev/null 2>&1 || echo "  (aviso) não instalei $p"; done
}

echo "== sistema"
if tem apt-get; then $SUDO apt-get update -qq >/dev/null 2>&1 || true; fi
tem python3 || apt_instala python3
python3 -m pip --version >/dev/null 2>&1 || apt_instala python3-pip
tem ffmpeg || apt_instala ffmpeg
tem ffprobe || { echo "ERRO: falta ffmpeg/ffprobe"; exit 1; }
# bibliotecas que o Chrome sem tela precisa no Linux (nomes variam entre versões do Ubuntu/Debian)
if [ "$(uname -s)" = "Linux" ]; then
  apt_instala libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxrandr2 libxfixes3 libgbm1 libpango-1.0-0 libcairo2 fonts-liberation fonts-noto-color-emoji
  apt_instala libasound2t64 || true
  apt_instala libasound2 || true
fi

echo "== python"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || { echo "ERRO: precisa de Python 3.10 ou mais novo"; exit 1; }
python3 -m pip install -q -r requirements.txt 2>/dev/null \
  || python3 -m pip install -q --user -r requirements.txt 2>/dev/null \
  || python3 -m pip install -q --user --break-system-packages -r requirements.txt \
  || { echo "ERRO: não consegui instalar o edge-tts"; exit 1; }
python3 -c "import edge_tts" || { echo "ERRO: edge-tts não importa"; exit 1; }

echo "== node"
versao_node() { node -e 'console.log(parseInt(process.versions.node))' 2>/dev/null || echo 0; }
if [ "$(versao_node)" -lt 22 ]; then
  echo "  Node ausente ou antigo ($(versao_node)); instalando o Node 22 (NodeSource)"
  if tem apt-get && tem curl; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO -E bash - >/dev/null 2>&1 && apt_instala nodejs
  fi
fi
[ "$(versao_node)" -ge 22 ] || { echo "ERRO: precisa de Node 22 ou mais novo (tenho $(versao_node))"; exit 1; }

echo "== hyperframes"
HF=$(python3 -c "from fato.comum import HF_VERSAO; print(HF_VERSAO)")
npx --yes "hyperframes@$HF" browser ensure >/dev/null 2>&1 || { echo "ERRO: não consegui preparar o Chrome do HyperFrames"; exit 1; }
# o recorte de fundo das fotos instala um componente na primeira vez: faz isso já, com a foto de exemplo
npx --yes "hyperframes@$HF" remove-background exemplos/teste-acervo/imagens/dom-pedro-ii.jpg -o /tmp/recorte-teste.png >/dev/null 2>&1   && echo "  recorte de fundo: ok" || echo "  (aviso) recorte de fundo indisponível; fotos com tratamento 'recorte' vão sair como 'marca'"
# o doctor marca como falha itens opcionais (ex.: whisper); só os obrigatórios contam
npx --yes "hyperframes@$HF" doctor --json 2>/dev/null | python3 -c "
import json, sys
s = sys.stdin.read(); d = json.loads(s[s.index('{'):])
ruins = [c for c in d.get('checks', []) if not c.get('ok') and 'optional' not in str(c.get('detail', '')).lower()]
for c in ruins: print('  (aviso)', c.get('name'), '-', c.get('detail'))
print('  doctor: ok' if not ruins else '  doctor: veja os avisos acima')
"

echo "== conferência"
python3 -m fato validar exemplos/teste-acervo >/dev/null && echo "pipeline pronto"
