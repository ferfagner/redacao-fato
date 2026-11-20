#!/usr/bin/env bash
# Prepara o ambiente para o pipeline (Linux do Manus ou máquina local).
set -euo pipefail
cd "$(dirname "$0")"

command -v python3 >/dev/null || { echo "falta Python 3.10+"; exit 1; }
command -v node >/dev/null || { echo "falta Node 22+"; exit 1; }
if ! command -v ffmpeg >/dev/null; then
  if command -v apt-get >/dev/null; then sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg; else echo "falta FFmpeg"; exit 1; fi
fi

python3 -m pip install -q -r requirements.txt
HF=$(python3 -c "from fato.comum import HF_VERSAO; print(HF_VERSAO)")
npx --yes "hyperframes@$HF" browser ensure
npx --yes "hyperframes@$HF" doctor --json | python3 -c "import json,sys; d=json.load(sys.stdin); print('doctor ok' if d.get('ok') else d)"
python3 -m fato validar exemplos/censo-2022 >/dev/null && echo "pipeline pronto"
