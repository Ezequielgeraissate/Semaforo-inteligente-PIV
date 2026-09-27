import requests
from datetime import datetime

from config import (
    ESP_CAPTURE_URL,
    PASTA_CAPTURAS
)


def capturar_imagem(via_sensor):

    PASTA_CAPTURAS.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Solicitando foto ao ESP32-CAM...")

    resposta = requests.get(
        ESP_CAPTURE_URL,
        timeout=10
    )

    if resposta.status_code != 200:
        raise RuntimeError(
            f"ESP32-CAM retornou HTTP "
            f"{resposta.status_code}"
        )

    if len(resposta.content) == 0:
        raise RuntimeError(
            "ESP32-CAM retornou imagem vazia."
        )

    horario = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    nome = (
        f"via_{via_sensor}_"
        f"{horario}.jpg"
    )

    caminho = PASTA_CAPTURAS / nome

    caminho.write_bytes(
        resposta.content
    )

    print(
        f"Imagem salva em: {caminho}"
    )

    return caminho
