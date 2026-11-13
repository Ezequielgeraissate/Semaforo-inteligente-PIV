import cv2
import json
import subprocess
from pathlib import Path

origem = Path("capturas/testes")
destino = origem / "visualizacoes_yolo"

destino.mkdir(
    parents=True,
    exist_ok=True
)

extensoes = {
    ".jpg",
    ".jpeg",
    ".png"
}

for caminho in sorted(origem.iterdir()):

    if caminho.suffix.lower() not in extensoes:
        continue

    print()
    print("=" * 70)
    print("Imagem:", caminho.name)
    print("=" * 70)

    resultado = subprocess.run(
        [
            "./yolo/modelo/yolo_fastest",
            str(caminho.resolve())
        ],
        capture_output=True,
        text=True
    )

    deteccoes = []

    for linha in resultado.stdout.splitlines():

        linha = linha.strip()

        if linha.startswith("[") and linha.endswith("]"):

            try:
                deteccoes = json.loads(linha)
            except json.JSONDecodeError:
                pass

    imagem = cv2.imread(
        str(caminho)
    )

    if imagem is None:

        print("ERRO ao abrir a imagem.")
        continue

    print(
        "Detecções:",
        len(deteccoes)
    )

    for i, d in enumerate(
        deteccoes,
        start=1
    ):

        x1 = int(d["x1"])
        y1 = int(d["y1"])
        x2 = int(d["x2"])
        y2 = int(d["y2"])

        classe = int(d["classe"])
        score = float(d["score"])

        print(
            f"{i}: "
            f"classe={classe} "
            f"score={score:.3f} "
            f"box=({x1},{y1})-({x2},{y2})"
        )

        cv2.rectangle(
            imagem,
            (x1, y1),
            (x2, y2),
            (255, 255, 255),
            4
        )

        texto = (
            f"classe={classe} "
            f"{score:.2f}"
        )

        posicao_y = max(
            30,
            y1 - 10
        )

        cv2.putText(
            imagem,
            texto,
            (x1, posicao_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

    saida = (
        destino
        / f"{caminho.stem}_yolo.jpg"
    )

    cv2.imwrite(
        str(saida),
        imagem
    )

    print(
        "Salvo em:",
        saida
    )
