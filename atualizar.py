"""Atualiza os números, as conquistas, os últimos vídeos e o humor do Rebite no README do perfil e publica.

Uso: python atualizar.py   (roda no fim da rotina de publicar do Canal 2)
"""
import csv
import datetime
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).parent
CANAIS = pathlib.Path(r"F:\Vídeo com IA\Canais")
INSTAGRAM = {"Canal 1": "boleiro3d", "Canal 2": "afabricadecanais"}
ULTIMOS = 4

TEXTOS = {
    "pt": {"arquivo": "README.md", "conquistas": "conquistas.svg",
           "postados": "vídeos_postados", "canais": "canais_no_ar", "views": "visualizações",
           "cartoes": ("vídeos postados", "canais no ar", "dias no ar", "na fila"),
           "titulo": "Conquistas da fábrica"},
    "en": {"arquivo": "README.en.md", "conquistas": "achievements.svg",
           "postados": "videos_posted", "canais": "channels_live", "views": "views",
           "cartoes": ("videos posted", "live channels", "days live", "in the queue"),
           "titulo": "Factory achievements"},
}


def postados(canal):
    pastas = []
    for nome in ("Postados", "Postados produtos"):
        base = CANAIS / canal / nome
        if base.is_dir():
            pastas += [p for p in base.iterdir() if (p / "video.mp4").exists()]
    return pastas


def na_fila(canal):
    total = 0
    for nome in ("Vídeos prontos", "Vídeos produtos prontos"):
        base = CANAIS / canal / nome
        if base.is_dir():
            total += sum(1 for p in base.iterdir() if (p / "video.mp4").exists())
    return total


def registro(canal):
    arquivo = CANAIS / canal / "registro.csv"
    if not arquivo.exists():
        return []
    with open(arquivo, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def numero(texto):
    try:
        return int(float(texto))
    except (TypeError, ValueError):
        return 0


def curto(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return str(n)


def svg_conquistas(titulo, cartoes):
    largura, alto = 200, 110
    blocos = []
    for i, (valor, rotulo, icone) in enumerate(cartoes):
        x = 10 + i * (largura + 14)
        blocos.append(
            f'<g transform="translate({x},44)">'
            f'<rect width="{largura}" height="{alto}" rx="14" fill="#16130F" stroke="#D97757" stroke-opacity=".45"/>'
            f'<text x="18" y="38" font-size="24">{icone}</text>'
            f'<text x="{largura - 18}" y="44" font-size="34" font-weight="800" fill="#D97757" text-anchor="end">{valor}</text>'
            f'<text x="18" y="88" font-size="15" fill="#F3EDE6">{rotulo}</text></g>'
        )
    w = 20 + len(cartoes) * (largura + 14) - 14
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="164" viewBox="0 0 {w} 164" '
        f'font-family="Segoe UI,Helvetica,Arial,sans-serif">'
        f'<rect width="100%" height="100%" rx="18" fill="#0B0A09"/>'
        f'<text x="20" y="30" font-size="16" font-weight="700" fill="#F3EDE6" letter-spacing="1">🏆 {titulo.upper()}</text>'
        + "".join(blocos) + "</svg>"
    )


def bloco(readme, nome, conteudo):
    padrao = re.compile(rf"(<!-- {nome}:inicio -->).*?(<!-- {nome}:fim -->)", re.S)
    return padrao.sub(lambda m: f"{m[1]}\n{conteudo}\n{m[2]}", readme)


def main():
    todos = {c: postados(c) for c in INSTAGRAM}
    total = sum(len(v) for v in todos.values())
    no_ar = sum(1 for v in todos.values() if v)
    fila = sum(na_fila(c) for c in INSTAGRAM)
    linhas = [l for c in INSTAGRAM for l in registro(c)]
    views = sum(numero(l.get("views")) for l in linhas)
    datas = [l["postado_em"][:10] for l in linhas if l.get("postado_em")]
    dias = (datetime.date.today() - datetime.date.fromisoformat(min(datas))).days + 1 if datas else 0

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
    rebite = f'<img align="right" src="assets/rebite/{humor}.jpg" width="200" alt="Rebite" />'

    for t in TEXTOS.values():
        selos = [
            f'<img src="https://img.shields.io/badge/🎬_{t["postados"]}-{total}-D97757?style=for-the-badge" alt="{total}" />',
            f'<img src="https://img.shields.io/badge/📺_{t["canais"]}-{no_ar}-0B0A09?style=for-the-badge" alt="{no_ar}" />',
        ]
        if views:  # só aparece quando o registro tiver visualizações preenchidas
            selos.append(f'<img src="https://img.shields.io/badge/👀_{t["views"]}-{curto(views)}-E4405F?style=for-the-badge" alt="{views}" />')
        valores = (total, no_ar, dias, fila)
        icones = ("🎬", "📺", "📅", "⏳")
        (REPO / "assets" / t["conquistas"]).write_text(
            svg_conquistas(t["titulo"], list(zip(valores, t["cartoes"], icones))), encoding="utf-8")

        arquivo = REPO / t["arquivo"]
        readme = arquivo.read_text(encoding="utf-8")
        readme = bloco(readme, "numeros", " ".join(selos))
        readme = bloco(readme, "ultimos", ultimos)
        readme = bloco(readme, "rebite", rebite)
        arquivo.write_text(readme, encoding="utf-8")

    if not subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True).stdout:
        print("Nada mudou.")
        return
    subprocess.run(["git", "add", "-A"], cwd=REPO, check=True)
    subprocess.run(["git", "commit", "-qm", f"Atualiza perfil: {total} vídeos postados"], cwd=REPO, check=True)
    subprocess.run(["git", "pull", "-q", "--rebase"], cwd=REPO, check=True)
    subprocess.run(["git", "push", "-q"], cwd=REPO, check=True)
    print(f"Perfil atualizado: {total} vídeos, {no_ar} canais, {dias} dias, {fila} na fila, {views} views, Rebite {humor}.")


if __name__ == "__main__":
    main()
