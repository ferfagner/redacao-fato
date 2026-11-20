"""Tratamento automático das fotos antes de entrarem no vídeo.

- natural: redimensiona, dá um pouco de contraste, cor e nitidez (padrão);
- marca:   duotone nas cores da marca (do quase preto ao cobalto claro), bom para fotos fracas ou de cores ruins;
- recorte: tira o fundo (pessoa ou objeto) com o `hyperframes remove-background` e põe sobre o fundo da marca.

Editar não muda a licença: a foto continua precisando de licença livre e crédito.
"""
from pathlib import Path

from .comum import npx_hf, rodar

TRATAMENTOS = ("natural", "marca", "recorte")


def tratar(orig: Path, pasta_assets: Path, nome: str, tratamento: str = "natural", cwd: Path = None):
    """Grava a foto tratada em pasta_assets e devolve (nome_do_arquivo, tratamento_aplicado, aviso)."""
    pasta_assets.mkdir(parents=True, exist_ok=True)
    escala = "scale='min(1600,iw)':-2"
    if tratamento == "recorte":
        png = pasta_assets / f"{nome}.png"
        r = npx_hf("remove-background", orig, "-o", png, cwd=cwd, check=False)
        if r.returncode == 0 and png.exists():
            return png.name, "recorte", None
        tratamento = "marca"
        aviso = "o recorte da foto falhou; usei o tratamento 'marca'"
    else:
        aviso = None
    saida = pasta_assets / f"{nome}.jpg"
    if tratamento == "marca":
        filtro = (f"{escala},format=gray,eq=contrast=1.15,format=rgb24,"
                  "lutrgb=r='15+val*123/255':g='15+val*134/255':b='23+val*232/255'")
    else:
        filtro = f"{escala},eq=contrast=1.06:saturation=1.08,unsharp=5:5:0.6"
    rodar("ffmpeg", "-y", "-v", "error", "-i", orig, "-vf", filtro, "-q:v", "3", saida)
    return saida.name, tratamento, aviso
