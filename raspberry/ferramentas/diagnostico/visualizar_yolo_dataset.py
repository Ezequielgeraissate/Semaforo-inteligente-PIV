import cv2
import json
import subprocess
from pathlib import Path

origem = Path("capturas/testes_dataset")
destino = origem / "visualizacoes"

destino.mkdir(
    parents=True,
    exist_ok=True
)

for caminho in sorted(origem.iterdir()):

    if caminho.suffix.lower() not in {
        ".jpg",
        ".jpeg",
        ".png"
    }:
        continue

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
            except:
                pass

    imagem = cv2.imread(
        str(caminho)
    )

    if imagem is None:
        continue

    for d in deteccoes:

        x1 = int(d["x1"])
        y1 = int(d["y1"])
        x2 = int(d["x2"])
        y2 = int(d["y2"])

        classe = d["classe"]
        score = d["score"]

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

        cv2.putText(
            imagem,
            texto,
            (x1, max(30, y1 - 10)),
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
        caminho.name,
        "->",
        len(deteccoes),
        "detecções"
    )
