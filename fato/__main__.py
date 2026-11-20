"""Comando único do pipeline. Rode a partir da raiz do repositório:

  python -m fato validar  PASTA   # confere ficha, roteiro e cenas (rápido, sem voz)
  python -m fato revisar  PASTA   # validar + voz + projeto + check + folha de quadros (para o Revisor, etapa B)
  python -m fato render   PASTA   # render do vídeo final + conferência (só depois do "aprovado" na etapa B)

PASTA tem ficha.json, roteiro.json e cenas.json. Tudo o que é gerado fica em PASTA/saida/.
Cada comando grava PASTA/saida/relatorio.json e sai com código 0 (ok), 2 (volta para um agente) ou 1 (falha técnica).
"""
import json
import re
import shutil
import sys
import time
from pathlib import Path

from .comum import Falha, duracao, ler_json, npx_hf, rodar, salvar_json
from .gerar import gerar
from .narrar import batidas, narrar, tempos_cenas
from .som import escolher_trilha, eventos, mixar
from .linguagem import legibilidade, validar_publicacao, validar_revisao
from .validar import validar_cenas, validar_ficha, validar_roteiro


def _carregar(pasta: Path):
    ficha, roteiro, cenas = (ler_json(pasta / n) for n in ("ficha.json", "roteiro.json", "cenas.json"))
    validar_ficha(ficha)
    av = validar_roteiro(roteiro)
    e_leg, av_leg, facilidade = legibilidade(roteiro)
    if e_leg:
        raise Falha("roteiro", e_leg, av_leg)
    av += av_leg
    av += validar_cenas(cenas, roteiro, ficha, pasta)
    ling = validar_revisao(pasta)
    ling["facilidade_leitura"] = facilidade
    pub = validar_publicacao(pasta)
    av += pub.pop("avisos")
    ling["publicacao"] = pub
    return ficha, roteiro, cenas["cenas"], cenas.get("tema", ""), av, ling


def cmd_validar(pasta: Path, saida: Path):
    *_, av, ling = _carregar(pasta)
    return {"etapa": "validar", "ok": True, "linguagem": ling, "avisos": av}


def _check(projeto: Path):
    r = npx_hf("check", "--json", cwd=projeto, check=False)
    try:
        dados = json.loads(r.stdout[r.stdout.index("{"):])
    except (ValueError, json.JSONDecodeError):
        return {"ok": r.returncode == 0, "bruto": (r.stdout + r.stderr)[-3000:]}
    return dados


def _resumo_check(dados):
    """Extrai erros e avisos do JSON do `hyperframes check` (o formato pode variar entre versões)."""
    erros, avisos = [], []

    def anda(x):
        if isinstance(x, dict):
            sev = str(x.get("severity", x.get("level", ""))).lower()
            msg = x.get("message") or x.get("msg") or x.get("rule")
            # a legenda fica perto do pé da tela por escolha do dono: avisos de área segura dela não contam
            if msg and "legenda.html" in str(x.get("sourceFile", "")) and "safe area" in str(msg):
                return
            if msg and sev in ("error", "erro"):
                erros.append(f"{x.get('rule', '')}: {msg} {x.get('file', '') or ''}".strip())
            elif msg and sev in ("warning", "warn"):
                avisos.append(f"{x.get('rule', '')}: {msg} {x.get('file', '') or ''}".strip())
            for v in x.values():
                anda(v)
        elif isinstance(x, list):
            for v in x:
                anda(v)
    anda(dados)
    # o perfil não publica no YouTube Shorts: avisos só dele não contam
    avisos = [a for a in avisos if not re.search(r"safe area: YouTube Shorts \([^)]*\)\.?$", a)]
    # a legenda fica centralizada por escolha do dono: a coluna de botões do TikTok pode cobrir a ponta direita
    avisos = [a for a in avisos if not re.search(r"safe area: TikTok \(right edge\)(, YouTube Shorts \([^)]*\))?\.?$", a)]
    # tamanho do arquivo da legenda é gerado pelo código, não é problema de quem revisa
    avisos = [a for a in avisos if "HTML composition file has" not in a]
    return sorted(set(erros)), sorted(set(avisos))


