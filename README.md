# redacao-fato

Pipeline do vídeo diário de fatos do **thebestnewsbr**. Recebe três arquivos JSON escritos pelos agentes (ficha, roteiro e cenas) e devolve um vídeo vertical de cerca de 60 s, feito com [HyperFrames](https://hyperframes.heygen.com). O vídeo tem narração (edge-tts), legenda com a palavra falada em destaque, fonte na tela e a identidade da marca.

- Manual dos agentes, com os contratos e o fluxo: [AGENTS.md](AGENTS.md)
- Pauta de exemplo: [exemplos/teste-acervo](exemplos/teste-acervo)

## Preparar o ambiente (uma vez por máquina ou sandbox)

```bash
bash setup.sh
```

O script precisa de Python 3.10 ou mais novo, Node 22 ou mais novo e FFmpeg. Ele instala o `edge-tts` e prepara o Chrome do HyperFrames. A versão do HyperFrames fica fixa em `fato/comum.py` (`HF_VERSAO`).

## Rodar

```bash
python -m fato validar exemplos/teste-acervo
python -m fato revisar exemplos/teste-acervo
python -m fato render  exemplos/teste-acervo
```

Medido num notebook Windows: `revisar` leva cerca de 1 min e `render` cerca de 3 min para um vídeo de 62 s.

## Estrutura

- `fato/validar.py`: regras dos três arquivos. Cada erro diz para qual agente volta.
- `fato/narrar.py`: voz por bloco, corte de silêncio, −16 LUFS e ajuste de velocidade (de −10% a +20%). Também calcula o tempo de cada palavra e liga cada cena à sua âncora.
- `fato/familias.py` e `fato/mapas.py`: as famílias de cena (seis básicas, mais mapa do Brasil e globo).
- `fato/som.py`: efeitos sonoros e trilha (opcional, em `modelo/assets/trilhas/`).
- `modelo/assets/lib/mascote.js` e `globo.js`: o mascote e o globo em Three.js. O globo usa a imagem Blue Marble da NASA, que é de domínio público, e a malha dos estados é a do IBGE.
- `fato/gerar.py`: monta o projeto HyperFrames (fundo, cenas, legenda e barra de progresso).
- `fato/__main__.py`: os comandos, a checagem, a folha de quadros e a conferência do vídeo.
- `modelo/`: fontes e logo copiados para cada projeto.
