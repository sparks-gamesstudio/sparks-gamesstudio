"""Atualiza os números, os últimos vídeos e o humor do Rebite no README do perfil e publica.

Uso: python atualizar.py   (roda depois de publicar vídeos)
"""
import datetime
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).parent
CANAIS = pathlib.Path(r"F:\Vídeo com IA\Canais")
INSTAGRAM = {"Canal 1": "boleiro3d", "Canal 2": "afabricadecanais"}
ULTIMOS = 4


def postados(canal):
    pastas = []
    for nome in ("Postados", "Postados produtos"):
        base = CANAIS / canal / nome
        if base.is_dir():
            pastas += [p for p in base.iterdir() if (p / "video.mp4").exists()]
    return pastas


def bloco(readme, nome, conteudo):
    padrao = re.compile(rf"(<!-- {nome}:inicio -->).*?(<!-- {nome}:fim -->)", re.S)
    return padrao.sub(lambda m: f"{m[1]}\n{conteudo}\n{m[2]}", readme)


def main():
    todos = {c: postados(c) for c in INSTAGRAM}
    total = sum(len(v) for v in todos.values())
    no_ar = sum(1 for v in todos.values() if v)
    numeros = (
        f'<img src="https://img.shields.io/badge/🎬_vídeos_postados-{total}-D97757?style=for-the-badge" alt="{total} vídeos postados" /> '
        f'<img src="https://img.shields.io/badge/📺_canais_no_ar-{no_ar}-0B0A09?style=for-the-badge" alt="{no_ar} canais no ar" />'
    )

    recentes = sorted(
        ((p, c) for c, ps in todos.items() for p in ps),
        key=lambda pc: (pc[0] / "video.mp4").stat().st_mtime,
        reverse=True,
    )[:ULTIMOS]
    thumbs = REPO / "assets" / "ultimos"
    thumbs.mkdir(parents=True, exist_ok=True)
    for velho in thumbs.glob("*.jpg"):
        velho.unlink()
    celulas = []
    for i, (pasta, canal) in enumerate(recentes, 1):
        capa = pasta / "capa.png"
        destino = thumbs / f"{i}.jpg"
        fonte = capa if capa.exists() else pasta / "video.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(fonte), "-frames:v", "1",
                        "-vf", "scale=180:-1", "-q:v", "5", str(destino)], check=True)
        titulo = pasta.name.split(" - ", 1)[-1]
        celulas.append(
            f'<td align="center" width="25%"><a href="https://instagram.com/{INSTAGRAM[canal]}">'
            f'<img src="assets/ultimos/{i}.jpg" width="140" alt="{titulo}" /></a><br/><sub>{titulo}</sub></td>'
        )
    ultimos = "<table><tr>\n" + "\n".join(celulas) + "\n</tr></table>"

    # Rebite muda de humor: comemora no fim de semana, pensa na segunda, acena ou dá joinha no resto
    dia = datetime.date.today().weekday()
    humor = {0: "pensar", 5: "comemorar", 6: "comemorar"}.get(dia, "acenar" if dia % 2 else "joinha")
    rebite = f'<img align="right" src="assets/rebite/{humor}.jpg" width="200" alt="Rebite, o mascote" />'

    arquivo = REPO / "README.md"
    readme = arquivo.read_text(encoding="utf-8")
    novo = bloco(bloco(bloco(readme, "numeros", numeros), "ultimos", ultimos), "rebite", rebite)
    if novo == readme and not subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                                             capture_output=True, text=True).stdout:
        print("Nada mudou.")
        return
    arquivo.write_text(novo, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=REPO, check=True)
    subprocess.run(["git", "commit", "-qm", f"Atualiza perfil: {total} vídeos postados"], cwd=REPO, check=True)
    subprocess.run(["git", "pull", "-q", "--rebase"], cwd=REPO, check=True)
    subprocess.run(["git", "push", "-q"], cwd=REPO, check=True)
    print(f"Perfil atualizado: {total} vídeos, {no_ar} canais, Rebite {humor}.")


if __name__ == "__main__":
    main()
