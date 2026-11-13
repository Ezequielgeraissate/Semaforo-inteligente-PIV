import sys
from pathlib import Path

import cv2
import numpy as np

from config import REGIOES_VIAS
from decisao.mapeamento_vias import localizar_via, ponto_representativo
from yolo.adapter import analisar_imagem


CORES = {
    "A": (0, 255, 0),       # verde
    "B": (255, 0, 0),       # azul
    "C": (0, 255, 255),     # amarelo
    "D": (255, 0, 255),     # rosa
    "FORA": (0, 0, 255)     # vermelho
}


def poligono_pixels(pontos_norm, largura, altura):
    pts = []
    for x, y in pontos_norm:
        pts.append([int(x * largura), int(y * altura)])
    return np.array(pts, dtype=np.int32)


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 visualizar_mapeamento_real.py caminho_da_imagem.jpg")
        sys.exit(1)

    caminho = Path(sys.argv[1])

    img = cv2.imread(str(caminho))
    if img is None:
        print(f"Erro ao abrir imagem: {caminho}")
        sys.exit(1)

    altura, largura = img.shape[:2]

    # desenhar regiões das vias
    for via, poligono_norm in REGIOES_VIAS.items():
        pol = poligono_pixels(poligono_norm, largura, altura)

        cv2.polylines(
            img,
            [pol],
            isClosed=True,
            color=CORES[via],
            thickness=3
        )

        cx = int(np.mean(pol[:, 0]))
        cy = int(np.mean(pol[:, 1]))

        cv2.putText(
            img,
            f"VIA {via}",
            (cx - 40, cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            CORES[via],
            2,
            cv2.LINE_AA
        )

    # rodar YOLO
    deteccoes = analisar_imagem(str(caminho))

    contagem = {
        "A": 0,
        "B": 0,
        "C": 0,
        "D": 0,
        "FORA": 0
    }

    for i, det in enumerate(deteccoes, start=1):
        x1 = int(det["x1"])
        y1 = int(det["y1"])
        x2 = int(det["x2"])
        y2 = int(det["y2"])
        classe = det["classe"]
        score = det["score"]

        via = localizar_via(det, largura=largura, altura=altura)
        if via is None:
            via_nome = "FORA"
        else:
            via_nome = via

        contagem[via_nome] += 1

        px, py = ponto_representativo(det)
        px = int(px)
        py = int(py)

        # bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 2)

        # ponto usado pelo algoritmo
        cv2.circle(img, (px, py), 5, CORES[via_nome], -1)

        texto = f"{i}: cls={classe} sc={score:.2f} -> {via_nome}"
        cv2.putText(
            img,
            texto,
            (x1, max(y1 - 10, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            CORES[via_nome],
            2,
            cv2.LINE_AA
        )

        print(
            f"Det {i}: classe={classe} score={score:.3f} "
            f"box=({x1},{y1},{x2},{y2}) ponto=({px},{py}) via={via_nome}"
        )

    print("\n=== CONTAGEM FINAL ===")
    for via in ["A", "B", "C", "D", "FORA"]:
        print(f"Via {via}: {contagem[via]}")

    saida = caminho.with_name(caminho.stem + "_mapeamento_real.jpg")
    cv2.imwrite(str(saida), img)

    print(f"\nImagem salva em: {saida}")


if __name__ == "__main__":
    main()
