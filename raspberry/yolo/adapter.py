import subprocess
import json


def analisar_imagem(caminho_imagem):

    processo = subprocess.run(
        [
            "./yolo/modelo/yolo_fastest",
            str(caminho_imagem)
        ],
        capture_output=True,
        text=True
    )

    if processo.returncode != 0:
        raise RuntimeError(
            processo.stderr
        )

    resultado = json.loads(
        processo.stdout
    )

    return resultado