def _folha(projeto: Path, saida: Path, cenas, tempos):
    quad = saida / "quadros"
    if quad.exists():
        shutil.rmtree(quad)
    ts = []
    for s, tp in zip(cenas, tempos):
        # depois que o título entrou: âncora + 1,4 s, sem passar do fim da cena
        ts.append(round(min(tp["ini"] + tp["ancora"] + 1.4, tp["fim"] - 0.35), 2))
    r = npx_hf("snapshot", "--at", ",".join(f"{t:g}" for t in ts), "--no-end", "--output", quad, "--json",
               cwd=projeto, check=False)
    pngs = sorted(quad.glob("*.png"), key=lambda p: float(re.sub(r"[^\d.]", "", p.stem.replace("at-", "")) or 0))
    if len(pngs) < len(ts):
        raise RuntimeError("snapshot não gerou todos os quadros:\n" + (r.stdout + r.stderr)[-2000:])
    for k, p in enumerate(pngs, 1):
        p.rename(quad / f"cena{k:02d}.png")
    linhas = (len(ts) + 5) // 6
    rodar("ffmpeg", "-y", "-v", "error", "-i", quad / "cena%02d.png",
          "-vf", f"scale=360:-1,tile=6x{linhas}:padding=8:color=0x333333", "-frames:v", "1", saida / "folha.png")
    return [{"cena": s["id"], "tempo": t, "arquivo": f"quadros/cena{s['id']:02d}.png"} for s, t in zip(cenas, ts)]


def cmd_revisar(pasta: Path, saida: Path):
    ficha, roteiro, cenas, tema, av, ling = _carregar(pasta)
    t0 = time.time()
    wav = saida / "narracao.wav"
    narr = narrar(roteiro, saida / "voz", wav)
    av += narr.pop("avisos")
    tempos = batidas(tempos_cenas(cenas, narr), narr)
    for s_, tp in zip(cenas, tempos):
        if tp["fim"] - tp["ini"] > 6.5:
            av.append(f"cena {s_['id']} dura {tp['fim'] - tp['ini']:.1f} s: acima de 6,5 s o vídeo perde ritmo; vale dividir")
    salvar_json(saida / "tempos.json", {"narracao": narr, "cenas": [dict(id=s["id"], **t) for s, t in zip(cenas, tempos)]})
    mixado = saida / "trilha.wav"
    som = mixar(wav, eventos(cenas, tempos), narr["total"], mixado, escolher_trilha(tema or pasta.name, ficha.get("categoria", "")))
    projeto = saida / "projeto"
    from . import gerar as _g
    _g.AVISOS.clear()
    srt = gerar(projeto, cenas, tempos, narr, mixado, titulo=tema, pasta=pasta)
    av += _g.AVISOS
    (saida / "legendas.srt").write_text(srt, encoding="utf-8")
    chk = _check(projeto)
    erros, avisos_chk = _resumo_check(chk)
    salvar_json(saida / "check.json", chk)
    folha = _folha(projeto, saida, cenas, tempos)
    return {"etapa": "revisar", "ok": not erros, "duracao_s": narr["total"], "velocidade_voz": narr["rate"],
            "linguagem": ling, "som": som, "folha": "folha.png", "quadros": folha, "legendas": "legendas.srt",
            "check_erros": erros, "check_avisos": avisos_chk, "avisos": av,
            "para_o_revisor": "Confira folha.png (uma imagem por cena), legendas.srt e as listas de avisos.",
            "tempo_s": round(time.time() - t0, 1)}


