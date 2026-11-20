"""Mixagem: narração + efeitos sonoros nas ações visíveis + trilha opcional (abaixa sozinha quando a voz fala)."""
import hashlib
from pathlib import Path

from .comum import MODELO, rodar

SFX = MODELO / "assets" / "sfx"
TRILHAS = MODELO / "assets" / "trilhas"


def eventos(cenas, tempos):
    """Lista (arquivo, tempo, volume) sincronizada com as entradas das cenas."""
    ev = []
    for i, (s, tp) in enumerate(zip(cenas, tempos)):
        ta = tp["ini"] + tp["ancora"]
        if i > 0:
            ev.append(("whoosh", max(0, tp["ini"] - 0.08), 0.22))
        for bt in tp.get("batidas", []):              # tique discreto em cada "soco" de zoom
            ev.append(("click", tp["ini"] + bt, 0.10))
        fam = s["familia"]
        if fam == "numero_heroi":
            ev.append(("pop", ta + 1.05, 0.30))          # o contador chega no valor
        elif fam in ("dado_comparado",):
            ev.append(("click", ta + 0.4, 0.28))
        elif fam == "mapa_brasil":
            ev.append(("pop", ta + 1.2, 0.30))           # rótulo do estado em destaque
        elif fam == "mapa_lugar":
            ev.append(("pop", ta + 1.4, 0.30))           # pino
        elif fam == "fecho_chamada":
            ev.append(("chime", ta + 0.5, 0.25))
    return [(SFX / f"{n}.mp3", round(t, 3), v) for n, t, v in ev if (SFX / f"{n}.mp3").exists()]


# categoria da pauta -> pastas de trilha, em ordem de preferência
POR_CATEGORIA = {"ciencia": ["ciencia", "tecnologia"], "tecnologia": ["tecnologia", "ciencia"],
                 "brasil": ["brasil", "mundo"], "mundo": ["mundo", "brasil"], "games": ["games", "tecnologia"]}


def escolher_trilha(semente: str, categoria: str = ""):
    """Escolhe uma trilha da categoria da pauta (a mesma pauta sempre recebe a mesma trilha)."""
    pastas = POR_CATEGORIA.get((categoria or "").strip().lower(), [])
    lista = []
    for p in pastas:
        lista = sorted((TRILHAS / p).glob("*.mp3"))
        if lista:
            break
    if not lista:
        lista = sorted(TRILHAS.rglob("*.mp3"))
    if not lista:
        return None
    k = int(hashlib.sha1(semente.encode("utf-8")).hexdigest(), 16) % len(lista)
    return lista[k]


def mixar(voz: Path, evs, total, saida: Path, trilha: Path = None):
    entradas = ["-i", voz]
    filtros = ["[0]aresample=48000,aformat=channel_layouts=stereo" + (",asplit=2[voz][vozsc]" if trilha else "[voz]")]
    mix = ["[voz]"]
    for k, (arq, t, vol) in enumerate(evs, 1):
        entradas += ["-i", arq]
        filtros.append(f"[{k}]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={int(t * 1000)}:all=1[s{k}]")
        mix.append(f"[s{k}]")
    n = len(evs) + 1
    if trilha:
        entradas += ["-stream_loop", "-1", "-i", trilha]
        # cada faixa é normalizada antes (as do banco têm volumes diferentes) para a trilha ficar
        # ~12 LU abaixo da voz: presente, sem brigar com a fala
        filtros.append(f"[{n}]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total + 1},"
                       f"loudnorm=I=-27:TP=-5:LRA=11,aresample=48000,atrim=0:{total},"
                       f"afade=t=in:d=0.4,afade=t=out:st={max(0, total - 1.5)}:d=1.5[bgm0]")
        # a voz abaixa a trilha um pouco (sidechain suave); a voz em si segue limpa
        filtros.append("[bgm0][vozsc]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=400[bgm]")
        mix.append("[bgm]")
    filtros.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:dropout_transition=0,"
                   f"atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[out]")
    rodar("ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex", ";".join(filtros),
          "-map", "[out]", "-ar", "48000", "-ac", "2", "-t", total, saida)
    return {"efeitos": len(evs), "trilha": trilha.name if trilha else None}
