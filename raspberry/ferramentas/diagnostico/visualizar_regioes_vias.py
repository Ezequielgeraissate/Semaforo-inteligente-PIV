import sys
from pathlib import Path

import cv2

from yolo.adapter import analisar_imagem

# ==========================================================
# COLE AQUI AS MESMAS COORDENADAS QUE VOCÊS USAM NO
# mapeamento_vias.py
#
# Formato:
# "VIA": (x1, y1, x2, y2)
# ==========================================================
REGIOES_VIAS = {
    "A": (1200, 1000, 1700, 1944),
    "B": (0, 700, 1100, 1200),
    "C": (1000, 0, 1500, 900),
    "D": (1500, 500, 2592, 1000),
}

CORES = {
    "A": (0, 255, 0),      # verde
    "B": (255, 0, 0),      # azul
    "C": (0, 255, 255),    # amarelo
    "D": (255, 0, 255),    # magenta
    "FORA": (0, 0, 255),   # vermelho
}


def via_do_ponto(px, py):
    for via, (x1, y1, x2, y2) in REGIOES_VIAS.items():
        if x1 <= px <= x2 and y1 <= py <= y2:
            return via
    return "FORA"


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 visualizar_regioes_vias.py caminho_da_imagem.jpg")
        sys.exit(1)

    imagem_path = sys.argv[1]
    img = cv2.imread(imagem_path)

    if img is None:
        print(f"Erro ao abrir imagem: {imagem_path}")
        sys.exit(1)

    # 1) desenha as regiões das vias
    for via, (x1, y1, x2, y2) in REGIOES_VIAS.items():
        cor = CORES[via]
        cv2.rectangle(img, (x1, y1), (x2, y2), cor, 2)
        cv2.putText(
            img,
            f"VIA {via}",
            (x1 + 5, max(20, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            cor,
            2,
            cv2.LINE_AA,
        )

    # 2) roda o YOLO
    detecoes = analisar_imagem(imagem_path)

    contagem = {"A": 0, "B": 0, "C": 0, "D": 0, "FORA": 0}

    # 3) desenha boxes e o ponto usado pelo algoritmo
    for i, det in enumerate(detecoes, start=1):
        x1 = int(det["x1"])
        y1 = int(det["y1"])
        x2 = int(det["x2"])
        y2 = int(det["y2"])
        classe = det["classe"]
        score = det["score"]

        # PONTO USADO PELO ALGORITMO:
        # centro inferior da bounding box
        px = (x1 + x2) // 2
        py = y2

        via = via_do_ponto(px, py)
        contagem[via] += 1

        # box branca da detecção
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 2)

        # ponto usado na classificação
        cv2.circle(img, (px, py), 6, CORES[via], -1)

        texto = f"{i}: cls={classe} sc={score:.2f} -> {via}"
        cv2.putText(
            img,
            texto,
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            CORES[via],
            2,
            cv2.LINE_AA,
        )

        print(
            f"Det {i}: classe={classe} score={score:.3f} "
            f"box=({x1},{y1},{x2},{y2}) ponto=({px},{py}) via={via}"
        )

    print("\n=== CONTAGEM FINAL ===")
    for via in ["A", "B", "C", "D", "FORA"]:
        print(f"Via {via}: {contagem[via]}")

    saida = Path(imagem_path).with_name(Path(imagem_path).stem + "_regioes.jpg")
    cv2.imwrite(str(saida), img)
    print(f"\nImagem salva em: {saida}")


if __name__ == "__main__":
    main()