def cmd_render(pasta: Path, saida: Path):
    projeto = saida / "projeto"
    if not (projeto / "index.html").exists():
        raise Falha("render", [{"para": "Coordenador", "msg": "rode 'revisar' antes de 'render'"}])
    t0 = time.time()
    video = saida / "video.mp4"
    r = npx_hf("render", "--quality", "delivery", "--output", video, "--quiet", cwd=projeto, check=False)
    if r.returncode != 0 or not video.exists():
        raise RuntimeError("render falhou:\n" + (r.stdout + r.stderr)[-3000:])
    conf = conferir(video, ler_json(saida / "tempos.json")["narracao"]["total"])
    conf["tempo_render_min"] = round((time.time() - t0) / 60, 1)
    if conf["ok"]:
        conf["entrega"] = entregar(pasta, saida, video)
    return conf


def entregar(pasta: Path, saida: Path, video: Path):
    """A entrega é só isto: o vídeo e um .txt com a descrição pronta para colar (hashtags no fim)."""
    pub = ler_json(pasta / "publicacao.json")
    texto = str(pub["descricao"]).strip() + "\n\n" + " ".join(pub["hashtags"]) + "\n"
    dest = saida / "entrega"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir()
    nome = pasta.name
    shutil.copy(video, dest / f"{nome}.mp4")
    (dest / f"{nome}.txt").write_text(texto, encoding="utf-8")
    return {"pasta": "saida/entrega", "video": f"{nome}.mp4", "descricao": f"{nome}.txt"}


def conferir(video: Path, alvo: float):
    r = rodar("ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate",
              "-show_entries", "format=duration", "-of", "json", video)
    info = json.loads(r.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    lufs = None
    if a:
        m = re.search(r"I:\s+(-?[\d.]+) LUFS", rodar("ffmpeg", "-nostats", "-i", video, "-vn", "-af", "ebur128",
                                                      "-f", "null", "-", check=False).stderr.split("Summary:")[-1])
        lufs = float(m.group(1)) if m else None
    problemas = []
    if not 58 <= dur <= 65.5:
        problemas.append(f"duração {dur:.1f} s fora de 58 a 65 s")
    if (v.get("width"), v.get("height")) != (1080, 1920):
        problemas.append(f"resolução {v.get('width')}x{v.get('height')}")
    if v.get("r_frame_rate") not in ("30/1", "30000/1000"):
        problemas.append(f"quadros por segundo {v.get('r_frame_rate')}")
    if not a:
        problemas.append("sem áudio")
    elif lufs is None or abs(lufs + 16) > 1.0:
        problemas.append(f"volume {lufs} LUFS (alvo -16)")
    if abs(dur - alvo) > 0.2:
        problemas.append(f"duração {dur:.2f} s diferente da narração ({alvo:.2f} s)")
    return {"etapa": "render", "ok": not problemas, "video": "video.mp4", "duracao_s": round(dur, 2),
            "resolucao": f"{v.get('width')}x{v.get('height')}", "fps": v.get("r_frame_rate"),
            "audio": bool(a), "lufs": lufs, "problemas": problemas}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    if len(sys.argv) != 3 or sys.argv[1] not in ("validar", "revisar", "render"):
        print(__doc__)
        sys.exit(1)
    cmd, pasta = sys.argv[1], Path(sys.argv[2]).resolve()
    saida = pasta / "saida"
    saida.mkdir(parents=True, exist_ok=True)
    try:
        rel = {"validar": cmd_validar, "revisar": cmd_revisar, "render": cmd_render}[cmd](pasta, saida)
        cod = 0 if rel.get("ok") else 2
    except Falha as f:
        rel = {"etapa": f.etapa, "ok": False, "erros": f.erros, "avisos": f.avisos}
        cod = 2
    except Exception as ex:  # falha técnica: não é culpa de nenhum agente
        rel = {"etapa": cmd, "ok": False, "falha_tecnica": f"{type(ex).__name__}: {ex}"}
        cod = 1
    salvar_json(saida / "relatorio.json", rel)
    print(json.dumps(rel, ensure_ascii=False, indent=2))
    sys.exit(cod)


if __name__ == "__main__":
    main()
