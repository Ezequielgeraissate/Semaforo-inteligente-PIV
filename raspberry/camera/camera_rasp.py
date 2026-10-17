import subprocess

from datetime import datetime

from config import (
    PASTA_CAPTURAS,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    CAMERA_TIMEOUT_MS
)


def capturar_imagem(
    via_sensor
):

    # ================================================
    # PASTA
    # ================================================

    PASTA_CAPTURAS.mkdir(
        parents=True,
        exist_ok=True
    )


    # ================================================
    # NOME DA IMAGEM
    # ================================================

    horario = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S_%f"
        )
    )


    nome = (
        f"via_{via_sensor}_"
        f"{horario}.jpg"
    )


    caminho = (
        PASTA_CAPTURAS
        / nome
    )


    # ================================================
    # RASPICAM
    # ================================================

    comando = [

        "rpicam-still",

        "--nopreview",

        "--timeout",
        str(
            CAMERA_TIMEOUT_MS
        ),

        "--width",
        str(
            CAMERA_WIDTH
        ),

        "--height",
        str(
            CAMERA_HEIGHT
        ),

        "--output",
        str(
            caminho
        )
    ]


    print(
        f"Capturando imagem da Via {via_sensor} "
        "com a camera da Raspberry..."
    )


    processo = subprocess.run(

        comando,

        capture_output=True,

        text=True
    )


    # ================================================
    # ERRO
    # ================================================

    if (
        processo.returncode
        != 0
    ):

        raise RuntimeError(
            "Erro na captura da camera:\n"
            + processo.stderr
        )


    # ================================================
    # VALIDAR ARQUIVO
    # ================================================

    if (
        not caminho.exists()
        or
        caminho.stat().st_size == 0
    ):

        raise RuntimeError(
            "A camera nao gerou "
            "uma imagem valida."
        )


    print(
        f"Imagem salva em: {caminho}"
    )


    return caminho
