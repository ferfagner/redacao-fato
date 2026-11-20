"""Funções comuns do pipeline."""
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "modelo"
HF_VERSAO = "0.9.72"

BLOCOS = ["gancho", "fato", "mecanismo", "virada", "ressalva", "chamada"]
FAMILIAS = ["numero_heroi", "tipo_cinetico", "dado_comparado", "objeto_profundidade", "citacao_fonte", "fecho_chamada",
            "mapa_brasil", "mapa_lugar"]
POSES = ["fala", "aponta", "surpreso", "pensa", "comemora", "nega"]
UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
       "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]


class Falha(Exception):
    """Erro que volta para um agente. `para` diz quem corrige."""

    def __init__(self, etapa, erros, avisos=None):
        super().__init__(f"{etapa}: {len(erros)} erro(s)")
        self.etapa, self.erros, self.avisos = etapa, erros, avisos or []


def erro(para, msg, cena=None):
    e = {"para": para, "msg": msg}
    if cena is not None:
        e["cena"] = cena
    return e


def ler_json(p: Path):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise Falha("entrada", [erro("Coordenador", f"arquivo não encontrado: {Path(p).name}")])
    except json.JSONDecodeError as e:
        raise Falha("entrada", [erro("Coordenador", f"{Path(p).name} não é JSON válido: {e}")])


def salvar_json(p: Path, dados):
    Path(p).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def exe(nome):
    e = shutil.which(nome)
    if not e:
        sys.exit(f"{nome} não encontrado no PATH")
    return e


def rodar(*args, cwd=None, check=True):
    return subprocess.run([exe(args[0]), *map(str, args[1:])], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=cwd, check=check)


def npx_hf(*args, cwd=None, check=True):
    return rodar("npx", "--yes", f"hyperframes@{HF_VERSAO}", *args, cwd=cwd, check=check)


def duracao(arq) -> float:
    r = rodar("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq)
    return float(r.stdout.strip())


def norm(s: str) -> str:
    """minúsculas, sem acento e sem pontuação (para comparar palavras)."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w%]+", "", s)


def palavras(texto: str):
    return [w for w in texto.split() if norm(w)]
